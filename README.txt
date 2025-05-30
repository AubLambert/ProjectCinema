To be able to operate CinemaGUI smoothly, users are required to install the following files in sequence:
For SQL database:
1. SchemaScript.sql
2. ImportScript.sql - sample data
3. ImportScript_2.sql - sample data
4. ImportScript_3(ScreeningOnly).sql - this file is for future screenings query
5. AssignRole_ControlAccess.sql - To gain access to different function
6. VIEW_admin.sql - For business dashboard
8. Trigger_UpdateSeat2.sql - For seat availability modifying automation
9. Trigger_OverBooking.sql
10. AdvancedDbObj.sql

To setup CinemaGUI, place both "Images" folder and CinemaGUI in 1 directory, for example:

ProjectCinema/
├── Images
├── CinemaGUI.py

Use either "admin" or "ticket_clerk" account to login (login credentials can be found in AssignRole_ControlAccess.sql file)