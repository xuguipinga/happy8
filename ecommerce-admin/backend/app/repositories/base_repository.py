from app.extensions import db

class BaseRepository:
    model = None

    @classmethod
    def get_by_id(cls, id):
        return db.session.get(cls.model, id)

    @classmethod
    def find_all(cls):
        return cls.model.query.all()

    @classmethod
    def save(cls, obj):
        db.session.add(obj)
        db.session.commit()
        return obj

    @classmethod
    def delete(cls, obj):
        db.session.delete(obj)
        db.session.commit()
