import requests
import os
import zipfile
from math import log10

# Download the GeoNames cities15000.txt file (contains cities with >15,000 population)
url = "https://download.geonames.org/export/dump/cities15000.zip"
filename = "cities15000.zip"

# Download and extract the file if not present

if not os.path.exists("cities15000.txt"):
    print("Downloading dataset...")
    r = requests.get(url)
    with open(filename, "wb") as f:
        f.write(r.content)
    with zipfile.ZipFile(filename, 'r') as zip_ref:
        zip_ref.extractall(".")

# Read and filter European cities
europe_countries = {
    'AL', 'AD', 'AM', 'AT', 'AZ', 'BY', 'BE', 'BA', 'BG', 'HR',
    'CY', 'CZ', 'DK', 'EE', 'FI', 'FR', 'GE', 'DE', 'GR', 'HU',
    'IS', 'IE', 'IT', 'KZ', 'XK', 'LV', 'LI', 'LT', 'LU', 'MT',
    'MD', 'MC', 'ME', 'NL', 'MK', 'NO', 'PL', 'PT', 'RO', 'RU',
    'SM', 'RS', 'SK', 'SI', 'ES', 'SE', 'CH', 'TR', 'UA', 'GB',
    'VA'
}

european_union_countries = {
    'AT', 'BE', 'BG', 'CY', 'CZ', 'DE', 'DK', 'EE', 'ES', 'FI',
    'FR', 'GR', 'HR', 'HU', 'IE', 'IT', 'LT', 'LU', 'LV', 'MT',
    'NL', 'PL', 'PT', 'RO', 'SE', 'SI', 'SK'
}
cities = []
with open("cities15000.txt", encoding="utf-8") as f:
    for line in f:
        parts = line.strip().split('\t')
        name = parts[1]
        country = parts[8]
        population = int(parts[14])
        lat = parts[4]
        lon = parts[5]
        if country in europe_countries:
            cities.append({
                "name": name,
                "country": country,
                "population": population,
                "lat": lat,
                "lon": lon
            })

# Sort by population and take top 200 (descending order)
cities.sort(key=lambda x: x["population"], reverse=True)
number_of_cities = len(cities)
if number_of_cities > len(cities):
    number_of_cities = len(cities)
number_padding = log10(number_of_cities) + 1
padding = 2
column_names = {
    "name": "City",
    "country": "Country",
    "population": "Population"
}
top_cities = cities[:number_of_cities]


paddings = {key: max(len(value), padding) for key, value in column_names.items()}
for column, head in column_names.items():
    # Calculate the padding length
    paddings[column] = max(len(head), max(len(str(city[column])) for city in top_cities)) + 2

print(paddings)
# Write to text file
with open(f"top_{number_of_cities}_european_cities.txt", "w", encoding="utf-8") as f:
    f.write(f"{'Rank':<5}{'City':<{paddings['name']}}{'Country':<{paddings['country']}}{'Population':>{paddings['population']}}\n")
    for i, city in enumerate(top_cities, 1):
        f.write(f"{i:<5}{city['name']:<{paddings['name']}}{city['country']:<{paddings['country']}}{city['population']:>{paddings['population']},}\n")

with open(f"top_{number_of_cities}_european_cities.csv", "w", encoding="utf-8") as f:
    f.write("Rank,City,Country,Population\n")
    for i, city in enumerate(top_cities, 1):
        f.write(f"{i},{city['name']},{city['country']},{city['population']}\n")
print(f"File 'top_{number_of_cities}_european_cities.txt' created.")
