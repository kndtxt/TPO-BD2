# models.py
from pydantic import BaseModel

class Telefono(BaseModel):
    codigoArea: int
    nroTel: int
    tipoTel: str

class Cliente(BaseModel):
    nroCliente: int
    nombre: str
    apellido: str
    direccion: str
    activo: int
    telefono: Telefono

    class Config:
        # We can specify this to handle MongoDB's ObjectId properly if needed
        orm_mode = True
