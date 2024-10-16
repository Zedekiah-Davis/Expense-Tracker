import sqlite3

# Connect to SQLite database (creates a new file if it doesn't exist)
conn = sqlite3.connect('expense_tracker.db')
cursor = conn.cursor()

# Create tables
cursor.executescript('''
    -- Create categories table
    CREATE TABLE IF NOT EXISTS categories (
        category_id INTEGER PRIMARY KEY,
        category_name TEXT NOT NULL UNIQUE
    );

    -- Create expenses table
    CREATE TABLE IF NOT EXISTS expenses (
        expense_id INTEGER PRIMARY KEY,
        date DATE NOT NULL,
        category_id INTEGER,
        amount NUMERIC,
        FOREIGN KEY (category_id) REFERENCES categories (category_id)
    );
''')

# Insert categories only if they don't already exist
categories = [('Food',), ('Transportation',), ('Utilities',), ('Entertainment',), ('Shopping',), ('Miscellaneous',)]
cursor.executemany('INSERT OR IGNORE INTO categories (category_name) VALUES (?)', categories)
conn.commit()

# Function to record a new expense
def record_expense(date, category_id, amount):
    cursor.execute('''
        INSERT INTO expenses (date, category_id, amount)
        VALUES (?, ?, ?)
    ''', (date, category_id, amount))
    conn.commit()

# Function to update an existing expense
def update_expense(expense_id, new_date=None, new_category_id=None, new_amount=None):
    query = 'UPDATE expenses SET '
    updates = []
    parameters = []
    
    if new_date:
        updates.append('date = ?')
        parameters.append(new_date)
    if new_category_id:
        updates.append('category_id = ?')
        parameters.append(new_category_id)
    if new_amount is not None:
        updates.append('amount = ?')
        parameters.append(new_amount)

    query += ', '.join(updates)
    query += ' WHERE expense_id = ?'
    parameters.append(expense_id)

    cursor.execute(query, parameters)
    conn.commit()

# Function to delete an expense
def delete_expense(expense_id):
    cursor.execute('DELETE FROM expenses WHERE expense_id = ?', (expense_id,))
    conn.commit()

# Function to get a spending summary
def get_spending_summary():
    cursor.execute('''
        SELECT c.category_name, SUM(e.amount) AS total_amount
        FROM expenses e
        JOIN categories c ON e.category_id = c.category_id
        GROUP BY c.category_name
    ''')
    rows = cursor.fetchall()
    for row in rows:
        print(f"{row[0]}: ${row[1]:.2f}")

# Function to query expenses within a date range
def get_expenses_by_date_range(start_date, end_date):
    cursor.execute('''
        SELECT * FROM expenses
        WHERE date BETWEEN ? AND ?
    ''', (start_date, end_date))
    rows = cursor.fetchall()
    
    for row in rows:
        print(f"Expense ID: {row[0]}, Date: {row[1]}, Category ID: {row[2]}, Amount: ${row[3]:.2f}")

# Example of recording an expense
record_expense('2024-10-11', 1, 25.50)  # Record $25.50 spent on Food
record_expense('2024-10-12', 2, 15.75)  # Record $15.75 spent on Transportation
record_expense('2024-10-13', 3, 45.00)  # Record $45.00 spent on Utilities
record_expense('2024-10-14', 4, 60.00)  # Record $60.00 spent on Entertainment
record_expense('2024-10-15', 5, 80.50)  # Record $80.50 spent on Shopping
record_expense('2024-10-16', 6, 12.00)  # Record $12.00 spent on Miscellaneous

# Example of updating an expense
update_expense(1, new_amount=30.00)  # Update amount of expense with ID 1 to $30.00
update_expense(2, new_category_id=3)  # Change category of expense ID 2 to Utilities
update_expense(3, new_date='2024-10-20', new_amount=50.00)  # Change date and amount for expense ID 3

# Example of deleting an expense
delete_expense(6)  # Delete the expense with ID 6 (Miscellaneous $12.00 expense)

# Print spending summaries
get_spending_summary()

# Example of querying expenses within a date range
print("\nExpenses between 2024-10-11 and 2024-10-15:")
get_expenses_by_date_range('2024-10-11', '2024-10-15')
