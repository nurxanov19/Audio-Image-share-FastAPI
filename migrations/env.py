import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.engine import Connection
from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine

from alembic import context

# --- CONFIGURATION --- #
# Alembic konfiguratsiya fayli (alembic.ini dan o'qiladi)
config = context.config

# Fayldagi logging sozlamalarini ishga tushiradi (Agar xohlasa loglarni ko‘rsatadi)
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# --- METADATA IMPORT --- #
# Bu yerda sening Base (ya'ni SQLAlchemy modellarning bazasi) import qilinadi
# ⚠️ Bu joyni o'z loyihang strukturasi asosida o'zgartir!
# Masalan, agar sening db.py fayling app/ papkada bo‘lsa:
from app.db import Base, DATABASE_URL  # Base — barcha modellarning ota klassi

# Metadata — bu jadval strukturasi. Alembic aynan shundan foydalanadi.
target_metadata = Base.metadata


# --- DATABASE URL --- #
# DATABASE_URL ni config fayldan emas, bevosita kodingdagi o'zgaruvchidan olamiz
# Buni xohlasang .env orqali ham boshqarishing mumkin
def get_url():
    return DATABASE_URL


# --- OFFLINE MIGRATIONS --- #
# Bu funksiya DB bilan real ulanmasdan, faqat SQL fayl yaratish uchun ishlatiladi.
def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode."""

    url = get_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,   # SQL so'rovlarni to‘liq matn shaklida chiqaradi
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


# --- ONLINE MIGRATIONS (ASYNC) --- #
# Bu joyda Alembic DB'ga real ulanadi va jadval o'zgarishlarini qo'llaydi.
def do_run_migrations(connection: Connection) -> None:
    """Actually run the migrations."""
    context.configure(
        connection=connection,
        target_metadata=target_metadata,
        compare_type=True,   # column turlaridagi o‘zgarishlarni ham aniqlaydi
        compare_server_default=True,  # default qiymatlar o‘zgarsa ham kuzatadi
    )

    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    """Run migrations in 'online' (async) mode."""
    connectable: AsyncEngine = create_async_engine(
        get_url(),
        poolclass=pool.NullPool,   # Connection pool ishlatilmaydi (async uchun mos)
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)

    await connectable.dispose()   # aloqani tozalaydi


def run_migrations_online() -> None:
    """Entry point for Alembic's CLI."""
    asyncio.run(run_async_migrations())


# --- ENTRY POINT --- #
# Alembic `alembic upgrade head` deganda mana shu joydan ishni boshlaydi.
if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()

