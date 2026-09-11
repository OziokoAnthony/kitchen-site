from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_current_user
from app.models import Customer
from app.schemas import CustomerResponse, LoginData, RegisterData
from app.security import check_password, hash_password

router = APIRouter()


@router.post("/register", response_model=CustomerResponse)
def register(data: RegisterData, db: Session = Depends(get_db)):
    old_customer = db.query(Customer).filter(
        Customer.email == data.email
    ).first()

    if old_customer:
        raise HTTPException(
            status_code=409,
            detail="Email already registered"
        )

    customer = Customer(
        name=data.name,
        email=data.email,
        password=hash_password(data.password),
        role="customer"
    )

    db.add(customer)
    db.commit()
    db.refresh(customer)

    return customer


@router.post("/login")
def login(
    data: LoginData,
    request: Request,
    db: Session = Depends(get_db)
):
    customer = db.query(Customer).filter(
        Customer.email == data.email
    ).first()

    if not customer or not check_password(
        data.password,
        customer.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Wrong email or password"
        )

    request.session["user_id"] = customer.id

    return {
        "message": "Login successful",
        "customer_id": customer.id,
        "role": customer.role
    }


@router.post("/logout")
def logout(request: Request):
    request.session.clear()
    return {"message": "Logout successful"}


@router.get("/me", response_model=CustomerResponse)
def me(current_user=Depends(get_current_user)):
    return current_user
