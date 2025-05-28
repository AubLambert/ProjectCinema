-- Drop old user
DROP USER 'admin'@'localhost';
DROP USER 'manager'@'localhost';
DROP USER 'ticket_clerk'@'localhost';
-- Create account for admin and ticket clerk
CREATE USER 'admin'@'localhost' IDENTIFIED BY 'quang123';
CREATE USER 'manager'@'localhost' IDENTIFIED BY 'khang123';
CREATE USER 'ticket_clerk'@'localhost' IDENTIFIED BY 'dat123';

-- Admin
GRANT ALL PRIVILEGES ON cinema_management.* TO 'admin'@'localhost';

-- Manager
GRANT SELECT, INSERT, UPDATE, DELETE ON cinema_management.movies TO 'manager'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON cinema_management.screenings TO 'manager'@'localhost';
GRANT SELECT, UPDATE, INSERT, DELETE ON cinema_management.customers TO 'manager'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON cinema_management.tickets TO 'manager'@'localhost';
GRANT SELECT, INSERT, UPDATE, DELETE ON cinema_management.cinemarooms TO 'manager'@'localhost';

-- Ticket_clerk 
GRANT SELECT ON cinema_management.movies TO 'ticket_clerk'@'localhost';
GRANT SELECT ON cinema_management.screenings TO 'ticket_clerk'@'localhost';
GRANT SELECT ON cinema_management.cinemarooms TO 'ticket_clerk'@'localhost';
GRANT SELECT ON cinema_management.seats TO 'ticket_clerk'@'localhost';

GRANT SELECT, INSERT, DELETE ON cinema_management.customers TO 'ticket_clerk'@'localhost';
GRANT SELECT, INSERT, DELETE ON cinema_management.tickets TO 'ticket_clerk'@'localhost';
GRANT SELECT, INSERT, DELETE ON cinema_management.payments TO 'ticket_clerk'@'localhost';
GRANT EXECUTE ON PROCEDURE cinema_management.ticket_booking TO 'ticket_clerk'@'localhost'