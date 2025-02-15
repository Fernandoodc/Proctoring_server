# src/database/audit.py

import datetime
import json
from sqlalchemy import Column, Integer, String, UnicodeText, DateTime, event, inspect, SmallInteger
from sqlalchemy.orm import class_mapper, sessionmaker, declarative_base
from sqlalchemy.orm.attributes import get_history
from flask_login import current_user
from .db_mysql import Base

ACTION_CREATE = 1
ACTION_UPDATE = 2
ACTION_DELETE = 3
PLEASE_AUDIT = [ACTION_UPDATE, ACTION_CREATE, ACTION_DELETE]

def _current_user_id_or_none():
    try:
        # Aquí debes implementar la obtención del ID del usuario actual
        return current_user.id
    except:
        return None

class TimestampableMixin:
    created_at = Column(DateTime, default=datetime.datetime.now)
    #updated_at = Column(DateTime, default=datetime.datetime.now, onupdate=datetime.datetime.now)

class AuditLog(TimestampableMixin, Base):
    __tablename__ = 'audit_log'
    id = Column(Integer, primary_key=True, nullable=False)
    user_id = Column(SmallInteger)
    target_type = Column(String(100), nullable=False)
    target_id = Column(Integer)
    action = Column(Integer)
    state_before = Column(UnicodeText)
    state_after = Column(UnicodeText)

    def __init__(self, target_type, target_id, action, state_before, state_after):
        self.user_id = _current_user_id_or_none()
        self.target_type = target_type
        self.target_id = target_id
        self.action = action
        self.state_before = state_before
        self.state_after = state_after

    def __repr__(self):
        return f'<AuditLog {self.user_id}: {self.target_type} -> {self.action}>'

    def save(self, session):
        session.add(self)
        session.commit()

class AuditableMixin:
    @staticmethod
    def create_audit(session, object_type, object_id, action, **kwargs):
        audit = AuditLog(
            object_type,
            object_id,
            action,
            kwargs.get('state_before'),
            kwargs.get('state_after')
        )
        audit.save(session)

    @classmethod
    def __declare_last__(cls):
        if ACTION_CREATE in PLEASE_AUDIT:
            event.listen(cls, 'after_insert', cls.audit_insert)
        if ACTION_DELETE in PLEASE_AUDIT:
            event.listen(cls, 'before_delete', cls.audit_delete)  # Change to before_delete to capture state
        if ACTION_UPDATE in PLEASE_AUDIT:
            event.listen(cls, 'after_update', cls.audit_update)

    @staticmethod
    def get_primary_key_name(target):
        mapper = class_mapper(target.__class__)
        primary_key = mapper.primary_key[0].name
        return primary_key

    @staticmethod
    def audit_insert(mapper, connection, target):
        session = sessionmaker(bind=connection.engine)()
        pk_name = AuditableMixin.get_primary_key_name(target)
        pk_value = getattr(target, pk_name)
        target.create_audit(session, target.__tablename__, pk_value, ACTION_CREATE)

    @staticmethod
    def audit_delete(mapper, connection, target):
        session = sessionmaker(bind=connection.engine)()
        state_before = {}
        attrs = class_mapper(target.__class__).column_attrs
        for attr in attrs:
            state_before[attr.key] = getattr(target, attr.key)
        
        pk_name = AuditableMixin.get_primary_key_name(target)
        pk_value = getattr(target, pk_name)
        
        target.create_audit(session, target.__tablename__, pk_value, ACTION_DELETE,
                            state_before=json.dumps(state_before),
                            state_after=None)

    @staticmethod
    def audit_update(mapper, connection, target):
        state_before = {}
        state_after = {}
        inspr = inspect(target)
        attrs = class_mapper(target.__class__).column_attrs
        for attr in attrs:
            hist = getattr(inspr.attrs, attr.key).history
            if hist.has_changes():
                state_before[attr.key] = get_history(target, attr.key)[2].pop()
                state_after[attr.key] = getattr(target, attr.key)
        
        session = sessionmaker(bind=connection.engine)()
        pk_name = AuditableMixin.get_primary_key_name(target)
        pk_value = getattr(target, pk_name)
        
        target.create_audit(session, target.__tablename__, pk_value, ACTION_UPDATE,
                            state_before=json.dumps(state_before),
                            state_after=json.dumps(state_after))