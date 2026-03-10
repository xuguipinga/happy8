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
from app.models.stock import Inventory, StockRecord
from app.services.currency_service import CurrencyService

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
    def _parse_sku_specification(sku_str):
        """
        从阿里 SKU 规格字符串中提取型号 (Model) 和规格 (Spec)
        例如: "Color:Black-B002,Length:20 cm (7.87in)" -> ("B002", "20cm")
        """
        if not sku_str:
            return None, None
        
        import re
        model = None
        spec = None
        
        # 提取型号: 通常是连字符后的部分，或者独立的字母数字组合 (如 B002, B025)
        # 观察规律：型号通常在横杠 '-' 后面，或者在逗号前面
        model_match = re.search(r'-([A-Z0-9]+)', sku_str) # 匹配 -B002
        if model_match:
            model = model_match.group(1)
        else:
            # 如果没找到横杠，尝试匹配独立的型号模式 (如 B001)
            model_match = re.search(r'\b([A-Z]\d{3,})\b', sku_str)
            if model_match:
                model = model_match.group(1)
        
        # 提取规格 (长度): 匹配 "Length:XX cm" 
        spec_match = re.search(r'Length:(\d+)\s*cm', sku_str, re.IGNORECASE)
        if spec_match:
            spec = f"{spec_match.group(1)}cm"
            
        return model, spec

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
            df = pd.read_excel(file_path, dtype=str)
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
    def import_orders(file_path, tenant_id):
        """导入订单数据 - 自动设置租户ID"""
        try:
            df = pd.read_excel(file_path, dtype=str)
            
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
                    
                    # 简单产品处理
                    if sku_val:
                        product = Product.query.filter_by(sku=sku_val, tenant_id=tenant_id).first()
                        if not product:
                            # SKU不存在,创建新产品
                            product = Product(sku=sku_val, name=product_val, tenant_id=tenant_id)
                            db.session.add(product)
                            db.session.flush()

                    # 2. 处理 Order - 按 (订单号, SKU) 唯一确定一条记录
                    order = Order.query.filter_by(
                        platform_order_no=platform_order_no, 
                        sku=sku_val, 
                        tenant_id=tenant_id
                    ).first()
                    
                    if not order:
                        order = Order(
                            platform_order_no=platform_order_no, 
                            sku=sku_val,
                            tenant_id=tenant_id
                        )
                    
                    # 映射字段
                    order.order_time = ExcelService._parse_date(row.get('订单创建时间(Order Create Time)'))
                    order.buyer_email = ExcelService._parse_str(row.get('邮箱(Email)'))
                    order.company_name = ExcelService._parse_str(row.get('公司名称(Company Name)'))
                    order.buyer_name = ExcelService._parse_str(row.get('买家名称(Buyer Name)'))
                    order.seller_name = ExcelService._parse_str(row.get('卖家名称(Seller Name)'))
                    order.product_name = product_val
                    order.sku = sku_val
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
                    
                    # Mapping new fields
                    order.initial_payment = ExcelService._parse_decimal(row.get('预付款(Initial Payment)'))
                    order.balance_payment = ExcelService._parse_decimal(row.get('尾款(Balance Payment)'))
                    order.appointed_delivery_time = ExcelService._parse_date(row.get('约定发货时间(Appointed Delivery Time)'))
                    
                    # 处理 "是否有合同附件(Attachment)"
                    has_attachment_str = str(row.get('是否有合同附件(Attachment)', '')).lower()
                    order.has_attachment = 'yes' in has_attachment_str or '是' in has_attachment_str

                    # 处理日期
                    order.actual_delivery_time = ExcelService._parse_date(row.get('实际发货时间(Actual Delivery Time)'))
                    
                    # --- [智能库存关联与财务闭环逻辑] ---
                    # 1. 解析 SKU 提取型号和规格
                    model, spec = ExcelService._parse_sku_specification(sku_val)
                    if model:
                        # 查找关联的库存
                        inventory = Inventory.query.filter_by(
                            model=model, 
                            spec=spec, 
                            tenant_id=tenant_id
                        ).first()
                        
                        # 如果库存不存在，自动初始化一个 (数量为0)
                        if not inventory:
                            inventory = Inventory(
                                model=model, 
                                spec=spec, 
                                tenant_id=tenant_id,
                                quantity=0
                            )
                            db.session.add(inventory)
                            db.session.flush()

                        # 记录并扣减库存: 仅针对状态为已付款或已发货的订单，且未扣减过
                        paid_statuses = ['待卖家发货', '待买家确认收货', '发货中', '交易成功', '订单完成']
                        
                        # 判断是否已经生成过出库记录 (防止重复导入扣减)
                        already_deducted = False
                        if order.id:
                            already_deducted = db.session.query(StockRecord.query.filter_by(order_id=order.id, record_type='OUT').exists()).scalar()
                        
                        if not already_deducted and order.order_status in paid_statuses and inventory.quantity > 0:
                            qty_to_deduct = Decimal(str(order.quantity or 1))
                            
                            # 创建出库记录
                            record = StockRecord(
                                tenant_id=tenant_id,
                                inventory_id=inventory.id,
                                order_id=None, # 稍后在 flush 后关联
                                record_type='OUT',
                                change_quantity=-qty_to_deduct,
                                balance_quantity=inventory.quantity - qty_to_deduct,
                                unit_cost=inventory.avg_cost,
                                remark=f"Order {platform_order_no} auto-deduction"
                            )
                            inventory.quantity -= qty_to_deduct
                            db.session.add(record)
                            # 注意：我们这里先不 commit，外层会统一 commit
                            # 为了获取 order.id，我们需要在 add(order) 后关联
                            order._pending_stock_record = record # 临时暂存，同步后处理

                    # 2. 成本平衡 (计算毛利时考虑平台费)
                    product_obj = Product.query.filter_by(sku=sku_val, tenant_id=tenant_id).first()
                    platform_fee_rate = product_obj.platform_fee_rate if product_obj else Decimal('0.0')
                    
                    if not order.cost_price or order.cost_price == 0:
                        if product_obj:
                             # 优先使用 landed_cost (落地成本)
                             effective_unit_cost = product_obj.landed_cost or product_obj.avg_cost_price or Decimal('0.0')
                             order.cost_price = effective_unit_cost * (order.quantity or 0)
                    
                    # 计算毛利: (实收(CNY) * (1 - 平台费率)) - 成本 - 物流 - 税费
                    if order.order_amount is not None:
                        # 实收金额转换为人民币 (基于订单日期)
                        actual_paid_cny = CurrencyService.convert_to_cny(
                            order.actual_paid or order.order_amount, 
                            order.currency or 'USD', 
                            order.order_time
                        )
                        
                        cost_val = order.cost_price if order.cost_price else 0
                        logistics_val = order.logistics_cost if order.logistics_cost else 0
                        tax_val = order.tax_fee if order.tax_fee else 0
                        
                        # 净收入 = 实收(CNY) * (1 - 平台费率)
                        net_income = actual_paid_cny * (Decimal('1.0') - platform_fee_rate)
                        order.profit = net_income - cost_val - logistics_val - tax_val
                        
                        if cost_val > 0:
                            order.profit_rate = order.profit / cost_val
                    
                    db.session.add(order)
                    db.session.flush() # 获取 order.id
                    
                    # 关联库存流水
                    if hasattr(order, '_pending_stock_record'):
                        order._pending_stock_record.order_id = order.id
                    
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
            df = pd.read_excel(file_path, dtype=str)
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
    def import_purchases(file_path, tenant_id):
        """导入采购数据 - 自动设置租户ID"""
        try:
            df = pd.read_excel(file_path, dtype=str)
            success_count = 0
            errors = []

            for index, row in df.iterrows():
                try:
                    purchase_no = ExcelService._parse_str(row.get('订单编号'))
                    sku_val = ExcelService._parse_str(row.get('单品货号')) or ExcelService._parse_str(row.get('SKU ID')) or ExcelService._parse_str(row.get('货号'))
                    
                    if not purchase_no or purchase_no == 'nan':
                        continue
                        
                    # 解决没有SKU报错的问题
                    product_name_val = ExcelService._parse_str(row.get('货品标题'))
                    if not sku_val or sku_val.lower() == 'nan':
                        if product_name_val:
                            import hashlib
                            # 使用商品标题的MD5前8位作为未知SKU标识
                            sku_val = f"NO_SKU_{hashlib.md5(product_name_val.encode('utf-8')).hexdigest()[:8].upper()}"
                        else:
                            sku_val = f"NO_SKU_ROW_{index+2}"

                    # 0. 去重校验: 检查该采购单+SKU是否已经导入过
                    existing_purchase = Purchase.query.filter_by(
                        purchase_no=purchase_no, 
                        sku=sku_val, 
                        tenant_id=tenant_id
                    ).first()
                    
                    if existing_purchase:
                        # 如果已存在，我们仅更新基础信息，跳过库存逻辑（防止重复增加库存）
                        is_new_purchase = False
                        purchase = existing_purchase
                    else:
                        is_new_purchase = True
                        purchase = Purchase(purchase_no=purchase_no, tenant_id=tenant_id)
                    
                    # 1. 优先提取并处理 SKU (Product)
                    product_name_val = ExcelService._parse_str(row.get('货品标题'))
                    if sku_val:
                        product = Product.query.filter_by(sku=sku_val, tenant_id=tenant_id).first()
                        if not product:
                            product = Product(sku=sku_val, name=product_name_val, tenant_id=tenant_id)
                            db.session.add(product)
                            db.session.flush()

                    # 2. 处理 库存增加 (仅对新采购记录)
                    if is_new_purchase:
                        # 提取型号和规格
                        model, spec = ExcelService._parse_sku_specification(sku_val)
                        if not model:
                             # 尝试从标题匹配 (例如: "B025 黑 18cm")
                             import re
                             model_match = re.search(r'\b([A-Z]\d{3,})\b', product_name_val or '')
                             if model_match:
                                 model = model_match.group(1)
                        
                        if model:
                            inventory = Inventory.query.filter_by(
                                model=model, 
                                spec=spec, 
                                tenant_id=tenant_id
                            ).first()
                            
                            if not inventory:
                                inventory = Inventory(
                                    model=model, 
                                    spec=spec, 
                                    tenant_id=tenant_id,
                                    quantity=0,
                                    avg_cost=Decimal('0.0')
                                )
                                db.session.add(inventory)
                                db.session.flush()

                            in_qty = ExcelService._parse_decimal(row.get('数量'))
                            in_price = ExcelService._parse_decimal(row.get('单价(元)'))
                            shipping_fee = ExcelService._parse_decimal(row.get('运费(元)'))
                            actual_total = ExcelService._parse_decimal(row.get('货品总价(元)')) + shipping_fee
                            
                            if in_qty > 0:
                                # 计算本次采购的落地单价 (Landed Cost per unit)
                                landed_unit_price = actual_total / in_qty
                                
                                # 更新 Inventory 表的加权平均成本
                                current_quantity = inventory.quantity
                                current_avg_cost = inventory.avg_cost or Decimal('0.0')
                                
                                total_val = (current_quantity * current_avg_cost) + (in_qty * landed_unit_price)
                                new_qty = current_quantity + in_qty
                                if new_qty > 0:
                                    inventory.avg_cost = total_val / new_qty
                                
                                # 同时同步更新 Product 表的数据作为参考
                                product = Product.query.filter_by(sku=sku_val, tenant_id=tenant_id).first()
                                if product:
                                    product.latest_purchase_price = in_price
                                    product.landed_cost = landed_unit_price # 本次落地成本
                                    # 产品全局平均成本也更新
                                    product.avg_cost_price = inventory.avg_cost

                                # 创建入库记录
                                record = StockRecord(
                                    tenant_id=tenant_id,
                                    inventory_id=inventory.id,
                                    purchase_id=None, # 稍后关联
                                    record_type='IN',
                                    change_quantity=in_qty,
                                    balance_quantity=new_qty,
                                    unit_cost=land_unit_price,
                                    remark=f"Purchase {purchase_no} auto-inbound (Landed)"
                                )
                                inventory.quantity = new_qty
                                db.session.add(record)
                                purchase._pending_stock_record = record

                    # 3. 处理 Purchase 字段更新
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
                    
                    # Mapping new fields
                    purchase.receiver_name = ExcelService._parse_str(row.get('收货人姓名'))
                    purchase.receiver_phone = ExcelService._parse_str(row.get('联系电话'))
                    purchase.receiver_mobile = ExcelService._parse_str(row.get('联系手机'))
                    purchase.unit = ExcelService._parse_str(row.get('单位'))
                    purchase.model = ExcelService._parse_str(row.get('型号'))
                    purchase.material_no = ExcelService._parse_str(row.get('物料编号')) or ExcelService._parse_str(row.get('货号'))
                    purchase.buyer_note = ExcelService._parse_str(row.get('买家留言'))
                    
                    purchase.invoice_title = ExcelService._parse_str(row.get('发票：购货单位名称'))
                    purchase.tax_id = ExcelService._parse_str(row.get('发票：纳税人识别号'))
                    purchase.invoice_address_phone = ExcelService._parse_str(row.get('发票：地址、电话'))
                    purchase.invoice_bank_account = ExcelService._parse_str(row.get('发票：开户行及账号'))
                    purchase.invoice_receiver_address = ExcelService._parse_str(row.get('发票收取地址'))
                    
                    is_dropship_raw = str(row.get('是否代发订单', '')).lower()
                    purchase.is_dropship = '是' in is_dropship_raw or 'yes' in is_dropship_raw or '1' in is_dropship_raw
                    
                    purchase.upstream_order_no = ExcelService._parse_str(row.get('下游订单号')) or ExcelService._parse_str(row.get('关联编号'))
                    purchase.order_batch_no = ExcelService._parse_str(row.get('下单批次号'))
                    
                    purchase.shipper_name = ExcelService._parse_str(row.get('发货方'))
                    purchase.zip_code = ExcelService._parse_str(row.get('邮编'))
                    purchase.product_no = ExcelService._parse_str(row.get('货号'))
                    purchase.offer_id = ExcelService._parse_str(row.get('Offer ID'))
                    purchase.category = ExcelService._parse_str(row.get('货品种类'))
                    purchase.agent_name = ExcelService._parse_str(row.get('代理商姓名'))
                    purchase.agent_contact = ExcelService._parse_str(row.get('代理商联系方式'))
                    purchase.dropship_provider_id = ExcelService._parse_str(row.get('代发服务商id'))
                    purchase.micro_order_no = ExcelService._parse_str(row.get('微商订单号'))
                    purchase.downstream_channel = ExcelService._parse_str(row.get('下游渠道'))
                    purchase.order_company_entity = ExcelService._parse_str(row.get('下单公司主体'))
                    purchase.initiator_login_name = ExcelService._parse_str(row.get('发起人登录名'))
                    purchase.is_auto_pay = ExcelService._parse_str(row.get('是否发起免密支付(1:淘货源诚e赊免密支付2:批量下单免密支付)'))
                    
                    db.session.add(purchase)
                    db.session.flush()
                    
                    # 关联库存流水
                    if hasattr(purchase, '_pending_stock_record'):
                        purchase._pending_stock_record.purchase_id = purchase.id

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
            df = pd.read_excel(file_path, dtype=str)
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
    def import_logistics(file_path, tenant_id):
        """导入物流数据 - 自动设置租户ID"""
        try:
            df = pd.read_excel(file_path, dtype=str)
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
                        logistics = Logistics(tracking_no=tracking_no, tenant_id=tenant_id)
                        db.session.add(logistics) # Add to session if new

                    # Update fields for both new and existing records
                    logistics.ref_no = ExcelService._parse_str(row.get('客户订单号')) or ExcelService._parse_str(row.get('信保订单号'))
                    logistics.ordering_account = ExcelService._parse_str(row.get('下单账号'))
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
                    
                    # Mapping new fields
                    logistics.service_type = ExcelService._parse_str(row.get('服务类型'))
                    logistics.warehouse = ExcelService._parse_str(row.get('仓库'))
                    logistics.inbound_time = ExcelService._parse_date(row.get('入库时间'))
                    logistics.outbound_time = ExcelService._parse_date(row.get('出库时间'))
                    logistics.payment_time = ExcelService._parse_date(row.get('支付时间'))
                    logistics.customer_order_no = ExcelService._parse_str(row.get('客户订单号'))
                    logistics.sender_name = ExcelService._parse_str(row.get('发件人姓名'))
                    logistics.sender_email = ExcelService._parse_str(row.get('发件人邮件'))
                    
                    logistics.create_time = ExcelService._parse_date(row.get('订单创建时间'))
                    
                    success_count += 1
                except Exception as e:
                    errors.append(f"Row {index + 2}: {str(e)}")

            db.session.commit()
            return {'success': True, 'count': success_count, 'errors': errors}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
