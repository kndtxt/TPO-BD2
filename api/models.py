from pydantic import BaseModel
from typing import List
from datetime import date


class NameAndSurnameParams(BaseModel):
  name: str = ""
  surname: str = ""

class Product(BaseModel):
  codProduct: int
  brand: str
  name: str
  description: str
  price: float
  stock: int
  billNbrs: List[int]

class BillDetail(BaseModel):
  itemNbr: int
  codProduct: int
  amount: float


class Bill(BaseModel):
  billNbr: int
  date: date
  total: float
  tax: float
  taxxedTotal: float
  details: List[BillDetail]
  clientNbr: int
