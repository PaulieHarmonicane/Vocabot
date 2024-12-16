from sqlalchemy import BigInteger, String, ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy.ext.asyncio import AsyncAttrs, async_sessionmaker, create_async_engine

engine = create_async_engine(url='sqlite+aiosqlite:///db.sqlite3')
async_session = async_sessionmaker(engine)

class Base(AsyncAttrs, DeclarativeBase):
    pass

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    name: Mapped[str] = mapped_column(String(25))
    languages = mapped_column(String(200))

class Languages(Base):
    __tablename__ = 'languages'

    id: Mapped[int] = mapped_column(primary_key=True)
    lang: Mapped[str] = mapped_column(String(25))
    category: Mapped[str] = mapped_column(String(5))

class Chinese_lib(Base):
    __tablename__ = '中文_lib'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    word: Mapped[str] = mapped_column(String(25))
    transcription: Mapped[str] = mapped_column(String(25))
    translation: Mapped[str] = mapped_column(String(100))
    freq_rate: Mapped[float] = mapped_column()

class English_lib(Base):
    __tablename__ = 'english_lib'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    word: Mapped[str] = mapped_column(String(25))
    translation: Mapped[str] = mapped_column(String(100))
    freq_rate: Mapped[float] = mapped_column()

class Spanish_lib(Base):
    __tablename__ = 'español_lib'

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id = mapped_column(BigInteger)
    word: Mapped[str] = mapped_column(String(25))
    translation: Mapped[str] = mapped_column(String(100))
    freq_rate: Mapped[float] = mapped_column()

async def async_main():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
