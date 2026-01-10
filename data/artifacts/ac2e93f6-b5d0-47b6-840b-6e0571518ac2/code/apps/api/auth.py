import os
from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import BaseModel, EmailStr, Field

# Configuration
# In a production environment, load this from environment variables or a secure config management system.
SECRET_KEY = os.getenv("JWT_SECRET_KEY", "your-super-secret-key-please-change-this-in-production")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against a hashed password."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Hashes a plain password."""
    return pwd_context.hash(password)

# JWT Token Management
def create_token(data: dict, expires_delta: Optional[timedelta] = None, token_type: str = "access") -> str:
    """
    Creates a JWT token (access or refresh).
    Args:
        data: Dictionary containing claims to encode (e.g., {"sub": username}).
        expires_delta: Optional timedelta for token expiration.
        token_type: "access" or "refresh" to differentiate token types.
    Returns:
        Encoded JWT string.
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        # Default expiration if not provided
        expire = datetime.utcnow() + timedelta(minutes=15) 
    
    to_encode.update({"exp": expire, "iat": datetime.utcnow(), "type": token_type})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates an access token with a default expiration."""
    if expires_delta is None:
        expires_delta = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    return create_token(data, expires_delta, token_type="access")

def create_refresh_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a refresh token with a default expiration."""
    if expires_delta is None:
        expires_delta = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    return create_token(data, expires_delta, token_type="refresh")

def decode_token(token: str) -> dict:
    """
    Decodes a JWT token.
    Raises ValueError if token is invalid or expired.
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        raise ValueError("Could not validate credentials")

# Pydantic Models for API input/output and internal data structures
class Token(BaseModel):
    """Model for JWT tokens returned upon login/refresh."""
    access_token: str
    token_type: str = "bearer"
    refresh_token: Optional[str] = None # Included for login, not always for refresh

class TokenData(BaseModel):
    """Model for data extracted from a JWT token payload."""
    username: Optional[str] = None
    token_type: Optional[str] = None # To distinguish access/refresh tokens

class UserCreate(BaseModel):
    """Model for creating a new user."""
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=8)

class UserLogin(BaseModel):
    """Model for user login credentials."""
    username: str # Can be username or email
    password: str

class UserOut(BaseModel):
    """Model for user profile data returned to the client."""
    id: str
    username: str
    email: EmailStr
    is_active: bool = True

    class Config:
        from_attributes = True # Allows Pydantic to create model from ORM objects or dicts