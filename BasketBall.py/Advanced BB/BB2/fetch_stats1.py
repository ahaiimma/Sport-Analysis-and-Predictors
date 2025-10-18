# fetch_stats.py
import os
import re
import requests
import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import random
import time
import cloudscraper
try:
    from nba_api.stats.static import teams as nba_teams
    NBA_AVAILABLE = True
except Exception:
    NBA_AVAILABLE = False

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

BASE_API = "http://b8c40s8.143.198.70.30.sslip.io/api"

# -------------------- TEAM MAP --------------------
BR_TEAM_MAP = {
    "Atlanta Hawks": "ATL", "Boston Celtics": "BOS", "Brooklyn Nets": "BRK",
    "Charlotte Hornets": "CHA", "Chicago Bulls": "CHI", "Cleveland Cavaliers": "CLE",
    "Dallas Mavericks": "DAL", "Denver Nuggets": "DEN", "Detroit Pistons": "DET",
    "Golden State Warriors": "GSW", "Houston Rockets": "HOU", "Indiana Pacers": "IND",
    "Los Angeles Clippers": "LAC", "Los Angeles Lakers": "LAL", "Memphis Grizzlies": "MEM",
    "Miami Heat": "MIA", "Milwaukee Bucks": "MIL", "Minnesota Timberwolves": "MIN",
    "New Orleans Pelicans": "NOP", "New York Knicks": "NYK", "Oklahoma City Thunder": "OKC",
    "Orlando Magic": "ORL", "Philadelphia 76ers": "PHI", "Phoenix Suns": "PHX",
    "Portland Trail Blazers": "POR", "Sacramento Kings": "SAC", "San Antonio Spurs": "SAS",
    "Toronto Raptors": "TOR", "Utah Jazz": "UTA", "Washington Wizards": "WAS"
}

# -------------------- LEAGUE DETECTION --------------------
EUROLEAGUE_KEYWORDS = ['fenerbahce', 'anadolu efes', 'real madrid', 'barcelona', 'maccabi']
FIBA_KEYWORDS = ['serbia', 'slovenia', 'spain']

def detect_league(team_name: str):
    t = team_name.lower()
    if any(k in t for k in EUROLEAGUE_KEYWORDS):
        return 'EUROLEAGUE'
    if any(k in t for k in FIBA_KEYWORDS):
        return 'FIBA'
    return 'NBA'

# -------------------- BASKETBALL REFERENCE SCRAPING --------------------

USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; rv:122.0) Gecko/20100101 Firefox/122.0",
]

COLUMN_MAP = {
    "No.": "No",
    "Player": "Player_Name",
    "Pos": "Role",
    "Ht": "Height",
    "Wt": "Weight",
    "Birth Date": "Birth_Date",
    "Birth": "Birth_Place",
    "Exp": "Experience",
    "College": "College"
}

def normalize_columns(df):
    # Match dynamically (case-insensitive)
    mapping = {}
    for col in df.columns:
        col_clean = col.strip()
        if col_clean in COLUMN_MAP:
            mapping[col] = COLUMN_MAP[col_clean]
        else:
            mapping[col] = col_clean.replace(" ", "_")
    return df.rename(columns=mapping)


def fetch_br_roster(team_abbr: str, season_year: str):
    team_abbr = team_abbr.upper().strip()
    scraper = cloudscraper.create_scraper(browser={
        'browser': 'chrome',
        'platform': 'windows',
        'mobile': False
    })
    
    url = f"https://www.basketball-reference.com/teams/{team_abbr}/{season_year}.html"
    print(f"📡 Fetching roster from {url}")

    r = scraper.get(url, timeout=10)
    if r.status_code != 200:
        print(f"⚠️ Failed to fetch roster: {r.status_code}")
        return pd.DataFrame()

    soup = BeautifulSoup(r.text, "lxml")
    roster_table = soup.find("table", id="roster")
    if not roster_table:
        print("⚠️ No roster table found.")
        return pd.DataFrame()
    
        df_list = pd.read_html(html)
        df = df_list[0]

    df = pd.read_html(str(roster_table))[0]
    df = df.rename(columns={'Player': 'Player_Name', 'Pos': 'Role'})

    df = pd.read_html(str(roster_table))[0]
    df = normalize_columns(df)

    # Filter only real players — if "No" is NaN or not a number, it's probably a header row
    df = df[df["No"].apply(lambda x: str(x).isdigit())].copy()


    

    # Skip rows with invalid player names (e.g., headers)
    invalid_names = ["No.", "Player", "Pos", "Ht", "Wt", "Birth Date", "Exp", "College"]
    df = df[~df["Player_Name"].isin(invalid_names)].copy()

    return df
