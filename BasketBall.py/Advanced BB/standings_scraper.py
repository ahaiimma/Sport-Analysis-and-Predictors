# standings_scraper.py
import os
import time
import pandas as pd
import requests
from bs4 import BeautifulSoup

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)

CACHE_EXPIRY = 60 * 60 * 6  # 6 hours

# ------------------- NBA -------------------
try:
    from nba_api.stats.endpoints import leaguestandings
    NBA_AVAILABLE = True
except ImportError:
    NBA_AVAILABLE = False

def cache_path(filename):
    return os.path.join(CACHE_DIR, filename)

def is_cache_fresh(path):
    return os.path.exists(path) and (time.time() - os.path.getmtime(path) < CACHE_EXPIRY)

def get_nba_standings(refresh=False):
    cache_file = cache_path("nba_standings.csv")
    if not refresh and is_cache_fresh(cache_file):
        return pd.read_csv(cache_file)

    if not NBA_AVAILABLE:
        raise RuntimeError("nba_api not installed, cannot fetch NBA standings.")

    standings = leaguestandings.LeagueStandings().get_data_frames()[0]
    standings.to_csv(cache_file, index=False)
    return standings

# ------------------- EuroLeague -------------------
def get_euroleague_standings(refresh=False):
    cache_file = cache_path("euroleague_standings.csv")
    if not refresh and is_cache_fresh(cache_file):
        return pd.read_csv(cache_file)

    url = "https://www.euroleaguebasketball.net/euroleague/standings/"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "lxml")

    data = []
    table = soup.find("table")
    if table:
        for row in table.select("tbody tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if cols:
                data.append(cols)

    df = pd.DataFrame(data)
    df.to_csv(cache_file, index=False)
    return df

# ------------------- FIBA -------------------
def get_fiba_standings(refresh=False):
    cache_file = cache_path("fiba_standings.csv")
    if not refresh and is_cache_fresh(cache_file):
        return pd.read_csv(cache_file)

    url = "https://www.fiba.basketball/worldcup/2023/standings"
    r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
    soup = BeautifulSoup(r.text, "lxml")

    data = []
    table = soup.find("table")
    if table:
        for row in table.select("tbody tr"):
            cols = [c.get_text(strip=True) for c in row.find_all("td")]
            if cols:
                data.append(cols)

    df = pd.DataFrame(data)
    df.to_csv(cache_file, index=False)
    return df

# ------------------- Public wrapper -------------------
def get_all_standings(league, refresh=False):
    if league.upper() == "NBA":
        return get_nba_standings(refresh)
    elif league.upper() == "EUROLEAGUE":
        return get_euroleague_standings(refresh)
    elif league.upper() == "FIBA":
        return get_fiba_standings(refresh)
    else:
        raise ValueError(f"Unknown league: {league}")
