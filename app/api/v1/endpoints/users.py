from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from app.models.users import User
from app.schemas.user import UserRead, UserCreate
from app.db.session import get_session
from app.core.jwt_handler import verify_token
from app.core.security import get_password_hash, get_current_user

# Initialize the router for user-related routes
router = APIRouter()

# OAuth2 password bearer for token authentication (to be used in the header of requests)
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/users")

@router.get("/users/me", response_model=UserRead)
def read_users_me(
    token: str = Depends(oauth2_scheme),  # Extract token from Authorization header
    session: Session = Depends(get_session)  # Get the DB session dependency
):
    """
    Endpoint to get the current authenticated user's details using the JWT token.

    Parameters:
    - `token`: The authentication token provided by the user (in the Authorization header).
    - `session`: The database session used to interact with the database.

    Returns:
    - A UserRead object containing the user's details.
    """
    # Verify the JWT token and extract the payload
    payload = verify_token(token)
    if payload is None:
        # If the token is invalid or expired, return a 401 Unauthorized error
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Extract the username from the decoded payload (sub represents the subject)
    username: str = payload.get("sub")
    
    # Query the database for the user based on the extracted username
    statement = select(User).where(User.username == username)
    user = session.exec(statement).first()  # Execute the query and get the first result
    
    if user is None:
        # If the user is not found or the account has been deleted, return a 404 error
        raise HTTPException(status_code=404, detail="User not found or account deleted")
    
    # Return the user's data serialized according to the UserRead schema
    return user


@router.post("/admin/users", response_model=UserRead)
def create_user(user: UserCreate, session: Session = Depends(get_session)):
    """
    Create a new user in the system.

    Parameters:
    - `user` (UserCreate): The user data for registration.
    - `session` (Session): Database session dependency.

    Returns:
    - `UserRead`: The newly created user (without password).
    """
    # Check if the user already exists by email
    existing_user = session.exec(select(User).where(User.email == user.email)).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="An account with this email already exists")

    # Hash the password before storing it
    hashed_password = get_password_hash(user.password)

    # Create the new user
    new_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hashed_password,
        role=user.role,
        is_active=False  # The user must be activated
    )
    
    session.add(new_user)
    session.commit()
    session.refresh(new_user)

    return new_user


@router.get("/admin/users")
def get_users(current_user: User = Depends(get_current_user), session: Session = Depends(get_session)):
    """
    Retrieve the list of all users (admin only).

    Parameters:
    - `current_user` (User): The authenticated user (must be admin).
    - `session` (Session): Database session dependency.

    Returns:
    - `dict`: A list of all users' names.
    """
    # Check if the user is authenticated and is an admin
    if not current_user or current_user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admins only")

    # Retrieve all users
    users = session.exec(select(User)).all()

    return {"Users": [user.username for user in users]}
