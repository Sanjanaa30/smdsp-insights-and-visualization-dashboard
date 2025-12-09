import os

import psycopg2
from pathlib import Path
from dotenv import load_dotenv
from app.utils.logger import Logger
from psycopg2.extras import execute_values

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = Logger("logs").get_logger()


class PLSQL:
    def __init__(self, database_url):
        logger.info("Connecting to PostgreSQL database...")
        logger.debug(f"DATABASE_URL: {database_url}")
        self.conn = psycopg2.connect(dsn=database_url)
        self.cur = self.conn.cursor()

    def get_data_from(self, query, params):
        try:
            logger.info("Fetching data from PostgreSQL database...")
            logger.debug(f"Select query: {query}")
            self.cur.execute(query, params)
            records = self.cur.fetchall()
            return records
        except Exception as e:
            logger.error(f"Error fetching data from PostgreSQL database: {e}")
            return []

    def close_connection(self):
        self.cur.close()
        self.conn.close()
        logger.info("PostgreSQL connection closed.")
