import asyncio
import pymysql
import time
import os
import config
import subprocess
from value_scraper import ValueScraper
from widget import *

async def main():
    
    connection = pymysql.connect(
        host = config.DB_HOST,
        user = config.DB_USER,
        password = config.DB_PASSWORD,
        database = config.DB_NAME
    )
    
    # input("Would you like to update the value data? (y/n): ")
    
    # if input == 'y':
    #     value_scraper = ValueScraper(connection, config.CSV_PATH)
    #     await value_scraper.run()
    
    app = App(connection)
    
        
    
if __name__ == "__main__":
    asyncio.run(main())