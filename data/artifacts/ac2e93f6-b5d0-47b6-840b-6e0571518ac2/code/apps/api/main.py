
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from auth_routes import router as auth_router
from routers.main import router as main_router

app = FastAPI()
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_methods=['*'], allow_headers=['*'])

app.include_router(auth_router, prefix='/auth', tags=['auth'])
app.include_router(main_router, prefix='/api', tags=['api'])

@app.get('/health')
def health(): return {'status': 'ok'}
