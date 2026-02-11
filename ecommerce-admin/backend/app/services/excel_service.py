import pandas as pd
from datetime import datetime
from app.extensions import db
from app.models.order import Order
from app.models.purchase import Purchase
from app.models.logistics import Logistics
from app.models.product import Product
import logging

logger = logging.getLogger(__name__)

from decimal import Decimal, ROUND_HALF_UP

class ExcelService:
    @staticmethod
    def _parse_date(date_str):
        """解析日期格式"""
        if pd.isna(date_str) or date_str == '':
            return None
        try:
            return pd.to_datetime(date_str)
        except:
            return None

    @staticmethod
    def _parse_decimal(value, precision=2):
        """解析数值格式为Decimal"""
        if pd.isna(value) or value == '':
            return Decimal('0.0')
        try:
            # 如果已经是数字，转为字符串再转Decimal
            val_str = str(value).strip()
            
            # 提取数字部分 (支持负数和小数)
            import re
            match = re.search(r'-?\d+(\.\d+)?', val_str)
            if match:
                d = Decimal(match.group())
                return d.quantize(Decimal(f"0.{'0'*precision}"), rounding=ROUND_HALF_UP)
            return Decimal('0.0')
        except:
            return Decimal('0.0')

    @staticmethod
    def _parse_str(value):
        """解析字符串格式，处理NaN"""
        if pd.isna(value) or value == '':
            return None
        return str(value).strip()

    @staticmethod
    def preview_orders(file_path):
        """预览订单数据导入"""
        try:
            df = pd.read_excel(file_path)
            stats = {
                'total': len(df),
                'new': 0,
                'update': 0,
                'errors': [],
                'preview_data': [] # 前5条用于展示
            }

            for index, row in df.iterrows():
                try:
                    # 使用实际的列名 (基于 headers.txt)
                    platform_order_no = ExcelService._parse_str(row.get('订单编号')) or ExcelService._parse_str(row.get('订单编号(Order Number)'))
                    if not platform_order_no or platform_order_no == 'nan':
                        continue
                    
                    # Check existence
                    exists = db.session.query(Order.query.filter_by(platform_order_no=platform_order_no).exists()).scalar()
                    if exists:
                        stats['update'] += 1
                    else:
                        stats['new'] += 1
                    
                    # 仅收集前5条有效数据用于预览
                    if len(stats['preview_data']) < 5:
                        stats['preview_data'].append({
                            'order_no': platform_order_no,
                            'product': ExcelService._parse_str(row.get('商品名称(Product Name)')),
                            'amount': ExcelService._parse_decimal(row.get('订单总价(Order Amount)')),
                            'status': '更新' if exists else '新增'
                        })

                except Exception as e:
                    stats['errors'].append(f"Row {index + 2}: {str(e)}")
            
            return {'success': True, 'data': stats}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def import_orders(file_path):
        """导入订单数据"""
        try:
            df = pd.read_excel(file_path)
            
            success_count = 0
            errors = []
            created_skus = set()

            for index, row in df.iterrows():
                try:
                    # 使用实际的列名 (基于 headers.txt)
                    platform_order_no = ExcelService._parse_str(row.get('订单编号')) or ExcelService._parse_str(row.get('订单编号(Order Number)'))
                    if not platform_order_no or platform_order_no == 'nan':
                        continue

                    # 1. 优先提取并处理 SKU (Product)
                    sku_val = ExcelService._parse_str(row.get('SKU规格(Sku Specification)'))
                    product_val = ExcelService._parse_str(row.get('商品名称(Product Name)'))
                    
                    if sku_val:
                        if sku_val not in created_skus:
                            # 试图查找产品
                            product = Product.query.filter_by(sku=sku_val).first()
                            if not product:
                                # 不存在则创建并立即写入数据库
                                product = Product(sku=sku_val, name=product_val)
                                db.session.add(product)
                                db.session.flush() # 关键：必须在 Order 引用它之前写入
                            created_skus.add(sku_val)

                    # 2. 处理 Order
                    order = Order.query.filter_by(platform_order_no=platform_order_no).first()
                    if not order:
                        order = Order(platform_order_no=platform_order_no)
                    
                    # 映射字段
                    order.order_time = ExcelService._parse_date(row.get('订单创建时间(Order Create Time)'))
                    order.buyer_email = ExcelService._parse_str(row.get('邮箱(Email)'))
                    order.company_name = ExcelService._parse_str(row.get('公司名称(Company Name)'))
                    order.buyer_name = ExcelService._parse_str(row.get('买家名称(Buyer Name)'))
                    order.seller_name = ExcelService._parse_str(row.get('卖家名称(Seller Name)'))
                    order.product_name = product_val
                    order.sku = sku_val # 在 Product 确认存在后赋值
                    order.quantity = int(ExcelService._parse_decimal(row.get('数量(Quantity)')))
                    order.unit_price = ExcelService._parse_decimal(row.get('单价(Unit Price)'))
                    order.order_amount = ExcelService._parse_decimal(row.get('订单总价(Order Amount)'))
                    order.shipping_fee_income = ExcelService._parse_decimal(row.get('运费(Shipping Fee)'))
                    order.discount_amount = ExcelService._parse_decimal(row.get('折扣金额(Discount Amount)'))
                    order.order_status = ExcelService._parse_str(row.get('状态(Status)'))
                    order.order_type = ExcelService._parse_str(row.get('订单类型(Order Type)'))
                    order.buyer_country = ExcelService._parse_str(row.get('买家国家(Buyer Country)'))
                    order.tax_fee = ExcelService._parse_decimal(row.get('税费,仅美国卖家适用(Tax Fee)'))
                    order.shipping_address = ExcelService._parse_str(row.get('收货地址(Shipping Address)'))
                    order.remark = ExcelService._parse_str(row.get('订单备注(Order Remark)'))
                    order.currency = ExcelService._parse_str(row.get('订单币种(Order Currency)'))
                    
                    # 处理 "是否有合同附件(Attachment)"
                    has_attachment_str = str(row.get('是否有合同附件(Attachment)', '')).lower()
                    order.has_attachment = 'yes' in has_attachment_str or '是' in has_attachment_str

                    # 处理日期
                    order.actual_delivery_time = ExcelService._parse_date(row.get('实际发货时间(Actual Delivery Time)'))
                    
                    
                    db.session.add(order)
                    success_count += 1
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")
            
            db.session.commit()
            return {'success': True, 'count': success_count, 'errors': errors}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}

    @staticmethod
    def preview_purchases(file_path):
        """预览采购数据导入"""
        try:
            df = pd.read_excel(file_path)
            stats = {
                'total': len(df),
                'new': 0,
                'update': 0,
                'errors': [],
                'preview_data': [] # 前5条用于展示
            }

            for index, row in df.iterrows():
                try:
                    purchase_no = ExcelService._parse_str(row.get('订单编号'))
                    if not purchase_no or purchase_no == 'nan':
                        continue
                     
                    # Check existence
                    exists = db.session.query(Purchase.query.filter_by(purchase_no=purchase_no).exists()).scalar()
                    if exists:
                        stats['update'] += 1
                    else:
                        stats['new'] += 1
                    
                    # 仅收集前5条有效数据用于预览
                    if len(stats['preview_data']) < 5:
                        stats['preview_data'].append({
                            'purchase_no': purchase_no,
                            'product': ExcelService._parse_str(row.get('货品标题')),
                            'amount': ExcelService._parse_decimal(row.get('实付款(元)')),
                            'status': '更新' if exists else '新增'
                        })

                except Exception as e:
                    stats['errors'].append(f"Row {index + 2}: {str(e)}")
            
            return {'success': True, 'data': stats}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def import_purchases(file_path):
        """导入采购数据"""
        try:
            df = pd.read_excel(file_path)
            success_count = 0
            errors = []
            created_skus = set()

            for index, row in df.iterrows():
                try:
                    purchase_no = ExcelService._parse_str(row.get('订单编号'))
                    if not purchase_no or purchase_no == 'nan':
                        continue

                    # 1. 优先提取并处理 SKU
                    # 注意：采购单可能包含多行（多个SKU），这里简化处理，假设purchase_no不唯一或者是子单号
                    sku_val = ExcelService._parse_str(row.get('单品货号')) or ExcelService._parse_str(row.get('SKU ID'))
                    product_name_val = ExcelService._parse_str(row.get('货品标题'))

                    if sku_val:
                         if sku_val not in created_skus:
                             product = Product.query.filter_by(sku=sku_val).first()
                             if not product:
                                 product = Product(sku=sku_val, name=product_name_val)
                                 db.session.add(product)
                                 db.session.flush()
                             
                             # Update product cost and stock
                             try:
                                 unit_price = ExcelService._parse_decimal(row.get('单价(元)'))
                                 quantity = ExcelService._parse_decimal(row.get('数量'))
                                 
                                 if unit_price > 0:
                                    product.latest_purchase_price = unit_price
                                    # Simple average cost update logic (optional, for now just use latest as fallback)
                                    if product.avg_cost_price <= 0:
                                        product.avg_cost_price = unit_price
                                 
                                 # Increment stock
                                 product.stock_qty += int(quantity)
                             except Exception as e:
                                 logger.warning(f"Failed to update product info for {sku_val}: {e}")

                             created_skus.add(sku_val)
                    
                    # 2. 处理 Purchase
                    purchase = Purchase.query.filter_by(purchase_no=purchase_no).first()
                    if not purchase:
                        purchase = Purchase(purchase_no=purchase_no)

                    purchase.sku = sku_val
                    purchase.product_name = product_name_val
                    purchase.quantity = ExcelService._parse_decimal(row.get('数量'))
                    purchase.unit_price = ExcelService._parse_decimal(row.get('单价(元)'))
                    purchase.goods_amount = ExcelService._parse_decimal(row.get('货品总价(元)'))
                    purchase.shipping_fee = ExcelService._parse_decimal(row.get('运费(元)'))
                    purchase.discount = ExcelService._parse_decimal(row.get('涨价或折扣(元)'))
                    purchase.actual_payment = ExcelService._parse_decimal(row.get('实付款(元)'))
                    purchase.order_status = ExcelService._parse_str(row.get('订单状态'))
                    purchase.create_time = ExcelService._parse_date(row.get('订单创建时间'))
                    purchase.pay_time = ExcelService._parse_date(row.get('订单付款时间'))
                    purchase.supplier_company = ExcelService._parse_str(row.get('卖家公司名'))
                    purchase.supplier_member = ExcelService._parse_str(row.get('卖家会员名'))
                    purchase.buyer_company = ExcelService._parse_str(row.get('买家公司名'))
                    purchase.buyer_member = ExcelService._parse_str(row.get('买家会员名'))
                    purchase.logistics_company = ExcelService._parse_str(row.get('物流公司'))
                    purchase.logistics_no = ExcelService._parse_str(row.get('运单号'))
                    purchase.receiver_address = ExcelService._parse_str(row.get('收货地址'))
                    
                    db.session.add(purchase)
                    success_count += 1
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")

            db.session.commit()
            return {'success': True, 'count': success_count, 'errors': errors}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}

    @staticmethod
    def preview_logistics(file_path):
        """预览物流数据导入"""
        try:
            df = pd.read_excel(file_path)
            stats = {
                'total': len(df),
                'new': 0,
                'update': 0,
                'errors': [],
                'preview_data': [] # 前5条用于展示
            }

            for index, row in df.iterrows():
                try:
                    tracking_no = ExcelService._parse_str(row.get('国际物流单号'))
                    if not tracking_no or tracking_no == 'nan':
                         tracking_no = ExcelService._parse_str(row.get('物流订单号'))
                    
                    if not tracking_no or tracking_no == 'nan':
                        continue

                    # Check existence
                    exists = db.session.query(Logistics.query.filter_by(tracking_no=tracking_no).exists()).scalar()
                    if exists:
                        stats['update'] += 1
                    else:
                        stats['new'] += 1
                    
                    # 仅收集前5条有效数据用于预览
                    if len(stats['preview_data']) < 5:
                        stats['preview_data'].append({
                            'tracking_no': tracking_no,
                            'ref_no': ExcelService._parse_str(row.get('客户订单号')) or ExcelService._parse_str(row.get('信保订单号')),
                            'channel': ExcelService._parse_str(row.get('服务线路')),
                            'fee': ExcelService._parse_decimal(row.get('物流运费')),
                            'status': '更新' if exists else '新增'
                        })

                except Exception as e:
                    stats['errors'].append(f"Row {index + 2}: {str(e)}")
            
            return {'success': True, 'data': stats}
        except Exception as e:
            return {'success': False, 'message': str(e)}

    @staticmethod
    def import_logistics(file_path):
        """导入物流数据"""
        try:
            df = pd.read_excel(file_path)
            success_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    # 优先使用国际物流单号，如果没有则使用物流订单号
                    tracking_no = ExcelService._parse_str(row.get('国际物流单号'))
                    if not tracking_no or tracking_no == 'nan':
                         tracking_no = ExcelService._parse_str(row.get('物流订单号'))
                    
                    if not tracking_no or tracking_no == 'nan':
                        continue

                    logistics = Logistics.query.filter_by(tracking_no=tracking_no).first()
                    if not logistics:
                        logistics = Logistics(tracking_no=tracking_no)
                        db.session.add(logistics) # Add to session if new

                    # Update fields for both new and existing records
                    logistics.ref_no = ExcelService._parse_str(row.get('客户订单号')) or ExcelService._parse_str(row.get('信保订单号'))
                    logistics.logistics_channel = ExcelService._parse_str(row.get('服务线路'))
                    logistics.order_status = ExcelService._parse_str(row.get('货件状态'))
                    
                    logistics.sent_date = ExcelService._parse_date(row.get('出库时间'))
                    logistics.destination = ExcelService._parse_str(row.get('目的地'))
                    logistics.pre_weight = ExcelService._parse_decimal(row.get('预估计费重（KG）'), precision=3)
                    logistics.actual_weight = ExcelService._parse_decimal(row.get('实际计费重（KG）'), precision=3)
                    logistics.declared_value = ExcelService._parse_decimal(row.get('申报价值（美元）'))
                    
                    # Debug logging for fee parsing
                    shipping_fee_raw = row.get('物流运费')
                    shipping_fee_val = ExcelService._parse_decimal(shipping_fee_raw)
                    # logger.info(f"Tracking: {tracking_no}, Raw Fee: {shipping_fee_raw}, Parsed: {shipping_fee_val}")
                    
                    logistics.shipping_fee = shipping_fee_val
                    logistics.discount_fee = ExcelService._parse_decimal(row.get('优惠金额'))
                    logistics.actual_fee = ExcelService._parse_decimal(row.get('实付金额'))
                    logistics.payment_method = ExcelService._parse_str(row.get('支付方式'))
                    logistics.create_time = ExcelService._parse_date(row.get('订单创建时间'))
                    
                    success_count += 1
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")

            db.session.commit()
            return {'success': True, 'count': success_count, 'errors': errors}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
