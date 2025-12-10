from pathlib import Path

import psycopg2
from app.utils.logger import Logger
from dotenv import load_dotenv

load_dotenv(Path(__file__).resolve().parent.parent / ".env")

logger = Logger("logs").get_logger()


class PLSQL:
    def __init__(self, database_url):
        logger.info("Connecting to PostgreSQL database...")
        logger.debug(f"DATABASE_URL: {database_url}")
        self.conn = psycopg2.connect(dsn=database_url)
        self.cur = self.conn.cursor()

    def get_data_from(self, query, params=None):
        try:
            logger.info("Fetching data from PostgreSQL database...")
            logger.debug(f"Select query: {query}")
            if params:
                logger.debug(f"Select params: {params}")
            else:
                logger.debug("Select params: None")
            
            self.cur.execute(query, params)
            records = self.cur.fetchall()
            logger.debug(f"Fetched {len(records)} records")
            return records
        except Exception as e:
            logger.error(f"PostgreSQL database error: {e}")
            raise

    def close_connection(self):
        self.cur.close()
        self.conn.close()
        logger.info("PostgreSQL connection closed.")


def get_data_db(database_url, query, param=None):
    plsql = PLSQL(database_url)
    result = plsql.get_data_from(query, param)
    plsql.close_connection()
    return result
