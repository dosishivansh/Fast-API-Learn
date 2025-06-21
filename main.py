from fastapi import FastAPI

app = FastAPI()

@app.get('/')
def home():
    return {'message': 'This is the home page for the site'}

@app.get('/about')
def about():
    return {'message': 'This is the about page'}