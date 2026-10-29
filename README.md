# Cities Rank Game

A terminal party game about European geography. Players take turns naming a city; each city is looked up in a ranking of 8,419 European cities by population and the player scores its rank if it is at or below the agreed target rank, or loses points that grow as (rank - target)^0.618 if the city is too small. Repeated cities score nothing. Typed names are matched fuzzily against the whole list with an edit-distance alignment computed in linear space (Hirschberg's divide-and-conquer version of Needleman-Wunsch), and the player picks among the five closest matches. Game state is saved to JSON after every turn so a game can be resumed.

## How to run
Python 3, standard library only. `python europe_cities.py` downloads GeoNames `cities15000.zip`, filters European country codes and writes `top_N_european_cities.csv/.txt`; `python rank_game.py` starts or continues a game. `edit_distance_efficient.py` holds the standalone alignment function.

## Notes
- City data comes from the GeoNames `cities15000` dump (cities with population above 15,000), licensed CC BY 4.0.
- `AB.json` and `prova.json` are saved games.
