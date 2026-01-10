import uuid
from typing import List, Optional
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from pydantic import BaseModel, EmailStr, Field

from auth import SECRET_KEY, ALGORITHM, decode_token, TokenData

# Pydantic model for a User in our "database"
class User(BaseModel):
    """
    Represents a user object as stored in our (in-memory) database.
    Includes sensitive information like hashed_password.
    """
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    email: EmailStr
    hashed_password: str
    is_active: bool = True

    class Config:
        from_attributes = True

# In-memory "database" for demonstration purposes.
# In a real application, this would be replaced with an actual database connection (e.g., SQLAlchemy, MongoDB).
fake_users_db: List[User] = []

def get_db():
    """
    Dependency to yield a database session.
    For this example, it yields our in-memory user list.
    In a real application, this would manage database connections (e.g., SQLAlchemy Session).
    """
    try:
        yield fake_users_db
    finally:
        # In a real app, you'd close the DB session here if it was opened per request
        pass

def get_user_by_username(db: List[User], username: str) -> Optional[User]:
    """
    Helper function to find a user by username or email in the fake DB.
    """
    for user in db:
        if user.username == username or user.email == username:
            return user
    return None

# OAuth2PasswordBearer for extracting the token from the Authorization header
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: List[User] = Depends(get_db)) -> User:
    """
    Dependency that validates the access token and retrieves the corresponding user.
    Raises HTTPException if the token is invalid, expired, or the user is not found.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_token(token)
        username: str = payload.get("sub")
        token_type: str = payload.get("type")

        if username is None or token_type != "access": # Ensure it's an access token
            raise credentials_exception
        token_data = TokenData(username=username, token_type=token_type)
    except ValueError: # Raised by decode_token for JWTError
        raise credentials_exception

    user = get_user_by_username(db, token_data.username)
    if user is None:
        raise credentials_exception
    return user

async def get_current_active_user(current_user: User = Depends(get_current_user)) -> User:
    """
    Dependency that ensures the current user is active.
    Raises HTTPException if the user is inactive.
    """
    if not current_user.is_active:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Inactive user")
    return current_user