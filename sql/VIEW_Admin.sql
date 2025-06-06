-- REVENUE
CREATE OR REPLACE VIEW revenue_alltime AS
WITH MinMaxDates AS (
    SELECT 
        MIN(DATE(PayTime)) AS MinDate,
        LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AS MaxDate
    FROM Payments
),
QuarterRanges AS (
    SELECT 
        DATE_FORMAT(
            DATE_ADD(MinDate, INTERVAL (n * 3) MONTH), 
            '%Y-%m-01'
        ) AS QuarterStart
    FROM MinMaxDates
    CROSS JOIN (
        SELECT a.N + b.N * 10 AS n
        FROM 
            (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a,
            (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
    ) numbers
    WHERE 
        DATE_ADD(MinDate, INTERVAL (n * 3) MONTH) <= MaxDate
),
ValidQuarters AS (
    SELECT 
        QuarterStart,
        LAST_DAY(DATE_ADD(QuarterStart, INTERVAL 2 MONTH)) AS QuarterEnd,
        CONCAT(
            YEAR(QuarterStart), '-Q', 
            CASE 
                WHEN MONTH(QuarterStart) IN (1, 2, 3) THEN 1
                WHEN MONTH(QuarterStart) IN (4, 5, 6) THEN 2
                WHEN MONTH(QuarterStart) IN (7, 8, 9) THEN 3
                WHEN MONTH(QuarterStart) IN (10, 11, 12) THEN 4
            END
        ) AS QuarterLabel
    FROM QuarterRanges
    WHERE 
        LAST_DAY(DATE_ADD(QuarterStart, INTERVAL 2 MONTH)) < CURDATE()
)
SELECT 
    QuarterLabel AS Date,
    COALESCE(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    ValidQuarters vq
LEFT JOIN Payments p 
    ON DATE(p.PayTime) BETWEEN vq.QuarterStart AND vq.QuarterEnd
GROUP BY 
    vq.QuarterLabel, vq.QuarterStart
ORDER BY 
    vq.QuarterStart ASC;
    
CREATE OR REPLACE VIEW revenue_year AS
WITH FullMonths AS (
    SELECT 
        DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL n MONTH), '%Y-%m-01') AS MonthStart
    FROM (
        SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
        UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
        UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
    ) AS months_back
    WHERE DATE_SUB(CURDATE(), INTERVAL n MONTH) < CURDATE()
),
ValidFullMonths AS (
    SELECT 
        MonthStart,
        LAST_DAY(MonthStart) AS MonthEnd
    FROM FullMonths
    WHERE LAST_DAY(MonthStart) < CURDATE()
)
SELECT 
    DATE_FORMAT(fm.MonthStart, '%Y-%m') AS Date,
    COALESCE(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    ValidFullMonths fm
LEFT JOIN Payments p 
    ON DATE(p.PayTime) BETWEEN fm.MonthStart AND fm.MonthEnd
GROUP BY 
    fm.MonthStart
ORDER BY 
    fm.MonthStart ASC;
    

CREATE OR REPLACE VIEW revenue_6months AS
WITH RECURSIVE DateRange AS (
    SELECT DATE_SUB(CURDATE(), INTERVAL 180 DAY) AS PaymentDate
    UNION ALL
    SELECT PaymentDate + INTERVAL 1 DAY
    FROM DateRange
    WHERE PaymentDate < CURDATE()
),
DateGroups AS (
    SELECT 
        PaymentDate,
        FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 15) AS PeriodGroup,
        DATE_SUB(CURDATE(), INTERVAL FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 15) * 15 DAY) AS PeriodStart,
        DATE_SUB(CURDATE(), INTERVAL (FLOOR(DATEDIFF(CURDATE(), PaymentDate) * 1.0 / 15) * 15 - 14) DAY) AS PeriodEnd
    FROM DateRange
),
FilteredGroups AS (
    SELECT 
        PeriodGroup,
        MIN(PeriodStart) AS PeriodStart,
        COUNT(*) AS DaysInGroup
    FROM DateGroups
    GROUP BY PeriodGroup
    HAVING COUNT(*) = 15
)
SELECT 
    DATE_FORMAT(fg.PeriodStart, '%Y-%m-%d') AS Date,
    COALESCE(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    FilteredGroups fg
JOIN DateGroups dg ON fg.PeriodGroup = dg.PeriodGroup
LEFT JOIN Payments p ON DATE(p.PayTime) = dg.PaymentDate
GROUP BY 
    fg.PeriodGroup, fg.PeriodStart
ORDER BY 
    fg.PeriodStart ASC;
    

CREATE OR REPLACE VIEW revenue_30days AS
WITH RECURSIVE DateRange AS (
    SELECT DATE_SUB(CURDATE(), INTERVAL 30 DAY) AS PaymentDate
    UNION ALL
    SELECT PaymentDate + INTERVAL 1 DAY
    FROM DateRange
    WHERE PaymentDate < CURDATE()
),
DateGroups AS (
    SELECT 
        PaymentDate,
        FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 3) AS PeriodGroup,
        DATE_SUB(CURDATE(), INTERVAL FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 3) * 3 DAY) AS PeriodStart,
        DATE_SUB(CURDATE(), INTERVAL (FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 3) * 3 - 2) DAY) AS PeriodEnd
    FROM DateRange
),
FilteredGroups AS (
    SELECT 
        PeriodGroup,
        MIN(PeriodStart) AS PeriodStart,
        COUNT(*) AS DaysInGroup
    FROM DateGroups
    GROUP BY PeriodGroup
    HAVING COUNT(*) = 3
)
SELECT 
    DATE_FORMAT(fg.PeriodStart, '%Y-%m-%d') AS Date,
    COALESCE(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    FilteredGroups fg
JOIN DateGroups dg ON fg.PeriodGroup = dg.PeriodGroup
LEFT JOIN Payments p ON DATE(p.PayTime) = dg.PaymentDate
GROUP BY 
    fg.PeriodGroup, fg.PeriodStart
ORDER BY 
    fg.PeriodStart ASC;
    
-- TICKET
CREATE OR REPLACE VIEW ticket_alltime AS
WITH MinMaxDates AS (
    SELECT 
        MIN(s.ScreeningDate) AS MinDate,
        LAST_DAY(DATE_SUB(CURDATE(), INTERVAL 1 MONTH)) AS MaxDate
    FROM Screenings s
    JOIN Tickets t ON t.ScreeningID = s.ScreeningID
),
QuarterRanges AS (
    SELECT 
        DATE_FORMAT(
            DATE_ADD(MinDate, INTERVAL (n * 3) MONTH), 
            '%Y-%m-01'
        ) AS QuarterStart
    FROM MinMaxDates
    CROSS JOIN (
        SELECT a.N + b.N * 10 AS n
        FROM 
            (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 
             UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) a,
            (SELECT 0 AS N UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4 
             UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9) b
    ) numbers
    WHERE 
        DATE_ADD(MinDate, INTERVAL (n * 3) MONTH) <= MaxDate
),
ValidQuarters AS (
    SELECT 
        QuarterStart,
        LAST_DAY(DATE_ADD(QuarterStart, INTERVAL 2 MONTH)) AS QuarterEnd,
        CONCAT(
            YEAR(QuarterStart), '-Q', 
            CASE 
                WHEN MONTH(QuarterStart) IN (1, 2, 3) THEN 1
                WHEN MONTH(QuarterStart) IN (4, 5, 6) THEN 2
                WHEN MONTH(QuarterStart) IN (7, 8, 9) THEN 3
                WHEN MONTH(QuarterStart) IN (10, 11, 12) THEN 4
            END
        ) AS QuarterLabel
    FROM QuarterRanges
    WHERE 
        LAST_DAY(DATE_ADD(QuarterStart, INTERVAL 2 MONTH)) < CURDATE()
)
SELECT 
    vq.QuarterLabel AS Date,
    COALESCE(COUNT(t.TicketID), 0) AS TotalTicketsSold
FROM 
    ValidQuarters vq
LEFT JOIN Screenings s 
    ON s.ScreeningDate BETWEEN vq.QuarterStart AND vq.QuarterEnd
LEFT JOIN Tickets t 
    ON t.ScreeningID = s.ScreeningID
GROUP BY 
    vq.QuarterLabel, vq.QuarterStart
ORDER BY 
    vq.QuarterStart ASC;
    

CREATE OR REPLACE VIEW ticket_year AS
WITH FullMonths AS (
    SELECT 
        DATE_FORMAT(DATE_SUB(CURDATE(), INTERVAL n MONTH), '%Y-%m-01') AS MonthStart
    FROM (
        SELECT 0 AS n UNION ALL SELECT 1 UNION ALL SELECT 2 UNION ALL SELECT 3 UNION ALL SELECT 4
        UNION ALL SELECT 5 UNION ALL SELECT 6 UNION ALL SELECT 7 UNION ALL SELECT 8 UNION ALL SELECT 9
        UNION ALL SELECT 10 UNION ALL SELECT 11 UNION ALL SELECT 12
    ) AS months_back
    WHERE DATE_SUB(CURDATE(), INTERVAL n MONTH) < CURDATE()
),
ValidFullMonths AS (
    SELECT 
        MonthStart,
        LAST_DAY(MonthStart) AS MonthEnd
    FROM FullMonths
    WHERE LAST_DAY(MonthStart) < CURDATE()
)
SELECT 
    DATE_FORMAT(fm.MonthStart, '%Y-%m') AS Date,
    COUNT(p.TicketID) AS TotalTicketsSold
FROM 
    ValidFullMonths fm
LEFT JOIN Payments p 
    ON DATE(p.PayTime) BETWEEN fm.MonthStart AND fm.MonthEnd
GROUP BY 
    fm.MonthStart
ORDER BY 
    fm.MonthStart ASC;
    

CREATE OR REPLACE VIEW ticket_6months AS
WITH RECURSIVE DateRange AS (
    SELECT DATE_SUB(CURDATE(), INTERVAL 180 DAY) AS PaymentDate
    UNION ALL
    SELECT PaymentDate + INTERVAL 1 DAY
    FROM DateRange
    WHERE PaymentDate < CURDATE()
),
DateGroups AS (
    SELECT 
        PaymentDate,
        FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 15) AS PeriodGroup,
        DATE_SUB(CURDATE(), INTERVAL FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 15) * 15 DAY) AS PeriodStart,
        DATE_SUB(CURDATE(), INTERVAL (FLOOR(DATEDIFF(CURDATE(), PaymentDate) * 1.0 / 15) * 15 - 14) DAY) AS PeriodEnd
    FROM DateRange
),
FilteredGroups AS (
    SELECT 
        PeriodGroup,
        MIN(PeriodStart) AS PeriodStart,
        COUNT(*) AS DaysInGroup
    FROM DateGroups
    GROUP BY PeriodGroup
    HAVING COUNT(*) = 15
)
SELECT 
    DATE_FORMAT(fg.PeriodStart, '%Y-%m-%d') AS Date,
    COUNT(p.TicketID) AS TotalTicketsSold
