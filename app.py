# ***************************************************************************
# * CS 340 Group Project
# * Spencer Wagner and Megan Marshall
# * General server-side code and CRUD queries for the Dark Tournament project
# ***************************************************************************

# Basic Flask functionality, importing modules for parsing results and accessing MySQL. 

from flask import Flask, render_template, json, redirect, url_for
from flask_mysqldb import MySQL
from flask import request

# Using environment variables on Flip to store our DB credentials. 
import os

app = Flask(__name__)
app.config['MYSQL_HOST'] = 'classmysql.engr.oregonstate.edu'
app.config['MYSQL_USER'] = os.environ.get("CS340DBUSER")
app.config['MYSQL_PASSWORD'] = os.environ.get("CS340DBPW")
app.config['MYSQL_DB'] = os.environ.get("CS340DB")
app.config['MYSQL_CURSORCLASS'] = 'DictCursor'

mysql = MySQL(app)
 
# -------------------------------------------------------------------------------------------------
# Main Index page 
# -------------------------------------------------------------------------------------------------
@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')   
    
# -------------------------------------------------------------------------------------------------
# Fighters Page - SELECT all Fighters
# -------------------------------------------------------------------------------------------------
@app.route('/fighters')
def fighters():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT f.fighterName, f.fighterID, (IFNULL(w.weaponName, 'No Weapon')) as `weapon`  FROM Fighters as f
        LEFT JOIN Weapons as w
        on f.weaponID=w.weaponID
        ORDER BY f.fighterName asc;''')
    fighters = cur.fetchall()
    # Get the weapon names to populate the available Weapon choices when creating a new Fighter.
    cur.execute('''SELECT weaponName, weaponID from Weapons''')
    available_weapons = cur.fetchall()
    
    return render_template('fighters.html', fighters=fighters, available_weapons=available_weapons) 

# -------------------------------------------------------------------------------------------------
# Fighters Page - INSERT new Fighters
# -------------------------------------------------------------------------------------------------
@app.route('/fighters', methods=['POST'])
def create_fighter():
    if request.form.get('new-fighter'):
        fighterName = request.form.get('fighter-name') or None
        weapon = request.form.get('fighter-weapon') or None
        try:
            con = mysql.connect
            cur = con.cursor()
            cur.execute('''INSERT INTO Fighters (fighterName, weaponID) 
                VALUES (%s, %s);''', (fighterName, weapon))
            con.commit()

            return fighters()

        except:
            print(fighterName, weapon)
            print("Fighter Insert Failed")
    
    elif request.form.get('fighter-update'):
        fighterID = request.form.get('fighter-id') or None
        
        if fighterID:
            return redirect(url_for('.update_fighter_page', fighterID=fighterID))
       
        else:
            print("No fighter ID entered")
        
    return fighters()


# -------------------------------------------------------------------------------------------------
# Fighters Page - UPDATE a single Fighters
# -------------------------------------------------------------------------------------------------
@app.route('/update-fighter')
def update_fighter_page():
    fighterID = request.args['fighterID']
    cur = mysql.connection.cursor()
    cur.execute('''SELECT f.fighterName, f.fighterID, (IFNULL(w.weaponName, 'No Weapon')) as `weapon`, w.weaponID  FROM Fighters as f
        LEFT JOIN Weapons as w
        on f.weaponID=w.weaponID
        WHERE fighterID=%s;''', (fighterID,))
    fighters = cur.fetchall()

    # Get the weapon names to populate the available Weapon choices when creating a new Fighter.
    cur.execute('''SELECT weaponName, weaponID from Weapons''')
    available_weapons = cur.fetchall()

    return render_template('update/update-fighter.html', fighters=fighters, available_weapons=available_weapons)

@app.route('/update-fighter', methods=['POST'])
def update_fighter():
    con = mysql.connect
    cur = con.cursor()

    fighterID = request.args.get('fighterID', default=1, type=int)
    fighterName = request.form.get('fighter-name') or None
    weapon = request.form.get('fighter-weapon') or None

    try:
        cur.execute('''UPDATE Fighters SET fighterName=%s, weaponID=%s WHERE fighterID=%s;''', (fighterName, weapon, fighterID))
        con.commit()

    except:
        print(fighterID, fighterName, weapon)
        print("Fighter Update Failed")

    return redirect(url_for('.fighters'))

# -------------------------------------------------------------------------------------------------
# Weapons Page - SELECT all Weapons
# -------------------------------------------------------------------------------------------------
@app.route('/weapons')
def weapons():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT w.weaponName, w.weaponID, w.weaponType, IF(w.ranged=1, "Yes", "No") as ranged,
        COUNT(f.fighterName)  as `WeaponUsers`
        FROM Weapons w
        LEFT JOIN Fighters as f 
        ON w.weaponID=f.weaponID
        GROUP BY w.weaponID;''')
    weapons = cur.fetchall()

    return render_template('weapons.html', weapons=weapons)

