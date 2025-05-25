CREATE VIEW revenue_alltime AS
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
    
CREATE VIEW revenue_year AS
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
    

CREATE VIEW revenue_6months AS
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
    

CREATE VIEW revenue_30days AS
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
    

CREATE VIEW ticket_alltime AS
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
    

CREATE VIEW ticket_year AS
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
    

CREATE VIEW ticket_6months AS
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
    
    
CREATE VIEW ticket_30days AS
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