from app.repositories.base_repository import BaseRepository
from app.models.stock import StockRecord

class StockRecordRepository(BaseRepository):
    model = StockRecord

    @classmethod
    def find_by_inventory(cls, tenant_id, inventory_id=None):
        query = cls.model.query.filter_by(tenant_id=tenant_id)
        if inventory_id:
            query = query.filter_by(inventory_id=inventory_id)
        return query.order_by(cls.model.created_at.desc())
