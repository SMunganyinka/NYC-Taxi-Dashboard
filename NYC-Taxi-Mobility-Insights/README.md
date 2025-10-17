ER Diagram Structure
+-------------+         +-------------+
|   vendors   |         |    trips    |
+-------------+         +-------------+
| vendor_id PK| <------ | vendor_id FK|
| vendor_name |         | trip_id PK  |
+-------------+         | pickup_*    |
                        | dropoff_*   |
                        | trip_duration|
                        | trip_distance|
                        | speed_kmph   |
                        | pickup_hour  |
                        | pickup_dayofweek |
                        +-------------+