FROM 
    FilteredGroups fg
JOIN DateGroups dg ON fg.PeriodGroup = dg.PeriodGroup
LEFT JOIN Payments p ON DATE(p.PayTime) = dg.PaymentDate
GROUP BY 
    fg.PeriodGroup, fg.PeriodStart
ORDER BY 
    fg.PeriodStart ASC;
    
-- TICKET
CREATE OR REPLACE VIEW ticket_30days AS
WITH RECURSIVE DateRange AS (
    SELECT DATE_SUB(CURDATE(), INTERVAL 30 DAY) AS PaymentDate
    UNION ALL
    SELECT PaymentDate + INTERVAL 1 DAY
    FROM DateRange
    WHERE PaymentDate < CURDATE()
),
DateGroups AS (
    SELECT 
        PaymentDate,
        FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 3) AS PeriodGroup,
        DATE_SUB(CURDATE(), INTERVAL FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 3) * 3 DAY) AS PeriodStart,
        DATE_SUB(CURDATE(), INTERVAL (FLOOR(DATEDIFF(CURDATE(), PaymentDate) / 3) * 3 - 2) DAY) AS PeriodEnd
    FROM DateRange
),
FilteredGroups AS (
    SELECT 
        PeriodGroup,
        MIN(PeriodStart) AS PeriodStart,
        COUNT(*) AS DaysInGroup
    FROM DateGroups
    GROUP BY PeriodGroup
    HAVING COUNT(*) = 3
)
SELECT 
    DATE_FORMAT(fg.PeriodStart, '%Y-%m-%d') AS Date,
    COUNT(p.TicketID) AS TotalTicketsSold
