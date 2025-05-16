-- Create account for admin and ticket clerk
CREATE USER 'Admin'@'local_host' IDENTIFIED BY 'Admin_password';
CREATE USER 'Ticket_clerk'@'local_host' IDENTIFIED BY 'Clerk_password';
-- Provide privileges for admin and ticket clerk
GRANT ALL PRIVILEGES ON cinema_management.* TO 'Admin'@'local_host';
GRANT SELECT, INSERT ON cinema_management.movies TO 'Ticket_clerk'@'local_host';
GRANT SELECT, INSERT ON cinema_management.customers TO 'Ticket_clerk'@'local_host';
GRANT SELECT, INSERT ON cinema_management.tickets TO 'Ticket_clerk'@'local_host';
-- Revoke Update, Delete from ticket clerk for customers information
REVOKE UPDATE, DELETE ON cinema_management.customers FROM 'Ticket_clerk'@'local_host';
