from pydantic import ConfigDict, EmailStr, Field, field_validator
from sqlmodel import SQLModel


class UserCreate(SQLModel):
	email: EmailStr
	password: str = Field(min_length=8, max_length=128)

	@field_validator("password")
	@classmethod
	def password_fits_bcrypt(cls, value: str) -> str:
		if len(value.encode("utf-8")) > 72:
			raise ValueError("Le mot de passe ne peut pas dépasser 72 octets")
		return value


class UserRead(SQLModel):
	model_config = ConfigDict(from_attributes=True)

	id: int
	email: str


class LoginRequest(SQLModel):
	email: EmailStr
	password: str = Field(min_length=1, max_length=128)

	@field_validator("password")
	@classmethod
	def password_fits_bcrypt(cls, value: str) -> str:
		if len(value.encode("utf-8")) > 72:
			raise ValueError("Le mot de passe ne peut pas dépasser 72 octets")
		return value


class TokenRead(SQLModel):
	access_token: str
	token_type: str = "bearer"