FROM 
    FilteredGroups fg
JOIN DateGroups dg ON fg.PeriodGroup = dg.PeriodGroup
LEFT JOIN Payments p ON DATE(p.PayTime) = dg.PaymentDate
GROUP BY 
    fg.PeriodGroup, fg.PeriodStart
ORDER BY 
    fg.PeriodStart ASC;


-- MOVIE
CREATE OR REPLACE VIEW movie_14days AS
SELECT 
    m.MovieID,
    m.MovieTitle,
    m.Genre,
    COUNT(t.TicketID) AS TicketsSold,
    SUM(p.Amount) AS TotalRevenue,
    COUNT(t.TicketID) * 1.0 / NULLIF(SUM(r.TotalSeats), 0) AS AttendanceRate
FROM Movies m
JOIN Screenings s ON m.MovieID = s.MovieID
JOIN CinemaRooms cr ON s.RoomID = cr.RoomID
JOIN (
    SELECT RoomID, COUNT(*) AS TotalSeats
    FROM Seats
    GROUP BY RoomID
) r ON cr.RoomID = r.RoomID
LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN Payments p ON t.TicketID = p.TicketID
WHERE s.ScreeningDate >= CURDATE() - INTERVAL 14 DAY
GROUP BY m.MovieID, m.MovieTitle, m.Genre
HAVING TotalRevenue > 0
ORDER BY 
    TotalRevenue DESC,
    TicketsSold DESC,
    AttendanceRate DESC;

-- MOVIE
CREATE OR REPLACE VIEW movie_30days AS
SELECT 
    m.MovieID,
    m.MovieTitle,
    m.Genre,
    COUNT(t.TicketID) AS TicketsSold,
    SUM(p.Amount) AS TotalRevenue,
    COUNT(t.TicketID) * 1.0 / NULLIF(SUM(r.TotalSeats), 0) AS AttendanceRate
FROM Movies m
JOIN Screenings s ON m.MovieID = s.MovieID
JOIN CinemaRooms cr ON s.RoomID = cr.RoomID
JOIN (
    SELECT RoomID, COUNT(*) AS TotalSeats
    FROM Seats
    GROUP BY RoomID
) r ON cr.RoomID = r.RoomID
LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN Payments p ON t.TicketID = p.TicketID
WHERE s.ScreeningDate >= CURDATE() - INTERVAL 30 DAY
GROUP BY m.MovieID, m.MovieTitle, m.Genre
HAVING TotalRevenue > 0
ORDER BY 
    TotalRevenue DESC,
    TicketsSold DESC,
    AttendanceRate DESC;

-- MOVIE
CREATE OR REPLACE VIEW movie_60days AS
SELECT 
    m.MovieID,
    m.MovieTitle,
    m.Genre,
    COUNT(t.TicketID) AS TicketsSold,
    SUM(p.Amount) AS TotalRevenue,
    COUNT(t.TicketID) * 1.0 / NULLIF(SUM(r.TotalSeats), 0) AS AttendanceRate
FROM Movies m
JOIN Screenings s ON m.MovieID = s.MovieID
JOIN CinemaRooms cr ON s.RoomID = cr.RoomID
JOIN (
    SELECT RoomID, COUNT(*) AS TotalSeats
    FROM Seats
    GROUP BY RoomID
) r ON cr.RoomID = r.RoomID
LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN Payments p ON t.TicketID = p.TicketID
WHERE s.ScreeningDate >= CURDATE() - INTERVAL 60 DAY
GROUP BY m.MovieID, m.MovieTitle, m.Genre
HAVING TotalRevenue > 0
ORDER BY 
    TotalRevenue DESC,
    TicketsSold DESC,
    AttendanceRate DESC;

-- OCCUPATION
CREATE OR REPLACE VIEW occupation AS
SELECT 
    DATE_FORMAT(daily.RoomDate, '%Y-%m') AS Month,
    SUM(daily.TicketsSold) AS Tickets_Sold,
    SUM(daily.ScreeningsInRoom) AS Total_Screenings,
    SUM(daily.SeatCount * daily.ScreeningsInRoom) AS TotalSeat,
    ROUND((SUM(daily.TicketsSold) / SUM(daily.SeatCount * daily.ScreeningsInRoom)) * 100, 2) AS `Occupation Rate (%)`
