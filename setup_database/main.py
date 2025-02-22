import pandas as pd
from sqlalchemy import create_engine, text
import subprocess
import zipfile
import os
import time
from datetime import datetime
import logging
from sqlalchemy.exc import SQLAlchemyError
import numpy as np
from typing import Optional

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(f'flight_data_upload_{datetime.now().strftime("%Y%m%d_%H%M%S")}.log'),
        logging.StreamHandler()
    ]
)

class DatabaseUploader:
    def __init__(self, 
                 username: str = os.getenv('DB_USER', 'postgres'),
                 password: str = os.getenv('DB_PASSWORD', 'password'),
                 host: str = os.getenv('DB_HOST', 'localhost'),
                 port: str = os.getenv('DB_PORT', '5432'),
                 database: str = os.getenv('DB_NAME', 'postgres'),
                 chunk_size: int = 10000):
        self.connection_string = f'postgresql://{username}:{password}@{host}:{port}/{database}'
        self.chunk_size = chunk_size
        self.engine = None

    def connect(self) -> None:
        """Establish database connection with retry mechanism"""
        max_retries = 3
        retry_delay = 5
        
        for attempt in range(max_retries):
            try:
                self.engine = create_engine(
                    self.connection_string,
                    pool_pre_ping=True,
                    pool_size=5,
                    max_overflow=10
                )
                # Test the connection
                with self.engine.connect() as conn:
                    conn.execute(text("SELECT 1"))
                logging.info("Database connection established successfully")
                return
            except SQLAlchemyError as e:
                logging.error(f"Attempt {attempt + 1}/{max_retries} failed: {str(e)}")
                if attempt < max_retries - 1:
                    time.sleep(retry_delay)
                else:
                    raise Exception("Failed to connect to database after multiple attempts")

    def download_dataset(self, dataset_url: str, extract_path: str = '.') -> None:
        """Download and extract dataset from Kaggle"""
        try:
            download_path = 'flight-delays.zip'
            subprocess.run(['kaggle', 'datasets', 'download', '-d', dataset_url, '-p', extract_path], 
                         check=True,
                         capture_output=True)
            
            with zipfile.ZipFile(download_path, 'r') as zip_ref:
                zip_ref.extractall(extract_path)
            
            os.remove(download_path)
            logging.info("Dataset downloaded and extracted successfully")
        except Exception as e:
            logging.error(f"Error downloading dataset: {str(e)}")
            raise

    def optimize_dataframe(self, df: pd.DataFrame) -> pd.DataFrame:
        """Optimize DataFrame memory usage"""
        for col in df.columns:
            if df[col].dtype == 'float64' and df[col].notnull().all():
                df[col] = pd.to_numeric(df[col], downcast='float')
            elif df[col].dtype == 'int64':
                df[col] = pd.to_numeric(df[col], downcast='integer')
            elif df[col].dtype == 'object':
                if df[col].nunique() / len(df) < 0.5:  # If column has low cardinality
                    df[col] = df[col].astype('category')
        return df

    def upload_dataframe(self, df: pd.DataFrame, table_name: str, if_exists: str = 'replace') -> None:
        """Upload DataFrame to database in chunks with progress tracking"""
        try:
            total_rows = len(df)
            chunks = np.array_split(df, np.ceil(total_rows / self.chunk_size))
            
            for i, chunk in enumerate(chunks, 1):
                try:
                    if i == 1 and if_exists == 'replace':
                        chunk.to_sql(table_name, self.engine, if_exists='replace', index=False)
                    else:
                        chunk.to_sql(table_name, self.engine, if_exists='append', index=False)
                    
                    logging.info(f"Uploaded chunk {i}/{len(chunks)} of {table_name} "
                               f"({i * self.chunk_size if i < len(chunks) else total_rows}/{total_rows} rows)")
                except SQLAlchemyError as e:
                    logging.error(f"Error uploading chunk {i} of {table_name}: {str(e)}")
                    raise
                
        except Exception as e:
            logging.error(f"Error uploading {table_name}: {str(e)}")
            raise

def main():
    try:
        # Initialize uploader
        uploader = DatabaseUploader()
        uploader.connect()

        # Download dataset
        dataset_url = 'usdot/flight-delays'
        uploader.download_dataset(dataset_url)

        # Load and process CSV files
        dfs = {
            'airlines': pd.read_csv('airlines.csv'),
            'airports': pd.read_csv('airports.csv'),
            'flights': pd.read_csv('flights.csv')
        }

        # Process and upload each DataFrame
        for table_name, df in dfs.items():
            logging.info(f"Processing {table_name} dataset...")
            
            # Convert column names to lowercase
            df.columns = df.columns.str.lower()
            
            # Optimize DataFrame
            df = uploader.optimize_dataframe(df)
            
            # Upload to database
            logging.info(f"Uploading {table_name} to database...")
            uploader.upload_dataframe(df, table_name)
            
            logging.info(f"{table_name} uploaded successfully")

        logging.info("All data uploaded successfully!")

    except Exception as e:
        logging.error(f"Error in main process: {str(e)}")
        raise

if __name__ == "__main__":
    main()