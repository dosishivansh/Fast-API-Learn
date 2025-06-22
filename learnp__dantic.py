from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator, computed_field
from typing import Optional, List, Dict, Annotated

class Patient(BaseModel):
    name : str
    height : float # meters
    email : EmailStr
    age : int
    weight : Annotated[float, Field(gt=0, strict= True)] #kg
    allergies : Annotated[Optional[List[str]], Field(default= None, max_length= 5)]
    contact_number : Dict[str,str]
    
    @field_validator('email')
    @classmethod
    def email_validator(cls, value):
        valid_domains = ['hdfc.com', 'icic.com']
        
        domain_name = value.split('@')[-1]
        
        if domain_name not in valid_domains:
            raise ValueError('Not a valid domain')
        return value
    
    @field_validator('name')
    @classmethod
    def transform_name(cls, value):
        return value.upper()
    
    @model_validator(mode= 'after') # used to apply validation on multiple fields
    @classmethod
    def validate_emergency_number(cls, model):
        if model.age >= 60 and 'emergency' not in model.contact_number:
            raise ValueError('Emergency Number not found')
        return model
    
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height)**2,2)
        return bmi
    
    
def print_patient(patient: Patient):
    print(patient.name)
    print(patient.email)
    print(patient.age)
    print(patient.weight)
    print(patient.allergies)
    print(patient.contact_number)
    print(f'BMI = {patient.bmi}')
    print('Inserted')
    
patient_info = {'name': 'Shivansh Dosi','height': 1.8, 'email': 'shivanshdosi@hdfc.com', 'age': 60, 'weight': 85.00, 'contact_number': {'mobileNo': '123456678', 'email': 'shivanshdosi@gmail.com', 'emergency': '87678687'}}

patient_01 = Patient(**patient_info)

print_patient(patient= patient_01)

temp = patient_01.model_dump()
print(temp)