FROM (
    SELECT 
        s.ScreeningDate AS RoomDate,
        s.RoomID,
        COUNT(DISTINCT s.ScreeningID) AS ScreeningsInRoom,
        COUNT(DISTINCT t.TicketID) AS TicketsSold,
        seat_counts.SeatCount
    FROM 
        Screenings s
    LEFT JOIN 
        Tickets t ON s.ScreeningID = t.ScreeningID
    JOIN (
        SELECT 
            RoomID, COUNT(*) AS SeatCount
        FROM 
            Seats
        GROUP BY 
            RoomID
    ) AS seat_counts ON s.RoomID = seat_counts.RoomID
    WHERE 
        s.ScreeningDate <= CURDATE()
    GROUP BY 
        s.ScreeningDate, s.RoomID
) AS daily
GROUP BY 
    DATE_FORMAT(daily.RoomDate, '%Y-%m')
ORDER BY 
    Month ASC;

-- DAY PERFORMANCE
CREATE OR REPLACE VIEW day_performance30 AS
WITH TicketCounts AS (
    SELECT 
        DAYNAME(s.ScreeningDate) AS WeekDay,
        s.ScreeningTime,
        COUNT(t.TicketID) AS TicketsSold
    FROM Tickets t
    JOIN Screenings s ON t.ScreeningID = s.ScreeningID
    WHERE s.ScreeningDate >= CURDATE() - INTERVAL 30 DAY
    GROUP BY WeekDay, s.ScreeningTime
),
DailyTotals AS (
    SELECT 
        WeekDay,
        SUM(TicketsSold) AS TicketSold
    FROM TicketCounts
    GROUP BY WeekDay
),
PopularShowtimes AS (
    SELECT 
        tc.WeekDay,
        tc.ScreeningTime AS MostPopularShowtime
    FROM TicketCounts tc
    JOIN (
        SELECT 
            WeekDay,
            MAX(TicketsSold) AS MaxSold
        FROM TicketCounts
        GROUP BY WeekDay
    ) mx ON tc.WeekDay = mx.WeekDay AND tc.TicketsSold = mx.MaxSold
)
SELECT 
    dt.WeekDay AS Day,
    dt.TicketSold,
    ps.MostPopularShowtime
