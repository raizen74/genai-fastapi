from datetime import UTC, datetime, timedelta
from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from pydantic import UUID4
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from building_genai_services.database import DBSessionDep

from .entities import User
from .exceptions import AlreadyRegisteredException, UnauthorizedException
from .repositories import TokenRepository
from .schemas import TokenCreate, TokenUpdate, UserCreate, UserInDB


class PasswordService:
    security = HTTPBearer()
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

    async def verify_password(self, password: str, hashed_password: str) -> bool:
        return self.pwd_context.verify(password, hashed_password)

    async def get_password_hash(self, password: str) -> str:
        return self.pwd_context.hash(password)


class TokenService(TokenRepository):
    secret_key = "your_secret_key"
    algorithm = "HS256"
    expires_in_minutes = 60

    async def create_access_token(
        self, data: dict, user_id: UUID4, expires_delta: timedelta | None = None
    ) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=self.expires_in_minutes)
        # Create token record in database
        token_record = await self.create(TokenCreate(user_id=user_id, expires_at=expire))
        to_encode.update({"exp": expire, "iss": "your_service_name", "sub": str(token_record.id)})
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt

    async def deactivate(self, token_id: UUID4) -> None:
        # Get the token first to create a proper update
        token = await self.get(token_id)
        if token:
            await self.update(
                token_id,
                TokenUpdate(user_id=token.user_id, expires_at=token.expires_at, is_active=False),
            )

    def decode(self, encoded_token: str) -> dict:
        try:
            return jwt.decode(encoded_token, self.secret_key, algorithms=[self.algorithm])
        except JWTError:
            raise UnauthorizedException

    async def validate(self, token_id: UUID4) -> bool:
        return (token := await self.get(token_id)) is not None and token.is_active


class UserService:
    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, username: str) -> User | None:
        """Get a user by username."""
        print(f"{username = }")
        async with self.session.begin():
            result = await self.session.execute(
                select(User).where(User.username == username),
            )
        return result.scalars().first()

    async def create(self, user: UserInDB) -> User:
        """Create a new user."""
        new_user = User(
            username=user.username,
            hashed_password=user.hashed_password,
            is_active=user.is_active,
            role=user.role,
        )
        async with self.session.begin():
            self.session.add(new_user)
            await self.session.flush()
            await self.session.refresh(new_user)
        return new_user


security = HTTPBearer()
LoginFormDep = Annotated[OAuth2PasswordRequestForm, Depends()]
AuthHeaderDep = Annotated[HTTPAuthorizationCredentials, Depends(security)]


class AuthService:
    def __init__(self, session: DBSessionDep):
        self.password_service = PasswordService()
        self.token_service = TokenService(session)
        self.user_service = UserService(session)

    async def register_user(self, user: UserCreate) -> User:
        print(f"Registering user: {user.username}")
        if await self.user_service.get(user.username):
            raise AlreadyRegisteredException
        hashed_password = await self.password_service.get_password_hash(user.password)
        return await self.user_service.create(
            UserInDB(username=user.username, hashed_password=hashed_password),
        )

    async def authenticate_user(self, form_data: LoginFormDep) -> str:
        print(f"Authenticating user: {form_data.username}")
        if not (user := await self.user_service.get(form_data.username)):
            raise UnauthorizedException
        if not await self.password_service.verify_password(
            form_data.password,
            user.hashed_password,
        ):
            raise UnauthorizedException
        # Convert SQLAlchemy User model to dict for JWT payload. Explicit, secure, only includes fields you want in the JWT token
        # Option 2: Via Pydantic with from_attributes=True -> user_dict = UserOut.model_validate(user).model_dump() Good for: API responses, but includes extra fields you may not want in JWT
        user_data = {
            "user_id": str(user.id),
            "username": user.username,
            "role": user.role,
        }
        return await self.token_service.create_access_token(user_data, user_id=user.id)

    async def get_current_user(self, credentials: AuthHeaderDep) -> User:
        if credentials.scheme != "Bearer":
            raise UnauthorizedException
        if not (token := credentials.credentials):
            raise UnauthorizedException
        payload = self.token_service.decode(token)
        if not await self.token_service.validate(payload.get("sub")):
            raise UnauthorizedException
        if not (username := payload.get("username")):
            raise UnauthorizedException
        if not (user := await self.user_service.get(username)):
            raise UnauthorizedException
        return user

    async def logout(self, credentials: AuthHeaderDep) -> None:
        payload = self.token_service.decode(credentials.credentials)
        await self.token_service.deactivate(payload.get("sub"))

    # Add Password Reset Method
    async def reset_password(self): ...