# -------------------------------------------------------------------------------------------------
# Weapons Page - INSERT or DELETE a Weapon
# -------------------------------------------------------------------------------------------------
@app.route('/weapons', methods=['POST'])
def modify_weapon():
    if request.form.get('new-weapon'):
        weaponName = request.form.get('weapon-name') or None
        weaponType = request.form.get('weapon-type') or None
        ranged = request.form.get('weapon-ranged')

        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''INSERT INTO Weapons (weaponName, weaponType, ranged) 
                VALUES (%s, %s, %s);''', (weaponName, weaponType, ranged))
            con.commit()
            
        except:
            print("Insert Failed")
    
    elif request.form.get('weapon-update'):
        weaponID = request.form.get('weapon-id') or None

        if weaponID:
            return redirect(url_for('.update_weapon_page', weaponID=weaponID))

        else:
            print("No weapon selected")

    elif request.form.get('weapon-delete-id'):
        weaponID = request.form.get('weapon-delete-id') or None

        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''DELETE FROM Weapons WHERE weaponID=%s;''', (weaponID,))
            con.commit()

        except:
            print("Weapon - Delete Failed")
                    
    return weapons()


# -------------------------------------------------------------------------------------------------
# Weapons Page - UPDATE a single Weapon
# -------------------------------------------------------------------------------------------------
@app.route('/update-weapon')
def update_weapon_page():
    weaponID = request.args['weaponID']
    cur = mysql.connection.cursor()

    cur.execute('''SELECT w.weaponName, w.weaponID, w.weaponType, IF(w.ranged=1, "Yes", "No") as ranged,
        IFNULL(GROUP_CONCAT(f.fighterName), "No Users") as `WeaponUsers`
        FROM Weapons w
        LEFT JOIN Fighters as f 
        ON w.weaponID=f.weaponID
        WHERE w.weaponID=%s;''', (weaponID,))
    weapons = cur.fetchall()

    return render_template('update/update-weapon.html', weapons=weapons)
    
@app.route('/update-weapon', methods=['POST'])
def update_weapon():
    weaponID = request.args['weaponID']
    weaponName = request.form.get('weapon-name') or None
    weaponType = request.form.get('weapon-type') or None
    ranged = request.form.get('weapon-ranged')

    try:
        con = mysql.connection
        cur = con.cursor()
        cur.execute('''UPDATE Weapons SET weaponName=%s, weaponType=%s, ranged=%s WHERE weaponID=%s''', (weaponName, weaponType, ranged, weaponID))
        con.commit()
        
    except:
        print("Weapon Update Failed")
    
    return redirect(url_for('.weapons'))

