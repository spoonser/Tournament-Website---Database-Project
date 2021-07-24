    cur.execute('''SELECT f.fighterName, f.fighterID, (IFNULL(w.weaponName, 'No Weapon')) as `weapon`  FROM Fighters as f
        LEFT JOIN Weapons as w
        on f.weapon=w.weaponID
        ORDER BY f.fighterName asc;''')
    fighters = cur.fetchall()
    
    return render_template('fighters.html', fighters=fighters) 
    
@app.route('/weapons')
def weapons():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT w.weaponName, w.weaponID, w.weaponType, IF(w.ranged=1, "Yes", "No") as ranged,
        IFNULL(GROUP_CONCAT(f.fighterName), "No Users") as `WeaponUsers`
        FROM Weapons w
        LEFT JOIN Fighters as f 
        ON w.weaponID=f.weapon
        GROUP BY w.weaponID;
		
-- Query for retrieving the 3 Fighters with the most Wins to populate the leaderboard
SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total` FROM 
        (SELECT fighter1 as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1
        UNION 
         SELECT fighter2 as fighterID, COUNT(fightID) as WinCounts  FROM Fights WHERE fighter2Won GROUP BY fighter2) AS Wins
        INNER JOIN Fighters
        ON Wins.fighterID = Fighters.fighterID
        GROUP BY Wins.fighterID
        ORDER BY Wins.WinCount DESC
        LIMIT 3;
    cur.execute('''SELECT one.fightID, one.fightDate, one.fighter1, two.fighter2, IF(one.fighter1Won=1, one.fighter1, IF(one.fighter2Won=1, two.fighter2, "No Winner")) as winner,
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
        ORDER BY one.fightDate desc;;''')
    fights = cur.fetchall()

    return render_template('fights.html', fights=fights)
    
@app.route('/prizes')
def prizes():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT p.prizeID, p.prizeType, IFNULL(f.fighterID, 'No Winners Yet') as fighterID, IFNULL(f.fighterName, 'No Winners Yet') as fighterName
        FROM Prizes as p 
        LEFT JOIN PrizesWon as pw ON p.prizeID=pw.prizeID
        JOIN Fighters as f 
        ON pw.fighterID=f.fighterID;''')