FROM DailyTotals dt
JOIN PopularShowtimes ps ON dt.WeekDay = ps.WeekDay
ORDER BY FIELD(dt.WeekDay, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');

-- DAY PERFORMANCE
CREATE OR REPLACE VIEW day_performance90 AS
WITH TicketCounts AS (
    SELECT 
        DAYNAME(s.ScreeningDate) AS WeekDay,
        s.ScreeningTime,
        COUNT(t.TicketID) AS TicketsSold
    FROM Tickets t
    JOIN Screenings s ON t.ScreeningID = s.ScreeningID
    WHERE s.ScreeningDate >= CURDATE() - INTERVAL 90 DAY
    GROUP BY WeekDay, s.ScreeningTime
),
DailyTotals AS (
    SELECT 
        WeekDay,
        SUM(TicketsSold) AS TicketSold
    FROM TicketCounts
    GROUP BY WeekDay
),
PopularShowtimes AS (
    SELECT 
        tc.WeekDay,
        tc.ScreeningTime AS MostPopularShowtime
    FROM TicketCounts tc
    JOIN (
        SELECT 
            WeekDay,
            MAX(TicketsSold) AS MaxSold
        FROM TicketCounts
        GROUP BY WeekDay
    ) mx ON tc.WeekDay = mx.WeekDay AND tc.TicketsSold = mx.MaxSold
)
SELECT 
    dt.WeekDay AS Day,
    dt.TicketSold,
    ps.MostPopularShowtime
FROM DailyTotals dt
JOIN PopularShowtimes ps ON dt.WeekDay = ps.WeekDay
ORDER BY FIELD(dt.WeekDay, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');

-- DAY PERFORMANCE
CREATE OR REPLACE VIEW day_performancealltime AS
WITH TicketCounts AS (
    SELECT 
        DAYNAME(s.ScreeningDate) AS WeekDay,
        s.ScreeningTime,
        COUNT(t.TicketID) AS TicketsSold
    FROM Tickets t
    JOIN Screenings s ON t.ScreeningID = s.ScreeningID
    GROUP BY WeekDay, s.ScreeningTime
),
DailyTotals AS (
    SELECT 
        WeekDay,
        SUM(TicketsSold) AS TicketSold
    FROM TicketCounts
    GROUP BY WeekDay
),
PopularShowtimes AS (
    SELECT 
        tc.WeekDay,
        tc.ScreeningTime AS MostPopularShowtime
    FROM TicketCounts tc
    JOIN (
        SELECT 
            WeekDay,
            MAX(TicketsSold) AS MaxSold
        FROM TicketCounts
        GROUP BY WeekDay
    ) mx ON tc.WeekDay = mx.WeekDay AND tc.TicketsSold = mx.MaxSold
)
SELECT 
    dt.WeekDay AS Day,
    dt.TicketSold,
    ps.MostPopularShowtime
FROM DailyTotals dt
JOIN PopularShowtimes ps ON dt.WeekDay = ps.WeekDay
ORDER BY FIELD(dt.WeekDay, 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday');

-- Screeningtime 
CREATE OR REPLACE VIEW screeningtime AS
WITH ScreeningStats AS (
    SELECT 
        s.ScreeningID,
        s.ScreeningTime,
        COUNT(t.TicketID) AS TicketsSold,
        cr.RoomID,
        (SELECT COUNT(*) FROM Seats WHERE RoomID = s.RoomID) AS SeatsAvailable,
        s.Price * COUNT(t.TicketID) AS Revenue
    FROM Screenings s
    LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
    JOIN CinemaRooms cr ON s.RoomID = cr.RoomID
    GROUP BY s.ScreeningID, s.ScreeningTime, cr.RoomID, s.Price
),
AggregatedStats AS (
    SELECT 
        ScreeningTime,
        SUM(TicketsSold) AS TicketSold,
        ROUND(SUM(TicketsSold) / SUM(SeatsAvailable), 2) AS OccupationRate,
        SUM(Revenue) AS Revenue
    FROM ScreeningStats
    GROUP BY ScreeningTime
)
SELECT 
    ScreeningTime,
    TicketSold,
    OccupationRate,
    Revenue
FROM AggregatedStats
ORDER BY ScreeningTime;

-- Screening Performance
CREATE OR REPLACE VIEW screeningtime30 AS
WITH ScreeningStats AS (
    SELECT 
        s.ScreeningID,
        s.ScreeningTime,
        COUNT(t.TicketID) AS TicketsSold,
        cr.RoomID,
        (SELECT COUNT(*) FROM Seats WHERE RoomID = s.RoomID) AS SeatsAvailable,
        s.Price * COUNT(t.TicketID) AS Revenue
    FROM Screenings s
    LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
    JOIN CinemaRooms cr ON s.RoomID = cr.RoomID
    WHERE s.ScreeningDate >= CURDATE() - INTERVAL 30 DAY
    GROUP BY s.ScreeningID, s.ScreeningTime, cr.RoomID, s.Price
),
AggregatedStats AS (
    SELECT 
        ScreeningTime,
        SUM(TicketsSold) AS TicketSold,
        ROUND(SUM(TicketsSold) / SUM(SeatsAvailable), 2) AS OccupationRate,
        SUM(Revenue) AS Revenue
    FROM ScreeningStats
    GROUP BY ScreeningTime
)
SELECT 
    ScreeningTime,
    TicketSold,
    OccupationRate,
    Revenue
FROM AggregatedStats
ORDER BY ScreeningTime;

-- Screening Performance
CREATE OR REPLACE VIEW screeningtime90 AS
WITH ScreeningStats AS (
    SELECT 
        s.ScreeningID,
        s.ScreeningTime,
        COUNT(t.TicketID) AS TicketsSold,
        cr.RoomID,
        (SELECT COUNT(*) FROM Seats WHERE RoomID = s.RoomID) AS SeatsAvailable,
        s.Price * COUNT(t.TicketID) AS Revenue
    FROM Screenings s
    LEFT JOIN Tickets t ON s.ScreeningID = t.ScreeningID
    JOIN CinemaRooms cr ON s.RoomID = cr.RoomID
    WHERE s.ScreeningDate >= CURDATE() - INTERVAL 90 DAY
    GROUP BY s.ScreeningID, s.ScreeningTime, cr.RoomID, s.Price
),
AggregatedStats AS (
    SELECT 
        ScreeningTime,
        SUM(TicketsSold) AS TicketSold,
        ROUND(SUM(TicketsSold) / SUM(SeatsAvailable), 2) AS OccupationRate,
        SUM(Revenue) AS Revenue
    FROM ScreeningStats
    GROUP BY ScreeningTime
)
SELECT 
    ScreeningTime,
    TicketSold,
    OccupationRate,
    Revenue
FROM AggregatedStats
ORDER BY ScreeningTime;

-- AGE
CREATE OR REPLACE VIEW age AS
SELECT
  CASE
    WHEN TIMESTAMPDIFF(YEAR, DOB, CURDATE()) BETWEEN 0 AND 12 THEN '0-12'
    WHEN TIMESTAMPDIFF(YEAR, DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
    WHEN TIMESTAMPDIFF(YEAR, DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
    WHEN TIMESTAMPDIFF(YEAR, DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
    WHEN TIMESTAMPDIFF(YEAR, DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
    WHEN TIMESTAMPDIFF(YEAR, DOB, CURDATE()) > 60 THEN '60+'
    ELSE 'Unknown'
  END AS AgeRange,
  COUNT(*) AS CustomerCount
FROM Customers
WHERE DOB IS NOT NULL
GROUP BY AgeRange
ORDER BY
  CASE AgeRange
    WHEN '0-12' THEN 1
    WHEN '13-17' THEN 2
    WHEN '18-25' THEN 3
    WHEN '26-40' THEN 4
    WHEN '41-60' THEN 5
    WHEN '60+' THEN 6
    ELSE 7
  END;

-- AGE
CREATE OR REPLACE VIEW age90 AS
SELECT
  CASE
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 0 AND 12 THEN '0-12'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) > 60 THEN '60+'
    ELSE 'Unknown'
  END AS AgeRange,
  COUNT(DISTINCT c.CustomerID) AS CustomerCount
FROM Customers c
JOIN Payments p ON c.CustomerID = p.CustomerID
WHERE c.DOB IS NOT NULL
  AND p.PayTime >= CURDATE() - INTERVAL 90 DAY
GROUP BY AgeRange
ORDER BY
  CASE AgeRange
    WHEN '0-12' THEN 1
    WHEN '13-17' THEN 2
    WHEN '18-25' THEN 3
    WHEN '26-40' THEN 4
    WHEN '41-60' THEN 5
    WHEN '60+' THEN 6
    ELSE 7
  END;
  
  -- AGE
CREATE OR REPLACE VIEW ageyear AS
SELECT
  CASE
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 0 AND 12 THEN '0-12'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
    WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) > 60 THEN '60+'
    ELSE 'Unknown'
  END AS AgeRange,
  COUNT(DISTINCT c.CustomerID) AS CustomerCount
FROM Customers c
JOIN Payments p ON c.CustomerID = p.CustomerID
WHERE c.DOB IS NOT NULL
  AND p.PayTime >= CURDATE() - INTERVAL 365 DAY
GROUP BY AgeRange
ORDER BY
  CASE AgeRange
    WHEN '0-12' THEN 1
    WHEN '13-17' THEN 2
    WHEN '18-25' THEN 3
    WHEN '26-40' THEN 4
    WHEN '41-60' THEN 5
    WHEN '60+' THEN 6
    ELSE 7
  END;
  
-- age 13-17
CREATE OR REPLACE VIEW age17 AS
SELECT m.Genre, COUNT(*) AS TicketsSold
FROM Tickets t
JOIN Customers c ON t.CustomerID = c.CustomerID
JOIN Screenings s ON t.ScreeningID = s.ScreeningID
JOIN Movies m ON s.MovieID = m.MovieID
WHERE TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17
GROUP BY m.Genre
ORDER BY TicketsSold DESC;

-- age 18-25
CREATE OR REPLACE VIEW age25 AS
SELECT m.Genre, COUNT(*) AS TicketsSold
FROM Tickets t
JOIN Customers c ON t.CustomerID = c.CustomerID
JOIN Screenings s ON t.ScreeningID = s.ScreeningID
JOIN Movies m ON s.MovieID = m.MovieID
WHERE TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25
GROUP BY m.Genre
ORDER BY TicketsSold DESC;

-- age 26-40
CREATE OR REPLACE VIEW age40 AS
SELECT m.Genre, COUNT(*) AS TicketsSold
FROM Tickets t
JOIN Customers c ON t.CustomerID = c.CustomerID
JOIN Screenings s ON t.ScreeningID = s.ScreeningID
JOIN Movies m ON s.MovieID = m.MovieID
WHERE TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40
GROUP BY m.Genre
ORDER BY TicketsSold DESC;

-- age 41-60
CREATE OR REPLACE VIEW age60 AS
SELECT m.Genre, COUNT(*) AS TicketsSold
FROM Tickets t
JOIN Customers c ON t.CustomerID = c.CustomerID
JOIN Screenings s ON t.ScreeningID = s.ScreeningID
JOIN Movies m ON s.MovieID = m.MovieID
WHERE TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60
GROUP BY m.Genre
ORDER BY TicketsSold DESC;

-- age 60+
CREATE OR REPLACE VIEW ageabove60 AS
SELECT m.Genre, COUNT(*) AS TicketsSold
FROM Tickets t
JOIN Customers c ON t.CustomerID = c.CustomerID
JOIN Screenings s ON t.ScreeningID = s.ScreeningID
JOIN Movies m ON s.MovieID = m.MovieID
WHERE TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) > 60
GROUP BY m.Genre
ORDER BY TicketsSold DESC;

-- genre-screening
CREATE OR REPLACE VIEW genre_screening AS
SELECT m.Genre, COUNT(*) AS TotalScreenings
FROM Screenings s
JOIN Movies m ON s.MovieID = m.MovieID
GROUP BY m.Genre
ORDER BY Genre;

-- Age-time
CREATE OR REPLACE VIEW age_time_30 AS
WITH AgeGroups AS (
  SELECT '13-17' AS AgeGroup
  UNION SELECT '18-25'
  UNION SELECT '26-40'
  UNION SELECT '41-60'
  UNION SELECT '60+'
),
AllTimes AS (
  SELECT DISTINCT ScreeningTime 
  FROM Screenings
  WHERE ScreeningDate >= CURDATE() - INTERVAL 30 DAY
),
AllCombinations AS (
  SELECT ag.AgeGroup, at.ScreeningTime
  FROM AgeGroups ag
  CROSS JOIN AllTimes at
),
TicketCounts AS (
  SELECT
    CASE
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+'
    END AS AgeGroup,
    s.ScreeningTime,
    COUNT(*) AS TicketsSold
  FROM Tickets t
  JOIN Customers c ON t.CustomerID = c.CustomerID
  JOIN Screenings s ON t.ScreeningID = s.ScreeningID
  WHERE c.DOB IS NOT NULL
    AND s.ScreeningDate >= CURDATE() - INTERVAL 30 DAY
  GROUP BY AgeGroup, s.ScreeningTime
)
SELECT ac.AgeGroup, ac.ScreeningTime, COALESCE(tc.TicketsSold, 0) AS TicketsSold
FROM AllCombinations ac
LEFT JOIN TicketCounts tc
  ON ac.AgeGroup = tc.AgeGroup AND ac.ScreeningTime = tc.ScreeningTime
ORDER BY ac.AgeGroup, ac.ScreeningTime;

-- Age-time
CREATE OR REPLACE VIEW age_time_90 AS
WITH AgeGroups AS (
  SELECT '13-17' AS AgeGroup
  UNION SELECT '18-25'
  UNION SELECT '26-40'
  UNION SELECT '41-60'
  UNION SELECT '60+'
),
AllTimes AS (
  SELECT DISTINCT ScreeningTime 
  FROM Screenings
  WHERE ScreeningDate >= CURDATE() - INTERVAL 90 DAY
),
AllCombinations AS (
  SELECT ag.AgeGroup, at.ScreeningTime
  FROM AgeGroups ag
  CROSS JOIN AllTimes at
),
TicketCounts AS (
  SELECT
    CASE
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+'
    END AS AgeGroup,
    s.ScreeningTime,
    COUNT(*) AS TicketsSold
  FROM Tickets t
  JOIN Customers c ON t.CustomerID = c.CustomerID
  JOIN Screenings s ON t.ScreeningID = s.ScreeningID
  WHERE c.DOB IS NOT NULL
    AND s.ScreeningDate >= CURDATE() - INTERVAL 90 DAY
  GROUP BY AgeGroup, s.ScreeningTime
)
SELECT ac.AgeGroup, ac.ScreeningTime, COALESCE(tc.TicketsSold, 0) AS TicketsSold
FROM AllCombinations ac
LEFT JOIN TicketCounts tc
  ON ac.AgeGroup = tc.AgeGroup AND ac.ScreeningTime = tc.ScreeningTime
ORDER BY ac.AgeGroup, ac.ScreeningTime;

-- Age-time
CREATE OR REPLACE VIEW age_time_year AS
WITH AgeGroups AS (
  SELECT '13-17' AS AgeGroup
  UNION SELECT '18-25'
  UNION SELECT '26-40'
  UNION SELECT '41-60'
  UNION SELECT '60+'
),
AllTimes AS (
  SELECT DISTINCT ScreeningTime 
  FROM Screenings
  WHERE ScreeningDate >= CURDATE() - INTERVAL 365 DAY
),
AllCombinations AS (
  SELECT ag.AgeGroup, at.ScreeningTime
  FROM AgeGroups ag
  CROSS JOIN AllTimes at
),
TicketCounts AS (
  SELECT
    CASE
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+'
    END AS AgeGroup,
    s.ScreeningTime,
    COUNT(*) AS TicketsSold
  FROM Tickets t
  JOIN Customers c ON t.CustomerID = c.CustomerID
  JOIN Screenings s ON t.ScreeningID = s.ScreeningID
  WHERE c.DOB IS NOT NULL
    AND s.ScreeningDate >= CURDATE() - INTERVAL 365 DAY
  GROUP BY AgeGroup, s.ScreeningTime
)
SELECT ac.AgeGroup, ac.ScreeningTime, COALESCE(tc.TicketsSold, 0) AS TicketsSold
FROM AllCombinations ac
LEFT JOIN TicketCounts tc
  ON ac.AgeGroup = tc.AgeGroup AND ac.ScreeningTime = tc.ScreeningTime
ORDER BY ac.AgeGroup, ac.ScreeningTime;


-- Age-time
CREATE OR REPLACE VIEW age_time_all AS
WITH AgeGroups AS (
  SELECT '13-17' AS AgeGroup
  UNION SELECT '18-25'
  UNION SELECT '26-40'
  UNION SELECT '41-60'
  UNION SELECT '60+'
),
AllTimes AS (
  SELECT DISTINCT ScreeningTime 
  FROM Screenings
),
AllCombinations AS (
  SELECT ag.AgeGroup, at.ScreeningTime
  FROM AgeGroups ag
  CROSS JOIN AllTimes at
),
TicketCounts AS (
  SELECT
    CASE
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+'
    END AS AgeGroup,
    s.ScreeningTime,
    COUNT(*) AS TicketsSold
  FROM Tickets t
  JOIN Customers c ON t.CustomerID = c.CustomerID
  JOIN Screenings s ON t.ScreeningID = s.ScreeningID
  WHERE c.DOB IS NOT NULL
  GROUP BY AgeGroup, s.ScreeningTime
)
SELECT ac.AgeGroup, ac.ScreeningTime, COALESCE(tc.TicketsSold, 0) AS TicketsSold
FROM AllCombinations ac
LEFT JOIN TicketCounts tc
  ON ac.AgeGroup = tc.AgeGroup AND ac.ScreeningTime = tc.ScreeningTime
ORDER BY ac.AgeGroup, ac.ScreeningTime;

-- Age-Format
CREATE OR REPLACE VIEW age_format_30 AS
WITH AgeGroups AS (
  SELECT '13-17' AS AgeGroup, 13 AS AgeMin, 17 AS AgeMax
  UNION ALL SELECT '18-25', 18, 25
  UNION ALL SELECT '26-40', 26, 40
  UNION ALL SELECT '41-60', 41, 60
  UNION ALL SELECT '60+', 61, 200
),
Formats AS (
  SELECT DISTINCT MovieFormat FROM Screenings
),
Sales AS (
  SELECT
    CASE
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+'
    END AS AgeGroup,
    s.MovieFormat,
    COUNT(*) AS TicketsSold
  FROM Tickets t
  JOIN Customers c ON t.CustomerID = c.CustomerID
  JOIN Screenings s ON t.ScreeningID = s.ScreeningID
  WHERE c.DOB IS NOT NULL
    AND s.ScreeningDate >= CURDATE() - INTERVAL 30 DAY
  GROUP BY AgeGroup, s.MovieFormat
)
SELECT 
  a.AgeGroup,
  f.MovieFormat,
  COALESCE(s.TicketsSold, 0) AS TicketsSold
FROM AgeGroups a
CROSS JOIN Formats f
LEFT JOIN Sales s ON s.AgeGroup = a.AgeGroup AND s.MovieFormat = f.MovieFormat
ORDER BY a.AgeMin, f.MovieFormat;

-- Age-Format
CREATE OR REPLACE VIEW age_format_90 AS
WITH AgeGroups AS (
  SELECT '13-17' AS AgeGroup, 13 AS AgeMin, 17 AS AgeMax
  UNION ALL SELECT '18-25', 18, 25
  UNION ALL SELECT '26-40', 26, 40
  UNION ALL SELECT '41-60', 41, 60
  UNION ALL SELECT '60+', 61, 200
),
Formats AS (
  SELECT DISTINCT MovieFormat FROM Screenings
),
Sales AS (
  SELECT
    CASE
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+'
    END AS AgeGroup,
    s.MovieFormat,
    COUNT(*) AS TicketsSold
  FROM Tickets t
  JOIN Customers c ON t.CustomerID = c.CustomerID
  JOIN Screenings s ON t.ScreeningID = s.ScreeningID
  WHERE c.DOB IS NOT NULL
    AND s.ScreeningDate >= CURDATE() - INTERVAL 90 DAY
  GROUP BY AgeGroup, s.MovieFormat
)
SELECT 
  a.AgeGroup,
  f.MovieFormat,
  COALESCE(s.TicketsSold, 0) AS TicketsSold
FROM AgeGroups a
CROSS JOIN Formats f
LEFT JOIN Sales s ON s.AgeGroup = a.AgeGroup AND s.MovieFormat = f.MovieFormat
ORDER BY a.AgeMin, f.MovieFormat;

-- Age-Format
CREATE OR REPLACE VIEW age_format_year AS
WITH AgeGroups AS (
  SELECT '13-17' AS AgeGroup, 13 AS AgeMin, 17 AS AgeMax
  UNION ALL SELECT '18-25', 18, 25
  UNION ALL SELECT '26-40', 26, 40
  UNION ALL SELECT '41-60', 41, 60
  UNION ALL SELECT '60+', 61, 200
),
Formats AS (
  SELECT DISTINCT MovieFormat FROM Screenings
),
Sales AS (
  SELECT
    CASE
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+'
    END AS AgeGroup,
    s.MovieFormat,
    COUNT(*) AS TicketsSold
  FROM Tickets t
  JOIN Customers c ON t.CustomerID = c.CustomerID
  JOIN Screenings s ON t.ScreeningID = s.ScreeningID
  WHERE c.DOB IS NOT NULL
    AND s.ScreeningDate >= CURDATE() - INTERVAL 365 DAY
  GROUP BY AgeGroup, s.MovieFormat
)
SELECT 
  a.AgeGroup,
  f.MovieFormat,
  COALESCE(s.TicketsSold, 0) AS TicketsSold
FROM AgeGroups a
CROSS JOIN Formats f
LEFT JOIN Sales s ON s.AgeGroup = a.AgeGroup AND s.MovieFormat = f.MovieFormat
ORDER BY a.AgeMin, f.MovieFormat;

-- Age-Format
CREATE OR REPLACE VIEW age_format_all AS
WITH AgeGroups AS (
  SELECT '13-17' AS AgeGroup, 13 AS AgeMin, 17 AS AgeMax
  UNION ALL SELECT '18-25', 18, 25
  UNION ALL SELECT '26-40', 26, 40
  UNION ALL SELECT '41-60', 41, 60
  UNION ALL SELECT '60+', 61, 200
),
Formats AS (
  SELECT DISTINCT MovieFormat FROM Screenings
),
Sales AS (
  SELECT
    CASE
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 13 AND 17 THEN '13-17'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 18 AND 25 THEN '18-25'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 26 AND 40 THEN '26-40'
      WHEN TIMESTAMPDIFF(YEAR, c.DOB, CURDATE()) BETWEEN 41 AND 60 THEN '41-60'
      ELSE '60+'
    END AS AgeGroup,
    s.MovieFormat,
    COUNT(*) AS TicketsSold
  FROM Tickets t
  JOIN Customers c ON t.CustomerID = c.CustomerID
  JOIN Screenings s ON t.ScreeningID = s.ScreeningID
  WHERE c.DOB IS NOT NULL
  GROUP BY AgeGroup, s.MovieFormat
)
SELECT 
  a.AgeGroup,
  f.MovieFormat,
  COALESCE(s.TicketsSold, 0) AS TicketsSold
FROM AgeGroups a
CROSS JOIN Formats f
LEFT JOIN Sales s ON s.AgeGroup = a.AgeGroup AND s.MovieFormat = f.MovieFormat
ORDER BY a.AgeMin, f.MovieFormat;

-- Format-Performance
CREATE OR REPLACE VIEW genre_format_30 AS
SELECT 
    m.Genre AS MovieGenre,
    s.MovieFormat,
    COUNT(t.TicketID) AS TotalTicketsSold,
    IFNULL(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    Movies m
JOIN 
    Screenings s ON m.MovieID = s.MovieID
JOIN 
    Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN 
    Payments p ON t.TicketID = p.TicketID
WHERE 
    p.PayTime >= NOW() - INTERVAL 30 DAY
GROUP BY 
    m.Genre, s.MovieFormat
ORDER BY 
    MovieFormat;
    
-- Format-Performance
CREATE OR REPLACE VIEW genre_format_30 AS
SELECT 
    m.Genre AS MovieGenre,
    s.MovieFormat,
    COUNT(t.TicketID) AS TotalTicketsSold,
    IFNULL(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    Movies m
JOIN 
    Screenings s ON m.MovieID = s.MovieID
JOIN 
    Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN 
    Payments p ON t.TicketID = p.TicketID
WHERE 
    p.PayTime >= NOW() - INTERVAL 30 DAY
GROUP BY 
    m.Genre, s.MovieFormat
ORDER BY 
    MovieFormat;
    
-- Format-Performance
CREATE OR REPLACE VIEW genre_format_90 AS
SELECT 
    m.Genre AS MovieGenre,
    s.MovieFormat,
    COUNT(t.TicketID) AS TotalTicketsSold,
    IFNULL(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    Movies m
JOIN 
    Screenings s ON m.MovieID = s.MovieID
JOIN 
    Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN 
    Payments p ON t.TicketID = p.TicketID
WHERE 
    p.PayTime >= NOW() - INTERVAL 90 DAY
GROUP BY 
    m.Genre, s.MovieFormat
ORDER BY 
    MovieFormat;
    
-- Format-Performance
CREATE OR REPLACE VIEW genre_format_year AS
SELECT 
    m.Genre AS MovieGenre,
    s.MovieFormat,
    COUNT(t.TicketID) AS TotalTicketsSold,
    IFNULL(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    Movies m
JOIN 
    Screenings s ON m.MovieID = s.MovieID
JOIN 
    Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN 
    Payments p ON t.TicketID = p.TicketID
WHERE 
    p.PayTime >= NOW() - INTERVAL 365 DAY
GROUP BY 
    m.Genre, s.MovieFormat
ORDER BY 
    MovieFormat;
    
-- Format-Performance
CREATE OR REPLACE VIEW genre_format_all AS
SELECT 
    m.Genre AS MovieGenre,
    s.MovieFormat,
    COUNT(t.TicketID) AS TotalTicketsSold,
    IFNULL(SUM(p.Amount), 0) AS TotalRevenue
FROM 
    Movies m
JOIN 
    Screenings s ON m.MovieID = s.MovieID
JOIN 
    Tickets t ON s.ScreeningID = t.ScreeningID
LEFT JOIN 
    Payments p ON t.TicketID = p.TicketID
GROUP BY 
    m.Genre, s.MovieFormat
ORDER BY 
    MovieFormat;

