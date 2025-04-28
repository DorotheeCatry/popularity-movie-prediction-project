from passlib.context import CryptContext
from fastapi import HTTPException, Depends, status
from app.models.users import User
from sqlalchemy.orm import Session
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import select
from app.db.session import get_session
from jose import jwt, JWTError
from app.core.config import SECRET_KEY, ALGORITHM

# Password hashing context (bcrypt)
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# OAuth2 password bearer for token retrieval
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="api/v1/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verifies that the provided plain password matches the hashed password.

    Parameters:
    - `plain_password`: The plain text password to verify.
    - `hashed_password`: The hashed password stored in the database.

    Returns:
    - `bool`: True if the passwords match, False otherwise.
    """
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """
    Hashes the provided password using bcrypt.

    Parameters:
    - `password`: The plain text password to hash.

    Returns:
    - `str`: The hashed password.
    """
    return pwd_context.hash(password)

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_session)) -> User:
    """
    Retrieves the current user based on the provided JWT token.

    Parameters:
    - `token`: The JWT token used for authentication.
    - `db`: The database session.

    Returns:
    - `User`: The authenticated user object.

    Raises:
    - `HTTPException`: If the token is invalid or expired.
    """
    try:
        # Decode the JWT token
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        
        if not username:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token")

        # Fetch user from the database based on username
        statement = select(User).where(User.username == username)
        result = db.execute(statement).first()
        user = result[0] if result else None

        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")

        return user
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid or expired token")
