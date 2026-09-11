import os


def write_receipt_and_log(order, customer, item_lines):
    os.makedirs("receipts", exist_ok=True)

    receipt_file = f"receipts/order_{order.id}.txt"

    with open(receipt_file, "w", encoding="utf-8") as file:
        file.write("IYA NGOZI'S KITCHEN RECEIPT\n")
        file.write("----------------------------\n")
        file.write(f"Order ID: {order.id}\n")
        file.write(f"Customer: {customer.name}\n")
        file.write(f"Total: {order.total:.2f}\n")
        file.write(f"Status: {order.status}\n\n")

        for line in item_lines:
            file.write(line + "\n")

    with open("kitchen.log", "a", encoding="utf-8") as log:
        log.write(
            f"NEW ORDER #{order.id} - {customer.name} - "
            f"Total: {order.total:.2f}\n"
        )
