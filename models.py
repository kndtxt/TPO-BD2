# models.py
from pydantic import BaseModel, validator
from typing import List

class Telefono(BaseModel):
    codigoArea: int
    nroTel: int
    tipoTel: str

    @validator('codigoArea')
    def validate_codigoArea(cls, v):
        if v > 1000:
            raise ValueError('El código de área debe ser de hasta 3 digitos')
        return v

    @validator('nroTel')
    def validate_nroTel(cls, v):
        if v > 10000000:
            raise ValueError('El teléfono debe ser de hasta 7 digitos')
        return v

    @validator('tipoTel')
    def validate_tipo(cls, v):
        if len(v) > 1:
            raise ValueError('El tipo debe ser de hasta 1 caracter')
        return v

class Cliente(BaseModel):
    nroCliente: int
    nombre: str
    apellido: str
    direccion: str
    activo: int
    telefonos: List[Telefono]

    @validator('nroCliente')
    def validate_nro_cliente(cls, v):
        if v <= 0:
            raise ValueError('El número de cliente debe ser mayor que cero')
        return v

    @validator('activo')
    def validate_activo(cls, v):
        if v <= 0:
            raise ValueError('El activo ser mayor que cero')
        return v

    @validator('nombre', 'apellido', 'direccion')
    def validate_nombre_apellido(cls, v):
        if len(v) > 45:
            raise ValueError('El nombre y apellido debe ser de hastas 45 caracteres')
        return v

    class Config:
        # We can specify this to handle MongoDB's ObjectId properly if needed
        use_enum_values = True
        orm_mode = True
