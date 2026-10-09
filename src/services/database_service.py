import sqlite3


databasePath = "../data/surfReport.db"

def initiate_database():
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS surfReport (
        rideId INTEGER PRIMARY KEY AUTOINCREMENT,
        rideDate TEXT,
        weather TEXT,
        friends BOOLEAN,
        injuries TEXT,
        temperature TEXT,
        timeOnWater DECIMAL,
        comments TEXT, 
        distance DECIMAL,
        instaLink TEXT,
        ctxPath TEXT,
        surfType TEXT,
        ledLights BOOLEAN,
        startPoint TEXT
        )
    """)

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS surfFriends (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        rideId INTEGER,
        person TEXT
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS gasReport (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        date TEXT,
        liters INTEGER,
        cost INTEGER
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS locations (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        startPoint TEXT,
        longitud DECIMAL,
        latitud DECIMAL
        )
    """)
    connection.commit()
    connection.close()

def save_surf_report(report, surfID):
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    if surfID == 0:
        cursor.execute("""
            INSERT INTO surfReport
            (
                rideDate,
                weather,
                friends,
                injuries,
                temperature,
                timeOnWater,
                comments, 
                distance,
                instaLink,
                ctxPath,
                surfType,
                ledLights,
                startPoint
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            report["date"],
            report["weather"],
            report["friends"],
            report["injuries"],
            report["temperature"],
            report["timeOnWater"],
            report["comments"],
            report["distance"],
            report["instaLink"],
            report["ctxPath"],
            report["surfType"],
            report["ledLights"],
            report["startPoint"]
        ))
        connection.commit()
        ride_id = cursor.lastrowid

        for person in report["friendsName"]:
            cursor.execute("""
                INSERT INTO surfFriends
                (
                    rideId,
                    person
                )
                VALUES (?, ?)
            """,
            (
                ride_id,
                person
            ))
            connection.commit()
    else:
        cursor.execute("""
            UPDATE surfReport
            SET
                rideDate = ?,
                weather = ?,
                friends = ?,
                injuries = ?,
                temperature = ?,
                timeOnWater = ?,
                comments = ?,
                distance = ?,
                instaLink = ?,
                ctxPath = ?,
                surfType = ?,
                ledLights = ?,
                startPoint = ?
            WHERE rideId = ?
        """,
        (
            report["date"],
            report["weather"],
            report["friends"],
            report["injuries"],
            report["temperature"],
            report["timeOnWater"],
            report["comments"],
            report["distance"],
            report["instaLink"],
            report["ctxPath"],
            report["surfType"],
            report["ledLights"],
            report["startPoint"],
            surfID
        ))
        connection.commit()

        cursor.execute("""
            DELETE FROM surfFriends
            WHERE rideId = ?
        """, (surfID,))

        for person in report["friendsName"]:
            cursor.execute("""
                INSERT INTO surfFriends
                (
                    rideId,
                    person
                )
                VALUES (?, ?)
            """,
           (
               surfID,
               person
           ))
            connection.commit()

        ride_id = surfID

    connection.close()

    return ride_id

def save_gas_report(report):
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()

    cursor.execute("""
        INSERT INTO gasReport
        (
            date,
            liters,
            cost
        )
        VALUES (?, ?, ?)
    """,
    (
        report['date'],
        report['liter'],
        report['cost']
    ))
    connection.commit()
    gas_id = cursor.lastrowid
    connection.close()
    return gas_id

def get_surf_report():
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM surfReport
        ORDER BY rideId DESC
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows

def get_gas_report():
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM gasReport
        ORDER BY id DESC
    """)
    rows = cursor.fetchall()
    connection.close()
    return rows

def get_next_id():
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM surfReport
        ORDER BY rideId DESC
    """)
    rows = cursor.fetchall()
    connection.close()
    nextNumber = len(rows)+1
    return nextNumber

def load_ride_from_id(id):
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()
    cursor.execute("""
        SELECT *
        FROM surfReport
        WHERE rideId == %s
    """ %(str(id)))
    currentRow = cursor.fetchone()
    currentRowList = list(currentRow)
    if currentRow[3] == 1:
        cursor.execute("""
            SELECT *
            FROM surfFriends
            WHERE rideId == %s
        """ % (str(id)))
        friendsRow = cursor.fetchall()
        friendsList = []
        for row in friendsRow:
           friendsList.append(row[2])
        currentRowList.append(friendsList)
    connection.close()
    return currentRowList