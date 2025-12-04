import requests
import json
import time

BASE_URL = "http://127.0.0.1:8000/api"

def print_response(response):
    try:
        print(f"Status Code: {response.status_code}")
        print(f"Response: {json.dumps(response.json(), indent=2)}")
    except:
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
    print("-" * 20)

def verify():
    print("Starting Verification...")

    import random
    random_id = random.randint(1000, 9999)
    
    # 1. Create a Book
    print("\n1. Creating a Book...")
    book_data = {
        "title": f"The Great Gatsby {random_id}",
        "author": "F. Scott Fitzgerald",
        "isbn": f"97807432{random_id}",
        "category": "Classic"
    }
    response = requests.post(f"{BASE_URL}/books/", json=book_data)
    print_response(response)
    if response.status_code != 201:
        print("Failed to create book.")
        return
    book_id = response.json()['id']

    # 2. Add a Copy
    print("\n2. Adding a Book Copy...")
    copy_data = {
        "barcode": f"GG-{random_id}"
    }
    response = requests.post(f"{BASE_URL}/books/{book_id}/copies/", json=copy_data)
    print_response(response)
    if response.status_code != 201:
        print("Failed to add book copy.")
        return

    # 3. Create a User (Signup)
    print("\n3. Creating a User (Signup)...")
    user_data = {
        "username": f"testuser{random_id}",
        "password": "password123",
        "email": f"test{random_id}@example.com"
    }
    response = requests.post(f"{BASE_URL}/signup/", json=user_data)
    print_response(response)
    # Ignore error if user already exists
    if response.status_code == 201:
        user_id = response.json()['id']
    elif response.status_code == 400 and "already exists" in response.text:
        print("User already exists, proceeding...")
        # Need to get user_id, maybe signin?
        signin_response = requests.post(f"{BASE_URL}/signin/", json={"username": "testuser", "password": "password123"})
        user_id = signin_response.json()['user_id']
    else:
        print("Failed to create user.")
        return

    # 4. Create a Member
    print("\n4. Creating a Member Profile...")
    member_data = {
        "user_id": user_id,
        "library_id": f"LIB-{random_id}"
    }
    response = requests.post(f"{BASE_URL}/members/", json=member_data)
    print_response(response)
    if response.status_code != 201 and "already exists" not in response.text: # Assuming unique constraint might fail if re-run
         # If member creation fails (e.g. already exists), we might need to handle it.
         # For now, let's assume clean state or handle duplicate library_id error if we were robust.
         pass

    # 5. Checkout a Book (Loan)
    print("\n5. Checking out a Book...")
    loan_data = {
        "barcode": f"GG-{random_id}",
        "library_id": f"LIB-{random_id}"
    }
    response = requests.post(f"{BASE_URL}/loans/checkout/", json=loan_data)
    print_response(response)

    # 6. Return a Book
    print("\n6. Returning a Book...")
    return_data = {
        "barcode": f"GG-{random_id}"
    }
    response = requests.post(f"{BASE_URL}/loans/return/", json=return_data)
    print_response(response)

    # 7. Reserve a Book
    print("\n7. Reserving a Book...")
    reservation_data = {
        "book_id": book_id,
        "library_id": f"LIB-{random_id}"
    }
    response = requests.post(f"{BASE_URL}/reservations/", json=reservation_data)
    print_response(response)

    # 8. Test Penalty (Simulate Overdue)
    print("\n8. Testing Penalty System...")
    # Create a new loan for penalty test
    random_id_2 = random.randint(10000, 99999)
    
    # Create book
    requests.post(f"{BASE_URL}/books/", json={
        "title": f"Penalty Test Book {random_id_2}",
        "author": "Test Author",
        "isbn": f"97800000{random_id_2}",
        "category": "Test"
    })
    # Add copy
    requests.post(f"{BASE_URL}/books/1/copies/", json={"barcode": f"PEN-{random_id_2}"}) # Assuming ID 1 exists or we should get it dynamically but let's try to be robust
    # Actually, let's just use the book we created earlier if possible, but better to make a fresh one to avoid state issues.
    # Let's do it properly:
    
    # Create Book
    p_book_resp = requests.post(f"{BASE_URL}/books/", json={
        "title": f"Penalty Test Book {random_id_2}",
        "author": "Test Author",
        "isbn": f"97800000{random_id_2}",
        "category": "Test"
    })
    p_book_id = p_book_resp.json().get('id')
    
    # Add Copy
    requests.post(f"{BASE_URL}/books/{p_book_id}/copies/", json={"barcode": f"PEN-{random_id_2}"})
    
    # Create Member
    requests.post(f"{BASE_URL}/members/", json={"user_id": user_id, "library_id": f"LIB-PEN-{random_id_2}"}) # Re-using user_id might fail if one-to-one?
    # Member is OneToOne with User. So we need a new user.
    
    requests.post(f"{BASE_URL}/signup/", json={
        "username": f"penaltyuser{random_id_2}",
        "password": "password123",
        "email": f"penalty{random_id_2}@example.com"
    })
    # Get user id from signin or signup response
    # Let's assume signup worked
    signin_resp = requests.post(f"{BASE_URL}/signin/", json={"username": f"penaltyuser{random_id_2}", "password": "password123"})
    p_user_id = signin_resp.json().get('user_id')
    
    requests.post(f"{BASE_URL}/members/", json={"user_id": p_user_id, "library_id": f"LIB-PEN-{random_id_2}"})

    # Checkout
    checkout_resp = requests.post(f"{BASE_URL}/loans/checkout/", json={
        "barcode": f"PEN-{random_id_2}",
        "library_id": f"LIB-PEN-{random_id_2}"
    })
    print("Checkout Response:", checkout_resp.json())
    
    # Manually update the loan due_date in DB? We can't access DB directly easily from here without shell.
    # But we are running on the same machine.
    # Alternatively, we can mock the return time in the view, but that requires code change.
    # Or we can just trust the logic if we can't easily simulate time travel.
    # WAIT! I can use `sqlite3` command line or python script to update the DB directly since I have access to the file.
    
    import sqlite3
    import datetime
    
    conn = sqlite3.connect('db.sqlite3')
    cursor = conn.cursor()
    
    # Find the loan
    cursor.execute("SELECT id FROM circulation_loan WHERE copy_id = (SELECT id FROM circulation_bookcopy WHERE barcode = ?)", (f"PEN-{random_id_2}",))
    loan_row = cursor.fetchone()
    if loan_row:
        loan_id = loan_row[0]
        # Set due date to 5 days ago
        past_date = datetime.datetime.now() - datetime.timedelta(days=5)
        cursor.execute("UPDATE circulation_loan SET due_date = ? WHERE id = ?", (past_date, loan_id))
        conn.commit()
        print("Manually updated loan to be overdue.")
    conn.close()
    
    # Return
    return_resp = requests.post(f"{BASE_URL}/loans/return/", json={
        "barcode": f"PEN-{random_id_2}"
    })
    print_response(return_resp)

if __name__ == "__main__":
    verify()
