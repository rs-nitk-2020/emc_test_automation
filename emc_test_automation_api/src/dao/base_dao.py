class BaseDAO:
    def __init__(self, session, model):
        self.session = session
        self.model = model

    def create(self, **kwargs):
        obj = self.model(**kwargs)
        self.session.add(obj)
        self.session.commit()
        return obj

    def get_all(self):
        return self.session.query(self.model).all()

    def get_by_id(self, id_field, value):
        return self.session.query(self.model).filter(getattr(self.model, id_field) == value).first()

    def update(self, id_field, id_value, **kwargs):
        obj = self.session.query(self.model).filter(getattr(self.model, id_field) == id_value).first()
        for key, value in kwargs.items():
            setattr(obj, key, value)
        self.session.commit()
        return obj

    def delete(self, id_field, value):
        obj = self.session.query(self.model).filter(getattr(self.model, id_field) == value).first()
        if obj:
            self.session.delete(obj)
            self.session.commit()
