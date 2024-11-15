#============ Imports ==================>
from pydantic import BaseModel, validator, root_validator
from typing import List
from datetime import date

#============ Models ==================>
class Producto(BaseModel):
    codProduct: int
    marca: str
    nombre: str
    descripcion: str
    precio: float
    stock: int
    facturas: List[int]#numeros de facturas

    @validator('codProduct')
    def validate_codigo_producto(cls, v):
        if v < 0:
            raise ValueError('El código del producto debe ser mayor que cero')
        return v

    @validator('nombre', 'marca', 'descripcion')
    def validate_nombre_apellido(cls, v):
        if len(v) > 45:
            raise ValueError('El nombre, marca y descripcion deben ser de hasta 45 caracteres')
        return v

    @validator('precio')
    def validate_precio(cls, v):
        if v < 0:
            raise ValueError('El precio debe ser mayor que cero')
        return v

    @validator('stock')
    def validate_stock(cls, v):
        if v < 0:
            raise ValueError('El stock no puede ser negativo')
        return v
    

class DetalleFactura(BaseModel):
    nroItem: int
    codProducto: int
    cantidad: float

    @validator('nroItem')
    def validate_numero_item(cls, v):
        if v <= 0:
            raise ValueError('El número de item debe ser mayor que cero')
        return v
    
    @validator('codProducto')
    def validate_codProducto(cls, v):
        if v < 0:
            raise ValueError('El código del producto debe ser mayor que cero')
        return v

    @validator('cantidad')
    def validate_cantidad(cls, v):
        if v < 0:
            raise ValueError('La cantidad debe ser mayor que cero')
        return v

class Factura(BaseModel):
    nroFactura: int
    fecha: date
    totalSinIva: float
    iva: float
    totalConIva: float
    detalles: List[DetalleFactura]
    nroCliente: int

    @validator('nroFactura')
    def validate_numero_factura(cls, v):
        if v < 0:
            raise ValueError('El número de factura debe ser mayor que cero')
        return v
    
    @validator('nroCliente')
    def validate_numero_cliente(cls, v):
        if v < 0:
            raise ValueError('El número de cliente debe ser mayor que cero')
        return v
    
    @validator('totalSinIva', 'iva', 'totalConIva')
    def validate_precio(cls, v):
        if v < 0:
            raise ValueError('El total e iva deben ser mayor que cero')
        return v

    @validator('fecha')
    def validate_fecha(cls, v):
        # Validar que la fecha no sea futura
        if v > date.today():
            raise ValueError('La fecha no puede ser futura')
        return v
    
    @root_validator
    def validate_detalles(cls, values):
        detalles = values.get('detalles', [])
        for detalle in detalles:
            if not isinstance(detalle, DetalleFactura):
                raise ValueError('Cada detalle debe ser una instancia válida de DetalleFactura')
        
        return values

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
            raise ValueError('El nombre y apellido deben ser de hasta 45 caracteres')
        return v
    
    @root_validator
    def validate_telefonos(cls, values):
        telefonos = values.get('telefonos', [])
        for telefono in telefonos:
            if not isinstance(telefono, Telefono):
                raise ValueError('Cada teléfono debe ser una instancia válida de Telefono')
        
        return values

    class Config:
        # We can specify this to handle MongoDB's ObjectId properly if needed
        use_enum_values = True
        orm_mode = True