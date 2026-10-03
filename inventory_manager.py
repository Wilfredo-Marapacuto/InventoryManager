"""Manage a product inventory using Python and a SQLite database."""

import math
import sqlite3
from pathlib import Path


DATABASE_PATH = Path(__file__).resolve().parent / "inventory.db"


def connect_database():
    """Open the database and allow access to columns by name."""
    connection = sqlite3.connect(DATABASE_PATH)
    connection.row_factory = sqlite3.Row
    return connection


def create_table(connection):
    """Create the products table if it does not already exist."""
    connection.execute(
        """
        CREATE TABLE IF NOT EXISTS products (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL CHECK(length(trim(name)) > 0),
            quantity INTEGER NOT NULL CHECK(quantity >= 0),
            price REAL NOT NULL CHECK(price >= 0)
        )
        """
    )
    connection.commit()


def read_name(prompt):
    """Request a product name and reject empty input."""
    while True:
        name = input(prompt).strip()
        if name:
            return name
        print("The product name cannot be empty.")


def read_integer(prompt, minimum=0):
    """Request a whole number that meets the minimum value."""
    while True:
        try:
            value = int(input(prompt))
            if value >= minimum:
                return value
            print(f"Enter a whole number of at least {minimum}.")
        except ValueError:
            print("Invalid input. Enter a whole number.")


def read_price(prompt):
    """Request a finite, nonnegative price with two decimal places."""
    while True:
        try:
            value = float(input(prompt))
            if math.isfinite(value) and value >= 0:
                return round(value, 2)
            print("Enter a valid price of zero or more.")
        except ValueError:
            print("Invalid input. Enter a number such as 12.50.")


def display_products(products):
    """Display query results with the value of each product's stock."""
    if not products:
        print("\nNo products found.")
        return

    print("\n" + "-" * 85)
    print(
        f"{'ID':<6} {'Product':<30} {'Quantity':>10} "
        f"{'Unit Price':>15} {'Stock Value':>15}"
    )
    print("-" * 85)

    for product in products:
        stock_value = product["quantity"] * product["price"]
        print(
            f"{product['id']:<6} "
            f"{product['name'][:30]:<30} "
            f"{product['quantity']:>10} "
            f"${product['price']:>14.2f} "
            f"${stock_value:>14.2f}"
        )

    print("-" * 85)


def get_product(connection, product_id):
    """Retrieve one product using a parameterized SQL query."""
    return connection.execute(
        "SELECT id, name, quantity, price FROM products WHERE id = ?",
        (product_id,),
    ).fetchone()


def add_product(connection):
    """Insert a product with the name, quantity, and price entered."""
    print("\nADD PRODUCT")
    name = read_name("Product name: ")
    quantity = read_integer("Quantity: ")
    price = read_price("Unit price ($): ")

    # Placeholders keep user input separate from SQL instructions.
    with connection:
        cursor = connection.execute(
            "INSERT INTO products (name, quantity, price) VALUES (?, ?, ?)",
            (name, quantity, price),
        )

    print(f"Product added successfully. Product ID: {cursor.lastrowid}")


def view_inventory(connection):
    """Retrieve all products and display them alphabetically."""
    products = connection.execute(
        """
        SELECT id, name, quantity, price
        FROM products
        ORDER BY name COLLATE NOCASE, id
        """
    ).fetchall()
    display_products(products)


def search_products(connection):
    """Find products whose names contain the entered search text."""
    search_text = read_name("\nEnter a product name to search: ")

    # instr searches for literal text without treating % as a wildcard.
    products = connection.execute(
        """
        SELECT id, name, quantity, price
        FROM products
        WHERE instr(lower(name), lower(?)) > 0
        ORDER BY name COLLATE NOCASE, id
        """,
        (search_text,),
    ).fetchall()
    display_products(products)


def update_product(connection):
    """Update an existing product after displaying its current values."""
    print("\nUPDATE PRODUCT")
    product_id = read_integer("Product ID: ", minimum=1)
    product = get_product(connection, product_id)

    if product is None:
        print("Product not found.")
        return

    display_products([product])
    print("Enter the new values for this product.")
    name = read_name("New product name: ")
    quantity = read_integer("New quantity: ")
    price = read_price("New unit price ($): ")

    with connection:
        connection.execute(
            """
            UPDATE products
            SET name = ?, quantity = ?, price = ?
            WHERE id = ?
            """,
            (name, quantity, price, product_id),
        )

    print("Product updated successfully.")


def delete_product(connection):
    """Delete a selected product only after explicit confirmation."""
    print("\nDELETE PRODUCT")
    product_id = read_integer("Product ID: ", minimum=1)
    product = get_product(connection, product_id)

    if product is None:
        print("Product not found.")
        return

    display_products([product])
    confirmation = input("Type YES to delete this product: ").strip()

    if confirmation.upper() != "YES":
        print("Deletion canceled.")
        return

    with connection:
        connection.execute(
            "DELETE FROM products WHERE id = ?",
            (product_id,),
        )

    print("Product deleted successfully.")


def inventory_report(connection):
    """Use SQL aggregate functions to summarize the inventory."""
    # COUNT and SUM produce useful totals directly in the database.
    report = connection.execute(
        """
        SELECT
            COUNT(*) AS product_count,
            COALESCE(SUM(quantity), 0) AS total_units,
            COALESCE(SUM(quantity * price), 0) AS total_value
        FROM products
        """
    ).fetchone()

    print("\nINVENTORY REPORT")
    print("-" * 40)
    print(f"Product records: {report['product_count']}")
    print(f"Total units: {report['total_units']}")
    print(f"Total inventory value: ${report['total_value']:.2f}")
    print("-" * 40)


def show_menu():
    """Display the available inventory operations."""
    print("\n========== INVENTORY MANAGER ==========")
    print("1. Add product")
    print("2. View inventory")
    print("3. Search products")
    print("4. Update product")
    print("5. Delete product")
    print("6. Inventory report")
    print("7. Exit")
    print("=======================================")


def run_menu(connection):
    """Keep processing menu choices until the user chooses to exit."""
    actions = {
        "1": add_product,
        "2": view_inventory,
        "3": search_products,
        "4": update_product,
        "5": delete_product,
        "6": inventory_report,
    }

    while True:
        show_menu()
        choice = input("Choose an option (1-7): ").strip()

        if choice == "7":
            print("Inventory saved. Goodbye!")
            return

        action = actions.get(choice)
        if action is None:
            print("Invalid option. Choose a number from 1 to 7.")
            continue

        try:
            action(connection)
        except sqlite3.Error as error:
            print(f"Database operation failed: {error}")


def main():
    """Initialize the database and close it when the program ends."""
    connection = None

    try:
        connection = connect_database()
        create_table(connection)
        print("Welcome to Inventory Manager!")
        run_menu(connection)
    except sqlite3.Error as error:
        print(f"Unable to open or initialize the database: {error}")
    except (KeyboardInterrupt, EOFError):
        print("\nProgram closed.")
    finally:
        if connection is not None:
            connection.close()


if __name__ == "__main__":
    main()