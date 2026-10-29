import csv
from unicodedata import name
import json
import os
from typing import List, Tuple
import math

#### CONSTANTS ####
FILENAME = "top_8419_european_cities.csv"
NUMBER_OF_CITIES = 8419
DEFAULT_TARGET_RANK = 8419
DEFAULT_MAX_LOSS = 8419
PADDINGS = {"Player": 20, "Score": 5, "Rank": 5, "Name": 20, "Population": 10}
MAX_MATCHES = 5
VERTICAL_SEPARATOR = "|"
HORIZONTAL_SEPARATOR = "-"
TABLE_PADDING = 1
####################

#### GLOBAL VARIABLES ####
cities = []
with open(FILENAME, "r", encoding="utf-8") as f:
    reader = csv.reader(f)
    header = next(reader)
    cities = list(reader)
    cities = [dict(zip(header, city)) for city in cities]
game_state = {
    "number_of_players": None,
    "player_names": [],
    "target_rank": None,
    "turns": []
}
number_of_players = 0
player_names = []
players = []
turn = 0
visible_cities = []
target_rank = DEFAULT_TARGET_RANK
####################

# def min_distance(str1, str2):
#     """
#     Calculate the minimum edit distance (Levenshtein distance) between two strings,
#     and return an optimal alignment.
#     """
#     m, n = len(str1), len(str2)
#     dp = [[0]*(n+1) for _ in range(m+1)]
#     back = [[None]*(n+1) for _ in range(m+1)]

#     for i in range(m+1):
#         dp[i][0] = i
#         back[i][0] = "U"  # Up: deletion
#     for j in range(n+1):
#         dp[0][j] = j
#         back[0][j] = "L"  # Left: insertion
#     back[0][0] = None

#     for i in range(1, m+1):
#         for j in range(1, n+1):
#             if str1[i-1] == str2[j-1]:
#                 dp[i][j] = dp[i-1][j-1]
#                 back[i][j] = "D"  # Diagonal: match
#             else:
#                 choices = [
#                     (dp[i-1][j] + 1, "U"),    # Deletion
#                     (dp[i][j-1] + 1, "L"),    # Insertion
#                     (dp[i-1][j-1] + 1, "D")   # Substitution
#                 ]
#                 dp[i][j], back[i][j] = min(choices)

#     # Traceback for alignment
#     align1, align2 = [], []
#     i, j = m, n
#     while i > 0 or j > 0:
#         if back[i][j] == "D":
#             align1.append(str1[i-1] if i > 0 else "-")
#             align2.append(str2[j-1] if j > 0 else "-")
#             i -= 1
#             j -= 1
#         elif back[i][j] == "U":
#             align1.append(str1[i-1])
#             align2.append("-")
#             i -= 1
#         elif back[i][j] == "L":
#             align1.append("-")
#             align2.append(str2[j-1])
#             j -= 1

#     return dp[m][n], "".join(reversed(align1)), "".join(reversed(align2))


