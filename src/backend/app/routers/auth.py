from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..dependencies.auth import get_current_user
from ..models.user import User
from ..repositories.user import UserRepository
from ..schemas.auth import LoginRequest, RegisterAdminRequest, TokenResponse, UserResponse
from ..services.auth import create_token, hash_password, verify_password

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
async def login(body: LoginRequest, session: AsyncSession = Depends(get_session)):
    repo = UserRepository(session)
    user = await repo.get_by_username(body.username)
    if not user or not verify_password(body.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials",
        )
    token = create_token(user.id, user.role)
    return TokenResponse(
        token=token,
        role=user.role,
        user=UserResponse(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        ),
    )


@router.get("/me", response_model=UserResponse)
async def me(user: User = Depends(get_current_user)):
    return UserResponse(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )


@router.post("/register-admin", response_model=TokenResponse)
async def register_admin(
    body: RegisterAdminRequest,
    session: AsyncSession = Depends(get_session),
):
    repo = UserRepository(session)
    existing = await repo.get_by_username(body.username)
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists",
        )
    user = await repo.create(
        username=body.username,
        hashed_password=hash_password(body.password),
        first_name="Admin",
        last_name="Test",
        role="admin",
    )
    token = create_token(user.id, user.role)
    return TokenResponse(
        token=token,
        role=user.role,
        user=UserResponse(
            id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name,
            role=user.role,
        ),
    )
