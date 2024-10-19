import asyncio
import pymysql
import time
import os
import config
import subprocess
from value_scraper import ValueScraper
from widget import *

async def main():
    
    #create datavase if it doesn't exist
    connection = pymysql.connect(
        host = config.DB_HOST,
        user = config.DB_USER,
        password = config.DB_PASSWORD
    )
    
    with connection.cursor() as cursor:
        cursor.execute(f"CREATE DATABASE IF NOT EXISTS {config.DB_NAME};")
        cursor.execute(f"USE {config.DB_NAME};")
        cursor.execute(f"""
            CREATE TABLE IF NOT EXISTS creatures (
                id VARCHAR(50) PRIMARY KEY,
                name VARCHAR(50) DEFAULT "Unknown" NOT NULL,
                value_min INT DEFAULT 0 NOT NULL,
                value_max INT DEFAULT 0 NOT NULL,
                demand INT DEFAULT 0 NOT NULL,
                stability ENUM('UNKNOWN', 'LOWERING', 'RISING', 'STABLE', 'UNSTABLE') DEFAULT 'UNKNOWN' NOT NULL
            );"""
        )
    
    input("Would you like to update the value data? (y/n): ")
    
    if input == 'y':
        value_scraper = ValueScraper(connection, config.CSV_PATH)
        await value_scraper.run()
    
    app = App(connection)
    
        
    
if __name__ == "__main__":
    asyncio.run(main())