#============ Imports ==================>
from pydantic import BaseModel, validator, root_validator
from typing import List
from datetime import date

#============ Models ==================>
class Product(BaseModel):
    codProduct: int
    brand: str
    name: str
    description: str
    price: float
    stock: int
    billNbrs: List[int]#numeros de facturas

    @validator('codProduct')
    def validate_codProduct(cls, v):
        if v < 0:
            raise ValueError('codProduct must be higher than 0')
        return v

    @validator('name', 'brand', 'description')
    def validate_strings(cls, v):
        if len(v) > 45:
            raise ValueError('name, marca y description must be shorter than 45 chars')
        return v

    @validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('price must be positive')
        return v

    @validator('stock')
    def validate_stock(cls, v):
        if v <= 0:
            raise ValueError('stock must be positive')
        return v
    

class BillDetail(BaseModel):
    itemNbr: int
    codProduct: int
    amount: float

    @validator('itemNbr')
    def validate_itemNbr(cls, v):
        if v <= 0:
            raise ValueError('itemNbr must be higher than 0')
        return v
    
    @validator('codProduct')
    def validate_codProduct(cls, v):
        if v < 0:
            raise ValueError('codProduct must be higher than 0')
        return v

    @validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('amount must be positive')
        return v

class Bill(BaseModel):
    billNbr: int
    date: date
    total: float
    tax: float
    taxxedTotal: float
    details: List[BillDetail]
    clientNbr: int

    @validator('billNbr')
    def validate_billNbr(cls, v):
        if v < 0:
            raise ValueError('billNbr must be higher than 0')
        return v
    
    @validator('clientNbr')
    def validate_clientNbr(cls, v):
        if v < 0:
            raise ValueError('clientNbr must be higher than 0')
        return v
    
    @validator('total', 'iva', 'totalConIva')
    def validate_total(cls, v):
        if v <= 0:
            raise ValueError('total must be positive')
        return v

    @validator('date')
    def validate_date(cls, v):
        # Validar que la fecha no sea futura
        if v > date.today():
            raise ValueError('date cant be in the future')
        return v
    
    @root_validator
    def validate_details(cls, values):
        details = values.get('details', [])
        for detail in details:
            if not isinstance(detail, BillDetail):
                raise ValueError('details must be BillDetail instances')
        
        return values

class Phone(BaseModel):
    areaCode: int
    phoneNbr: int
    phoneType: str

    @validator('areaCode')
    def validate_areaCode(cls, v):
        if v > 1000:
            raise ValueError('areaCode must have less than 3 digits')
        return v

    @validator('phoneNbr')
    def validate_phoneNbr(cls, v):
        if v > 10000000:
            raise ValueError('phoneNbr must have less than 7 digits')
        return v

    @validator('phoneType')
    def validate_phoneType(cls, v):
        if len(v) > 1:
            raise ValueError('phoneType should have only 1 char')
        return v

class Client(BaseModel):
    clientNbr: int
    name: str
    lastName: str
    address: str
    active: int
    phones: List[Phone]
    billNbrs: List[int]

    @validator('clientNbr')
    def validate_clientNbr(cls, v):
        if v <= 0:
            raise ValueError('clientNbr must be higher than 0')
        return v

    @validator('active')
    def validate_active(cls, v):
        if v <= 0:
            raise ValueError('active must be higher than 0')
        return v

    @validator('name', 'lastName', 'address')
    def validate_strings(cls, v):
        if len(v) > 45:
            raise ValueError('name, lastName and address must have less than 45 chars')
        return v
    
    @root_validator
    def validate_phones(cls, values):
        phones = values.get('phones', [])
        for phone in phones:
            if not isinstance(phone, Phone):
                raise ValueError('All phones should be instance of Phone')
        
        return values

    class Config:
        # We can specify this to handle MongoDB's ObjectId properly if needed
        use_enum_values = True
        orm_mode = True