-- Select all Fighters and their Weapon. If the Fighter has NULL as a Weapon, populates with 'No Weapon' to be more readable.
SELECT f.fighterName, f.fighterID, (IFNULL(w.weaponName, 'No Weapon')) as `weapon`  FROM Fighters as f
        LEFT JOIN Weapons as w
        on f.weapon=w.weaponID
        ORDER BY f.fighterName asc;
		
-- Insert a new Fighter. Parameters are provided by code in the Flask application and are commented out below.
INSERT INTO Fighters (fighterName, weapon) 
            VALUES (%s, %s);
	--Full syntax: cur.execute('''INSERT INTO Fighters (fighterName, weapon) VALUES (%s, %s);''', (fighterName, weapon))
    
-- -----------------------------------------------------------------------------------------------------------------------	

-- Select all Weapons and their attributes.
SELECT w.weaponName, w.weaponID, w.weaponType, IF(w.ranged=1, "Yes", "No") as ranged,
        IFNULL(GROUP_CONCAT(f.fighterName), "No Users") as `WeaponUsers`
        FROM Weapons w
        LEFT JOIN Fighters as f 
        ON w.weaponID=f.weapon
        GROUP BY w.weaponID;
-- Insert a new Weapon. Parameters are provided by code in the Flask application and are commented out below.
INSERT INTO Weapons (weaponName, weaponType, ranged) 
            VALUES (%s, %s, %s);
	--Full syntax: cur.execute('''INSERT INTO Weapons (weaponName, weaponType, ranged) VALUES (%s, %s, %s);''', (weaponName, weaponType, ranged))
	
-- -----------------------------------------------------------------------------------------------------------------------	

-- Select the 3 Fighters with the most Wins to populate the leaderboard
SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total` FROM 
        (SELECT fighter1 as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1
        UNION 
         SELECT fighter2 as fighterID, COUNT(fightID) as WinCounts  FROM Fights WHERE fighter2Won GROUP BY fighter2) AS Wins
        INNER JOIN Fighters
        ON Wins.fighterID = Fighters.fighterID
        GROUP BY Wins.fighterID
        ORDER BY Wins.WinCount DESC
        LIMIT 3;

-- Select/filter Fighters' results by name.
SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total` FROM 
        (SELECT fighter1 as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1
        UNION 
         SELECT fighter2 as fighterID, COUNT(fightID) as WinCounts  FROM Fights WHERE fighter2Won GROUP BY fighter2) AS Wins
        INNER JOIN Fighters
        ON Wins.fighterID = Fighters.fighterID
        AND Fighters.fighterName = %s
        GROUP BY Wins.fighterID;

-- No insert statement here, as the leaderboard is not directly associated with an entity--it's an extra page of reporting.

-- -----------------------------------------------------------------------------------------------------------------------	

-- Select all Fights and their attributes
SELECT one.fightID, one.fightDate, one.fighter1, two.fighter2, IF(one.fighter1Won=1, one.fighter1, IF(one.fighter2Won=1, two.fighter2, "No Winner")) as winner,
        IFNULL(Prizes.prizeType, "No Prize") as prize FROM
        (SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter1, Fights.fighter1Won, Fights.fighter2Won, Fights.prize
        FROM Fights
        LEFT JOIN Fighters
        on Fights.fighter1=Fighters.fighterID) as one
        JOIN
        (SELECT Fights.fightID, Fights.fightDate, Fighters.fighterName as fighter2
        FROM Fights
        LEFT JOIN Fighters
        ON Fights.fighter2=Fighters.fighterID) AS two
        LEFT JOIN Prizes 
        ON one.prize=Prizes.prizeID
        WHERE one.fightID=two.fightID
        ORDER BY one.fightDate desc

-- Insert a new Fight. Parameters are provided by code in the Flask application and are commented out below.
INSERT INTO Fights (fighter1, fighter2, prize, fightDate) 
                VALUES (%s, %s, %s, %s); 
	--Full syntax: cur.execute('''INSERT INTO Fights (fighter1, fighter2, prize, fightDate)  VALUES (%s, %s, %s, %s);''', (fighter1, fighter2, prize, fightDate))	

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
