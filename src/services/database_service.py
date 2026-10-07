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
    connection.commit()
    connection.close()

def save_report(report):
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
    connection.close()

    return ride_id

