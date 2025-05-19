import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "datk572004",
    database="cinema_management"
)

mycursor = mydb.cursor()

#Seat booking call store procedure

cust_name = input("Enter Customer name: ")
cust_phone = input("Enter Phone number: ")
screening_id = input("Enter Screening ID: ")
seat_number = input("Enter Seat Number: ")

def call_seat_availability(screening_id, seat_number):
    try:
        mycursor.callproc('seat_availability', (screening_id, seat_number, ''))
        mydb.commit()
        print("Seat is available!")
    except mysql.connector.errors as err:
        print(f"Seat check failed: {err.msg}")

def call_ticket_booking(cust_name, cust_phone, screening_id, seat_number):
    try:
        result = mycursor.callproc('ticket_booking', (cust_name, cust_phone, screening_id, seat_number, ''))
        booking_status = result[4]

        print("Booking result:", booking_status)

    except mysql.connector.Error as err:
        print(f"Error during booking: {err.msg}")

# Find customer's ticket through phone number

def find_tickets_by_phone(phone_number):
    query = """
    SELECT t.TicketID, c.CustomerName, t.ScreeningID, t.SeatNumber
    FROM Tickets t
    JOIN Customers c ON t.CustomerID = c.CustomerID
    WHERE c.PhoneNumber = %s
    """
    mycursor.execute(query, (phone_number,))
    results = mycursor.fetchall()

    if not results:
        print("No tickets found for this phone number.")
        return []

    print("Tickets found:")
    for row in results:
        print(f"TicketID: {row[0]}, Customer: {row[1]}, ScreeningID: {row[2]}, Seat: {row[3]}")
    return results

#Cancellation

def cancel_ticket(ticket_id):
    while True:
        confirmation = input(f"Are you want to cancel TicketID {ticket_id}? (y/n): ").strip().lower()

        if confirmation in ['y', 'n']:
            break
        else:
            print("Invalid input. Please enter 'y' or 'n' only.")

    if confirmation == 'y':
        print("Cancellation successfully.")
        return

    try:
        mycursor.execute("DELETE FROM Tickets WHERE TicketID = %s", (ticket_id,))
        mydb.commit()
        print("Ticket has been cancelled.")
    except mysql.connector.Error as err:
        print(f"Failed to cancel ticket: {err.msg}")

#Cancellation program

def cancellation_program():
    phone_number = input("Enter customer's phone number: ")
    tickets = find_tickets_by_phone(phone_number)

    if tickets:
        ticket_id = input("Enter TicketID to cancel: ")
        cancel_ticket(ticket_id)

cancellation_program()

mycursor.close()
mydb.close()