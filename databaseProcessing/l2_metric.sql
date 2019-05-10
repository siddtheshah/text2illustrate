DELIMITER //

CREATE PROCEDURE L2SQ_3 (x1 decimal, y1 decimal, z1 decimal, x2 decimal, y2 decimal, z2 decimal)
RETURNS decimal
DETERMINISTIC
BEGIN
    DECLARE dist decimal;
    SET dist = ((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1) + (z2 - z1)*(z2 - z1));
    RETURN dist;
END

//


DELIMITER //

CREATE PROCEDURE L2SQ_2 (x1 decimal, y1 decimal, x2 decimal, y2 decimal)
RETURNS decimal
DETERMINISTIC
BEGIN
    DECLARE dist decimal;
    SET dist = ((x2 - x1)*(x2 - x1) + (y2 - y1)*(y2 - y1));
    RETURN dist;
END

//

DELIMITER //

CREATE PROCEDURE L2SQ_1 (x1 decimal, z1 decimal)
RETURNS decimal
DETERMINISTIC
BEGIN
    DECLARE dist decimal;
    SET dist = ((x2 - x1)*(x2 - x1));
    RETURN dist;
END

//