# Achtung: Dieser Code wurde (teilweise) mit Hilfe von KI-Tools generiert (Copilot Agent).<br/> 
# Bitte sorgfältig prüfen und vor dem produktiven Einsatz testen! 
# OK Lab Köln

# pip3 install requests
import requests
from bs4 import BeautifulSoup
import json
import os



# request the target URL
def crawler():

    """Initialisiert eine leere GeoJSON-Datei."""
    file_path = 'geojson_results.json'
    empty_geojson = {"type": "FeatureCollection", "features": []}
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(empty_geojson, json_file, ensure_ascii=False, indent=4)
    print(f"GeoJSON-Datei wurde geleert: {file_path}")

    response = requests.get("https://codeforcologne.github.io/linked-distributed-data/index.html")
    response.raise_for_status()

    # Load the HTML file
    with open('index.html', 'r', encoding='utf-8') as file:
        content = file.read()

    # Parse the HTML content
    soup = BeautifulSoup(content, 'html.parser')

    # Find all links in the nav tag with id 'resources'
    nav_links = soup.select('#resources a')

    # Print the href attribute of each link and crawl them
    for link in nav_links:
        print(link.get('href'))

    crawl_links(nav_links)

def crawl_links(links):
    for link in links:
        href = link.get('href')
        if href:
            try:
                link_response = requests.get(href)
                link_response.raise_for_status()
                print(f"Successfully crawled: {href}")
                
                # Parse the HTML content of the crawled link
                link_soup = BeautifulSoup(link_response.text, 'html.parser')
                
                # Find all links in the nav tag with id 'resources'
                nested_nav_links = link_soup.select('#resources a')
                
                # Print the href attribute of each nested link
                for nested_link in nested_nav_links:
                    print(nested_link.get('href'))
                    
                # Recursively crawl nested links
                crawl_websites(nested_nav_links)

            except requests.RequestException as e:
                print(f"Failed to crawl: {href} with error: {e}")

# crawl the json-ld of the website
def crawl_json_ld(soup):
    json_ld = soup.find_all('script', type='application/ld+json')
    json_ld_data = []
    for item in json_ld:
        try:
            # Parse the JSON-LD content as a string
            
            json_data = json.loads(item.string)
            if "spatialCoverage" in json_data and "geo" in json_data["spatialCoverage"]:
                geo = json_data["spatialCoverage"]["geo"]
                geojson_data = {
                    "type": "Feature",
                    "geometry": {
                        "type": "Point",
                        "coordinates": [
                            geo["longitude"],
                            geo["latitude"]
                        ]
                    },
                    "properties": {
                        "name": json_data.get("name", "Unknown"),
                        "url": json_data.get("url", ""),
                        "thumbnail": json_data.get("thumbnail", ""),
                        "license": json_data.get("license", ""),
                        "creator": json_data.get("creator", {}).get("name", "Unknown")
                    }
                }
            json_ld_data.append(geojson_data)

        except json.JSONDecodeError as e:
            print(f"Failed to parse JSON-LD: {e}")
        #print(item.string)
        #json_ld_data.append(item)
    print(json_ld_data)
    append_to_json_file('geojson_results.json', json_ld_data)

def append_to_json_file(file_path, new_features):
    """Append new GeoJSON features to an existing GeoJSON file."""
    if os.path.exists(file_path):
        # Load existing GeoJSON data
        with open(file_path, 'r', encoding='utf-8') as json_file:
            try:
                existing_data = json.load(json_file)
            except json.JSONDecodeError:
                existing_data = {"type": "FeatureCollection", "features": []}
    else:
        # Initialize an empty GeoJSON structure if the file doesn't exist
        existing_data = {"type": "FeatureCollection", "features": []}

    # Append new features to the existing features list
    existing_data["features"].extend(new_features)

    # Save updated GeoJSON data back to the file
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(existing_data, json_file, ensure_ascii=False, indent=4)
    print(f"Appended GeoJSON data to {file_path}")

def crawl_websites(links):
    """Recursively crawl nested links."""
    for link in links:
        href = link.get('href')
        if href:
            try:
                link_response = requests.get(href)
                link_response.raise_for_status()
                print(f"Recursively crawled: {href}")
                
                # Parse the HTML content of the crawled link
                link_soup = BeautifulSoup(link_response.text, 'html.parser')
                
                # Optionally, extract JSON-LD data
                crawl_json_ld(link_soup)

            except requests.RequestException as e:
                print(f"Failed to recursively crawl: {href} with error: {e}")

# execute the crawler
crawler()