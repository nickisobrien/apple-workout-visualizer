import psycopg2
from lxml import etree
from datetime import datetime

# Parse the XML file
tree = etree.parse('export.xml')

# Find all 'Workout' elements in the XML
workouts = tree.xpath('//Workout')

# Filter for cycling workouts
cycling_workouts = []
for workout in workouts:
    if workout.attrib.get('workoutActivityType') == 'HKWorkoutActivityTypeCycling':
        metadata_entries = {entry.attrib['key']: entry.attrib['value'] for entry in workout.xpath('MetadataEntry')}
        workout_stats = {stat.attrib['type']: stat.attrib.get('sum', '0') for stat in workout.xpath('WorkoutStatistics')}

        cycling_workouts.append({
            'workoutActivityType': workout.attrib.get('workoutActivityType'),
            'duration': float(workout.attrib.get('duration', 0)),
            'durationUnit': workout.attrib.get('durationUnit'),
            'sourceName': workout.attrib.get('sourceName'),
            'sourceVersion': workout.attrib.get('sourceVersion'),
            'device': workout.attrib.get('device'),
            'creationDate': datetime.strptime(workout.attrib.get('creationDate'), '%Y-%m-%d %H:%M:%S %z'),
            'startDate': datetime.strptime(workout.attrib.get('startDate'), '%Y-%m-%d %H:%M:%S %z'),
            'endDate': datetime.strptime(workout.attrib.get('endDate'), '%Y-%m-%d %H:%M:%S %z'),
            'weather_temperature': float(metadata_entries.get('HKWeatherTemperature', '0').split()[0]),
            'weather_humidity': float(metadata_entries.get('HKWeatherHumidity', '0').split()[0]),
            'active_energy_burned': float(workout_stats.get('HKQuantityTypeIdentifierActiveEnergyBurned', '0')),
            'distance_cycling': float(workout_stats.get('HKQuantityTypeIdentifierDistanceCycling', '0')),
            'elevation_ascended': float(metadata_entries.get('HKElevationAscended', '0').split()[0]),
            'basal_energy_burned': float(workout_stats.get('HKQuantityTypeIdentifierBasalEnergyBurned', '0'))
        })

# Connect to the database
conn = psycopg2.connect(
    dbname='workouts',
    user='postgres',
    password='password',
    host='localhost',
    port='5432'
)
cur = conn.cursor()

# Insert data into the database
# Insert data into the database
for workout in cycling_workouts:
    cur.execute("""
        INSERT INTO cycle (
            workoutActivityType, duration, durationUnit, 
            sourceName, sourceVersion, device, creationDate,
            startDate, endDate, weather_temperature, weather_humidity,
            active_energy_burned, distance_cycling, elevation_ascended,
            basal_energy_burned
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """,
        (
            workout['workoutActivityType'],
            workout['duration'],
            workout['durationUnit'],
            workout['sourceName'],
            workout['sourceVersion'],
            workout['device'],
            workout['creationDate'],
            workout['startDate'],
            workout['endDate'],
            workout['weather_temperature'],
            workout['weather_humidity'],
            workout['active_energy_burned'],
            workout['distance_cycling'],
            workout['elevation_ascended'],
            workout['basal_energy_burned']
        )
    )
conn.commit()
cur.close()
conn.close()

