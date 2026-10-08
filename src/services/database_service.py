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

def save_surf_report(report):
    connection = sqlite3.connect(databasePath)
    cursor = connection.cursor()

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

