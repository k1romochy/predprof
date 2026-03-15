from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from ..core.database import get_session
from ..dependencies.auth import require_admin
from ..models.user import User
from ..repositories.user import UserRepository
from ..schemas.admin import CreateUserRequest
from ..schemas.auth import UserResponse
from ..services.auth import hash_password

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/users", response_model=UserResponse)
async def create_user(
    body: CreateUserRequest,
    session: AsyncSession = Depends(get_session),
    _admin: User = Depends(require_admin),
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
        first_name=body.first_name,
        last_name=body.last_name,
        role="user",
    )
    return UserResponse(
        id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name,
        role=user.role,
    )
