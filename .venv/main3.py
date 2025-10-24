import mysql.connector
import random
import string
from datetime import datetime, timedelta
from datetime import datetime
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

'''def create_reservation():
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
'''
'''
def get_vip_id_by_code():
    vip_code = input("Enter VIP Code (leave blank if not VIP): ").strip()
    if not vip_code:
        return None
    cursor.execute("SELECT vip_id FROM vip_customers WHERE vip_code=%s", (vip_code,))
    result = cursor.fetchone()
    if result:
        return result[0]  # VIP id
    else:
        print("⚠️ Invalid VIP code. Proceeding as normal customer.")
        return None

'''

'''
def get_valid_time():
    while True:
        time_in = input("Enter Time (24hr format, e.g. 19:30): ")
        try:
            # This will raise ValueError if invalid
            valid_time = datetime.strptime(time_in, "%H:%M")
            # Optional: enforce business hours
            if not (10 <= valid_time.hour <= 22):
                print("⚠️ Reservations allowed only between 10:00 and 22:00.")
                continue
            return time_in
        except ValueError:
            print("⚠️ Invalid time format. Please enter in HH:MM format (24hr).")
'''

from datetime import datetime, timedelta

MAX_GUESTS = 20  # maximum allowed guests per reservation
BUSINESS_HOURS_START = 10  # 10:00
BUSINESS_HOURS_END = 22    # 22:00
BUFFER_MINUTES = 30        # minimum buffer between reservations


# Utility: parse and validate time
def get_valid_time():
    while True:
        time_in = input("Enter Time (24hr format, e.g. 19:30): ")
        try:
            valid_time = datetime.strptime(time_in, "%H:%M")
            if not (BUSINESS_HOURS_START <= valid_time.hour < BUSINESS_HOURS_END):
                print(f"⚠️ Reservations allowed only between {BUSINESS_HOURS_START}:00 and {BUSINESS_HOURS_END}:00")
                continue
            return time_in
        except ValueError:
            print("⚠️ Invalid time format. Please enter in HH:MM format (24hr).")


# Utility: add minutes to time string
def add_minutes(time_str, minutes):
    time_obj = datetime.strptime(time_str, "%H:%M")
    new_time = time_obj + timedelta(minutes=minutes)
    return new_time.strftime("%H:%M")


# VIP verification
def get_vip_id_by_code():
    vip_code = input("Enter VIP Code (leave blank if not VIP): ").strip()
    if not vip_code:
        return None
    cursor.execute("SELECT vip_id FROM vip_customers WHERE vip_code=%s", (vip_code,))
    result = cursor.fetchone()
    if result:
        return result[0]
    else:
        print("⚠️ Invalid VIP code. Proceeding as normal customer.")
        return None


