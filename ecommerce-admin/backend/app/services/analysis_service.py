from app.extensions import db
from app.models.order import Order
from app.models.product import Product
from app.models.logistics import Logistics
from sqlalchemy import func
import logging

logger = logging.getLogger(__name__)

class AnalysisService:
    @staticmethod
    def calculate_profit():
        """
        计算所有订单的毛利
        逻辑:
        1. 遍历所有 Order (或者未计算的 Order)
        2. 获取 Order.sku 对应的 Product.avg_cost_price 或 latest_purchase_price 作为 cost_price
        3. 获取 Order.platform_order_no 对应的 Logistics.shipping_fee/actual_fee 作为 logistics_cost
        4. Profit = actual_paid - (quantity * cost_price) - logistics_cost - tax_fee
        5. 更新 Order
        """
        try:
            orders = Order.query.all() # 优化: 可以只查 profit 为空的
            count = 0
            
            for order in orders:
                # 1. 计算采购成本 (COGS)
                total_cogs = 0
                
                # 优先使用已锁定的成本 (Snapshot)
                if order.cost_price and order.cost_price > 0:
                    total_cogs = float(order.cost_price)
                else:
                    # Fallback: 实时计算 (并保存以免未来变动)
                    cost_unit_price = 0
                    product = Product.query.filter_by(sku=order.sku).first()
                    if product:
                        # 优先使用平均成本，如果没有则使用最新采购价
                        if product.avg_cost_price and product.avg_cost_price > 0:
                            cost_unit_price = float(product.avg_cost_price)
                        elif product.latest_purchase_price and product.latest_purchase_price > 0:
                            cost_unit_price = float(product.latest_purchase_price)
                    
                    total_cogs = cost_unit_price * float(order.quantity or 0)
                    order.cost_price = total_cogs
                
                # 2. 计算物流成本
                logistics_cost = 0
                # 尝试通过订单号匹配物流单
                # Logistics.ref_no 可能是订单号
                if order.platform_order_no:
                    logistics = Logistics.query.filter_by(ref_no=order.platform_order_no).first()
                    if logistics:
                        logistics_cost = float(logistics.actual_fee if logistics.actual_fee else (logistics.shipping_fee or 0))
                
                order.logistics_cost = logistics_cost
                
                # 3. 计算毛利
                # Profit = 实付金额 - 商品总成本 - 物流成本 - 税费
                # 注意: actual_paid 通常是买家支付的总额 (含税含运费). 
                # 这里的逻辑需要根据实际业务调整. 
                # 假设: Profit = actual_paid - tax_fee - total_cogs - logistics_cost
                
                actual_paid = float(order.actual_paid or 0)
                tax_fee = float(order.tax_fee or 0)
                
                profit = actual_paid - tax_fee - total_cogs - logistics_cost
                order.profit = profit
                
                count += 1
            
            db.session.commit()
            return {'success': True, 'count': count}
        except Exception as e:
            db.session.rollback()
            logger.error(f"Calculate profit failed: {e}")
            return {'success': False, 'message': str(e)}

    @staticmethod
    def get_profit_stats():
        """获取盈亏统计数据"""
        # 总收入
        total_revenue = db.session.query(func.sum(Order.actual_paid)).scalar() or 0
        # 总利润
        total_profit = db.session.query(func.sum(Order.profit)).scalar() or 0
        # 总订单数
        total_orders = db.session.query(func.count(Order.id)).scalar() or 0
        
        # 利润率
        profit_margin = 0
        if total_revenue > 0:
            profit_margin = (total_profit / total_revenue) * 100
            
        return {
            'total_revenue': float(total_revenue),
            'total_profit': float(total_profit),
            'total_orders': int(total_orders),
            'profit_margin': round(float(profit_margin), 2)
        }
