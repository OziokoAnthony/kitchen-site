# Iya Ngozi's Kitchen API

Beginner-friendly FastAPI ordering service using session + cookie authentication.

## Requirements

- Python 3.11+ recommended
- VS Code
- Git (optional)
- Internet connection for installing Python packages

## Install

Create and activate a virtual environment:

### Windows Git Bash

```bash
python -m venv .venv
source .venv/Scripts/activate
python -m pip install -r requirements.txt
```

If `python` does not work, use the Python command that works on your computer.

## Run

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001
```

Open:

- Swagger UI: http://127.0.0.1:8001/docs
- ReDoc: http://127.0.0.1:8001/redoc

The SQLite database is created automatically.

## Demo accounts

The application creates these accounts on first startup:

- Customer: `customer@example.com` / `customer123`
- Staff: `staff@example.com` / `staff123`

Change these passwords before using the project for real users.

## Main features

- Register and login
- Session + cookie authentication
- Public menu browsing
- Filter dishes by branch/category
- Staff-only dish management
- Sold-out dishes
- Multi-item orders
- Customer-only access to their own orders
- Order totals
- Order status progression
- 401, 403, 404 and 409 errors
- Background receipt and kitchen log
- Timing middleware
- Today's orders for staff
- Busiest dish today endpoint
- Basic SSE order status stream
