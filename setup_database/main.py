import pandas as pd
from sqlalchemy import create_engine
import subprocess
import zipfile
import os
import time

# Database connection details
db_username = os.getenv('DB_USER', 'postgres')
db_password = os.getenv('DB_PASSWORD', 'password')
db_host = os.getenv('DB_HOST', 'localhost')
db_port = os.getenv('DB_PORT', '5432')
db_name = os.getenv('DB_NAME', 'postgres')

# Create a database connection
engine = create_engine(f'postgresql://{db_username}:{db_password}@{db_host}:{db_port}/{db_name}')

# Download dataset from Kaggle
dataset_url = 'usdot/flight-delays'
download_path = 'flight-delays.zip'
extract_path = '.'

# Use Kaggle API to download the dataset
subprocess.run(['kaggle', 'datasets', 'download', '-d', dataset_url, '-p', extract_path])

# Unzip the downloaded file
with zipfile.ZipFile(download_path, 'r') as zip_ref:
    zip_ref.extractall(extract_path)

# Remove the zip file after extraction
os.remove(download_path)

# Load CSV files into DataFrames
airlines_df = pd.read_csv('airlines.csv')
airports_df = pd.read_csv('airports.csv')
flights_df = pd.read_csv('flights.csv')

# Convert column names to all lowercase
airlines_df.columns = airlines_df.columns.str.lower()
airports_df.columns = airports_df.columns.str.lower()
flights_df.columns = flights_df.columns.str.lower()

print(flights_df.columns)

# Upload DataFrames to PostgreSQL
airlines_df.to_sql('airlines', engine, if_exists='replace', index=False)
airports_df.to_sql('airports', engine, if_exists='replace', index=False)
flights_df.to_sql('flights', engine, if_exists='replace', index=False)

print("Data uploaded successfully!")