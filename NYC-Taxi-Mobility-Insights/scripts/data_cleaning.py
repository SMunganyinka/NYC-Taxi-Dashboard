"""
NYC Taxi Trip Data Cleaning Script (Complete & Runnable)
--------------------------------------------------------
- Ensures data/processed and logs directories exist
- Loads raw CSV from data/raw/train.csv
- Handles duplicates, missing values, invalid records, outliers
- Normalizes timestamps and coordinates
- Derives features: trip_distance_km, speed_kmph, pickup_hour, pickup_dayofweek
- Logs excluded records with reasons for transparency
- Applies Z-score normalization to coordinate columns (mean=0, std=1)
"""

import pandas as pd
import numpy as np
from pathlib import Path

# -------------------------
# Project directories
# -------------------------
BASE_DIR = Path(__file__).resolve().parent.parent  # project root (one level above scripts/)
RAW_DIR = BASE_DIR / "data" / "raw"
PROCESSED_DIR = BASE_DIR / "data" / "processed"
LOG_DIR = BASE_DIR / "logs"

# Ensure directories exist
RAW_DIR.mkdir(parents=True, exist_ok=True)
PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
LOG_DIR.mkdir(parents=True, exist_ok=True)

# File paths
RAW_FILE = RAW_DIR / "train.csv"
CLEAN_FILE = PROCESSED_DIR / "cleaned_train.csv"
LOG_FILE = LOG_DIR / "excluded_records.log"

# -------------------------
# Utilities
# -------------------------
def haversine(lat1, lon1, lat2, lon2):
    """Return distance in km between two points using Haversine formula."""
    R = 6371.0
    phi1, phi2 = np.radians(lat1), np.radians(lat2)
    dphi = np.radians(lat2 - lat1)
    dlambda = np.radians(lon2 - lon1)
    a = np.sin(dphi / 2) ** 2 + np.cos(phi1) * np.cos(phi2) * np.sin(dlambda / 2) ** 2
    return R * 2 * np.arctan2(np.sqrt(a), np.sqrt(1 - a))

def zscore_series(s):
    return (s - s.mean()) / s.std(ddof=0)

# -------------------------
# Load data
# -------------------------
print(f"Loading dataset from: {RAW_FILE}")
if not RAW_FILE.exists():
    raise FileNotFoundError(f"Raw file not found: {RAW_FILE}. Place train.csv in data/raw/")

df = pd.read_csv(RAW_FILE)
print(f"Initial shape: {df.shape}")

# -------------------------
# Basic cleaning
# -------------------------
df = df.drop_duplicates()
print(f"After drop_duplicates: {df.shape}")

required_cols = [
    'pickup_datetime', 'dropoff_datetime',
    'pickup_longitude', 'pickup_latitude',
    'dropoff_longitude', 'dropoff_latitude'
]
missing_required = [c for c in required_cols if c not in df.columns]
if missing_required:
    raise KeyError(f"Required columns missing from CSV: {missing_required}")

df = df.dropna(subset=required_cols)
print(f"After dropping rows with missing required fields: {df.shape}")

df['pickup_datetime'] = pd.to_datetime(df['pickup_datetime'], errors='coerce')
df['dropoff_datetime'] = pd.to_datetime(df['dropoff_datetime'], errors='coerce')
df = df.dropna(subset=['pickup_datetime', 'dropoff_datetime'])
print(f"After parsing timestamps: {df.shape}")

# -------------------------
# Derived fields
# -------------------------
# Trip duration (seconds)
df['trip_duration'] = (df['dropoff_datetime'] - df['pickup_datetime']).dt.total_seconds()

# Haversine distance (km)
df['trip_distance_km'] = haversine(
    df['pickup_latitude'].astype(float), df['pickup_longitude'].astype(float),
    df['dropoff_latitude'].astype(float), df['dropoff_longitude'].astype(float)
)

# Speed (km/h)
df['speed_kmph'] = np.where(
    df['trip_duration'] > 0,
    df['trip_distance_km'] / (df['trip_duration'] / 3600.0),
    np.nan
)

# Temporal features
df['pickup_hour'] = df['pickup_datetime'].dt.hour
df['pickup_dayofweek'] = df['pickup_datetime'].dt.day_name()

# -------------------------
# Identify invalid / outlier records
# -------------------------
conditions = [
    ('negative_or_zero_duration', df['trip_duration'] <= 0),
    ('missing_or_invalid_coords', df[['pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude']].isna().any(axis=1)),
    ('zero_or_negative_distance', df['trip_distance_km'] <= 0),
    ('unrealistic_speed', df['speed_kmph'] > 120),
    ('extreme_coords', (df['pickup_latitude'].abs() > 90) | (df['dropoff_latitude'].abs() > 90) |
                       (df['pickup_longitude'].abs() > 180) | (df['dropoff_longitude'].abs() > 180))
]

exclude_mask = pd.Series(False, index=df.index)
exclude_reason = pd.Series("", index=df.index)

for reason, mask in conditions:
    mask = mask.fillna(False)
    new_exclusions = mask & (~exclude_mask)
    exclude_reason.loc[new_exclusions] = reason
    exclude_mask = exclude_mask | mask

excluded = df[exclude_mask].copy()
if not excluded.empty:
    excluded['exclude_reason'] = exclude_reason[exclude_mask]
    excluded.to_csv(LOG_FILE, index=False)
    print(f"Excluded {len(excluded)} invalid records logged to {LOG_FILE}")
else:
    pd.DataFrame(columns=list(df.columns)+['exclude_reason']).to_csv(LOG_FILE, index=False)
    print("No excluded records. Empty log file created.")

df_cleaned = df[~exclude_mask].copy()
print(f"Rows remaining after exclusion: {df_cleaned.shape}")

# -------------------------
# Z-score normalization for coordinates
# -------------------------
coord_cols = ['pickup_longitude','pickup_latitude','dropoff_longitude','dropoff_latitude']
for col in coord_cols:
    df_cleaned[col] = pd.to_numeric(df_cleaned[col], errors='coerce')
df_cleaned = df_cleaned.dropna(subset=coord_cols)
for col in coord_cols:
    df_cleaned[col + '_z'] = zscore_series(df_cleaned[col])

print("Applied Z-score normalization to coordinates (produced *_z columns).")

# -------------------------
# Round numeric fields
# -------------------------
df_cleaned['trip_distance_km'] = df_cleaned['trip_distance_km'].round(5)
df_cleaned['speed_kmph'] = df_cleaned['speed_kmph'].round(3)

# -------------------------
# Save cleaned data
# -------------------------
df_cleaned.to_csv(CLEAN_FILE, index=False)
print(f"Clean dataset saved to: {CLEAN_FILE}")
print(f"Final shape: {df_cleaned.shape}")

# -------------------------
# Summary of derived features
# -------------------------
print("\nDerived Features:")
print("- trip_distance_km : distance in km computed by Haversine (spatial analysis)")
print("- speed_kmph       : average speed (km/h) for anomaly detection and mobility analysis")
print("- pickup_hour      : hour of day for temporal analysis")
print("- pickup_dayofweek : day of week for weekday/weekend analysis")
print("- *_z columns      : Z-score normalized coordinates (mean=0, std=1)")
print(f"Cleaned data saved to: {CLEAN_FILE}")
print(f"Final shape: {df_cleaned.shape}")
