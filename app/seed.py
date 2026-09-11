from app.models import Customer, Dish
from app.security import hash_password


def seed_database(db):
    if db.query(Customer).count() == 0:
        customer = Customer(
            name="Anthony",
            email="anthony@gmail.com",
            password=hash_password("customer123"),
            role="customer"
        )

        staff = Customer(
            name="Arkland",
            email="arkland@gmail.com",
            password=hash_password("staff123"),
            role="staff"
        )

        db.add(customer)
        db.add(staff)
        db.commit()

    if db.query(Dish).count() == 0:
        dishes = [
            Dish(
                name="Jollof Rice",
                description="Party style jollof rice",
                price=2500,
                branch="Enugu",
                category="rice"
            ),
            Dish(
                name="Egusi Soup",
                description="Traditional egusi soup",
                price=3000,
                branch="Enugu",
                category="soups"
            ),
            Dish(
                name="Fried Plantain",
                description="Sweet fried plantain",
                price=1500,
                branch="Abuja",
                category="sides"
            ),
            Dish(
                name="White Rice",
                description="Steamed white rice",
                price=2000,
                branch="Lagos",
                category="rice"
            )
        ]

        db.add_all(dishes)
        db.commit()
