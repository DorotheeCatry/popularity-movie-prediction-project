from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List

class User(SQLModel, table=True):
    """
    Model representing a user in the system.

    Attributes:
    - `id`: Unique identifier for the user (primary key).
    - `username`: Unique username used for authentication.
    - `email`: Unique email address of the user.
    - `hashed_password`: Hashed password of the user for security.
    - `role`: Role of the user (default is "user").
    - `is_active`: User's status, default is active.
    """
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(index=False, unique=False)
    email: str = Field(unique=False, index=False)
    hashed_password: str
    role: str = Field(nullable=False, default="user")
    is_active: bool = Field(default=True)  # User's status, non-active by default (I put it to active for our project, easier to insert EliteLoans in the BDD)

    # Defining the relationship with LoanRequests model (a user can have many loan requests)
    loan_requests: List["LoanRequests"] = Relationship(back_populates="user")
