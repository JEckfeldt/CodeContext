from fastapi import APIRouter, HTTPException, status

from app.core.auth_deps import CurrentUser
from app.core.deps import DbSession
from app.core.security import create_access_token
from app.schemas.auth import (
    AuthResponse,
    UserLoginRequest,
    UserRead,
    UserRegisterRequest,
)
from app.services import auth_service
from app.services.auth_service import EmailAlreadyRegisteredError, InvalidCredentialsError

router = APIRouter(prefix="/auth", tags=["auth"])


def _auth_response(user) -> AuthResponse:
    token = create_access_token(subject=str(user.id))
    return AuthResponse(
        access_token=token,
        user=UserRead.model_validate(user),
    )


@router.post("/register", response_model=AuthResponse, status_code=status.HTTP_201_CREATED)
async def register_user(
    payload: UserRegisterRequest,
    session: DbSession,
) -> AuthResponse:
    try:
        user = await auth_service.register_user(
            session,
            email=payload.email,
            password=payload.password,
        )
    except EmailAlreadyRegisteredError as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(exc),
        ) from exc
    return _auth_response(user)


@router.post("/login", response_model=AuthResponse)
async def login_user(
    payload: UserLoginRequest,
    session: DbSession,
) -> AuthResponse:
    try:
        user = await auth_service.authenticate_user(
            session,
            email=payload.email,
            password=payload.password,
        )
    except InvalidCredentialsError as exc:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=str(exc),
        ) from exc
    return _auth_response(user)


@router.get("/me", response_model=UserRead)
async def read_current_user(current_user: CurrentUser) -> UserRead:
    return UserRead.model_validate(current_user)
