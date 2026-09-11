import asyncio
import json
from datetime import datetime

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import func
from sqlalchemy.orm import Session

from app.background import write_receipt_and_log
from app.database import get_db
from app.dependencies import get_current_user, get_staff_user
from app.models import Dish, Order, OrderItem
from app.schemas import OrderCreate

router = APIRouter()

STATUS_FLOW = [
    "received",
    "cooking",
    "out_for_delivery",
    "delivered"
]


def order_to_dict(order):
    items = []

    for item in order.items:
        items.append({
            "dish_id": item.dish_id,
            "dish_name": item.dish.name,
            "quantity": item.quantity,
            "price_each": item.price,
            "line_total": item.quantity * item.price
        })

    return {
        "id": order.id,
        "customer_id": order.customer_id,
        "status": order.status,
        "total": order.total,
        "created_at": order.created_at,
        "items": items
    }


@router.post("/")
def create_order(
    data: OrderCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    if not data.items:
        raise HTTPException(
            status_code=400,
            detail="Order must contain at least one dish"
        )

    order = Order(
        customer_id=current_user.id,
        status="received",
        total=0
    )

    db.add(order)
    db.flush()

    total = 0
    item_lines = []

    for requested_item in data.items:
        dish = db.query(Dish).filter(
            Dish.id == requested_item.dish_id
        ).first()

        if not dish:
            db.rollback()
            raise HTTPException(
                status_code=404,
                detail=f"Dish {requested_item.dish_id} not found"
            )

        if dish.sold_out:
            db.rollback()
            raise HTTPException(
                status_code=409,
                detail=f"{dish.name} is sold out"
            )

        line_total = dish.price * requested_item.quantity
        total += line_total

        item = OrderItem(
            order_id=order.id,
            dish_id=dish.id,
            quantity=requested_item.quantity,
            price=dish.price
        )

        db.add(item)

        item_lines.append(
            f"{dish.name} x {requested_item.quantity} = {line_total:.2f}"
        )

    order.total = total
    db.commit()
    db.refresh(order)

    background_tasks.add_task(
        write_receipt_and_log,
        order,
        current_user,
        item_lines
    )

    return {
        "message": "Order received",
        "order": order_to_dict(order)
    }


@router.get("/mine")
def my_orders(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    orders = db.query(Order).filter(
        Order.customer_id == current_user.id
    ).order_by(Order.created_at.desc()).all()

    return [order_to_dict(order) for order in orders]


@router.get("/{order_id}")
def get_my_order(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot see another customer's order"
        )

    return order_to_dict(order)


@router.get("/staff/today")
def todays_orders(
    db: Session = Depends(get_db),
    staff=Depends(get_staff_user)
):
    today = datetime.utcnow().date()

    orders = db.query(Order).filter(
        func.date(Order.created_at) == str(today)
    ).order_by(Order.created_at.desc()).all()

    return [order_to_dict(order) for order in orders]


@router.patch("/{order_id}/next-status")
def next_status(
    order_id: int,
    db: Session = Depends(get_db),
    staff=Depends(get_staff_user)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    current_index = STATUS_FLOW.index(order.status)

    if current_index == len(STATUS_FLOW) - 1:
        raise HTTPException(
            status_code=409,
            detail="Order is already delivered"
        )

    order.status = STATUS_FLOW[current_index + 1]
    db.commit()
    db.refresh(order)

    return {
        "message": "Order status updated",
        "order_id": order.id,
        "status": order.status
    }


@router.get("/bonus/busiest-dish-today")
def busiest_dish_today(
    db: Session = Depends(get_db),
    staff=Depends(get_staff_user)
):
    today = datetime.utcnow().date()

    result = (
        db.query(
            Dish.id,
            Dish.name,
            func.sum(OrderItem.quantity).label("quantity")
        )
        .join(OrderItem, OrderItem.dish_id == Dish.id)
        .join(Order, Order.id == OrderItem.order_id)
        .filter(func.date(Order.created_at) == str(today))
        .group_by(Dish.id, Dish.name)
        .order_by(func.sum(OrderItem.quantity).desc())
        .first()
    )

    if not result:
        return {"message": "No orders today"}

    return {
        "dish_id": result.id,
        "dish": result.name,
        "quantity_sold": result.quantity
    }


@router.get("/{order_id}/stream")
async def order_stream(
    order_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user)
):
    order = db.query(Order).filter(
        Order.id == order_id
    ).first()

    if not order:
        raise HTTPException(
            status_code=404,
            detail="Order not found"
        )

    if order.customer_id != current_user.id:
        raise HTTPException(
            status_code=403,
            detail="You cannot watch another customer's order"
        )

    async def event_generator():
        last_status = None

        for _ in range(30):
            db2 = next(get_db())
            try:
                current_order = db2.query(Order).filter(
                    Order.id == order_id
                ).first()

                if not current_order:
                    break

                if current_order.status != last_status:
                    last_status = current_order.status
                    data = json.dumps({
                        "order_id": order_id,
                        "status": last_status
                    })
                    yield f"data: {data}\n\n"

                if last_status == "delivered":
                    break
            finally:
                db2.close()

            await asyncio.sleep(2)

    return StreamingResponse(
        event_generator(),
        media_type="text/event-stream"
    )
