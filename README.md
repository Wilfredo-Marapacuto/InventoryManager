# Overview

Inventory Manager is a console application that helps users manage product names, quantities, and prices. My purpose in creating this software is to develop my understanding of SQL and persistent data storage using Python.

The program integrates with SQLite to create a database, insert products, retrieve and search records, update product information, and delete products after confirmation. It also calculates inventory totals using SQL aggregate functions.

To run the program on Windows, open a terminal in the project folder and enter:

    py inventory_manager.py

Select an option from the menu and follow the prompts. The program automatically creates its database on the first run and keeps the data between sessions.

[Software Demo Video](https://youtu.be/4VwdEypnX5A)

# Relational Database

This application uses SQLite, a relational database stored locally in a file named inventory.db. Python communicates with the database through the sqlite3 standard library.

The database contains one table named products with these columns:

- id: An integer primary key generated automatically.
- name: A required text value containing the product name.
- quantity: A required nonnegative integer representing available units.
- price: A required nonnegative real number representing the unit price.

The program uses CREATE TABLE, INSERT, SELECT, UPDATE, and DELETE statements. Parameterized queries keep user input separate from SQL instructions.

The inventory report uses COUNT to calculate the number of product records and SUM to calculate total units and total inventory value. COALESCE makes empty inventory totals display as zero.

# Development Environment

I developed and ran this application using Visual Studio Code and its integrated PowerShell terminal on Windows.

The programming language is Python 3. The application uses these standard libraries:

- sqlite3: Creates and accesses the SQLite database.
- pathlib: Locates the database in the same folder as the program.
- math: Checks that entered prices are finite numbers.

No external Python packages are required.

# Useful Websites

- [Python sqlite3 Documentation](https://docs.python.org/3/library/sqlite3.html)
- [SQLite Documentation](https://www.sqlite.org/docs.html)
- [Python Documentation](https://docs.python.org/3/)

# Future Work

- Add categories in a separate table and use SQL joins.
- Record stock changes with dates and transaction history.
- Export inventory reports to CSV files.
- Store prices as integer cents for exact currency calculations.