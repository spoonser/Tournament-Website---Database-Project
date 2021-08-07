-- Select all Fighters and their Weapon. If the Fighter has NULL as a Weapon, populates with 'No Weapon' to be more readable.
SELECT f.fighterName, f.fighterID, (IFNULL(w.weaponName, 'No Weapon')) as `weapon`  FROM Fighters as f
        LEFT JOIN Weapons as w
        on f.weaponID=w.weaponID
        ORDER BY f.fighterName asc;

	
-- Select all fighterNames and fighterIDs. Used to populate a dropdown and prevent direct user entry of the fighterID.
SELECT fighterName, fighterID from Fighters
ORDER BY fighterName asc;
	
-- Insert a new Fighter. Parameters are provided by code in the Flask application and are commented out below.
INSERT INTO Fighters (fighterName, weaponID) 
            VALUES (%s, %s);
	--Full syntax: cur.execute('''INSERT INTO Fighters (fighterName, weapon) VALUES (%s, %s);''', (fighterName, weapon))
    
-- -----------------------------------------------------------------------------------------------------------------------	

-- Select all Weapons and their attributes.
SELECT w.weaponName, w.weaponID, w.weaponType, IF(w.ranged=1, "Yes", "No") as ranged,
        COUNT(f.fighterName)  as `WeaponUsers`
        FROM Weapons w
        LEFT JOIN Fighters as f 
        ON w.weaponID=f.weaponID
        GROUP BY w.weaponID;

-- Select weaponIDs and weaponNames. Used to populate a dropdown and prevent direct user entry of the weaponID.
SELECT weaponName, weaponID from Weapons

-- Insert a new Weapon. Parameters are provided by code in the Flask application and are commented out below.
INSERT INTO Weapons (weaponName, weaponType, ranged) 
            VALUES (%s, %s, %s);
	--Full syntax: cur.execute('''INSERT INTO Weapons (weaponName, weaponType, ranged) VALUES (%s, %s, %s);''', (weaponName, weaponType, ranged))

-- Delete a Weapon. Foreign key in the Fighters table is set to SET NULL when this occurs; any Fighter associated with the deleted Weapon will now have no Weapon.
DELETE FROM Weapons WHERE weaponID=%s
-- -----------------------------------------------------------------------------------------------------------------------	

