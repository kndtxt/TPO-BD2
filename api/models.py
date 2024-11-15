from pydantic import BaseModel

class NameAndSurname(BaseModel):
  name: str
  surname: str