# -------------------------------------------------------------------------------------------------
# Results Page - Leaderboard of Fighters with the most wins
# -------------------------------------------------------------------------------------------------
@app.route('/results')
def results():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total` FROM 
        (SELECT fighter1ID as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1ID
        UNION 
         SELECT fighter2ID as fighterID, COUNT(fightID) as WinCounts  FROM Fights WHERE fighter2Won GROUP BY fighter2ID) AS Wins
        INNER JOIN Fighters
        ON Wins.fighterID = Fighters.fighterID
        GROUP BY Wins.fighterID
        ORDER BY Wins.WinCount DESC
        LIMIT 3;''')
    leaders = cur.fetchall()
    return render_template('results.html', leaders=leaders)

# -------------------------------------------------------------------------------------------------
# Results Page - Leaderboard of Fighters with the most wins, filtered Prizes for a single Fighter
# -------------------------------------------------------------------------------------------------    
@app.route('/results', methods=['POST'])
def filtered_results():
    fighterName = request.form.get('fighterName') or None
    con = mysql.connection
    cur = con.cursor()
 
    # Query to generate the leaderboard, or the 3 Fighters with the most wins. 
    cur.execute('''SELECT Fighters.fighterName, SUM(Wins.WinCount) as `Total` FROM 
        (SELECT fighter1ID as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1ID
        UNION 
         SELECT fighter2ID as fighterID, COUNT(fightID) as WinCount  FROM Fights WHERE fighter2Won GROUP BY fighter2ID) AS Wins
        INNER JOIN Fighters
        ON Wins.fighterID = Fighters.fighterID
        GROUP BY Wins.fighterID
        ORDER BY Wins.WinCount DESC
        LIMIT 3;''')
    leaders = cur.fetchall()

    # Query to generate the win results for a single Fighter, filtered by name. 
    cur.execute('''SELECT Fighters.fighterName, IFNULL(SUM(Wins.WinCount), 0) as `Total` FROM 
		Fighters LEFT JOIN 
        (SELECT fighter1ID as fighterID, COUNT(fightID) as WinCount FROM Fights WHERE fighter1Won GROUP BY fighter1ID
        UNION 
         SELECT fighter2ID as fighterID, COUNT(fightID) as WinCount  FROM Fights WHERE fighter2Won GROUP BY fighter2ID) AS Wins
        
        ON Wins.fighterID = Fighters.fighterID
        WHERE Fighters.fighterName = %s
        GROUP BY Wins.fighterID;''', (fighterName,))
    individual = cur.fetchall()
       
    # Query to generate the prize results for a single Fighter, filtered by name. 
    cur.execute('''SELECT IFNULL(p.prizeType, 'No Prizes Won') as prizeType, f.fighterName
        FROM Fighters as f
        LEFT JOIN PrizesWon as pw ON f.fighterID=pw.fighterID
        LEFT JOIN Prizes as p 
        ON pw.prizeID=p.prizeID
        WHERE f.fighterName = %s;''', (fighterName,))
    prizesWon = cur.fetchall()
    
    return render_template('results.html', leaders=leaders, individual=individual, prizesWon=prizesWon)

      

# -------------------------------------------------------------------------------------------------
# Fights Page - SELECT all Fights
# -------------------------------------------------------------------------------------------------
@app.route('/fights')
def fightsetup(error=None):
    cur = mysql.connection.cursor()
    cur.execute('''SELECT one.fightID, one.fightDate, one.fighter1, two.fighter2, IF(one.fighter1Won=1, one.fighter1, IF(one.fighter2Won=1, two.fighter2, "No Winner")) as winner,
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
        ORDER BY one.fightDate desc;''')
    fights = cur.fetchall()
    cur.execute('''SELECT fightID from Fights ORDER BY fightID asc;''')
    fightIDs = cur.fetchall()
    cur.execute('''SELECT fighterName, fighterID from Fighters ORDER BY fighterName asc;''')
    available_fighters=cur.fetchall()
    cur.execute('''SELECT prizeID, prizeType from Prizes;''')
    available_prizes=cur.fetchall()

    return render_template('fights.html', fights=fights, available_fighters=available_fighters, available_prizes=available_prizes, fightIDs=fightIDs, error=error)
 
# -------------------------------------------------------------------------------------------------
# Fights Page - INSERT a new Fight and its associated PrizesWon if any. Filter Fights by fightDate(s)
# ------------------------------------------------------------------------------------------------- 
@app.route('/fights', methods=['POST'])
def create_fight():
    error=None
    if request.form.get('fight-update'):
        fightID = request.form.get('old-fight-id') or None

        if fightID:
            return redirect(url_for('.update_fight_page', fightID=fightID))
        
        else:
            print("Fight ID required for update")
        
    elif request.form.get('fight-insert'):
        fighter1 = request.form.get('fighter1-id') or None
        fighter2 = request.form.get('fighter2-id') or None
        result = request.form.get('fight-winner') or None
            
        prize = request.form.get('prize-id') or None
        fightDate = request.form.get('fight-date') or None
        
        fighter1Won = 0
        fighter2Won = 0
        prizeFighterID = None
        
        if result == 'fighter1-won': 
            fighter1Won = 1
            fighter2Won = 0
            prizeFighterID = fighter1

        elif result == 'fighter2-won': 
            fighter1Won = 0
            fighter2Won = 1
            prizeFighterID = fighter2
        # Fights require two distinct Fighters.
        if fighter1 == fighter2:
            error = 'Fights must be between two different Fighters. Try again.'
        if fightDate is None:
            error = 'Fight Date is a required field. Try again.'
     
        
        else:
            try:
                con = mysql.connection
                cur = con.cursor()
                cur.execute('''INSERT INTO Fights (fighter1ID, fighter2ID, prizeID, fightDate, fighter1Won, fighter2Won) 
                    VALUES (%s, %s, %s, %s, %s, %s);''', (fighter1, fighter2, prize, fightDate, fighter1Won, fighter2Won))
                con.commit()
                
                if prize is not None:
                    cur.execute('''INSERT INTO PrizesWon (fighterID, prizeID) VALUES (%s, %s);''', (prizeFighterID, prize))
                    con.commit()

            except:
                print(fighter1, fighter2, fighter1Won, fighter2Won, fightDate, prize, prizeFighterID)
                print('Insert Failed')
        
    elif request.form.get('fight-filter'):
        startDate = request.form.get('start-date') or None
        endDate = request.form.get('end-date') or None

        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''SELECT one.fightID, one.fightDate, one.fighter1, two.fighter2, IF(one.fighter1Won=1, one.fighter1, IF(one.fighter2Won=1, two.fighter2, "No Winner")) as winner,
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
                ORDER BY one.fightDate desc;''', (startDate, startDate, endDate, endDate))
                
                
            fights = cur.fetchall()
            
            cur.execute('''SELECT fightID from Fights WHERE (fightDate >= %s OR %s IS NULL) AND (fightDate <= %s OR %s IS NULL) ORDER BY fightID asc;''', (startDate, startDate, endDate, endDate))
            fightIDs = cur.fetchall()
            cur.execute('''SELECT fighterName, fighterID from Fighters ORDER BY fighterName asc;''')
            available_fighters=cur.fetchall()
            cur.execute('''SELECT prizeID, prizeType from Prizes;''')
            available_prizes=cur.fetchall()
            return render_template('fights.html', fights=fights, available_fighters=available_fighters, available_prizes=available_prizes, fightIDs=fightIDs, error=error, filtered=1)
        except:
            print('Fight Filter Failed')
    
    elif request.form.get('clear-fight-filter'):
        pass
    return fightsetup(error=error)


# -------------------------------------------------------------------------------------------------
# Fights Page - UPDATE a single Fight
# -------------------------------------------------------------------------------------------------
@app.route('/update-fight')
def update_fight_page(error=None):
    fightID = request.args['fightID']
    cur = mysql.connection.cursor()
    cur.execute('''SELECT one.fightID, one.fightDate, one.fighter1, two.fighter2, IF(one.fighter1Won=1, one.fighter1, IF(one.fighter2Won=1, two.fighter2, "No Winner")) as winner,
        IFNULL(Prizes.prizeType, "No Prize") as prizeType, one.prizeID, one.fighter1Won, one.fighter2Won FROM
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
        AND one.fightID=%s;''', (fightID,))
    fights = cur.fetchall()
    cur.execute('''SELECT fightID from Fights ORDER BY fightID asc;''')
    fightIDs = cur.fetchall()
    cur.execute('''SELECT fighterName, fighterID from Fighters ORDER BY fighterName asc;''')
    available_fighters=cur.fetchall()
    cur.execute('''SELECT prizeID, prizeType from Prizes;''')
    available_prizes=cur.fetchall()
    return render_template('update/update-fight.html', fights=fights, available_fighters=available_fighters, available_prizes=available_prizes, fightIDs=fightIDs, error=error)

@app.route('/update-fight', methods=['POST'])
def update_fight():
    fightID = request.args['fightID']
    con = mysql.connection
    cur = con.cursor()

    # If the fightDate and prizeWon weren't assigned, stay with the current values in the database.
    cur.execute('''SELECT fightDate, fighter1ID, fighter2ID, fighter1Won, fighter2Won, prizeID FROM Fights WHERE fightID = %s;''', (fightID,))
    originalFightDetails = cur.fetchone()
    fightDate = request.form.get('new-fight-date') or originalFightDetails['fightDate']
    prizeID = request.form.get('new-prize-id') or originalFightDetails['prizeID']
    originalPrizeID = originalFightDetails['prizeID']
    fighter1 = originalFightDetails['fighter1ID']
    originalWinner = 0
    originalWinnerID = 0
    fighter2 = originalFightDetails['fighter2ID']
    result = request.form.get('fight-winner') or None
    

    fighter1Won = 0
    fighter2Won = 0
    prizeFighterID = None

    # Store the original winner -- if this changes, we may need to update PrizesWon.
    if originalFightDetails['fighter1Won'] == 1:
        originalWinner = 'fighter1-won'
        originalWinnerID = originalFightDetails['fighter1ID']
        
    elif originalFightDetails['fighter2Won'] == 1:
        originalWinner = 'fighter2-won'
        originalWinnerID = originalFightDetails['fighter2ID']
    

    # Set the fighterWon flags according to the user's input.
    if result == 'fighter1-won': 
        fighter1Won = 1
        fighter2Won = 0
        prizeFighterID = fighter1

    elif result == 'fighter2-won': 
        fighter1Won = 0
        fighter2Won = 1
        prizeFighterID = fighter2

    try:
        cur.execute('''UPDATE Fights SET fightDate = %s, fighter1Won = %s, fighter2Won = %s, prizeID = %s WHERE fightID = %s;''', (fightDate, fighter1Won, fighter2Won, 
        prizeID, fightID))
        con.commit()
        
        if result == originalWinner and prizeID != originalPrizeID and originalPrizeID is not None:
            # Prize has changed, and the old PrizesWon entry should be removed.
            cur.execute('''DELETE FROM PrizesWon WHERE fighterID = %s AND prizeID = %s;''', (prizeFighterID, originalPrizeID))
            con.commit()
        if result != originalWinner and originalWinnerID != 0 and prizeID == originalPrizeID and originalPrizeID is not None:
            # Fight winner has changed. Previous victor no longer gets the original Prize.
            cur.execute('''DELETE FROM PrizesWon WHERE fighterID = %s and prizeID = %s;''', (originalWinnerID, originalPrizeId))
            con.commit()
        if prizeID is not None:
            # Award the winning Fighter the associated Prize.
            cur.execute('''INSERT INTO PrizesWon (fighterID, prizeID) VALUES (%s, %s);''', (prizeFighterID, prizeID))
            con.commit()
        
        
    except:
        print(fightID, fightDate, fighter1Won, fighter2Won, prizeID)
        print('Fight Update Failed')

    return redirect(url_for('.fightsetup'))

# -------------------------------------------------------------------------------------------------
# Prizes Page - SELECT all Prizes
# -------------------------------------------------------------------------------------------------
@app.route('/prizes')
def prizes():
    cur = mysql.connection.cursor()
    cur.execute('''SELECT p.prizeID, p.prizeType, IFNULL(f.fighterID, 'No Winners Yet') as fighterID, IFNULL(f.fighterName, 'No Winners Yet') as fighterName
        FROM Prizes as p 
        LEFT JOIN PrizesWon as pw ON p.prizeID=pw.prizeID
        JOIN Fighters as f 
        ON pw.fighterID=f.fighterID;''')
    prizesWon = cur.fetchall()

    cur.execute('''SELECT prizeID, prizeType 
        FROM Prizes;''')
    allPrizes=cur.fetchall()
    cur.execute('''SELECT fighterName, fighterID from Fighters''')
    available_fighters=cur.fetchall()
    cur.execute('''SELECT prizeID, prizeType from Prizes''')
    available_prizes=cur.fetchall()
    
    return render_template('prizes.html', allPrizes=allPrizes, prizesWon=prizesWon, available_fighters=available_fighters, available_prizes=available_prizes)

# -------------------------------------------------------------------------------------------------
# Prizes Page - INSERT a new Prize or INSERT a new PrizesWon relationship
# -------------------------------------------------------------------------------------------------
@app.route('/prizes', methods=['POST'])
def create_prize():
    if request.form.get('new-prize'):
        prizeType = request.form.get('prize-type') or None 
        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''INSERT INTO Prizes (prizeType) VALUES(%s);''', (prizeType,))
            # Note to future reader: the trailing comma after the prizeType variable is absolutely required for Python to identify this as a tuple.
            con.commit()

        except:
            print("Prizes - Insert Failed")
    elif request.form.get('prize-won'):
        prizeID = request.form.get('prize-id') 
        fighterID = request.form.get('fighter-id')
        try:
            con = mysql.connection
            
            cur = con.cursor()
            cur.execute('''INSERT INTO PrizesWon (fighterID, prizeID) VALUES (%s, %s);''', (fighterID, prizeID))
            con.commit()

        except:
            print(request.form.to_dict())
            print("PrizesWon - Insert Failed")
    
    elif request.form.get('prize-won-delete'):
        prizeID = eval(request.form.get('prize-won-delete'))[0]
        fighterID = eval(request.form.get('prize-won-delete'))[1] 

        try:
            con = mysql.connection
            cur = con.cursor()
            cur.execute('''DELETE FROM PrizesWon WHERE fighterID=%s and prizeID=%s;''', (fighterID, prizeID))
            con.commit()

        except:
            print(fighterID, prizeID)
            print("PrizesWon - Delete Failed")
                    
    return prizes()
    
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 61557))
    app.run(port=port, debug=True)