-- Select the 3 Fighters with the most Wins to populate the leaderboard
SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total` FROM 
        (SELECT fighter1ID as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1ID
        UNION 
         SELECT fighter2ID as fighterID, COUNT(fightID) as WinCount  FROM Fights WHERE fighter2Won GROUP BY fighter2ID) AS Wins
        INNER JOIN Fighters
        ON Wins.fighterID = Fighters.fighterID
        GROUP BY Wins.fighterID
        ORDER BY Wins.WinCount DESC
        LIMIT 3;

-- Select/filter Fighters' results by name.
SELECT Fighters.fighterName, IFNULL(SUM(Wins.WinCount), 0) as `Total` FROM 
		Fighters LEFT JOIN 
        (SELECT fighter1ID as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1ID
        UNION 
         SELECT fighter2ID as fighterID, COUNT(fightID) as WinCount  FROM Fights WHERE fighter2Won GROUP BY fighter2ID) AS Wins
        
        ON Wins.fighterID = Fighters.fighterID
        WHERE Fighters.fighterName = %s
        GROUP BY Wins.fighterID;
		
-- Select/filter PrizesWon by Fighter names.
SELECT IFNULL(p.prizeType, 'No Prizes Won') as prizeType, f.fighterName
        FROM Fighters as f
        LEFT JOIN PrizesWon as pw ON f.fighterID=pw.fighterID
        LEFT JOIN Prizes as p 
        ON pw.prizeID=p.prizeID
        WHERE f.fighterName = %s;
		
-- No insert statement here, as the leaderboard is not directly associated with an entity--it's an extra page of reporting.

-- -----------------------------------------------------------------------------------------------------------------------	

-- Select all Fights and their attributes
SELECT one.fightID, one.fightDate, one.fighter1ID, two.fighter2, IF(one.fighter1Won=1, one.fighter1ID, IF(one.fighter2Won=1, two.fighter2ID, "No Winner")) as winner,
        IFNULL(Prizes.prizeType, "No Prize") as prize FROM
        (SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter1, Fights.fighter1Won, Fights.fighter2Won, Fights.prizeID
        FROM Fights
        LEFT JOIN Fighters
        on Fights.fighter1ID=Fighters.fighterID) as one
        JOIN
        (SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter2
        FROM Fights
        LEFT JOIN Fighters
        ON Fights.fighter2ID=Fighters.fighterID) AS two
        LEFT JOIN Prizes 
        ON one.prizeID=Prizes.prizeID
        WHERE one.fightID=two.fightID
        ORDER BY one.fightDate desc

-- Insert a new Fight. Parameters are provided by code in the Flask application and are commented out below.
INSERT INTO Fights (fighter1, fighter2, prizeID, fightDate) 
                VALUES (%s, %s, %s, %s); 
	--Full syntax: cur.execute('''INSERT INTO Fights (fighter1, fighter2, prize, fightDate)  VALUES (%s, %s, %s, %s);''', (fighter1, fighter2, prize, fightDate))	

	
-- Filter Fights by a date range. Parameters are provided by code in the Flask application.
SELECT one.fightID, one.fightDate, one.fighter1ID, two.fighter2ID, IF(one.fighter1Won=1, one.fighter1ID, IF(one.fighter2Won=1, two.fighter2ID, "No Winner")) as winner,
	IFNULL(Prizes.prizeType, "No Prize") as prize FROM
	(SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter1, Fights.fighter1Won, Fights.fighter2Won, Fights.prizeID
	FROM Fights
	LEFT JOIN Fighters
	on Fights.fighter1ID=Fighters.fighterID) as one
	JOIN
	(SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter2
	FROM Fights
	LEFT JOIN Fighters
	ON Fights.fighter2ID=Fighters.fighterID) AS two
	LEFT JOIN Prizes 
	ON one.prizeID=Prizes.prizeID
	WHERE one.fightID=two.fightID
	AND (one.fightDate >= %s OR %s IS NULL)
	AND (one.fightDate <= %s OR %s IS NULL)
	ORDER BY one.fightDate desc;

-- Select all fightIDs. Used to populate a dropdown and prevent direct user entry of the fightID.
SELECT fightID from Fights ORDER BY fightID asc;

-- Select fightIDs from a filtered date range. Used to populate  a dropdown and prevent direct user entry of the fightID, but also allow the user to see a subset of target IDs.
SELECT fightID from Fights WHERE (fightDate >= %s OR %s IS NULL) AND (fightDate <= %s OR %s IS NULL) ORDER BY fightID asc;

-- Select a single Fight's details. Modified version used to support editing a single fight. 
SELECT one.fightID, one.fightDate, one.fighter1ID, two.fighter2ID, IF(one.fighter1Won=1, one.fighter1ID, IF(one.fighter2Won=1, two.fighter2ID, "No Winner")) as winner,
        IFNULL(Prizes.prizeType, "No Prize") as prizeType, one.prize, one.fighter1Won, one.fighter2Won FROM
        (SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter1, Fights.fighter1Won, Fights.fighter2Won, Fights.prizeID
        FROM Fights 
        LEFT JOIN Fighters
        on Fights.fighter1ID=Fighters.fighterID) as one
        JOIN
        (SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter2
        FROM Fights
        LEFT JOIN Fighters
        ON Fights.fighter2ID=Fighters.fighterID) AS two
        LEFT JOIN Prizes 
        ON one.prizeID=Prizes.prizeID
        WHERE one.fightID=two.fightID
        AND one.fightID=%s;

-- Get current values for a given Fight. Used to populate specific variables in case of update issues.
SELECT fightDate FROM Fights WHERE fightID = %s;        
SELECT prizeID FROM Fights WHERE fightID = %s;

-- Update a Fight. Parameters are provided by code in the Flask application and are commented out below.	
UPDATE Fights 
	SET fightDate = %s,
	fighter1Won = %s,
	fighter2Won = %s,
	prizeID = %s
	WHERE fightID = %s;
	--Full syntax: cur.execute('''UPDATE Fights SET fightDate = %s, fighter1Won = %s, fighter2Won = %s, prizeID = %s WHERE fightID = %s;''', (fightDate, fighter1Won, fighter2Won, prizeID, fightID))
-- -----------------------------------------------------------------------------------------------------------------------	

-- Select all Prizes and their attributes
SELECT p.prizeID, p.prizeType, IFNULL(f.fighterID, 'No Winners Yet') as fighterID, IFNULL(f.fighterName, 'No Winners Yet') as fighterName
        FROM Prizes as p 
        LEFT JOIN PrizesWon as pw ON p.prizeID=pw.prizeID
        JOIN Fighters as f 
        ON pw.fighterID=f.fighterID;
		
-- Select all prizeIDs and prizeTypes. Used to populate a dropdown and prevent direct user entry of the prizeID.
SELECT prizeID, prizeType from Prizes;

-- Insert a new Prize. Parameters are provided by code in the Flask application and are commented out below.
INSERT INTO Prizes (prizeType) 
            VALUES (%s);
	--Full syntax:  cur.execute('''INSERT INTO Prizes (prizeType) VALUES (%s);''', (prizeType))
-- Insert a new entry into PrizesWon. Parameters are provided by code in the Flask application and are commented out below.
INSERT INTO PrizesWon (fighterID, prizeID) VALUES (%s, %s);
	--Full syntax: cur.execute('''INSERT INTO PrizesWon (fighterID, prizeID) VALUES (%s, %s);''', (fighterID, prizeID))
	
-- Delete a PrizesWon entry. Parameters are provided by code in the Flask application and are commented out below.
DELETE FROM PrizesWon WHERE fighterID=%s and prizeID=%s;
	--Full syntax: cur.execute('''DELETE FROM PrizesWon WHERE fighterID=%s and prizeID=%s;''', (fighterID, prizeID))
