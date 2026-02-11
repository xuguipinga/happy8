from app.models.order import Order
from app.models.product import Product
from app.models.logistics import Logistics
from app.models.purchase import Purchase
from app.extensions import db
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

class ProfitService:
    @staticmethod
    def calculate_order_profit(order):
        """
        计算单个订单的利润
        Profit = (Order Amount + Shipping Income - Discount - Tax) - (Product Cost * Quantity) - Logistics Cost
        """
        try:
            # 1. 收入部分 (Income)
            # 注意: 这里的计算公式需要根据具体业务调整，暂定为：实付金额 - 税费 (假设实付已包含运费和折扣)
            # 或者更细致：订单金额 + 运费收入 - 折扣
            
            # 使用 actual_paid 作为基础收入，减去税费(如果是代缴税)
            income = order.actual_paid if order.actual_paid else Decimal(0)
            
            # 如果 actual_paid 为0，尝试用 components 计算
            if income == 0:
                income = (order.order_amount or 0) + (order.shipping_fee_income or 0) - (order.discount_amount or 0) - (order.tax_fee or 0)

            # 2. 产品成本 (Product Cost)
            product_cost = Decimal(0)
            if order.sku:
                product = Product.query.filter_by(sku=order.sku).first()
                if product:
                    # 优先使用平均成本，如果没有则使用最新采购价
                    unit_cost = product.avg_cost_price if product.avg_cost_price > 0 else product.latest_purchase_price
                    product_cost = unit_cost * Decimal(order.quantity)
                    
                    # 更新订单上的 snapshot 成本
                    order.cost_price = product_cost

            # 3. 物流成本 (Logistics Cost)
            logistics_cost = Decimal(0)
            # 尝试通过平台订单号关联物流单
            # 注意：Logistics.ref_no 对应 Order.platform_order_no
            logistics_list = Logistics.query.filter_by(ref_no=order.platform_order_no).all()
            for log in logistics_list:
                # 累加所有关联物流单的费用
                fee = log.actual_fee if log.actual_fee is not None else (log.shipping_fee or 0)
                logistics_cost += fee
            
            order.logistics_cost = logistics_cost

            # 4. 计算毛利 (Gross Profit)
            # 毛利 = 收入 - 产品成本 - 物流成本
            profit = income - product_cost - logistics_cost
            order.profit = profit
            
            # 5. 计算利润率 (Profit Rate)
            # 利润率 = 毛利 / 收入
            if income > 0:
                order.profit_rate = (profit / income).quantize(Decimal("0.0001"))
            else:
                order.profit_rate = Decimal(0)

            return True
        except Exception as e:
            logger.error(f"Error calculating profit for order {order.platform_order_no}: {e}")
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
