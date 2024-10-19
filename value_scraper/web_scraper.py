import asyncio as aio
import requests as req
from bs4 import BeautifulSoup
import os
import csv

SITE_URL = 'https://www.game.guide/'

class StabilityType():
    UNKNOWN = 'UNKNOWN'
    LOWERING = 'LOWERING'
    RISING = 'RISING'
    STABLE = 'STABLE'
    UNSTABLE = 'UNSTABLE'
    
def text_to_number(text: str) -> int:
    multipliers = {
        'k': 1000,
        'm': 1000000,
        'b': 1000000000
    }
    
    text = text.lower().strip()
    
    if text[-1] in multipliers:
        return int(float(text[:-1]) * multipliers[text[-1]])
    else:
        return int(text)
    
def parse_value(value: str) -> dict:
    value = value.replace('Value:', '').strip()
    
    if '-' in value:
        min_value, max_value = value.split('-')
        return { "min": text_to_number(min_value), "max": text_to_number(max_value) }
    else:
        return { "min": text_to_number(value), "max": text_to_number(value) }
    
def parse_demand(demand: str) -> int:
    demand = demand.replace('Demand:', '').strip()
    demand = demand.replace('/10', '')
    
    return int(demand)

def parse_stability(stability: str) -> str:
    stability = stability.replace('Stability:', '').strip()
    
    if 'LOWERING' in stability:
        return StabilityType.LOWERING
    elif 'RISING' in stability:
        return StabilityType.RISING
    elif 'STABLE' in stability:
        return StabilityType.STABLE
    elif 'UNSTABLE' in stability:
        return StabilityType.UNSTABLE
    else:
        return StabilityType.UNKNOWN

def retrieve_creature_names(file_path, column_index: str) -> list:
    column_data = []
    
    try:
        abs_file_path = os.path.abspath(file_path)
        
        with open(abs_file_path, mode='r', newline='') as file:
            csv_reader = csv.reader(file)
            
            for row in csv_reader:
                if len(row) >= column_index:
                    column_data.append(row[column_index-1])
                else:
                    print(f"Row {csv_reader.line_num} does not have column {column_index}")
    except FileNotFoundError:
        print(f"Could not find the file {abs_file_path}")
    except Exception as e:
        print(f"An error occurred: {e}")
        
    return column_data

async def fetch(url: str) -> str:
    response = req.get(url)
    return response.text

async def get_creature_data(slug: str, name: str) -> dict:
    # Fetch the page
    url = f'{SITE_URL}{slug}-value-creatures-of-sonaria'
    page = await fetch(url)
    
    creature = { # Default values in case the data is not found (unused yet)
        "slug": 'unknown',
        "name": "Unknown",
        "value_min": 0,
        "value_max": 0,
        "demand": 1,
        "stability": StabilityType.UNKNOWN,
    }
    
    soup = BeautifulSoup(page, 'html.parser') # Parse the page in a workable format
    data_container = soup.find("div", class_="e-con-inner")
    
    value = soup.find(lambda tag: tag.name == "p" and "Value:" in tag.text)
    demand = soup.find(lambda tag: tag.name == "p" and "Demand:" in tag.text)
    stability = soup.find(lambda tag: tag.name == "p" and "Stability:" in tag.text)
    
    if value and demand and stability:
        creature['slug'] = slug
        creature['name'] = name
        creature['value_min'] = parse_value(value.text).get('min')
        creature['value_max'] = parse_value(value.text).get('max')
        creature['demand'] = parse_demand(demand.text)
        creature['stability'] = parse_stability(stability.text)
    else:
        print(f"Could not find the data for {slug}")
        
    return creature
    
async def collect_creatures(file_path: str) -> list:
    data = []
    
    # Fetch the list of creature names and slugs
    creature_slugs = retrieve_creature_names(file_path, 3)
    creature_names = retrieve_creature_names(file_path, 1)
    
    # Remove first index as it's the csv headers
    creature_names.pop(0)
    creature_slugs.pop(0)
    
    for slug in creature_slugs:
        slug_index = creature_slugs.index(slug)
        creature_name = creature_names[slug_index]
        
        print(f"Fetching data for {creature_name}...")
        
        creature = await get_creature_data(slug, creature_name)
        
        if creature:
            completion = round((slug_index + 1) / len(creature_slugs) * 100)
            print(f"Data for {creature_name} fetched successfully ({completion}% Done)")
            data.append(creature)
            
    print("Successfully fetched all creatures")
        
    return data