def min_edit_alignment_linear(s: str, t: str, ins_cost: int = 1, del_cost: int = 1, sub_cost: int = 1):
    """
    Optimal global alignment via Hirschberg's algorithm (linear space).
    Returns:
        distance (int),
        aligned_s (str),  # '-' when there's a gap in s (i.e., insertion from t)
        aligned_t (str)   # '-' when there's a gap in t (i.e., deletion from s)
    Costs:
        ins_cost: cost to insert a character from t (gap in s)
        del_cost: cost to delete a character from s (gap in t)
        sub_cost: cost to substitute s[i] -> t[j] (0 if equal, else sub_cost)
    """
    def _nw_last_row(sa: str, tb: str) -> List[int]:
        # Last row of Needleman–Wunsch DP using O(len(tb)) space.
        m = len(tb)
        prev = [j * ins_cost for j in range(m + 1)]
        for si in sa:
            curr0 = prev0 = prev[0] + del_cost
            curr = [curr0] + [0] * m
            left = curr0
            for j, tj in enumerate(tb, start=1):
                cost_diag = prev[j - 1] + (0 if si == tj else sub_cost)
                cost_up   = prev[j] + del_cost
                cost_left = left + ins_cost
                val = min(cost_diag, cost_up, cost_left)
                curr[j] = val
                left = val
            prev = curr
        return prev

    def _base_align_len1(sa: str, tb: str) -> Tuple[str, str]:
        n, m = len(sa), len(tb)
        if n == 0:
            return "-" * m, tb
        if m == 0:
            return sa, "-" * n

        if n == 1:
            a = sa[0]
            # Option A: delete a, insert all tb
            cost_del = del_cost + m * ins_cost
            # Option B: substitute a with one tb[j], insert the rest
            best_sub = min((0 if a == b else sub_cost) for b in tb)
            j_best = min(range(m), key=lambda j: (0 if a == tb[j] else sub_cost))
            cost_sub = best_sub + (m - 1) * ins_cost
            if cost_del <= cost_sub:
                return a + "-" * m, "-" + tb
            else:
                return "-" * j_best + a + "-" * (m - j_best - 1), tb[:j_best] + tb[j_best] + tb[j_best+1:]

        # m == 1
        b = tb[0]
        cost_ins = ins_cost + n * del_cost
        best_sub = min((0 if a == b else sub_cost) for a in sa)
        i_best = min(range(n), key=lambda i: (0 if sa[i] == b else sub_cost))
        cost_sub = best_sub + (n - 1) * del_cost
        if cost_ins <= cost_sub:
            return sa + "-", "-" * n + b
        else:
            return sa[:i_best] + sa[i_best] + sa[i_best+1:], "-" * i_best + b + "-" * (n - i_best - 1)

    def _hirschberg(sa: str, tb: str) -> Tuple[str, str]:
        n, m = len(sa), len(tb)
        if n == 0:
            return "-" * m, tb
        if m == 0:
            return sa, "-" * n
        if n == 1 or m == 1:
            return _base_align_len1(sa, tb)

        i_mid = n // 2
        L = _nw_last_row(sa[:i_mid], tb)
        R = _nw_last_row(sa[i_mid:][::-1], tb[::-1])
        # Split point k that minimizes L[k] + R[m-k]
        k = min(range(m + 1), key=lambda j: L[j] + R[m - j])

        left_s, left_t = _hirschberg(sa[:i_mid], tb[:k])
        right_s, right_t = _hirschberg(sa[i_mid:], tb[k:])
        return left_s + right_s, left_t + right_t

    def _alignment_cost(al_s: str, al_t: str) -> int:
        cost = 0
        for a, b in zip(al_s, al_t):
            if a == b and a != '-':
                continue
            if a == '-':
                cost += ins_cost
            elif b == '-':
                cost += del_cost
            else:
                cost += sub_cost
        return cost

    al_s, al_t = _hirschberg(s, t)
    dist = _alignment_cost(al_s, al_t)
    return dist, al_s, al_t


def get_guess():
    """
    Get a guess from the player, ensuring it is a valid city name.
    """
    choice = None
    while True:
        guess = input("Enter your guess, or type 'quit' to exit: ").strip()
        if guess.lower() == "quit":
            return "quit"
        
        # create distance and alignments for all cities in the list
        distances = []
        for city in cities:
            city_name = city["City"]
            distance, align1, align2 = min_edit_alignment_linear(guess, city_name)
            distances.append({"Rank": city["Rank"], "Distance": distance, "Name": city_name, "align1": align1, "align2": align2})
        
        # sort by distance
        distances.sort(key=lambda x: x["Distance"])

        # print the closest cities
        print(f"These are the closest matches for '{guess}':")
        for i in range(MAX_MATCHES):
            city = distances[i]
            print(f"  {i + 1}. {city["Name"]}")
        print()

        # Enter choice
        while True:
            choice = input(f"Choose a match by number (1-{MAX_MATCHES}), write 'reguess' to try again, or send no guess: ").strip()

            if choice.lower() == "reguess":
                break

            if choice.isdigit() and 1 <= int(choice) <= MAX_MATCHES:
                chosen_city = distances[int(choice) - 1]
                return chosen_city["Rank"]
            
            if not choice:
                return None
            
            print("Invalid choice. Please try again.")
            print()

        print("You chose to reguess. Please enter a new guess.")
        print()

