from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional
import jwt
from datetime import datetime, timedelta
import uvicorn

# Configuración de seguridad
SECRET_KEY = "Password"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 60

# Instancia de la aplicación FastAPI
app = FastAPI(title="API de Autenticación")

# Configuración de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Base models
class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    username: Optional[str] = None

class User(BaseModel):
    username: str
    password: str

class UserInDB(User):
    id: int
    name: str

# Base de datos simulada de usuarios
fake_users_db = {
    "usuario1": {
        "id": 1,
        "username": "usuario1",
        "password": "password123",
        "name": "Usuario Ejemplo"
    },
    "usuario2": {
        "id": 2,
        "username": "usuario2",
        "password": "clave456",
        "name": "Otro Usuario"
    }
}

# OAuth2
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

# Funciones auxiliares
def get_user(username: str):
    if username in fake_users_db:
        user_dict = fake_users_db[username]
        return UserInDB(**user_dict)
    return None

def authenticate_user(username: str, password: str):
    user = get_user(username)
    if not user or user.password != password:
        return False
    return user

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Credenciales inválidas",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        token_data = TokenData(username=username)
    except jwt.PyJWTError:
        raise credentials_exception
    
    user = get_user(username=token_data.username)
    if user is None:
        raise credentials_exception
    return user

# Rutas de la API
@app.post("/api/login")
async def login(form_data: User):
    user = authenticate_user(form_data.username, form_data.password)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Nombre de usuario o contraseña incorrectos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.username}, expires_delta=access_token_expires
    )

    return Token(
        access_token=access_token,
        token_type="bearer"
    )

@app.get("/api/profile")
async def get_profile(current_user: UserInDB = Depends(get_current_user)):
    return {
        "message": "Acceso autorizado",
        "user": {
            "id": current_user.id,
            "username": current_user.username,
            "name": current_user.name
        }
    }

# Punto de entrada
if __name__ == "__main__":
    uvicorn.run("omar:app", host="0.0.0.0", port=8000, reload=True)
