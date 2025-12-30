from typing import Annotated

from fastapi import APIRouter, Depends

from building_genai_services.database import DBSessionDep

from .schemas import TokenOut, UserCreate, UserOut
from .services import AuthHeaderDep, AuthService, LoginFormDep

router = APIRouter(prefix="/auth", tags=["Authentication"])


def get_auth_service(session: DBSessionDep) -> AuthService:
    """Dependency to create AuthService with database session."""
    return AuthService(session)

# FastAPI creates a NEW AuthService instance for EVERY request and injects it as a controller argument
# This is actually the correct and recommended pattern because:
# Fresh database sessions - Each request gets its own DB session (essential for transaction isolation)
# No state pollution - No shared state between requests
# Thread-safe - No concurrency issues
# Resource cleanup - Sessions properly close after each request
AuthServiceDep = Annotated[AuthService, Depends(get_auth_service)]


@router.post("/register")
async def register_user_controller(
    user: UserCreate,
    auth_service: AuthServiceDep,
) -> UserOut:
    new_user = await auth_service.register_user(user)
    return UserOut.model_validate(new_user)


@router.post("/token")
async def login_for_access_token_controller(
    form_data: LoginFormDep,
    auth_service: AuthServiceDep,
) -> TokenOut:
    access_token = await auth_service.authenticate_user(form_data)
    return TokenOut(access_token=access_token, token_type="bearer")


@router.post("/logout")
async def logout_access_token_controller(
    credentials: AuthHeaderDep,
    auth_service: AuthServiceDep,
) -> dict:
    await auth_service.logout(credentials)
    return {"message": "Logged out"}


@router.post("/reset-password")
async def reset_password_controller(
    auth_service: AuthServiceDep,
) -> dict:
    await auth_service.reset_password()
    return {
        "message": "If an account exists, a password reset link will be sent to the provided email"
    }
