import psycopg2
from psycopg2 import pool, sql
import logging
from typing import List, Tuple, Any, Optional
from contextlib import contextmanager
import os
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DatabaseConnection:
    """Database connection manager with connection pooling"""
    
    def __init__(self, min_connections: int = 1, max_connections: int = 10):
        """Initialize database connection pool"""
        load_dotenv()  # Load environment variables
        
        self.db_config = {
            "dbname": os.getenv("DB_NAME", "postgres"),
            "user": os.getenv("DB_USER", "postgres"),
            "password": os.getenv("DB_PASSWORD", "password"),
            "host": os.getenv("DB_HOST", "localhost"),
            "port": os.getenv("DB_PORT", "5432")
        }
        
        try:
            self.pool = psycopg2.pool.SimpleConnectionPool(
                min_connections,
                max_connections,
                **self.db_config
            )
            logger.info("Database connection pool created successfully")
        except psycopg2.Error as e:
            logger.error(f"Error creating connection pool: {e}")
            raise

    @contextmanager
    def get_connection(self):
        """Get a database connection from the pool"""
        conn = None
        try:
            conn = self.pool.getconn()
            yield conn
        except psycopg2.Error as e:
            logger.error(f"Database connection error: {e}")
            raise
        finally:
            if conn:
                self.pool.putconn(conn)

    def execute_query(self, query: str, params: tuple = None) -> List[Tuple[Any]]:
        """Execute a SELECT query and return results"""
        with self.get_connection() as conn:
            try:
                with conn.cursor() as cursor:
                    cursor.execute(sql.SQL(query), params)
                    results = cursor.fetchall()
                    if cursor.description:
                        columns = [desc[0] for desc in cursor.description]
                        return columns, results
                    return None, results
            except psycopg2.Error as e:
                logger.error(f"Query execution error: {e}")
                conn.rollback()
                raise
            finally:
                conn.commit()


    def __del__(self):
        """Clean up connection pool on deletion"""
        if hasattr(self, 'pool'):
            self.pool.closeall()

# if __name__ == "__main__":
#     # Example usage
#     db = DatabaseConnection()
#     query = "SELECT * FROM airlines LIMIT 5"
#     columns, results = db.execute_query(query)
#     print(columns)
#     print(results)