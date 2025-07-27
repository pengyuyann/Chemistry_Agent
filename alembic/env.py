from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# 添加项目根目录到 Python 路径
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
from app.core.db.models import Base

target_metadata = Base.metadata

# 直接构建数据库 URL，确保路径正确
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
app_dir = os.path.join(project_root, 'app')
db_path = os.path.join(app_dir, 'chemagent.db')

# 确保使用绝对路径
db_path = os.path.abspath(db_path)
DATABASE_URL = f"sqlite:///{db_path}"

# 确保数据库文件存在
if not os.path.exists(db_path):
    # 如果主数据库文件不存在，检查是否在 core/db 目录下
    alt_db_path = os.path.join(app_dir, 'core', 'db', 'chemagent.db')
    alt_db_path = os.path.abspath(alt_db_path)
    if os.path.exists(alt_db_path):
        print(f"Warning: Using database from {alt_db_path}")
        DATABASE_URL = f"sqlite:///{alt_db_path}"
        db_path = alt_db_path
    else:
        print(f"Warning: Database file not found. Will create at {db_path}")

print(f"Alembic using database: {DATABASE_URL}")

# 使用构建的数据库 URL
config.set_main_option('sqlalchemy.url', DATABASE_URL)

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
