
class Client:
    def __init__(self, name, email, phone):
        self.name = name
        self.email = email
        self.phone = phone

    def __str__(self):
        return f'{self.name} - {self.email} - {self.phone}'
    
class Phone:
    def __init__(self, areaCode, number, phoneType):
        self.areaCode = areaCode
        self.number = number
        self.phoneType = phoneType

    def __str__(self):
        return f'{self.areaCode} - {self.number} - {self.phoneType}'