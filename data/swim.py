import psycopg2
from lxml import etree

# Parse the XML file
tree = etree.parse('apple_health_export/export.xml')

# Find all 'Workout' elements in the XML
workouts = tree.xpath('//Workout')

# Filter for swimming workouts
swimming_workouts = []
for workout in workouts:
    if workout.attrib.get('workoutActivityType') == 'HKWorkoutActivityTypeSwimming':
        metadata_entries = {entry.attrib['key']: entry.attrib['value'] for entry in workout.xpath('MetadataEntry')}
        workout_stats = {stat.attrib['type']: stat.attrib.get('sum', '0') for stat in workout.xpath('WorkoutStatistics')}

        swimming_workouts.append({
            'workoutActivityType': workout.attrib.get('workoutActivityType'),
            'duration': float(workout.attrib.get('duration', 0)),
            'durationUnit': workout.attrib.get('durationUnit'),
            'sourceName': workout.attrib.get('sourceName'),
            'sourceVersion': workout.attrib.get('sourceVersion'),
            'device': workout.attrib.get('device'),
            'creationDate': workout.attrib.get('creationDate'),
            'startDate': workout.attrib.get('startDate'),
            'endDate': workout.attrib.get('endDate'),
            'weather_temperature': float(metadata_entries.get('HKWeatherTemperature', '0').split()[0]),
            'weather_humidity': float(metadata_entries.get('HKWeatherHumidity', '0').split()[0]),
            'active_energy_burned': float(workout_stats.get('HKQuantityTypeIdentifierActiveEnergyBurned', '0')),
            'basal_energy_burned': float(workout_stats.get('HKQuantityTypeIdentifierBasalEnergyBurned', '0')),
            'lap_length': float(metadata_entries.get('HKLapLength', '0').split()[0]),
            'swimming_location_type': int(metadata_entries.get('HKSwimmingLocationType', '0')),
            'distance_swimming': float(workout_stats.get('HKQuantityTypeIdentifierDistanceSwimming', '0')),
            'swimming_stroke_count': int(workout_stats.get('HKQuantityTypeIdentifierSwimmingStrokeCount', '0')),
            'average_METs': float(metadata_entries.get('HKAverageMETs', '0').split()[0])
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
for workout in swimming_workouts:
    cur.execute("""
        INSERT INTO swim (
            workoutActivityType, duration, durationUnit, sourceName,
            sourceVersion, device, creationDate, startDate, endDate,
            weather_temperature, weather_humidity, active_energy_burned,
            basal_energy_burned, lap_length, swimming_location_type,
            distance_swimming, swimming_stroke_count, average_METs
        ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
        """, (
            workout['workoutActivityType'], workout['duration'], workout['durationUnit'], 
            workout['sourceName'], workout['sourceVersion'], workout['device'], 
            workout['creationDate'], workout['startDate'], workout['endDate'], 
            workout['weather_temperature'], workout['weather_humidity'], 
            workout['active_energy_burned'], workout['basal_energy_burned'], 
            workout['lap_length'], workout['swimming_location_type'], 
            workout['distance_swimming'], workout['swimming_stroke_count'], 
            workout['average_METs']
        ))

# Commit changes
conn.commit()

# Close connection
conn.close()