def print_table(data):
    headers = data[0].keys()
    column_widths = {header: max(len(header), max(len(str(row[header])) for row in data)) for header in headers}
    delimiter = " " * TABLE_PADDING + VERTICAL_SEPARATOR + " " * TABLE_PADDING
    table_width = sum(column_widths.values()) + len(headers) * len(delimiter) + 1
    table_line = " " * TABLE_PADDING + HORIZONTAL_SEPARATOR * table_width

    # Print header
    print(table_line)
    print(delimiter + delimiter.join(f"{header:<{column_widths[header]}}" for header in headers) + delimiter)
    print(table_line)

    # Print rows
    for row in data:
        row_strs = []
        for header in headers:
            value = str(row[header])
            # Align right if value is a number (including negative), else left
            if value.lstrip("-").replace(".", "", 1).isdigit():
                row_strs.append(f"{value:>{column_widths[header]}}")
            else:
                row_strs.append(f"{value:<{column_widths[header]}}")
        print(delimiter + delimiter.join(row_strs) + delimiter)
    print(table_line)

def save_game_state(filename):
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(game_state, f, indent=2)

def load_game_state(filename):
    with open(filename, "r", encoding="utf-8") as f:
        global game_state
        game_state = json.load(f)

def prompt_game_mode():
    while True:
        mode = input("Type 'new' to start a new game or 'continue' to resume: ").strip().lower()
        if mode in ["new", "continue"]:
            return mode
        print("Invalid input. Please type 'new' or 'continue'.")
        print()

def prompt_new_game_filename():
    while True:
        filename = input("Enter a filename for the new game (e.g., game1.json): ").strip()
        if filename and not os.path.exists(filename):
            return filename
        print("Invalid or existing filename. Please try again.")
        print()

def prompt_continue_game_filename():
    while True:
        filename = input("Enter the filename of the saved game to continue: ").strip()
        if os.path.exists(filename):
            return filename
        print("File not found. Please try again.")
        print()

def prompt_number_of_players():
    while True:
        number_of_players = input("Enter the number of players: ")
        if number_of_players.isdigit() and int(number_of_players) > 1:
            number_of_players = int(number_of_players)
            return number_of_players
        print("Invalid input. Please enter an integer greater than 1.")
        print()

def prompt_player_names(number_of_players):
    while True:
        player_names = input("Enter player names separated by commas: ").split(",")
        if len(player_names) == number_of_players and all(name.strip() != "" for name in player_names):
            return [name.strip() for name in player_names]
        print(f"Invalid input. Please enter exactly {number_of_players} player names separated by commas.")
        print()

def prompt_target_rank():
    while True:
        target_rank = input(f"Enter the target rank (default is {DEFAULT_TARGET_RANK}, press Enter to use default): ")
        if not target_rank:
            return DEFAULT_TARGET_RANK
        if target_rank.isdigit() and 1 < int(target_rank) <= NUMBER_OF_CITIES:
            return int(target_rank)
        print(f"Invalid input. Please enter a positive integer higher than 1 and less than or equal to {NUMBER_OF_CITIES}.")
        print()

