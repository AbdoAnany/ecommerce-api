from logging.config import fileConfig
from sqlalchemy import pool
from sqlalchemy import create_engine
from alembic import context

import os
import sys

# إضافة المسار الجذر للمشروع
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# استيراد التطبيق وتهيئة الـ context
from app import create_app, db

# أنشئ التطبيق وفعّل الـ context
app = create_app(os.getenv("FLASK_ENV", "development"))
app.app_context().push()

# إعدادات Alembic
config = context.config
fileConfig(config.config_file_name)

# اجعل Alembic يستخدم الميتاداتا من SQLAlchemy
target_metadata = db.metadata

def run_migrations_offline():
    """تشغيل الترحيلات في الوضع offline"""
    url = app.config['SQLALCHEMY_DATABASE_URI']
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """تشغيل الترحيلات في الوضع online"""
    connectable = create_engine(
        app.config['SQLALCHEMY_DATABASE_URI'],
        poolclass=pool.NullPool,
    )
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
