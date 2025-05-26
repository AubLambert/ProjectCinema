import tkinter as tk
from tkinter import *
import mysql.connector
from mysql.connector import Error
from datetime import datetime

mydb = mysql.connector.connect(
    host = "localhost",
    user = "admin",
    password = "quang123",
    database="cinema_management"
)


class ticket_searching:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Ticket searching")
        self.root.geometry("960x600")
        self.root.resizable(False, False)
        
        self.search_interface()
        self.root.mainloop()
        
    def search_interface(self):
        ### Back button:
       #TODO:back command     
        back_btn = tk.Button(
            self.root, text="BACK", font=('Arial', 10), borderwidth=1, width=7, height=1,
            command=""
        )
        back_btn.place(x=30, y=30)
        
        
        ### Searchbar with effect
        self.search_var = tk.StringVar()
        search_entry = tk.Entry(
            self.root, textvariable=self.search_var, font=('Arial', 12), justify="center", relief='solid',fg ="grey",
            borderwidth=1, width=50
        )
        search_entry.place(x=230, y=65, width=500, height=30)
        search_entry.insert(0, "Type in phone number or ticketID")
        
        search_entry.bind('<FocusIn>', self.on_entry_click)
        search_entry.bind('<FocusOut>', self.on_focusout)
        search_entry.bind('<Return>', lambda event: self.search_ticket())
        
        search_btn = tk.Button(
            self.root, text="Search", font=('Arial', 10), bg='#007bff', fg='white', relief='solid',
            padx=20, pady=5, command= self.search_ticket
        )
        search_btn.place(x=750, y=65, width=80, height=30)
        
        # Result panel outer frame
        self.canvas_frame = tk.Frame(self.root)
        self.canvas_frame.place(x=79.5, y=130, width=800, height=320)
        
        # Outer canvas
        self.canvas = tk.Canvas(self.canvas_frame, bg='white')
        self.scrollbar_x = tk.Scrollbar(self.canvas_frame, orient='horizontal', command=self.canvas.xview)
        self.scrollbar_y = tk.Scrollbar(self.canvas_frame, orient='vertical', command=self.canvas.yview)
        self.canvas.configure(xscrollcommand=self.scrollbar_x.set, yscrollcommand=self.scrollbar_y.set)
        
        self.scrollbar_x.pack(side='bottom', fill='x')
        self.scrollbar_y.pack(side='right', fill='y')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Container canvas
        self.scrollable_container = tk.Frame(self.canvas, bg='white')
        self.canvas.create_window((0, 0), window=self.scrollable_container, anchor='nw')
        
        # Bind scroll region update
        self.scrollable_container.bind(
            "<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        )
        
        # Headings frame
        self.heading_frame = tk.Frame(self.scrollable_container, bg='white')
        self.heading_frame.grid(row=0, column=0, sticky='nw')
        
        headings = ["Ticket ID", "Customer Name", "Phone", "Movie", "Room", "Date", "Seat", "Time", "Price", "Payment Time", "Action"]
        for col, title in enumerate(headings):
            lbl = tk.Label(self.heading_frame, text=title, font=('Arial', 10, 'bold'),
                           borderwidth=1, relief='solid', width=17)
            lbl.grid(row=0, column=col, sticky='nsew')
        
        # Results frame
        self.inner_frame = tk.Frame(self.scrollable_container, bg='white')
        self.inner_frame.grid(row=1, column=0, sticky='nw')
        self.rows = []
    
            
    def on_entry_click(self, event):
        if self.search_var.get() == "Type in phone number or ticketID":
            self.search_var.set("")
            event.widget.config(fg='black')

    def on_focusout(self, event):
        if self.search_var.get() == "":
            self.search_var.set("Type in phone number or ticketID")
            event.widget.config(fg='grey')
            
    def clear_rows(self):
        for widgets in self.rows:
            for w in widgets:
                w.destroy()
        self.rows.clear()
        
        
    # Find customer's ticket through input
    def search_ticket(self):
        user_input = self.search_var.get().strip()
        try:
            mycursor= mydb.cursor()
            query = """
            SELECT t.TicketID, c.CustomerName, c.PhoneNumber, m.MovieTitle, r.RoomName, se.SeatNumber, 
            s.ScreeningDate, s.ScreeningTime, s.Price, p.PayTime
            FROM Tickets t
            JOIN Customers c ON t.CustomerID = c.CustomerID
            JOIN Screenings s ON t.ScreeningID = s.ScreeningID
            JOIN Seats se ON t.SeatID = se.SeatID
            JOIN Movies m ON s.MovieID = m.MovieID
            JOIN Cinemarooms r ON s.RoomID = r.RoomID
            JOIN Payments p ON t.TicketID = p.TicketID
            WHERE {}
            """
            if user_input.isdigit():
                condition = "t.TicketID = %s OR c.PhoneNumber = %s"
            
            final_query = query.format(condition)
            mycursor.execute(final_query, (user_input, user_input))
            results = mycursor.fetchall()
            self.display_results(results)
        
        except Error as e:
            print(f"Database error: {e}")
            return []
        except Exception as e:
            print(f"Error: {e}")
            self.display_results([])

        if not results:
            print("No tickets found for this phone number.")
            self.display_results([])

        
    def display_results(self, results):
        self.clear_rows()
        
        if not results:
            # Show "No results found" message
            no_result_lbl = tk.Label(self.inner_frame, text="No tickets found", 
                                   font=('Arial', 12), bg='white', fg='gray')
            no_result_lbl.grid(row=0, column=0, columnspan=11, pady=20)
            self.rows.append([no_result_lbl])
            return
        
        for i, row in enumerate(results):
            widgets = []
            ticket_id, customer_name, phone_number, movie, room, seat_num, date, time, price, pay_time = row
            
            # Check if action should be available
            show_action = self.check_action_conditions(row)
            values = [ticket_id, customer_name, phone_number, movie, room, date, seat_num, time, price, pay_time, 'Cancel' if show_action else '']

            for j, val in enumerate(values):
                lbl = tk.Label(self.inner_frame, text=val, font=('Arial', 10), bg='white', 
                             relief='solid', borderwidth=1, width=17)
                lbl.grid(row=i, column=j, sticky='nsew')  # Fixed: use self.inner_frame

                # Make Cancel button clickable
                if j == len(values)-1 and val == 'Cancel':
                    lbl.bind("<Button-1>", lambda e, tid=ticket_id: self.handle_action_click(tid))
                    lbl.config(fg='red', cursor='hand2')

                widgets.append(lbl)
            self.rows.append(widgets)
        
        # Update canvas scroll region after adding content
        self.root.after(10, lambda: self.canvas.configure(scrollregion=self.canvas.bbox("all")))

    def check_action_conditions(self, ticket_data):
        try:
            ticket_date = datetime.strptime(str(ticket_data[6]), '%Y-%m-%d').date()
            today = datetime.now().date()
            return ticket_date >= today
        except (ValueError, IndexError) as e:
            print(f"Date parsing error: {e}")
            return False

    def handle_action_click(self, ticket_id):
        print(f"Cancel action clicked for ticket: {ticket_id}")
        # TODO
        result = tk.messagebox.askyesno("Confirm Cancellation", 
                                      f"Are you sure you want to cancel ticket {ticket_id}?")
        if result:
            try:
                mycursor = mydb.cursor()
                delete_query = "DELETE FROM Tickets WHERE TicketID = %s"
                mycursor.execute(delete_query, (ticket_id,))
                mydb.commit()
    
                if mycursor.rowcount > 0:
                    messagebox.showinfo("Success", f"Ticket {ticket_id} successfully cancelled.")
                else:
                    messagebox.showwarning("Warning", f"Ticket {ticket_id} was not found or already deleted.")
    
                self.search_ticket()  # Refresh the results
    
            except Error as e:
                messagebox.showerror("Database Error", f"An error occurred: {e}")

if __name__ == "__main__":
    app=ticket_searching()
    
mydb.close()