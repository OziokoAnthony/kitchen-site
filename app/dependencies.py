from fastapi import Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import Customer


def get_current_user(
    request: Request,
    db: Session = Depends(get_db)
):
    user_id = request.session.get("user_id")

    if not user_id:
        raise HTTPException(
            status_code=401,
            detail="You must login first"
        )

    user = db.query(Customer).filter(Customer.id == user_id).first()

    if not user:
        request.session.clear()
        raise HTTPException(
            status_code=401,
            detail="Session is invalid"
        )

    return user


def get_staff_user(
    current_user: Customer = Depends(get_current_user)
):
    if current_user.role != "staff":
        raise HTTPException(
            status_code=403,
            detail="Only kitchen staff can do this"
        )

    return current_user
