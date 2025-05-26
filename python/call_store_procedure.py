import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    port = 3307,
    user = "root",
    password = "datk572004",
    database="cinema_management"
)

mycursor = mydb.cursor()


# Call store procedure seat availability

def call_seat_availability(screening_id, seat_code):
    try:
         mycursor.callproc('seat_availability', (screening_id, seat_code))
         for result in mycursor.stored_results():
            rows = result.fetchall()
        
            if not rows:
                print("No available seats found.")
                return []

            print("Available seats:")
            for row in rows:
                print(f"- SeatID: {row[0]}")
            return [row[0] for row in rows]  
    except mysql.connector.Error as err:
        print(f"Error checking seat availability: {err.msg}")
        return []

# Call store procedure ticket booking
def call_ticket_booking(cust_name, cust_phone, screening_id, seat_code):
    try:
        result = mycursor.callproc('ticket_booking', (cust_name, cust_phone, screening_id, seat_code, ''))
        booking_status = result[4]

        print("Booking result:", booking_status)

    except mysql.connector.Error as err:
        print(f"Error booking ticket: {err.msg}")

#Booking seat program
def booking_seat_process():
    print("Welcome to the Cinema Booking System")
    cust_name = input("Enter customer name: ")
    cust_phone = input("Enter phone number: ")
    screening_id = int(input("Enter screening ID: "))
    seat_code = input("Enter seat code: ")

    available_seats = call_seat_availability(screening_id, seat_code)

    if not available_seats:
        print("Cannot proceed with booking because there are no available seats.")
        return

    call_ticket_booking(cust_name, cust_phone, screening_id, seat_code)

booking_seat_process()

# Find customer's ticket through phone number

def find_tickets_by_phone(phone_number):
    query = """
    SELECT t.TicketID, c.CustomerName, t.ScreeningID, s.ScreeningDate, s.ScreeningTime, se.SeatNumber
    FROM Tickets t
    JOIN Customers c ON t.CustomerID = c.CustomerID
    JOIN Screenings s ON t.ScreeningID = s.ScreeningID
    JOIN Seats se ON t.SeatID = se.SeatID
    WHERE c.PhoneNumber = %s
    """
    mycursor.execute(query, (phone_number,))
    results = mycursor.fetchall()

    if not results:
        print("No tickets found for this phone number.")
        return []

    print("Tickets found:")
    for row in results:
        print(f"TicketID: {row[0]}, Customer: {row[1]}, ScreeningID: {row[2]}, Date: {row[3]}, Time: {row[4]}, Seat: {row[5]}")
    return results

#Cancellation confirmation

def cancel_ticket(ticket_id):
    while True:
        confirmation = input(f"Do you want to cancel TicketID {ticket_id}? (y/n): ").strip().lower()

        if confirmation in ['y', 'n']:
            break
        else:
            print("Invalid input. Please enter 'y' or 'n' only.")

    if confirmation == 'y':
        try:
            mycursor.execute("DELETE FROM Tickets WHERE TicketID = %s", (ticket_id,))
            mydb.commit()
            print("Ticket has been cancelled.")
        except mysql.connector.Error as err:
            print(f"Failed to cancel ticket: {err.msg}")
    else:
        print("Cancellation aborted.")

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