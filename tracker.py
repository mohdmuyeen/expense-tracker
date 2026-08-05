import sqlite3
from datetime import datetime

DB_NAME = 'tracker.db'

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS expenses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            date TEXT NOT NULL,
            category TEXT NOT NULL,
            amount REAL NOT NULL,
            description TEXT        
        )
    """)
    conn.commit()
    conn.close()

def add_expense():
    date = input("Enter the date (YYYY-MM-DD): ").strip()
    if not date:
        date = datetime.now().strftime("%Y-%m-%d")
    category = input("Enter the category: ").strip()
    amount = float(input("Enter the amount: ").strip())
    description = input("Enter a description (optional): ").strip()

    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO expenses (date, category, amount, description) VALUES (?, ?, ?, ?)",
        (date, category, amount, description)
    )
    conn.commit()
    conn.close()
    print("✓ Expense added!\n")

def view_expenses():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT id, date, category, amount, description FROM expenses ORDER BY date DESC")
    expenses = cursor.fetchall()
    conn.close()

    if not expenses:
        print("No expenses found.")
        return

    print(f"\n{'ID':<5} {'Date':<12} {'Category':<15} {'Amount':<10} {'Description'}")
    print("-" * 60)
    for expense in expenses:
        id, date, category, amount, description = expense
        print(f"{id:<5} {date:<12} {category:<15} {amount:<10.2f} {description}")
    print()

def delete_expense():
    expense_id = input("Enter the ID of the expense to delete: ").strip()
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
    conn.commit()
    deleted_rows = cursor.rowcount
    conn.close()
    print("✓ Deleted.\n" if deleted_rows else "No expense with that ID.\n")

def summary():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("SELECT category, SUM(amount) FROM expenses GROUP BY category ORDER BY 2 DESC")
    summary_data = cursor.fetchall()
    cursor.execute("SELECT SUM(amount) FROM expenses")
    total_amount = cursor.fetchone()[0] or 0
    conn.close()

    if not summary_data:
        print("No expenses to summarize.")
        return

    print(f"\n{'Category':<15} {'Total Amount'}")
    print("-" * 30)
    for category, total in summary_data:
        print(f"{category:<15} {total:.2f}")
    print(f"{'TOTAL':<15} ${total_amount:.2f}\n")
    print()

def main():
    init_db()
    while True:
        print("Expense Tracker")
        print("1. Add Expense")
        print("2. View Expenses")
        print("3. Delete Expense")
        print("4. Summary")
        print("5. Exit")
        choice = input("Choose an option: ").strip()

        if choice == '1':
            add_expense()
        elif choice == '2':
            view_expenses()
        elif choice == '3':
            delete_expense()
        elif choice == '4':
            summary()
        elif choice == '5':
            print("Exiting...")
            break
        else:
            print("Invalid option. Please try again.\n")
if __name__ == "__main__":
    main()