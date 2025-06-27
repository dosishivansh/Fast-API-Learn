from fastapi import FastAPI, Path, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, computed_field
from typing import Optional, Annotated, Literal
import json

app = FastAPI()

class Patient(BaseModel):
    id: Annotated[str, Field(..., description= 'Id of the patient', example= 'P001')]
    name: Annotated[str, Field(..., description= 'Name of the Patient', example= 'Shivansh', max_length= 50)]
    city: Annotated[Optional[str], Field( description= 'City of the patient', default= None)]
    age: Annotated[int, Field(gt= 0, lt= 120, description= 'Age of the patient')]
    gender: Annotated[Literal['male', 'female', 'others'], Field(..., description= 'Gender of the patient')]
    height: Annotated[float, Field(gt= 0, description= 'height of the patient in mtrs', strict= True)]
    weight: Annotated[float, Field(gt= 0, description= 'weight of the patient in kgs', strict= True)]
    

            
    @computed_field
    @property
    def bmi(self) -> float:
        bmi = round(self.weight/(self.height)**2,2)
        return bmi

    @computed_field
    @property
    def verdict(self) -> str:
        if self.bmi < 18.5:
            return 'Underweight'
        elif self.bmi < 24.9:
            return 'Healthy'
        elif self.bmi < 29.9:
            return 'Overweight'
        else:
            return 'Obese'
        
class UpdatePatient(BaseModel):
    name : Annotated[Optional[str], Field(default= None)]
    city: Annotated[Optional[str], Field(default= None)]
    age: Annotated[Optional[int], Field(default= None)]
    gender: Annotated[Optional[Literal['male', 'female', 'others']], Field(default= None)]
    height: Annotated[Optional[float], Field(default= None, gt= 0, strict= True)]
    weight: Annotated[Optional[float], Field(default= None, gt= 0, strict= True)]

def load_data():
    with open('patients.json', mode='r') as f:
        data = json.load(f)
    return data

def save_data(data):
    with open('patients.json', mode= 'w') as f:
        json.dump(data, f)

@app.get('/')
def home():
    return {'message': 'This is the home page for the site'}

@app.get('/about')
def about():
    return {'message': 'This is the about page'}

@app.get('/view')
def view(sort_by: str = Query(None, description= 'Sort on the basis of height, weight, BMI'), order: str = Query('desc', description= 'asc or desc')):
    valid_fileds = ['height', 'weight', 'bmi']
    data = load_data()
    if sort_by is None and order is not None:
        sorted_order = True if order == 'desc' else False
        sorted_data = {key: data[key] for key in sorted(data.keys(), reverse=sorted_order)}
        return sorted_data
    
    else:
        if sort_by not in valid_fileds:
            raise HTTPException(status_code= 400, detail= f'Invalid Field select form {valid_fileds} ')
        if order not in ['asc', 'desc']:
            raise HTTPException(status_code= 400, detail= 'Invalid order select between asc or desc')
        
        sorted_order = True if order == 'desc' else False
        
        # sorted_data = sorted(data.values(), key= lambda x:x.get(sort_by, 0), reverse= sorted_order)  
        sorted_data = {
            key: value
            for key, value in sorted(data.items(), key=lambda item: item[1].get(sort_by, 0), reverse=sorted_order)
        }            
        return sorted_data
    

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description= 'Id of the patient in the db', example= 'P001')):
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code= 404, detail= 'Patient not Found')

@app.post('/create')
def create_patient(patient: Patient):
    
    data = load_data()
    
    if patient.id in data:
        raise HTTPException(status_code= 400, detail= 'Patient already exists')
    
    data[patient.id] = patient.model_dump(exclude=['id'])
    
    save_data(data)
    
    return JSONResponse(status_code= 201, content= {'message': 'Patient created successfully'})

@app.put('/edit/{patient_id}')
def update_patient(patient_id: str, patient_update: UpdatePatient):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code= 404, detail= 'Patient not found')
    
    existing_patient = data[patient_id]
    
    updated_patient = patient_update.model_dump(exclude_unset= True)
    
    for key, value in updated_patient.items():
        existing_patient[key] = value
    
    existing_patient['id'] = patient_id
    
    patient_pydantic_object = Patient(**existing_patient)
    
    existing_patient = patient_pydantic_object.model_dump(exclude= 'id')
    
    data[patient_id] = existing_patient
    
    save_data(data)
    
    return JSONResponse(status_code= 201, content= 'Patient Info successfully updated')

@app.delete('/delete/{patient_id}')
def delete_patient(patient_id: str):
    data = load_data()
    
    if patient_id not in data:
        raise HTTPException(status_code= 404, detail= 'Patient not found')
    
    del data[patient_id]
    save_data(data)
    
    return JSONResponse(status_code= 201, content= 'Patient deleted successfully')