# Main reservation function
def create_reservation():
    print("\n--- Create Reservation ---")
    first_name = input("Enter First Name: ").strip()
    last_name = input("Enter Last Name: ").strip()
    email = input("Enter Email: ").strip()
    phone = input("Enter Phone Number: ").strip()
    date = input("Enter Date (YYYY-MM-DD): ").strip()

    try:
        datetime.strptime(date, "%Y-%m-%d")
    except ValueError:
        print("⚠️ Invalid date format. Please enter YYYY-MM-DD.")
        return

    try:
        guests = int(input("Enter Number of Guests: "))
        if guests > MAX_GUESTS or guests <= 0:
            print(f"⚠️ Number of guests must be between 1 and {MAX_GUESTS}")
            return
    except ValueError:
        print("⚠️ Invalid number of guests.")
        return

    extra = input("Any Extra Details: ").strip()
    vip_id = get_vip_id_by_code()
    is_vip = vip_id is not None

    while True:
        time_in = get_valid_time()

        # Check if same date/time is booked
        cursor.execute("""
            SELECT reservation_id, vip_id FROM reservations
            WHERE date=%s AND time_in=%s AND status='Confirmed'
        """, (date, time_in))
        conflict = cursor.fetchone()

        if conflict:
            existing_id, existing_vip_id = conflict
            if is_vip and not existing_vip_id:
                # VIP overrides normal reservation
                cursor.execute("UPDATE reservations SET status='Cancelled' WHERE reservation_id=%s", (existing_id,))
                conn.commit()
                print(f"⚠️ Normal reservation {existing_id} cancelled to make room for VIP")
            else:
                # Suggest next available time
                suggested_time = add_minutes(time_in, BUFFER_MINUTES)
                cursor.execute("""
                    SELECT * FROM reservations
                    WHERE date=%s AND time_in=%s AND status='Confirmed'
                """, (date, suggested_time))
                next_conflict = cursor.fetchone()
                if next_conflict:
                    suggested_time = add_minutes(time_in, BUFFER_MINUTES * 2)

                print(f"\n⚠️ {time_in} on {date} is already booked.")
                print(f"👉 Next available time suggestion: {suggested_time}")
                try_again = input("Would you like to try the suggested time? (yes/no): ").lower()
                if try_again == "yes":
                    time_in = suggested_time
                else:
                    print("\nReservation not confirmed. You can try again later.\n")
                    return

        # Confirm reservation
        reservation_id = generate_reservation_id()
        cursor.execute("""
            INSERT INTO reservations 
            (reservation_id, first_name, last_name, email, phone, date, time_in, guests, extra, status, vip_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'Confirmed',%s)
        """, (reservation_id, first_name, last_name, email, phone, date, time_in, guests, extra, vip_id))
        conn.commit()
        print(f"\n✅ Reservation Confirmed Successfully!")
        print(f"Reservation ID: {reservation_id}")
        print(f"Date: {date} | Time: {time_in}\n")
        return





'''
def create_reservation():
    print("\n--- Create Reservation ---")
    first_name = input("Enter First Name: ")
    last_name = input("Enter Last Name: ")
    email = input("Enter Email: ")
    phone = input("Enter Phone Number: ")
    date = input("Enter Date (YYYY-MM-DD): ")
    guests = int(input("Enter Number of Guests: "))
    extra = input("Any Extra Details: ")

    vip_id = get_vip_id_by_code()  # Check if user is VIP
    is_vip = vip_id is not None

    while True:
        time_in = input("Enter Time (24hr format, e.g. 19:30): ")
        time_in = get_valid_time()

        # Check conflicts
        cursor.execute("""
            SELECT reservation_id, vip_id FROM reservations
            WHERE time_in = %s AND date = %s AND status = 'Confirmed'
        """, (time_in, date))
        conflict = cursor.fetchone()

        if conflict:
            existing_id, existing_vip_id = conflict
            if is_vip and not existing_vip_id:
                # VIP overrides normal reservation
                cursor.execute("UPDATE reservations SET status='Cancelled' WHERE reservation_id=%s", (existing_id,))
                conn.commit()
                print(f"⚠️ Normal reservation {existing_id} cancelled to make room for VIP")
            else:
                # Suggest next available time
                suggested_time = add_minutes(time_in, 30)
                cursor.execute("""
                    SELECT * FROM reservations
                    WHERE time_in = %s AND date = %s AND status = 'Confirmed'
                """, (suggested_time, date))
                next_conflict = cursor.fetchone()
                if next_conflict:
                    suggested_time = add_minutes(time_in, 60)

                print(f"\n⚠️ {time_in} on {date} is already booked.")
                print(f"👉 Next available time suggestion: {suggested_time}")
                try_again = input("Would you like to try the suggested time? (yes/no): ").lower()
                if try_again == "yes":
                    time_in = suggested_time
                else:
                    print("\nReservation not confirmed. You can try again later.\n")
                    return

        # Confirm reservation
        reservation_id = generate_reservation_id()
        cursor.execute("""
            INSERT INTO reservations (reservation_id, first_name, last_name, email, phone, date, time_in,
                                      guests, extra, status, vip_id)
            VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,'Confirmed',%s)
        """, (reservation_id, first_name, last_name, email, phone, date, time_in, guests, extra, vip_id))
        conn.commit()
        print(f"\n✅ Reservation Confirmed Successfully!")
        print(f"Reservation ID: {reservation_id}")
        print(f"Date: {date} | Time: {time_in}\n")
        return
'''



