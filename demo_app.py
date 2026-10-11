import sqlite3

def get_user_data(user_id):
    # Intentional Bug: SQL Injection vulnerability
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    query = f"SELECT * FROM users WHERE id = '{user_id}'"
    cursor.execute(query)
    return cursor.fetchall()

def process_numbers(numbers):
    # Intentional Bug: Division by zero risk & missing error handling
    total = 0
    for num in numbers:
        total += 100 / num
    return total
def hardcoded_credentials_test():
    # Intentional Bug: Hardcoded API Key
    api_key = "12345-ABCDE-SECRET-KEY"
    print(f"Connecting with key: {api_key}")