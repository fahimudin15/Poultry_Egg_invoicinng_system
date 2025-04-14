import sqlite3
from datetime import datetime

class EggManagementSystem:
    def __init__(self, db_name):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.create_table()

    def create_table(self):
        self.cursor.execute('''
            CREATE TABLE IF NOT EXISTS orders
            (id INTEGER PRIMARY KEY, customer_name TEXT, num_crates INTEGER, price REAL, due_time TEXT)
        ''')
        self.conn.commit()

    def add_order(self, customer_name, num_crates, price, due_time):
        self.cursor.execute('''
            INSERT INTO orders (customer_name, num_crates, price, due_time)
            VALUES (?, ?, ?, ?)
        ''', (customer_name, num_crates, price, due_time))
        self.conn.commit()

    def view_orders(self):
        self.cursor.execute('SELECT * FROM orders')
        return self.cursor.fetchall()

    def delete_order(self, order_id):
        self.cursor.execute('DELETE FROM orders WHERE id = ?', (order_id,))
        self.conn.commit()

    def edit_order(self, order_id, customer_name, num_crates, price, due_time):
        self.cursor.execute('''
            UPDATE orders
            SET customer_name = ?, num_crates = ?, price = ?, due_time = ?
            WHERE id = ?
        ''', (customer_name, num_crates, price, due_time, order_id))
        self.conn.commit()

    def close_connection(self):
        self.conn.close()

# Example usage
if __name__ == '__main__':
    db_name = 'egg_management.db'
    system = EggManagementSystem(db_name)

    while True:
        print("1. Add order")
        print("2. View orders")
        print("3. Delete order")
        print("4. Edit order")
        print("5. Exit")
        choice = input("Enter your choice: ")
        
        if choice == '1':
            customer_name = input("Enter customer name: ")
            num_crates = int(input("Enter number of crates: "))
            price = float(input("Enter price: "))
            due_time = input("Enter due time (YYYY-MM-DD HH:MM): ")
            system.add_order(customer_name, num_crates, price, due_time)
            print("Order added successfully!")
        elif choice == '2':
            orders = system.view_orders()
            for order in orders:
                print(f"ID: {order[0]}, Customer: {order[1]}, Crates: {order[2]}, Price: {order[3]}, Due Time: {order[4]}")
        elif choice == '3':
            order_id = int(input("Enter the ID of the order to delete: "))
            system.delete_order(order_id)
            print("Order deleted successfully!")
        elif choice == '4':
            order_id = int(input("Enter the ID of the order to edit: "))
            customer_name = input("Enter new customer name: ")
            num_crates = int(input("Enter new number of crates: "))
            price = float(input("Enter new price: "))
            due_time = input("Enter new due time (YYYY-MM-DD HH:MM): ")
            system.edit_order(order_id, customer_name, num_crates, price, due_time)
            print("Order updated successfully!")
        elif choice == '5':
            system.close_connection()
            break
        else:
            print("Invalid choice. Please try again.")
            