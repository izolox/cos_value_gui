import asyncio as aio
from .web_scraper import collect_creatures

async def fetch_data(path: str) -> list:
    data = await collect_creatures(path)
    return data

async def upsert_creature(connection, slug, name, value_min, value_max, demand, stability):
    try:
        with connection.cursor() as cursor:
            sql = """
                INSERT INTO creatures (id, name, value_min, value_max, demand, stability)
                VALUES (%s, %s, %s, %s, %s, %s)
                ON DUPLICATE KEY UPDATE
                    id = VALUES(id),
                    value_min = VALUES(value_min),
                    value_max = VALUES(value_max),
                    demand = VALUES(demand),
                    stability = VALUES(stability);
            """
            cursor.execute(sql, (slug, name, value_min, value_max, demand, stability))
            connection.commit()
    except Exception as e:
        print(f"A error occurred: {e}")
        connection.rollback()

async def export(connection, csv_path):
    print("Starting data collection...")
    
    data = await fetch_data(csv_path)
    
    if not connection:
        print("Could not connect to the database")
        return
    
    print(f"Successfully connected to the database {DB_NAME}:{DB_HOST}")

    if data:
        for creature in data:
            slug = creature['slug']
            name = creature['name']
            value_min = creature['value_min']
            value_max = creature['value_max']
            demand = creature['demand']
            stability = creature['stability']
            
            await upsert_creature(connection, slug, name, value_min, value_max, demand, stability)
    
    print('Purging unknown creatures...')
    
    try:
        with connection.cursor() as cursor:
            cursor.execute("DELETE FROM creatures WHERE name = 'Unknown';")
            connection.commit()
    except Exception as e:
        print(f"A error occurred: {e}")
        connection.rollback()
            
    print("Data has successfully been imported")
    
class ValueScraper:
    def __init__(self, connection, csv_path):
        self.connection = connection
        self.csv_path = csv_path
        
    async def run(self):
        await export(self.connection, self.csv_path)