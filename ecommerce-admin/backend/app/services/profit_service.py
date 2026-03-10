from app.models.order import Order
from app.models.product import Product
from app.models.logistics import Logistics
from app.models.purchase import Purchase
from app.api.stock import Inventory # 补充导入
from app.extensions import db
from app.utils.sku_parser import parse_sku # 导入解析器
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ProfitService:
    @staticmethod
    def calculate_order_profit(order):
        """
        计算单个行级订单的利润（一行 = 一个 SKU、一笔销售）
        收入 = unit_price × quantity（行级，避免整单实付重复叠加）
        成本 = 从采购明细表按 SKU 查询最新采购单价 × 数量
        物流 = 按同订单号的所有 SKU 行数均摊
        毛利 = 收入 - 成本 - 物流
        """
        try:
            from app.models.purchase import PurchaseItem
            from app.models.stock import Inventory

            qty = Decimal(str(order.quantity or 0))

            # 1. 行级收入：单价 × 数量，不用整单 actual_paid 避免多行重复叠加
            unit_price = order.unit_price if order.unit_price else Decimal(0)
            income = unit_price * qty

            # 2. 产品成本（RMB）：按 SKU 从采购明细表查最新单价
            product_cost = Decimal(0)
            if order.sku:
                # 优先从采购明细子表查
                purchase_item = (
                    PurchaseItem.query
                    .filter_by(sku=order.sku)
                    .order_by(PurchaseItem.id.desc())
                    .first()
                )
                if purchase_item and purchase_item.unit_price:
                    product_cost = Decimal(str(purchase_item.unit_price)) * qty
                else:
                    # 回退：从 Product 表或 Inventory 表
                    product = Product.query.filter_by(sku=order.sku).first()
                    if product:
                        unit_cost = product.avg_cost_price if (product.avg_cost_price and product.avg_cost_price > 0) else (product.latest_purchase_price or 0)
                        product_cost = Decimal(str(unit_cost)) * qty
                    else:
                        model, spec = parse_sku(order.sku)
                        if model:
                            inv = Inventory.query.filter_by(model=model).first()
                            if inv and inv.avg_cost:
                                product_cost = Decimal(str(inv.avg_cost)) * qty

            order.cost_price = product_cost

            # 3. 物流成本：按订单号下的行数均摊，避免每行都叠加全额运费
            logistics_cost = Decimal(0)
            logistics_list = Logistics.query.filter_by(ref_no=order.platform_order_no).all()
            total_logistics = Decimal(0)
            for log in logistics_list:
                fee = log.actual_fee if log.actual_fee is not None else (log.shipping_fee or 0)
                total_logistics += Decimal(str(fee))

            if total_logistics > 0:
                # 统计同订单号下的行数（用于均摊）
                row_count = Order.query.filter_by(
                    platform_order_no=order.platform_order_no,
                    tenant_id=order.tenant_id
                ).count()
                logistics_cost = total_logistics / Decimal(str(max(row_count, 1)))

            order.logistics_cost = logistics_cost

            # 4. 毛利
            profit = income - product_cost - logistics_cost
            order.profit = profit

            # 5. 利润率
            if income > 0:
                order.profit_rate = (profit / income).quantize(Decimal("0.0001"))
            else:
                order.profit_rate = Decimal(0)

            return True
        except Exception as e:
            logger.error(f"Error calculating profit for order row {order.id} ({order.platform_order_no}): {e}")
            return False

    @staticmethod
    def recalculate_all_profits():
        """
        重新计算所有订单的利润
        """
        try:
            orders = Order.query.all()
            count = 0
            for order in orders:
                if ProfitService.calculate_order_profit(order):
                    count += 1
                
                # 批量提交，避免内存溢出
                if count % 100 == 0:
                    db.session.commit()
            
            db.session.commit()
            return {'success': True, 'count': count}
        except Exception as e:
            db.session.rollback()
            return {'success': False, 'message': str(e)}
