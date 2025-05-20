DELIMITER $$

CREATE TRIGGER NotifyOverbooking
BEFORE INSERT ON Tickets
FOR EACH ROW
BEGIN
  DECLARE capacity INT;
  DECLARE booked INT;

  SELECT COUNT(*) INTO capacity
    FROM Seats
    WHERE RoomID = (SELECT RoomID FROM Screenings WHERE ScreeningID = NEW.ScreeningID);

  SELECT COUNT(*) INTO booked
    FROM Tickets
    WHERE ScreeningID = NEW.ScreeningID;

  IF booked > capacity THEN
    SIGNAL SQLSTATE '45000'
      SET MESSAGE_TEXT = 'Overbooking detected: no seats available.';
  END IF;
END$$

DELIMITER ;