from app.repositories.base_repository import BaseRepository
from app.models.stock import Inventory

class InventoryRepository(BaseRepository):
    model = Inventory

    @classmethod
    def find_by_model_and_spec(cls, tenant_id, model, spec):
        return cls.model.query.filter_by(
            tenant_id=tenant_id, 
            model=model, 
            spec=spec
        ).first()

    @classmethod
    def find_by_tenant(cls, tenant_id, search=None, status=None, series=None):
        query = cls.model.query.filter_by(tenant_id=tenant_id)
        if search:
            query = query.filter(cls.model.model.ilike(f'%{search}%') | cls.model.spec.ilike(f'%{search}%'))
        
        if series:
            query = query.filter(cls.model.series == series)
        
        if status == 'NORMAL':
            query = query.filter(cls.model.quantity > 5)
        elif status == 'LOW':
            query = query.filter(cls.model.quantity > 0, cls.model.quantity <= 5)
        elif status == 'OUT':
            query = query.filter(cls.model.quantity <= 0)
        
        return query
