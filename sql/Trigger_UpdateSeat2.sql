-- BƯỚC 1: Thêm cột trạng thái ghế vào bảng Seats
ALTER TABLE Seats ADD COLUMN SeatStatus ENUM('Available', 'Booked') DEFAULT 'Available';

-- BƯỚC 2: Trigger tự động cập nhật trạng thái ghế khi đặt vé
DELIMITER //
CREATE TRIGGER update_seat_status_after_booking
AFTER INSERT ON Tickets
FOR EACH ROW
BEGIN
    UPDATE Seats 
    SET SeatStatus = 'Booked' 
    WHERE SeatID = NEW.SeatID;
END//
DELIMITER ;

-- BƯỚC 3: Trigger tự động cập nhật trạng thái ghế khi hủy vé
DELIMITER //
CREATE TRIGGER update_seat_status_after_cancel
AFTER DELETE ON Tickets
FOR EACH ROW
BEGIN
    UPDATE Seats 
    SET SeatStatus = 'Available' 
    WHERE SeatID = OLD.SeatID;
END//
DELIMITER ;

-- BƯỚC 4: Trigger cập nhật khi cập nhật vé (nếu đổi ghế)
DELIMITER //
CREATE TRIGGER update_seat_status_after_update
AFTER UPDATE ON Tickets
FOR EACH ROW
BEGIN
    -- Nếu đổi ghế khác
    IF OLD.SeatID != NEW.SeatID THEN
        -- Ghế cũ chuyển về Available
        UPDATE Seats 
        SET SeatStatus = 'Available' 
        WHERE SeatID = OLD.SeatID;
        
        -- Ghế mới chuyển thành Booked
        UPDATE Seats 
        SET SeatStatus = 'Booked' 
        WHERE SeatID = NEW.SeatID;
    END IF;
END//
DELIMITER ;

/*
-- BƯỚC 5: Event tự động reset ghế sau khi suất chiếu kết thúc
DELIMITER //
CREATE EVENT reset_expired_bookings
ON SCHEDULE EVERY 1 HOUR
DO
BEGIN
    -- Cập nhật trạng thái ghế về Available cho các suất chiếu đã kết thúc
    UPDATE Seats s
    JOIN Tickets t ON s.SeatID = t.SeatID
    JOIN Screenings sc ON t.ScreeningID = sc.ScreeningID
    SET s.SeatStatus = 'Available'
    WHERE ADDTIME(CONCAT(sc.ScreeningDate, ' ', sc.ScreeningTime), 
                  SEC_TO_TIME(m.DurationMinutes * 60)) < NOW()
    AND s.SeatStatus = 'Booked';
    
    -- Xóa các vé đã hết hạn (suất chiếu đã kết thúc)
    DELETE t FROM Tickets t
    JOIN Screenings sc ON t.ScreeningID = sc.ScreeningID
    JOIN Movies m ON sc.MovieID = m.MovieID
    WHERE ADDTIME(CONCAT(sc.ScreeningDate, ' ', sc.ScreeningTime), 
                  SEC_TO_TIME(m.DurationMinutes * 60)) < NOW();
    
    -- Xóa các payment tương ứng với vé đã bị xóa
    DELETE p FROM Payments p
    WHERE p.TicketID NOT IN (SELECT TicketID FROM Tickets);
END//
DELIMITER ;
*/