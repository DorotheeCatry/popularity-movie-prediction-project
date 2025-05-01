from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlmodel import Session, select
from app.schemas.user import UserCreate, UserRead, UserUpdate  # Import schemas for user data handling
from app.schemas.auth import Token, AuthData  # Import schemas for authentication data (Token, AuthData)
from app.models.users import User  # Import the User model to interact with the database
from app.db.session import get_session  # Import the session dependency for database interaction
from app.core.security import get_password_hash, verify_password, get_current_user  # Import security utilities
from app.core.jwt_handler import create_access_token  # Import the JWT creation utility

router = APIRouter()  # Initialize the router for authentication-related routes


def validate_password(password: str):
    """
    Validate the password strength to meet the required criteria:
    - At least 8 characters long
    - Contains at least one digit
    - Contains at least one uppercase letter

    Parameters:
    - password (str): The password string to validate.

    Raises:
    - HTTPException: If any password criteria are not met.
    """
    if len(password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters long.")
    if not any(char.isdigit() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one digit.")
    if not any(char.isupper() for char in password):
        raise HTTPException(status_code=400, detail="Password must contain at least one uppercase letter.")
    
    

@router.post("/auth/register", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def register(user: UserCreate, session: Session = Depends(get_session)):
    """
    Register a new user by creating their account with the provided data.
    This function checks if the username or email already exists in the system
    and validates the password strength.

    Parameters:
    - user (UserCreate): The data for the new user (username, email, password).
    - session (Session): The session object to interact with the database.

    Returns:
    - UserRead: The created user object with the user's basic information (id, username, email).
    """
    # Check if the username or email already exists in the database
    statement = select(User).where((User.username == user.username) | (User.email == user.email))
    existing_user = session.exec(statement).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Username or email already in use")
    
    # Validate the password
    validate_password(user.password)

    # Hash the password before saving it in the database
    hashed_password = get_password_hash(user.password)
    
    # Create a new user object and store it in the database
    db_user = User(username=user.username, email=user.email, hashed_password=hashed_password)
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    # Return the user data without sensitive information (password)
    return UserRead(id=db_user.id, username=db_user.username, email=db_user.email, is_active=True)



@router.post("/auth/login", response_model=Token)
def login(form: AuthData, session: Session = Depends(get_session)):
    """
    Login a user by verifying their username and password.
    Upon successful authentication, a JWT token is created and returned.

    Parameters:
    - form (AuthData): Contains the username and password for authentication.
    - session (Session): The session object to interact with the database.

    Returns:
    - Token: The JWT token for the authenticated user.
    """
    # Query the database to find the user by their username
    statement = select(User).where(User.username == form.username)
    db_user = session.exec(statement).first()

    # Verify user existence and password validity
    if not db_user or not verify_password(form.password, db_user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create an access token (JWT) for the authenticated user
    access_token = create_access_token(data={"sub": db_user.username, "id": db_user.id})
    
    # Return the token as part of the response
    return Token(access_token=access_token, token_type="bearer")


@router.post("/auth/activate", response_model=dict)
def activate_account(
    request: UserUpdate,
    session: Session = Depends(get_session)
):
    """
    Activate a user account by setting a new password.

    Parameters:
    - request (UserUpdate): The new password data.
    - session (Session): The session to interact with the database.

    Returns:
    - dict: Success message confirming the account activation.
    """
    # Check if the user exists and is not already active
    statement = select(User).where(User.email == request.email)
    db_user = session.exec(statement).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    if db_user.is_active:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Account is already activated."
        )

    # Validate the new password
    validate_password(request.password)

    # Hash the new password and activate the account
    db_user.hashed_password = get_password_hash(request.password)
    db_user.is_active = True
    session.add(db_user)
    session.commit()
    session.refresh(db_user)
    
    return {"success": True, "message": "Account activated successfully!"}



@router.post("/auth/reset-password", response_model=dict)
def reset_password(
    request: UserUpdate,  # Contains the new password for the user
    current_user: User = Depends(get_current_user),  # Get the current authenticated user
    session: Session = Depends(get_session)  # Database session to interact with the database
):
    """
    Reset the password for the current authenticated user.
    The user must provide a new password and it will be updated in the database.

    Parameters:
    - request (UserUpdate): The new password data.
    - current_user (User): The currently authenticated user, fetched from the token.
    - session (Session): The session to interact with the database.

    Returns:
    - dict: Success message confirming the password reset.
    """
    # Check if the user is authenticated
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found."
        )
    
    # Check if the new password is provided
    if request.password is None:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password is required."
        )
    
    # Validate the new password
    validate_password(request.password)

    # Hash the new password and update the current user's password
    current_user.hashed_password = get_password_hash(request.password)
    session.add(current_user)
    session.commit()
    session.refresh(current_user)
    
    # Return a success message
    return {"success": True, "message": "Password reset successfully!"}

@router.post("/auth/logout", response_model=dict)
def logout(response: Response):
    """
    Logout the current user by deleting the access token cookie.

    Parameters:
    - response (Response): The response object where the cookie will be deleted.

    Returns:
    - dict: Success message confirming the logout.
    """
    # Delete the access token cookie
    response.delete_cookie(key="access_token")
    
    # Return a logout success message
    return {"message": "Logout successful"}
