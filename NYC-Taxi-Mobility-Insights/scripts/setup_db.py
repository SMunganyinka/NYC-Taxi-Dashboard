import mysql.connector

# ------------------------------
# Database connection configuration
# ------------------------------
db_config = {
    'host': 'localhost',
    'user': 'public',
    'password': '', 
    'database': 'nyc_taxi_db'
}


# ------------------------------
# SQL statements for database and tables
# ------------------------------
sql_statements = [
    "CREATE DATABASE IF NOT EXISTS nyc_taxi_db",
    "USE nyc_taxi_db",
    """
    CREATE TABLE IF NOT EXISTS vendors (
        vendor_id INT PRIMARY KEY,
        vendor_name VARCHAR(50) DEFAULT NULL
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS trips (
        trip_id BIGINT PRIMARY KEY,
        vendor_id INT,
        pickup_datetime DATETIME,
        dropoff_datetime DATETIME,
        passenger_count INT,
        store_and_fwd_flag CHAR(1),
        trip_duration INT,
        trip_distance_km DECIMAL(10,2),
        speed_kmph DECIMAL(10,2),
        pickup_hour TINYINT,
        pickup_dayofweek TINYINT,
        FOREIGN KEY (vendor_id) REFERENCES vendors(vendor_id)
    )
    """,
    """
    CREATE TABLE IF NOT EXISTS locations (
        location_id BIGINT AUTO_INCREMENT PRIMARY KEY,
        trip_id BIGINT,
        pickup_longitude DECIMAL(10,6),
        pickup_latitude DECIMAL(10,6),
        dropoff_longitude DECIMAL(10,6),
        dropoff_latitude DECIMAL(10,6),
        FOREIGN KEY (trip_id) REFERENCES trips(trip_id)
    )
    """,
    "CREATE INDEX IF NOT EXISTS idx_pickup_datetime ON trips(pickup_datetime)",
    "CREATE INDEX IF NOT EXISTS idx_dropoff_datetime ON trips(dropoff_datetime)",
    "CREATE INDEX IF NOT EXISTS idx_pickup_dayofweek ON trips(pickup_dayofweek)",
    "CREATE INDEX IF NOT EXISTS idx_pickup_coords ON locations(pickup_longitude, pickup_latitude)",
    "CREATE INDEX IF NOT EXISTS idx_dropoff_coords ON locations(dropoff_longitude, dropoff_latitude)"
]

# ------------------------------
# Execute statements
# ------------------------------
try:
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()

    for stmt in sql_statements:
        cursor.execute(stmt)

    print("Database 'nyc_taxi_db' and tables created successfully!")

finally:
    cursor.close()
    connection.close()

    print("Database connection closed.")    