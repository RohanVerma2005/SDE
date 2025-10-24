import mysql.connector

# ---------- Database Connection ----------
def connect_db():
    try:
        db = mysql.connector.connect(
            host="localhost",
            user="root",              # change this to your username
            password="qwer123", # change this to your MySQL password
            database="food"
        )
        return db
    except mysql.connector.Error as err:
        print(f"❌ Database connection failed: {err}")
        exit()

# ---------- View All Items ----------
def view_all_items(cursor):
    cursor.execute("SELECT * FROM food_items;")
    rows = cursor.fetchall()
    print("\n--- 🍴 Food Menu ---")
    if not rows:
        print("No food items found.")
    else:
        for row in rows:
            print(f"ID: {row[0]}, Name: {row[1]}, Price: ₹{row[2]}, Description: {row[3]}")
    print("----------------------")

# ---------- Add New Item ----------
def add_item(cursor, db):
    name = input("Enter food name: ")
    price = float(input("Enter price (₹): "))
    description = input("Enter short description: ")
    cursor.execute("INSERT INTO food_items (name, price, description) VALUES (%s, %s, %s)", (name, price, description))
    db.commit()
    print(f"✅ '{name}' added successfully!")

# ---------- Update Item ----------
def update_item(cursor, db):
    id = input("Enter the ID of the item to update: ")
    print("What do you want to update?")
    print("1. Name\n2. Price\n3. Description")
    choice = input("Enter choice (1-3): ")

    if choice == "1":
        new_value = input("Enter new name: ")
        cursor.execute("UPDATE food_items SET name=%s WHERE id=%s", (new_value, id))
    elif choice == "2":
        new_value = float(input("Enter new price: "))
        cursor.execute("UPDATE food_items SET price=%s WHERE id=%s", (new_value, id))
    elif choice == "3":
        new_value = input("Enter new description: ")
        cursor.execute("UPDATE food_items SET description=%s WHERE id=%s", (new_value, id))
    else:
        print("❌ Invalid choice.")
        return

    db.commit()
    print("✅ Item updated successfully!")

# ---------- Delete Item ----------
def delete_item(cursor, db):
    id = input("Enter the ID of the item to delete: ")
    cursor.execute("DELETE FROM food_items WHERE id=%s", (id,))
    db.commit()
    print("🗑️ Item deleted successfully!")

# ---------- Search Item ----------
def search_item(cursor):
    print("1. Search by Name")
    print("2. Search by Price Range")
    choice = input("Enter choice (1/2): ")

    if choice == "1":
        keyword = input("Enter name keyword: ")
        cursor.execute("SELECT * FROM food_items WHERE name LIKE %s", (f"%{keyword}%",))
    elif choice == "2":
        min_price = float(input("Enter minimum price: "))
        max_price = float(input("Enter maximum price: "))
        cursor.execute("SELECT * FROM food_items WHERE price BETWEEN %s AND %s", (min_price, max_price))
    else:
        print("❌ Invalid choice.")
        return

    results = cursor.fetchall()
    if not results:
        print("No matching items found.")
    else:
        print("\n--- 🔍 Search Results ---")
        for row in results:
            print(f"ID: {row[0]}, Name: {row[1]}, Price: ₹{row[2]}, Description: {row[3]}")

