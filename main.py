from fastapi import FastAPI, Path, HTTPException, Query
import json

app = FastAPI()

def load_data():
    with open('patients.json', mode='r') as f:
        data = json.load(f)
    return data

@app.get('/')
def home():
    return {'message': 'This is the home page for the site'}

@app.get('/about')
def about():
    return {'message': 'This is the about page'}

@app.get('/view')
def view(sort_by: str = Query(None, description= 'Sort on the basis of height, weight, BMI'), order: str = Query('asc', description= 'asc or desc')):
    valid_fileds = ['height', 'weight', 'bmi']
    data = load_data()
    if sort_by is None:
        return data
    else:
        if sort_by not in valid_fileds:
            raise HTTPException(status_code= 400, detail= f'Invalid Field select form {valid_fileds} ')
        if order not in ['asc', 'desc']:
            raise HTTPException(status_code= 400, detail= 'Invalid order select between asc or desc')
        
        data = load_data()
        
        sorted_order = True if order == 'desc' else False
        
        sorted_data = sorted(data.values(), key= lambda x:x.get(sort_by, 0), reverse= sorted_order)        
            
        return sorted_data
    

@app.get('/patient/{patient_id}')
def view_patient(patient_id: str = Path(..., description= 'Id of the patient in the db', example= 'P001')):
    data = load_data()
    
    if patient_id in data:
        return data[patient_id]
    raise HTTPException(status_code= 404, detail= 'Patient not found')
