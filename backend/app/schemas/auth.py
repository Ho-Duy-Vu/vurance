from pydantic import BaseModel, EmailStr, field_validator


class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    full_name: str | None = None
    province: str | None = None

    @field_validator("password")
    @classmethod
    def password_strength(cls, v: str) -> str:
        if len(v) < 8:
            raise ValueError("Mật khẩu phải có ít nhất 8 ký tự")
        if not any(c.isupper() for c in v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ hoa")
        if not any(c.islower() for c in v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ thường")
        if not any(c.isdigit() for c in v):
            raise ValueError("Mật khẩu phải có ít nhất 1 chữ số")
        return v


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class UserResponse(BaseModel):
    id: str
    email: str
    full_name: str | None
    role: str
    province: str | None
    region: str | None
    is_active: bool

    @classmethod
    def from_user(cls, user) -> "UserResponse":
        return cls(
            id=str(user.id),
            email=user.email,
            full_name=user.full_name,
            role=user.role,
            province=user.province,
            region=user.region,
            is_active=user.is_active,
        )
