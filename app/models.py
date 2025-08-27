# app/models.py
from sqlalchemy import String, Integer, Float, ForeignKey, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.database import Base

class Producer(Base):
    __tablename__ = "producers"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    cpf_cnpj: Mapped[str] = mapped_column(String(14), unique=True, index=True)  # só dígitos
    name: Mapped[str] = mapped_column(String(120))

    farms: Mapped[list["Farm"]] = relationship(back_populates="producer", cascade="all, delete-orphan")

class Farm(Base):
    __tablename__ = "farms"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    producer_id: Mapped[int] = mapped_column(ForeignKey("producers.id", ondelete="CASCADE"))
    name: Mapped[str] = mapped_column(String(120))
    city: Mapped[str] = mapped_column(String(80))
    state: Mapped[str] = mapped_column(String(2))  # UF
    area_total: Mapped[float] = mapped_column(Float)
    area_agricultable: Mapped[float] = mapped_column(Float, default=0.0)
    area_vegetation: Mapped[float] = mapped_column(Float, default=0.0)

    producer: Mapped["Producer"] = relationship(back_populates="farms")
    plantings: Mapped[list["Planting"]] = relationship(back_populates="farm", cascade="all, delete-orphan")

class Season(Base):
    __tablename__ = "seasons"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(20), unique=True)  # 'Safra 2021'
    plantings: Mapped[list["Planting"]] = relationship(back_populates="season", cascade="all, delete-orphan")

class Planting(Base):
    __tablename__ = "plantings"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    farm_id: Mapped[int] = mapped_column(ForeignKey("farms.id", ondelete="CASCADE"))
    season_id: Mapped[int] = mapped_column(ForeignKey("seasons.id", ondelete="CASCADE"))
    culture: Mapped[str] = mapped_column(String(80))  # Soja, Milho, Café...

    farm: Mapped["Farm"] = relationship(back_populates="plantings")
    season: Mapped["Season"] = relationship(back_populates="plantings")

    __table_args__ = (
        UniqueConstraint("farm_id", "season_id", "culture", name="uix_planting_unique"),
    )
