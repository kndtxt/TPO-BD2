#============ Imports ==================>
from pydantic import BaseModel, field_validator, model_validator
from typing import List
from datetime import datetime

#============ Models ==================>
class Product(BaseModel):
    codProduct: int = 10
    brand: str = 'Lorem Ipsum'
    name: str = 'Dolor sit amet'
    description: str = 'Consectetur adipiscing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua'
    price: float = '199.99'
    stock: int = 17
    billNbrs: List[int] = [3]

    @field_validator('codProduct')
    def validate_codProduct(cls, v):
        if v < 0:
            raise ValueError('codProduct must be higher than 0')
        return v

    @field_validator('name', 'brand', 'description')
    def validate_strings(cls, v):
        if len(v) > 45:
            raise ValueError('name, brand and description must be shorter than 45 chars')
        return v

    @field_validator('price')
    def validate_price(cls, v):
        if v <= 0:
            raise ValueError('price must be positive')
        return v

    @field_validator('stock')
    def validate_stock(cls, v):
        if v <= 0:
            raise ValueError('stock must be positive')
        return v
    

class BillDetail(BaseModel):
    itemNbr: int = 171
    codProduct: int = 10
    amount: float = 17

    @field_validator('itemNbr')
    def validate_itemNbr(cls, v):
        if v <= 0:
            raise ValueError('itemNbr must be higher than 0')
        return v
    
    @field_validator('codProduct')
    def validate_codProduct(cls, v):
        if v < 0:
            raise ValueError('codProduct must be higher than 0')
        return v

    @field_validator('amount')
    def validate_amount(cls, v):
        if v <= 0:
            raise ValueError('amount must be positive')
        return v

class Bill(BaseModel):
    billNbr: int = 171
    date: datetime = datetime(2024,9,11)
    total: float = 201.71
    tax: float = 21
    taxxedTotal: float = 244.07
    details: List[BillDetail] = []
    clientNbr: int = 9

    @field_validator('billNbr')
    def validate_billNbr(cls, v):
        if v < 0:
            raise ValueError('billNbr must be higher than 0')
        return v
    
    @field_validator('clientNbr')
    def validate_clientNbr(cls, v):
        if v < 0:
            raise ValueError('clientNbr must be higher than 0')
        return v
    
    @field_validator('total', 'tax', 'taxxedTotal')
    def validate_total(cls, v):
        if v <= 0:
            raise ValueError('total, tax and taxxedTotal must be positive')
        return v

    @field_validator('date')
    def validate_date(cls, v):
        # Validar que la fecha no sea futura
        if isinstance(v, str):
            v = datetime.fromisoformat(v)
        if v > datetime.today():
            raise ValueError('date cant be in the future')
        return v
    
    @model_validator(mode='after')
    def validate_details(cls, values):
        details = values.details
        for detail in details:
            if not isinstance(detail, BillDetail):
                raise ValueError('details must be BillDetail instances')
        
        return values

class Phone(BaseModel):
    areaCode: int = 624
    phoneNbr: int = 4263378
    phoneType: str = 'F'

    @field_validator('areaCode')
    def validate_areaCode(cls, v):
        if v > 1000:
            raise ValueError('areaCode must have less than 3 digits')
        return v

    @field_validator('phoneNbr')
    def validate_phoneNbr(cls, v):
        if v > 10000000:
            raise ValueError('phoneNbr must have less than 7 digits')
        return v

    @field_validator('phoneType')
    def validate_phoneType(cls, v):
        if len(v) > 1:
            raise ValueError('phoneType should have only 1 char')
        return v

class Client(BaseModel):
    clientNbr: int = 9
    name: str = 'John'
    lastName: str = 'Smith'
    address: str = 'Awesome St. 557'
    active: int = 63
    phones: List[Phone] = []
    billNbrs: List[int] = []

    @field_validator('clientNbr')
    def validate_clientNbr(cls, v):
        if v <= 0:
            raise ValueError('clientNbr must be higher than 0')
        return v

    @field_validator('active')
    def validate_active(cls, v):
        if v <= 0:
            raise ValueError('active must be higher than 0')
        return v

    @field_validator('name', 'lastName', 'address')
    def validate_strings(cls, v):
        if len(v) > 45:
            raise ValueError('name, lastName and address must have less than 45 chars')
        return v
    
    @model_validator(mode='after')
    def validate_phones(cls, values):
        phones = values.phones
        for phone in phones:
            if not isinstance(phone, Phone):
                raise ValueError('All phones should be instance of Phone')
        
        return values
