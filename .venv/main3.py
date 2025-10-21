import mysql.connector
import random
import string
from datetime import datetime, timedelta

# -----------------------
# Utility functions
# -----------------------

# Generate 8-character uppercase alphanumeric reservation ID
def generate_reservation_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

# Convert "HH:MM" string to datetime object
def parse_time(t):
    return datetime.strptime(t, "%H:%M")

# Add minutes to a given "HH:MM" time string
def add_minutes(time_str, minutes):
    time_obj = parse_time(time_str)
    new_time = time_obj + timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")

# -----------------------
# Database connection
# -----------------------

conn = mysql.connector.connect(
    host="localhost",
    user="root",              # change if needed
    password="qwer123", # your MySQL password
    database="reservation_system"
)
cursor = conn.cursor()

# -----------------------
# Reservation creation
# -----------------------

def create_reservation():
    print("\n--- Create Reservation ---")
    first_name = input("Enter First Name: ")
    last_name = input("Enter Last Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone Number: ")
    date = input("Enter Date (YYYY-MM-DD): ")
    guests = int(input("Enter Number of Guests: "))
    extra = input("Any Extra Details: ")

    while True:
        time_in = input("Enter Time (24hr format, e.g. 19:30): ")

        # Check if the same time and date already have a confirmed reservation
        cursor.execute("""
            SELECT * FROM reservations
            WHERE time_in = %s AND date = %s AND status = 'Confirmed'
        """, (time_in, date))
        conflict = cursor.fetchone()

        if conflict:
            # Suggest next available time slot (+30 minutes)
            suggested_time = add_minutes(time_in, 30)

            # Check if suggested time is free
            cursor.execute("""
                SELECT * FROM reservations
                WHERE time_in = %s AND date = %s AND status = 'Confirmed'
            """, (suggested_time, date))
            next_conflict = cursor.fetchone()

            if next_conflict:
                suggested_time = add_minutes(time_in, 60)  # try +1 hour

            # Insert not confirmed reservation (optional record keeping)
            cursor.execute("""
                INSERT INTO reservations (first_name, last_name, email, phone, date, time_in, guests, extra, status)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, 'Not Confirmed')
            """, (first_name, last_name, email, phone, date, time_in, guests, extra))
            conn.commit()

            print(f"\n⚠️ Sorry, {time_in} on {date} is already booked.")
            print(f"👉 Next available time suggestion: {suggested_time}")
            try_again = input("Would you like to try the suggested time? (yes/no): ").lower()
            if try_again == "yes":
                time_in = suggested_time
                # confirm new booking
                reservation_id = generate_reservation_id()
                cursor.execute("""
                               INSERT INTO reservations (reservation_id, first_name, last_name, email, phone, date,
                                                         time_in,
                                                         guests, extra, status)
                               VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                               """, (reservation_id, first_name, last_name, email, phone, date, time_in, guests, extra,
                                     "Confirmed"))
                conn.commit()
                print(f"\n✅ Reservation Confirmed Successfully!")
                print(f"Reservation ID: {reservation_id}")
                print(f"Date: {date} | Time: {time_in}\n")
                return
            else:
                print("\nReservation not confirmed. You can try again later.\n")
                return

        else:
            # Confirm reservation directly
            reservation_id = generate_reservation_id()
            cursor.execute("""
                           INSERT INTO reservations (reservation_id, first_name, last_name, email, phone, date, time_in,
                                                     guests, extra, status)
                           VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                           """, (reservation_id, first_name, last_name, email, phone, date, time_in, guests, extra,
                                 "Confirmed"))
            conn.commit()
            print(f"\n✅ Reservation Confirmed Successfully!")
            print(f"Reservation ID: {reservation_id}")
            print(f"Date: {date} | Time: {time_in}\n")
            return

# -----------------------
# Update reservation
# -----------------------

def update_reservation():
    rid = input("Enter Reservation ID to update: ").upper()
    new_date = input("Enter New Date (YYYY-MM-DD): ")
    new_time = input("Enter New Time (24hr format): ")
    new_guests = input("Enter New Number of Guests: ")

    cursor.execute("""
        SELECT * FROM reservations
        WHERE time_in = %s AND date = %s AND status = 'Confirmed' AND reservation_id != %s
    """, (new_time, new_date, rid))
    conflict = cursor.fetchone()

    if conflict:
        print("⚠️ The new date/time slot is already booked. Update not confirmed.\n")
    else:
        cursor.execute("""
            UPDATE reservations SET date=%s, time_in=%s, guests=%s WHERE reservation_id=%s
        """, (new_date, new_time, new_guests, rid))
        conn.commit()
        print("✅ Reservation Updated Successfully!\n")

# -----------------------
# Cancel reservation
# -----------------------

def cancel_reservation():
    rid = input("Enter Reservation ID to cancel: ").upper()
    cursor.execute("UPDATE reservations SET status='Cancelled' WHERE reservation_id=%s", (rid,))
    conn.commit()
    print("❌ Reservation Cancelled Successfully!\n")

# -----------------------
# Check reservation
# -----------------------

def check_reservation():
    rid = input("Enter Reservation ID to check: ").upper()
    cursor.execute("""
        SELECT reservation_id, first_name, last_name, date, time_in, status
        FROM reservations WHERE reservation_id=%s
    """, (rid,))
    result = cursor.fetchone()

    if result:
        print(f"\nReservation ID : {result[0]}")
        print(f"Name           : {result[1]} {result[2]}")
        print(f"Date           : {result[3]}")
        print(f"Time           : {result[4]}")
        print(f"Status         : {result[5]}\n")
    else:
        print("⚠️ No reservation found with that ID.\n")

# -----------------------
# Main menu
# -----------------------

def main():
    while True:
        print("\n--- Reservation System Menu ---")
        print("1. Create Reservation")
        print("2. Update Reservation")
        print("3. Cancel Reservation")
        print("4. Check Reservation Status")
        print("5. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            create_reservation()
        elif choice == "2":
            update_reservation()
        elif choice == "3":
            cancel_reservation()
        elif choice == "4":
            check_reservation()
        elif choice == "5":
            print("👋 Goodbye!")
            break
        else:
            print("Invalid choice. Try again.")

if __name__ == "__main__":
    main()