# -------------------- API PLAYER STATS --------------------
def fetch_player_stats_from_api(player_name: str, season: int):
    url = f"{BASE_API}/PlayerDataTotals/query"
    params = {"playerName": player_name, "season": season}
    try:
        r = requests.get(url, params=params, timeout=10)
    except Exception as e:
        print(f"❌ API request failed for {player_name}: {e}")
        return {}

    if r.status_code != 200:
        print(f"⚠ API returned {r.status_code} for {player_name}")
        return {}

    data = r.json()
    if not data:
        print(f"⚠ No stats returned for {player_name}")
        return {}
    return data[0]

# -------------------- ROLE MAPPING --------------------
def map_role(pos):
    if pd.isna(pos):
        return np.nan
    pos = str(pos).upper()
    if pos in ["PG", "SG"]:
        return "Guard"
    if pos in ["SF", "PF"]:
        return "Forward"
    if pos == "C":
        return "Center"
    return pos

# -------------------- EURO/FIBA SCRAPERS --------------------
def fetch_euroleague_team(team_name: str):
    print(f"📡 Fetching EuroLeague data for {team_name}")
    return pd.DataFrame([{"Player_Name": "Placeholder Player", "Role": "Forward", "Team": team_name}])

def fetch_fiba_team(team_name: str):
    print(f"📡 Fetching FIBA data for {team_name}")
    return pd.DataFrame([{"Player_Name": "Placeholder Player", "Role": "Forward", "Team": team_name}])

# -------------------- MAIN TEAM DATA FETCH --------------------
def fetch_team_data(team_name: str, season_year="2025", refresh=False):
    team_name = team_name.strip()
    INVALID_TEAM_NAMES = ["No.", "Player_Name", "Role", "Ht", "Wt", "Birth Date", 
                      "Birth", "Exp", "College", "Player"]

    if team_name in INVALID_TEAM_NAMES:
        print(f"⏩ Skipping invalid team name: {team_name}")
        return pd.DataFrame(columns=["Player_Name", "Role", "Team"])

    cache_file = os.path.join(CACHE_DIR, f"{team_name.replace(' ', '_')}_{season_year}.csv")

    if os.path.exists(cache_file) and not refresh:
        print(f"💾 Loading cached data for {team_name}")
        return pd.read_csv(cache_file)

    league = detect_league(team_name)
    df = pd.DataFrame()

    if league == "NBA":
        abbr = BR_TEAM_MAP.get(team_name)
        if not abbr:
            print(f"❌ No abbreviation for team: '{team_name}'")
            return pd.DataFrame(columns=["Player_Name", "Role", "Team"])
        roster_df = fetch_br_roster(abbr, season_year)
        if roster_df.empty:
            print(f"⚠ No roster data for {team_name}")
            return pd.DataFrame(columns=["Player_Name", "Role", "Team"])

        roster_df["Role"] = roster_df["Role"].apply(map_role)
        stats_list = []
        for _, player in roster_df.iterrows():
            # Place the check for invalid player names here
            if player["Player_Name"] in ["No.", "Player", "Player_Name", "Pos", "Role", "Ht", "Wt", "Birth Date", "Birth", "Exp", "College"]:
                continue # This will skip to the next iteration of the loop
            
            stats = fetch_player_stats_from_api(player["Player_Name"], int(season_year))
            stats_row = {**player.to_dict(), **stats}
            stats_list.append(stats_row)
        df = pd.DataFrame(stats_list)

    elif league == "EUROLEAGUE":
        df = fetch_euroleague_team(team_name)
    elif league == "FIBA":
        df = fetch_fiba_team(team_name)

    if not df.empty:
        df.to_csv(cache_file, index=False)
        print(f"✅ Saved data for {team_name} to cache")
    else:
        print(f"⚠ No data to save for {team_name}")

    return df if not df.empty else pd.DataFrame(columns=["Player_Name", "Role", "Team"])
