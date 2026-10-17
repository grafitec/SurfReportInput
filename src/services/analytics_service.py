import pandas as pd
import matplotlib.pyplot as plt
import sqlite3
import traceback

databasePath = "../data/surfReport.db"



def runAnalytics():
    try:
        #get_rides_per_month()
        #total_fuel_cost()
        #chart = ChartWidget()
        #type_of_surf()
        return chart

    except Exception:
        traceback.print_exc()

def get_rides_per_month():
    conn = sqlite3.connect(databasePath)

    df = pd.read_sql(
        "SELECT * FROM surfReport",
        conn
    )
    print(df)

    return (
        df.groupby("month")
          .size()
    )


def total_fuel_cost():
    conn = sqlite3.connect(databasePath)
    df = pd.read_sql(
        "SELECT * FROM gasReport",
        conn
    )
    print(df["cost"].sum())
    return df["cost"].sum()

def type_of_surf():
    conn = sqlite3.connect(databasePath)

    df = pd.read_sql(
        "SELECT * FROM surfReport",
        conn
    )
    surf_counts = df["surfType"].value_counts()

    plt.pie(
        surf_counts,
        labels=surf_counts.index,
        autopct="%1.1f%%"
    )

    plt.show()