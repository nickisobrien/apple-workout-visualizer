import psycopg2
from lxml import etree

# Parse the XML file
tree = etree.parse('apple_health_export/export.xml')

# Find all 'Workout' elements in the XML
workouts = tree.xpath('//Workout')

# Filter for running workouts
running_workouts = []
for workout in workouts:
    if workout.attrib.get('workoutActivityType') == 'HKWorkoutActivityTypeRunning':
        metadata_entries = {entry.attrib['key']: entry.attrib['value'] for entry in workout.xpath('MetadataEntry')}
        workout_stats = {stat.attrib['type']: stat.attrib.get('sum', 0) for stat in workout.xpath('WorkoutStatistics')}

        running_workouts.append({
            'workoutActivityType': workout.attrib.get('workoutActivityType'),
            'duration': float(workout.attrib.get('duration', 0)),
            'durationUnit': workout.attrib.get('durationUnit'),
            'totalDistance': float(workout.attrib.get('totalDistance', 0)),
            'totalDistanceUnit': workout.attrib.get('totalDistanceUnit'),
            'totalEnergyBurned': float(workout.attrib.get('totalEnergyBurned', 0)),
            'totalEnergyBurnedUnit': workout.attrib.get('totalEnergyBurnedUnit'),
            'sourceName': workout.attrib.get('sourceName'),
            'sourceVersion': workout.attrib.get('sourceVersion'),
            'device': workout.attrib.get('device'),
            'creationDate': workout.attrib.get('creationDate'),
            'startDate': workout.attrib.get('startDate'),
            'endDate': workout.attrib.get('endDate'),
            'weather_temperature': float(metadata_entries.get('HKWeatherTemperature', '0').split()[0]),
            'weather_humidity': float(metadata_entries.get('HKWeatherHumidity', '0').split()[0]),
            'active_energy_burned': float(workout_stats.get('HKQuantityTypeIdentifierActiveEnergyBurned', 0)),
            'distance_walking_running': float(workout_stats.get('HKQuantityTypeIdentifierDistanceWalkingRunning', 0)),
            'elevation_ascended': float(metadata_entries.get('HKElevationAscended', '0').split()[0]),
            'basal_energy_burned': float(workout_stats.get('HKQuantityTypeIdentifierBasalEnergyBurned', 0))
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
for workout in running_workouts:
    cur.execute("""
        INSERT INTO run (
            workoutActivityType, duration, durationUnit, totalDistance,
            totalDistanceUnit, totalEnergyBurned, totalEnergyBurnedUnit,
            sourceName, sourceVersion, device, creationDate,
            startDate, endDate, weather_temperature, weather_humidity,
            active_energy_burned, distance_walking_running, elevation_ascended,
            basal_energy_burned
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
    """, (
        workout['workoutActivityType'], workout['duration'], workout['durationUnit'],
        workout['totalDistance'], workout['totalDistanceUnit'], workout['totalEnergyBurned'],
        workout['totalEnergyBurnedUnit'], workout['sourceName'], workout['sourceVersion'],
        workout['device'], workout['creationDate'], workout['startDate'], workout['endDate'],
        workout['weather_temperature'], workout['weather_humidity'], workout['active_energy_burned'],
        workout['distance_walking_running'], workout['elevation_ascended'], workout['basal_energy_burned']
    ))

# Commit the transaction
conn.commit()

# Close the connection
cur.close()
conn.close()

