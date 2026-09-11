from typing import Optional

from pydantic import BaseModel, Field


class RegisterData(BaseModel):
    name: str
    email: str
    password: str


class LoginData(BaseModel):
    email: str
    password: str


class CustomerResponse(BaseModel):
    id: int
    name: str
    email: str
    role: str


class DishCreate(BaseModel):
    name: str
    description: str = ""
    price: float = Field(gt=0)
    branch: str
    category: str


class DishUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None
    price: Optional[float] = Field(default=None, gt=0)
    branch: Optional[str] = None
    category: Optional[str] = None
    sold_out: Optional[bool] = None


class OrderItemCreate(BaseModel):
    dish_id: int
    quantity: int = Field(gt=0)


class OrderCreate(BaseModel):
    items: list[OrderItemCreate]
