import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns

def db_get_connection():
    conn = psycopg2.connect(
        dbname='workouts',
        user='postgres',
        password='password',
        host='localhost',
        port='5432'
    )

    return conn

def db_close_connection(conn):
    conn.close()

def db_execute_query(conn, query):
    cur = conn.cursor()
    cur.execute(query)
    return cur

def load_cycle_df(conn):
    cur = db_execute_query(conn, "SELECT * from cycle where startdate >= '2023-01-01'")
    data = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    cur.close()
    df = pd.DataFrame(data, columns=col_names)
    df['startdate'] = pd.to_datetime(df['startdate'])
    df['enddate'] = pd.to_datetime(df['enddate'])
    df['duration_hours'] = df['duration'] / 60  # convert duration from minutes to hours
    df['speed'] = df['distance_cycling'] / df['duration_hours']  # speed = distance/time
    return df

def load_outdoor_cycle_df(conn):
    cur = db_execute_query(conn, "SELECT * from cycle where startdate >= '2023-01-01' and distance_cycling > 1")
    data = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    cur.close()
    df = pd.DataFrame(data, columns=col_names)
    df['startdate'] = pd.to_datetime(df['startdate'])
    df['enddate'] = pd.to_datetime(df['enddate'])
    df['duration_hours'] = df['duration'] / 60  # convert duration from minutes to hours
    df['speed'] = df['distance_cycling'] / df['duration_hours']  # speed = distance/time
    return df

def load_swim_df(conn):
    cur = db_execute_query(conn, "SELECT * from swim where startdate >= '2023-01-01'")
    data = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    cur.close()
    df = pd.DataFrame(data, columns=col_names)
    df['startdate'] = pd.to_datetime(df['startdate'])
    df['enddate'] = pd.to_datetime(df['enddate'])
    df['speed'] = df['distance_swimming'] / df['duration']  # speed = distance/time
    return df

def load_run_df(conn):
    cur = db_execute_query(conn, "SELECT * from run where startdate >= '2023-01-01'")
    data = cur.fetchall()
    col_names = [desc[0] for desc in cur.description]
    cur.close()
    df = pd.DataFrame(data, columns=col_names)
    df['startdate'] = pd.to_datetime(df['startdate'])
    df['enddate'] = pd.to_datetime(df['enddate'])
    df['duration_hours'] = df['duration'] / 60
    df['speed'] = df['distance_walking_running'] / df['duration_hours']  # speed = distance/time
    return df

db_conn = db_get_connection()

def plot_weekly_workout_count(db_conn):
    cycle_df = load_cycle_df(db_conn)
    swim_df = load_swim_df(db_conn)
    run_df = load_run_df(db_conn)

    ## Plotting workout count

    swim_df['week'] = swim_df['startdate'].dt.isocalendar().week
    run_df['week'] = run_df['startdate'].dt.isocalendar().week
    cycle_df['week'] = cycle_df['startdate'].dt.isocalendar().week

    plt.hist([swim_df['week'], run_df['week'], cycle_df['week']], bins=52, stacked=True, label=['Swim', 'Run', 'Cycle'])

    plt.xlabel('Week of the year')
    plt.ylabel('Count')
    plt.title('Number of Workouts per Week')
    plt.legend()

    plt.show(block=False)
    plt.pause(1)
    input()
    plt.close()

def plot_weekly_workout_duration(db_conn):
    cycle_df = load_cycle_df(db_conn)
    swim_df = load_swim_df(db_conn)
    run_df = load_run_df(db_conn)

    swim_df['week'] = swim_df['startdate'].dt.isocalendar().week
    run_df['week'] = run_df['startdate'].dt.isocalendar().week
    cycle_df['week'] = cycle_df['startdate'].dt.isocalendar().week

    plt.hist([swim_df['week'], run_df['week'], cycle_df['week']], bins=52, stacked=True, label=['Swim', 'Run', 'Cycle'], weights=[swim_df['duration'], run_df['duration'], cycle_df['duration']])
    plt.xlabel('Week of the year')
    plt.ylabel('Duration (minutes)')
    plt.title('Workout Duration per Week')
    plt.legend()

    plt.show(block=False)
    plt.pause(1)
    input()
    plt.close()

def plot_cycle_speed(db_conn):
    # Convert dates to a format that can be used in a mathematical formula, if not already done
    df = load_outdoor_cycle_df(db_conn)

    df['date_numeric'] = pd.to_datetime(df['startdate']).map(lambda date: date.toordinal())

    # Calculate coefficients for the polynomial (we use a degree 1 polynomial here which is a line)
    coefficients = np.polyfit(df['date_numeric'], df['speed'], 1)

    # Create a range of x values for the dates
    x_values = range(min(df['date_numeric']), max(df['date_numeric']))

    # Calculate the corresponding y values for the trendline
    y_values = [coefficients[0]*x + coefficients[1] for x in x_values]

    plt.figure(figsize=(10,6))

    # Plot the actual data
    plt.plot_date(df['date_numeric'], df['speed'], 'b-', label='Cycle')

    # Plot the trendline
    plt.plot_date(x_values, y_values, 'r-', label='Trendline')

    plt.xlabel('Date')
    plt.ylabel('Speed')
    plt.title('Speed over time for Cycle with Trendline')
    plt.legend()

    plt.show(block=False)
    plt.pause(1)
    input()
    plt.close()
