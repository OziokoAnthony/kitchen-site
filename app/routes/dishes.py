from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies import get_staff_user
from app.models import Dish
from app.schemas import DishCreate, DishUpdate

router = APIRouter()


@router.get("/")
def get_dishes(
    branch: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db)
):
    query = db.query(Dish)

    if branch:
        query = query.filter(Dish.branch == branch)

    if category:
        query = query.filter(Dish.category == category)

    return query.all()


@router.get("/{dish_id}")
def get_dish(dish_id: int, db: Session = Depends(get_db)):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()

    if not dish:
        raise HTTPException(
            status_code=404,
            detail="Dish not found"
        )

    return dish


@router.post("/")
def add_dish(
    data: DishCreate,
    db: Session = Depends(get_db),
    staff=Depends(get_staff_user)
):
    dish = Dish(**data.model_dump())
    db.add(dish)
    db.commit()
    db.refresh(dish)

    return dish


@router.put("/{dish_id}")
def update_dish(
    dish_id: int,
    data: DishUpdate,
    db: Session = Depends(get_db),
    staff=Depends(get_staff_user)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()

    if not dish:
        raise HTTPException(
            status_code=404,
            detail="Dish not found"
        )

    values = data.model_dump(exclude_unset=True)

    for key, value in values.items():
        setattr(dish, key, value)

    db.commit()
    db.refresh(dish)

    return dish


@router.patch("/{dish_id}/sold-out")
def mark_sold_out(
    dish_id: int,
    db: Session = Depends(get_db),
    staff=Depends(get_staff_user)
):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()

    if not dish:
        raise HTTPException(
            status_code=404,
            detail="Dish not found"
        )

    dish.sold_out = True
    db.commit()

    return {"message": "Dish marked as sold out"}
