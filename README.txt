## Option 1: CinemaGUI.exe
Executable app can be found at: https://drive.google.com/drive/folders/1FzVOp4zyP3ZbNaE3qptblQQFEyYY4gN-?usp=drive_link
-- CinemaGUI application --
To be able to run CinemaGUI.exe smoothly, users are required to install the following files in sequence:
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

Then:
1. Download CinemaGUI.rar 
2. Extract CinemaGUI.rar 
3. Run CinemaGUI.exe

Use either "admin" or "ticket_clerk" account to login (login credentials can be found in AssignRole_ControlAccess.sql file)
-- Database Backup --
To automatically back up the database: Use the database_backup.bat file in our python folder (change the config to suit you) and use Task Scheduler (detailed guide vid:https://www.youtube.com/watch?v=xLOw7LeoBwo)


## Option 2: CinemaGUI.py for source code inspection

-- CinemaGUI.py Python and SQL setup --
To be able to operate CinemaGUI.py smoothly, users are required to install the following files in sequence:
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