def load_game(filename):
    load_game_state(filename)
    global number_of_players, player_names, target_rank, players, turn, visible_cities
    number_of_players = game_state["number_of_players"]
    player_names = game_state["player_names"]
    target_rank = game_state["target_rank"]
    turns = game_state["turns"]
    players = [{"Name": name, "Score": 0} for name in player_names]
    # Replay turns to rebuild state
    for t in turns:
        player_id = t["player_id"]
        choice = t["choice"]
        if choice is None:
            players[player_id]["Score"] -= DEFAULT_MAX_LOSS
        else:
            chosen_city = cities[choice - 1]
            if choice in [int(city["Rank"]) for city in visible_cities]:
                pass
            elif choice <= target_rank:
                players[player_id]["Score"] += choice
            else:
                players[player_id]["Score"] -= math.floor(math.pow(choice - target_rank, 0.618))
            if choice not in [int(city["Rank"]) for city in visible_cities]:
                visible_cities.append(chosen_city)
                visible_cities.sort(key=lambda x: int(x["Rank"]))
        turn += 1

if __name__ == "__main__":
    print()
    print("Welcome to the Cities Rank Game!")

    mode = prompt_game_mode()
    print(f"Game mode selected: {mode}")
    print()

    if mode == "continue":
        filename = prompt_continue_game_filename()
        print(f"Continuing game from file: {filename}")
        print()
        load_game(filename)
        print(f"Game loaded. {number_of_players} players: {", ".join(player_names)}. Target rank: {target_rank}.")
        print()
        print_table(visible_cities)
        print()
        print_table(players)
        print()
    else:
        filename = prompt_new_game_filename()
        print(f"Starting a new game. File: {filename}")
        print()
        number_of_players = prompt_number_of_players()
        print(f"Number of players selected: {number_of_players}")
        print()
        player_names = prompt_player_names(number_of_players)
        print(f"Player names: {", ".join(player_names)}")
        print()
        target_rank = prompt_target_rank()
        print(f"Target rank set to: {target_rank}")
        print()

        players = [{"Name": name, "Score": 0} for name in player_names]
        game_state["number_of_players"] = number_of_players
        game_state["player_names"] = [player["Name"] for player in players]
        game_state["target_rank"] = target_rank
        game_state["turns"] = []
        print("Game initialized.")

    # Main game loop
    while True:
        player_id = turn % number_of_players
        player_name = players[player_id]["Name"]
        print(f"Turn {turn + 1}")
        print(f"Player: {player_name}")
        print()

        # Get player's guess
        choice = get_guess()

        # Save turn info
        turn_info = {"player_id": player_id, "choice": None}
        if choice is None:
            print(f"No guess made. You lose {DEFAULT_MAX_LOSS} points.")
            print()
            players[player_id]["Score"] -= DEFAULT_MAX_LOSS
            turn_info["choice"] = None
            turn += 1
            game_state["turns"].append(turn_info)
            save_game_state(filename)
            continue

        if choice == "quit":
            print("Game ended.")
            print()
            break

        choice = int(choice)
        turn_info["choice"] = choice
        chosen_city = cities[choice - 1]
        print(f"Player {player_name} guessed n.{choice}: {chosen_city["City"]}")

        if choice in [int(city["Rank"]) for city in visible_cities]:
            print(f"City {chosen_city["City"]} is already visible. Player {player_name} loses a turn")
        elif choice <= target_rank:
            players[player_id]["Score"] += choice
            print(f"Player {player_name} gained {choice} points")
        else:
            players[player_id]["Score"] -= math.floor(math.pow(choice - target_rank, 0.618))
            print(f"Player {player_name} lost {math.floor(math.pow(choice - target_rank, 0.618))} points")

        if choice not in [int(city["Rank"]) for city in visible_cities]:
            visible_cities.append(chosen_city)
            visible_cities.sort(key=lambda x: int(x["Rank"]))

        print()
        print_table(visible_cities)
        print()
        print_table(players)
        print()

        turn += 1
        game_state["turns"].append(turn_info)
        save_game_state(filename)

    # Print final scores and winner
    print("Final Scores:")
    print_table(players)

    winner = max(players, key=lambda x: x["Score"])
    print(f"\nWinner: {winner["Name"]} with {winner["Score"]} points!")