def update_reservation():
    rid = input("Enter Reservation ID to update: ").upper()

    # Fetch existing reservation
    cursor.execute("SELECT vip_id FROM reservations WHERE reservation_id=%s", (rid,))
    res = cursor.fetchone()
    if not res:
        print("⚠️ Reservation ID not found.\n")
        return
    vip_id = res[0]
    is_vip = vip_id is not None

    # New date input with validation
    new_date = input("Enter New Date (YYYY-MM-DD): ").strip()
    try:
        datetime.strptime(new_date, "%Y-%m-%d")
    except ValueError:
        print("⚠️ Invalid date format. Please enter YYYY-MM-DD.")
        return

    # New time input with validation
    new_time = get_valid_time()

    # New guests input with validation
    try:
        new_guests = int(input("Enter New Number of Guests: "))
        if new_guests > MAX_GUESTS or new_guests <= 0:
            print(f"⚠️ Number of guests must be between 1 and {MAX_GUESTS}")
            return
    except ValueError:
        print("⚠️ Invalid number of guests.")
        return

    # Check for conflicts
    cursor.execute("""
        SELECT reservation_id, vip_id FROM reservations
        WHERE date=%s AND time_in=%s AND status='Confirmed' AND reservation_id != %s
    """, (new_date, new_time, rid))
    conflict = cursor.fetchone()

    if conflict:
        existing_id, existing_vip_id = conflict
        if is_vip and not existing_vip_id:
            # VIP overrides normal reservation
            cursor.execute("UPDATE reservations SET status='Cancelled' WHERE reservation_id=%s", (existing_id,))
            conn.commit()
            print(f"⚠️ Normal reservation {existing_id} cancelled to make room for VIP")
        else:
            print("⚠️ The new date/time slot is already booked. Update not confirmed.\n")
            return

    # Update reservation
    cursor.execute("""
        UPDATE reservations 
        SET date=%s, time_in=%s, guests=%s 
        WHERE reservation_id=%s
    """, (new_date, new_time, new_guests, rid))
    conn.commit()
    print("✅ Reservation Updated Successfully!\n")









'''
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

'''



# -----------------------
# Cancel reservation
# -----------------------




'''
def cancel_reservation():
    rid = input("Enter Reservation ID to cancel: ").upper()
    cursor.execute("UPDATE reservations SET status='Cancelled' WHERE reservation_id=%s", (rid,))
    conn.commit()
    print("❌ Reservation Cancelled Successfully!\n")

'''



def cancel_reservation():
    rid = input("Enter Reservation ID to cancel: ").upper()

    # Check if reservation exists
    cursor.execute("SELECT reservation_id, vip_id, status FROM reservations WHERE reservation_id=%s", (rid,))
    res = cursor.fetchone()
    if not res:
        print("⚠️ Reservation ID not found.\n")
        return

    if res[2] == 'Cancelled':
        print("⚠️ Reservation is already cancelled.\n")
        return

    cursor.execute("UPDATE reservations SET status='Cancelled' WHERE reservation_id=%s", (rid,))
    conn.commit()
    print("❌ Reservation Cancelled Successfully!\n")






# -----------------------
# Check reservation
# -----------------------
'''
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
'''


def check_reservation():
    rid = input("Enter Reservation ID to check: ").upper()
    cursor.execute("""
        SELECT r.reservation_id, r.first_name, r.last_name, r.date, r.time_in, r.status, v.vip_name
        FROM reservations r
        LEFT JOIN vip_customers v ON r.vip_id = v.vip_id
        WHERE r.reservation_id=%s
    """, (rid,))
    result = cursor.fetchone()

    if result:
        print(f"\nReservation ID : {result[0]}")
        print(f"Name           : {result[1]} {result[2]}")
        print(f"Date           : {result[3]}")
        print(f"Time           : {result[4]}")
        print(f"Status         : {result[5]}")
        if result[6]:
            print(f"VIP            : {result[6]}")
        else:
            print(f"VIP            : No")
        print()
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
