# app/schemas.py
from typing import Optional
from pydantic import BaseModel, Field, field_validator
from app.validators import validate_cpf_cnpj, normalize_cpf_cnpj

class ProducerCreate(BaseModel):
    cpf_cnpj: str = Field(..., min_length=11, max_length=18)  # aceita com máscara
    name: str

    @field_validator("cpf_cnpj")
    @classmethod
    def _valid_cpf_cnpj(cls, v: str) -> str:
        if not validate_cpf_cnpj(v):
            raise ValueError("CPF/CNPJ inválido.")
        return normalize_cpf_cnpj(v)

class ProducerUpdate(BaseModel):
    name: Optional[str] = None

class ProducerOut(BaseModel):
    id: int
    cpf_cnpj: str
    name: str

    model_config = {"from_attributes": True}

class FarmBase(BaseModel):
    producer_id: int
    name: str
    city: str
    state: str = Field(..., min_length=2, max_length=2)  # UF
    area_total: float
    area_agricultable: float
    area_vegetation: float

    @field_validator("area_total", "area_agricultable", "area_vegetation")
    @classmethod
    def non_negative(cls, v: float) -> float:
        if v < 0:
            raise ValueError("Área não pode ser negativa.")
        return v

    @field_validator("state")
    @classmethod
    def uf_upper(cls, v: str) -> str:
        return v.upper()

class FarmCreate(FarmBase):
    pass

class FarmUpdate(BaseModel):
    name: Optional[str] = None
    city: Optional[str] = None
    state: Optional[str] = Field(default=None, min_length=2, max_length=2)
    area_total: Optional[float] = None
    area_agricultable: Optional[float] = None
    area_vegetation: Optional[float] = None

class FarmOut(FarmBase):
    id: int
    model_config = {"from_attributes": True}

# --- Seasons (Safras) ---
class SeasonBase(BaseModel):
    name: str  # ex.: "Safra 2023"

class SeasonCreate(SeasonBase):
    pass

class SeasonOut(SeasonBase):
    id: int
    model_config = {"from_attributes": True}

# --- Plantings (Culturas por safra e fazenda) ---
class PlantingBase(BaseModel):
    farm_id: int
    season_id: int
    culture: str  # ex.: "Soja", "Milho", "Café"

class PlantingCreate(PlantingBase):
    pass

class PlantingOut(PlantingBase):
    id: int
    model_config = {"from_attributes": True}