# ---------- Customize Food ----------
def customize_food(cursor, db):
    print("\n--- 🍳 Customize Your Food ---")
    view_all_items(cursor)
    food_id = input("Enter the ID of the food you want to customize: ")

    cursor.execute("SELECT name, price FROM food_items WHERE id=%s", (food_id,))
    result = cursor.fetchone()
    if not result:
        print("❌ Invalid food ID.")
        return
    base_name, base_price = result
    total_price = base_price

    print(f"\nYou selected: {base_name} (Base Price: ₹{base_price})")

    # Available Add-ons
    addons = {
        1: ("Extra Cheese", 30),
        2: ("French Fries", 50),
        3: ("Cold Drink", 40),
        4: ("Garlic Dip", 20),
        5: ("Extra Mayo", 25),
        6: ("Peri Peri Seasoning", 15),
        7: ("Tandoori Sauce", 35),
        8: ("Grilled Paneer", 45),
        9: ("Butter Topping", 10),
        10: ("Extra Veggies", 30),
        11: ("Double Patty", 60),
        12: ("Masala Corn", 25),
        13: ("Egg Topping", 35),
        14: ("Chilli Flakes", 10),
        15: ("Oregano Mix", 10),
        16: ("Cheese Burst Filling", 50),
        17: ("Schezwan Sauce", 20),
        18: ("Barbeque Sauce", 25),
        19: ("Creamy Garlic Sauce", 30),
        20: ("Herb Butter", 15),
        21: ("Crispy Onions", 20),
        22: ("Sweet Corn", 15),
        23: ("Cucumber Slices", 10),
        24: ("Lettuce", 15),
        25: ("Pickles", 15),
        26: ("Jalapeños", 20),
        27: ("Olives", 25),
        28: ("Smoked Chicken", 55),
        29: ("Bacon Strips", 60),
        30: ("Sausage Bits", 45),
        0: ("No Add-ons", 0)
    }

    print("\nAvailable Add-ons:")
    for k, v in addons.items():
        print(f"{k}. {v[0]} (+₹{v[1]})")
    print("0. No Add-ons")

    selected_addons = []
    while True:
        choice = int(input("Select add-on (enter 0 to finish): "))
        if choice == 0:
            break
        if choice in addons:
            selected_addons.append(addons[choice][0])
            total_price += addons[choice][1]
        else:
            print("Invalid choice.")

    # Choose spice level
    print("\nSpice Levels:")
    print("1. Mild 🌿\n2. Medium 🌶️\n3. Spicy 🔥")
    spice_choice = input("Select spice level (1-3): ")

    spice_map = {"1": "Mild", "2": "Medium", "3": "Spicy"}
    spice_level = spice_map.get(spice_choice, "Medium")

    addons_text = ", ".join(selected_addons) if selected_addons else "No Add-ons"

    print("\n✅ Your Custom Order Summary:")
    print(f"Base Food: {base_name}")
    print(f"Add-ons: {addons_text}")
    print(f"Spice Level: {spice_level}")
    print(f"Total Price: ₹{total_price}")

    # Create customization table if not exists
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS customizations (
            id INT AUTO_INCREMENT PRIMARY KEY,
            base_food VARCHAR(100),
            addons VARCHAR(255),
            spice_level VARCHAR(20),
            total_price DECIMAL(6,2)
        )
    """)

    # Insert record
    cursor.execute("""
        INSERT INTO customizations (base_food, addons, spice_level, total_price)
        VALUES (%s, %s, %s, %s)
    """, (base_name, addons_text, spice_level, total_price))
    db.commit()
    print("🍽️ Customization saved successfully!")


#---orders----
def place_order():
    db = connect_db()
    cursor = db.cursor()

    while True:
        cursor.execute("SELECT * FROM food_items;")
        items = cursor.fetchall()

        print("\n🍽️ --- Available Food Items ---")
        for item in items:
            print(f"{item[0]}. {item[1]} - ₹{item[2]}")

        try:
            customer_id = int(input("\nEnter your customer ID: "))
            food_id = int(input("Enter Food ID to order: "))
            quantity = int(input("Enter quantity: "))

            cursor.execute("SELECT price FROM food_items WHERE id = %s", (food_id,))
            price = cursor.fetchone()

            if not price:
                print("❌ Invalid Food ID. Please try again.")
                continue

            total_price = price[0] * quantity

            cursor.execute(
                "INSERT INTO orders (customer_id, food_id, total_price) VALUES (%s, %s, %s)",
                (customer_id, food_id, total_price)
            )
            db.commit()

            print(f"✅ Order placed successfully! Total: ₹{total_price:.2f}")

        except ValueError:
            print("⚠️ Invalid input! Please enter numbers only.")
            continue
        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()

        # Ask user if they want to place another order
        again = input("\nDo you want to place another order? (yes/no): ").strip().lower()
        if again not in ('yes', 'y'):
            print("👋 Thank you for ordering! Have a great day!")
            break

    cursor.close()
    db.close()



#----custom orders----
def place_custom_order():
    db = connect_db()
    cursor = db.cursor()

    while True:
        cursor.execute("SELECT * FROM customizations;")
        items = cursor.fetchall()

        print("\n🍽️ --- Available Food Items ---")
        for item in items:
            print(f"{item[0]}. {item[1]}-- {item[2]}--{item[3]} - ₹{item[4]}")

        try:
            customer_id = int(input("\nEnter your customer ID: "))
            food_id = int(input("Enter Food ID to order: "))
            quantity = int(input("Enter quantity: "))

            cursor.execute("SELECT total_price FROM customizations WHERE id = %s", (food_id,))
            price = cursor.fetchone()

            if not price:
                print("❌ Invalid Food ID. Please try again.")
                continue

            total_price = price[0] * quantity

            cursor.execute(
                "INSERT INTO custom_orders  (customer_id, food_id, total_price) VALUES (%s, %s, %s)",
                (customer_id, food_id, total_price)
            )
            db.commit()

            print(f"✅ Order placed successfully! Total: ₹{total_price:.2f}")

        except ValueError:
            print("⚠️ Invalid input! Please enter numbers only.")
            continue
        except Exception as e:
            print(f"❌ Error: {e}")
            db.rollback()

        # Ask user if they want to place another order
        again = input("\nDo you want to place another order? (yes/no): ").strip().lower()
        if again not in ('yes', 'y'):
            print("👋 Thank you for ordering! Have a great day!")
            break

    cursor.close()
    db.close()




# ---------- Main Menu ----------
def main():
    db = connect_db()
    cursor = db.cursor()

    while True:
        print("\n=== 🍽️ FOOD MENU MANAGEMENT ===")
        print("1. View All Items")
        print("2. Add New Item")
        print("3. Update Item")
        print("4. Delete Item")
        print("5. Search Item")
        print("6. Customize Food")
        print("7. Place Order")
        print("8. Place Order from Customized Menu")
        print("9. Exit")

        choice = input("Enter your choice (1-9): ")

        if choice == "1":
            view_all_items(cursor)
        elif choice == "2":
            add_item(cursor, db)
        elif choice == "3":
            update_item(cursor, db)
        elif choice == "4":
            delete_item(cursor, db)
        elif choice == "5":
            search_item(cursor)
        elif choice == "6":
            customize_food(cursor, db)
        elif choice == "7":
            place_order()
        elif choice == "8":
            place_custom_order()
        elif choice == "9":
            print("👋 Exiting... Goodbye!")
            break
        else:
            print("❌ Invalid input, please try again.")

    cursor.close()
    db.close()
    print("🔒 Database connection closed.")

# ---------- Run the program ----------
if __name__ == "__main__":
    main()

'''
def place_order():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM food_items;")
    items = cursor.fetchall()

    print("\n🍽️ --- Available Food Items ---")
    for item in items:
        print(f"{item[0]}. {item[1]} - ₹{item[2]}")

    customer_id = int(input("Enter your customer ID: "))
    food_id = int(input("Enter Food ID to order: "))
    quantity = int(input("Enter quantity: "))

    cursor.execute("SELECT price FROM food_items WHERE id = %s", (food_id,))
    price = cursor.fetchone()[0]
    total_price = price * quantity

    cursor.execute("INSERT INTO orders (customer_id, food_id, total_price) VALUES (%s, %s, %s)", 
                   (customer_id, food_id, total_price))
    db.commit()

    print(f"✅ Order placed successfully! Total: ₹{total_price}")
    cursor.close()
    db.close()
'''


'''
def place_order_customized():
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT * FROM customizations;")
    items = cursor.fetchall()

    print("\n🍽️ --- Available customize Food Items ---")
    for item in items:
        print(f"{item[0]}. {item[1]} {item[2]} - ₹{item[3]}")

    customer_id = int(input("Enter your customer ID: "))
    food_id = int(input("Enter Food ID to order: "))
    quantity = int(input("Enter quantity: "))

    cursor.execute("SELECT price FROM customizations WHERE id = %s", (food_id,))
    price = cursor.fetchone()[0]
    total_price = price * quantity

    cursor.execute("INSERT INTO orders (customer_id, food_id, total_price) VALUES (%s, %s, %s)", 
                   (customer_id, food_id, total_price))
    db.commit()

    print(f"✅ Order placed successfully! Total: ₹{total_price}")
    cursor.close()
    db.close()
'''
