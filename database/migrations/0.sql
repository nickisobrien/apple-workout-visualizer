CREATE DATABASE workouts;

CREATE TABLE workouts.run (
  id SERIAL PRIMARY KEY,
  workoutActivityType TEXT,
  duration REAL,
  durationUnit TEXT,
  totalDistance REAL,
  totalDistanceUnit TEXT,
  totalEnergyBurned REAL,
  totalEnergyBurnedUnit TEXT,
  sourceName TEXT,
  sourceVersion TEXT,
  device TEXT,
  creationDate TIMESTAMP,
  startDate TIMESTAMP,
  endDate TIMESTAMP,
  weather_temperature REAL,
  weather_humidity REAL,
  active_energy_burned REAL,
  distance_walking_running REAL,
  elevation_ascended REAL,
  basal_energy_burned REAL
);

CREATE TABLE swim (
  workout_id serial PRIMARY KEY,
  workoutActivityType text,
  duration double precision,
  durationUnit text,
  sourceName text,
  sourceVersion text,
  device text,
  creationDate timestamp,
  startDate timestamp,
  endDate timestamp,
  weather_temperature double precision,
  weather_humidity double precision,
  active_energy_burned double precision,
  basal_energy_burned double precision,
  lap_length double precision,
  swimming_location_type int,
  distance_swimming double precision,
  swimming_stroke_count int,
  average_METs double precision
);

CREATE TABLE cycle (
  workoutActivityType TEXT,
  duration FLOAT,
  durationUnit TEXT,
  totalDistance FLOAT,
  totalDistanceUnit TEXT,
  totalEnergyBurned FLOAT,
  totalEnergyBurnedUnit TEXT,
  sourceName TEXT,
  sourceVersion TEXT,
  device TEXT,
  creationDate TIMESTAMP,
  startDate TIMESTAMP,
  endDate TIMESTAMP,
  weather_temperature FLOAT,
  weather_humidity FLOAT,
  active_energy_burned FLOAT,
  distance_cycling FLOAT,
  elevation_ascended FLOAT,
  basal_energy_burned FLOAT
);
