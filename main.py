#!/usr/bin/env python3
# run this : uvicorn main:app --reload --host 0.0.0.0 --port 5000
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sessions import InMemorySessions

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
    expose_headers=['*'],
)

class Data:
    def __init__(self):
        self.name = 'guest'
        self.count = 0
        self.isguest = True

sessions = InMemorySessions(Data, timeout=None)

def protected(data: Data = Depends(sessions.getifpresent)):
    if data is None or data.isguest:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail='Not authenticated'
        )
    return {}

@app.post('/auth')
async def login(data: dict = Depends(sessions.get)):
    data.name = 'user'
    data.isguest = False
    return {}

@app.get('/protected')
async def protected_endpoint(data = Depends(protected)):
    return { "message": "this is protected method" }

@app.post('/drop')
async def drop(result: bool = Depends(sessions.drop)):
    if result:
        return { 'message': 'Logged out successfully' }
    else:
        return { 'message': 'Already logged out' }

@app.get('/whoami')
async def whoami(data: Data = Depends(sessions.getifpresent)):
    if data is None:
        return { 'name' : 'guest' }
    else:
        return { 'name' : data.name }
    
@app.get('/count')
async def get_today(data: Data = Depends(sessions.get)):
    data.count += 1
    
    return { 'count' : data.count }