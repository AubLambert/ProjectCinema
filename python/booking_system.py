import mysql.connector

mydb = mysql.connector.connect(
    host = "localhost",
    user = "root",
    password = "your_password",
    database="cinema_management"
)

mycursor = mydb.cursor()

#Booking system: Show screening --> Check seat --> Book ticket --> Cancel ticket
#Show screening
def show_screenings ():
    mycursor.execute("SELECT * FROM screenings")
    myresult = mycursor.fetchall()
    for x in myresult:
        print(x)

#Check available seat
def check_available_seat (ScreeningID):
    mycursor.execute("SELECT SeatNumber FROM tickets WHERE ScreeningID = %s", (ScreeningID,))
    booked_seats = [row[0] for row in mycursor.fetchall()]

    if not booked_seats:
        print(f"No seats have been booked for screening {ScreeningID}.")
    else:
        print(f"Booked seats for screening {ScreeningID}: {booked_seats}")

#Book ticket
def book_ticket(CustomerID, ScreeningID, SeatNumber):
    query = "INSERT INTO tickets (CustomerID, ScreeningID, SeatNumber) VALUES (%s, %s, %s)"
    values = (CustomerID, ScreeningID, SeatNumber)
    mycursor.execute(query, values)
    mydb.commit()
    print("Ticket booked successfully!")

#Cancellation
def cancel_ticket(TicketID):
    mycursor.execute("DELETE FROM tickets WHERE TicketID = %s", (TicketID,))
    mydb.commit()
    print("Ticket cancelled.")