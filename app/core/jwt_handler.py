from datetime import datetime, timedelta, timezone
import jwt
from app.core.config import SECRET_KEY, ALGORITHM, ACCESS_TOKEN_EXPIRE_MINUTES

def create_access_token(data: dict) -> str:
    """
    Creates a JWT token with an expiration time and the provided data.
    
    Parameters:
    - `data` (dict): Information to encode in the JWT token.
    
    Returns:
    - `str`: Encoded JWT token.
    """
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=int(ACCESS_TOKEN_EXPIRE_MINUTES))  # Set expiration time
    to_encode.update({"exp": expire})  # Add expiration field
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)  # Encode token
    return encoded_jwt

def verify_token(token: str):
    """
    Verifies a JWT token by decoding and checking for expiration.
    
    Parameters:
    - `token` (str): The JWT token to be verified.
    
    Returns:
    - `dict` or `None`: The decoded token payload if valid, or `None` if invalid or expired.
    """
    try:
        # Decode the token and check the expiration
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM], options={"require": ["exp"]})
        return payload
    except jwt.ExpiredSignatureError:
        print("Token has expired")  # Handle expired token error
        return None
    except jwt.InvalidTokenError as e:
        print(f"Invalid token error: {e}")  # Handle invalid token error
        return None
    except Exception as e:
        print(f"Error verifying token: {e}")  # Handle general errors
        return None
