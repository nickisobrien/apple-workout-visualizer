import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import seaborn as sns
from mpl_toolkits.mplot3d import Axes3D
import matplotlib.dates as mdates

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

def average_cycle_speed_with_climb(db_conn):
    df = load_outdoor_cycle_df(db_conn)

    df['elevation_ascended_meters'] = df['elevation_ascended'] / 100
    # Define bins for different ranges of elevation ascended
    bins = [0, 500, 1000, 1500, 2000] # Adjust these values based on your specific data
    labels = ['0-500', '500-1000', '1000-1500', '1500-2000']

    # Create a new column in the DataFrame for the elevation category
    df['elevation_category'] = pd.cut(df['elevation_ascended_meters'], bins=bins, labels=labels)

    df['year'] = df['startdate'].dt.year
    df['month'] = df['startdate'].dt.month

    avg_speed_by_elevation_month = df.groupby(['month', 'elevation_category'])['speed'].mean()

    plt.figure(figsize=(10, 6))

    months = df['month'].sort_values().unique()

    plt.figure(figsize=(10, 6))

    for i, month in enumerate(months):
        avg_speed = avg_speed_by_elevation_month[month]
        plt.bar(np.arange(len(avg_speed)) + i * 0.2, avg_speed, width=0.2, label=str(month))

    plt.xlabel('Elevation Ascended (m)')
    plt.ylabel('Average Speed')
    plt.xticks(ticks=np.arange(len(labels)), labels=labels)  # assuming labels from the previous example
    plt.ylim([df['speed'].min()-1, df['speed'].max() + 1])
    plt.legend(title='Month')
    plt.title('Average Cycling Speed by Elevation Ascended and Month')

    plt.show(block=False)
    plt.pause(1)
    input()
    plt.close()

def plot_swim_speed(db_conn):
    # Convert dates to a format that can be used in a mathematical formula, if not already done
    df = load_swim_df(db_conn)

    df['date_numeric'] = pd.to_datetime(df['startdate']).map(lambda date: date.toordinal())

    # Calculate coefficients for the polynomial (we use a degree 1 polynomial here which is a line)
    coefficients = np.polyfit(df['date_numeric'], df['speed'], 1)

    # Create a range of x values for the dates
    x_values = range(min(df['date_numeric']), max(df['date_numeric']))

    # Calculate the corresponding y values for the trendline
    y_values = [coefficients[0]*x + coefficients[1] for x in x_values]

    plt.figure(figsize=(10,6))

    # Plot the actual data
    plt.plot_date(df['date_numeric'], df['speed'], 'b-', label='Swim')

    # Plot the trendline
    plt.plot_date(x_values, y_values, 'r-', label='Trendline')

    plt.xlabel('Date')
    plt.ylabel('Speed (yards per minute)')
    plt.title('Speed over time for Swim with Trendline')
    plt.legend()

    plt.show(block=False)
    plt.pause(1)
    input()
    plt.close()

def plot_swim_efficiency(db_conn):
    # Convert dates to a format that can be used in a mathematical formula, if not already done
    df = load_swim_df(db_conn)

    df['efficiency'] = df['distance_swimming'] / df['swimming_stroke_count']
    df['date_numeric'] = pd.to_datetime(df['startdate']).map(lambda date: date.toordinal())

    # Calculate coefficients for the polynomial (we use a degree 1 polynomial here which is a line)
    coefficients = np.polyfit(df['date_numeric'], df['efficiency'], 1)

    # Create a range of x values for the dates
    x_values = range(min(df['date_numeric']), max(df['date_numeric']))

    # Calculate the corresponding y values for the trendline
    y_values = [coefficients[0]*x + coefficients[1] for x in x_values]

    plt.figure(figsize=(10,6))

    # Plot the actual data
    plt.plot_date(df['date_numeric'], df['efficiency'], 'b-', label='Swim')

    # Plot the trendline
    plt.plot_date(x_values, y_values, 'r-', label='Trendline')

    plt.xlabel('Date')
    plt.ylabel('Efficiency (yards per stroke)')
    plt.title('Efficiency over time for Swim with Trendline')
    plt.legend()

    plt.show(block=False)
    plt.pause(1)
    input()
    plt.close()

plot_swim_efficiency(db_conn)
