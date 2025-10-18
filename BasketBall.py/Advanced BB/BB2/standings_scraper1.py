# standings_scraper.py
import os
import time
import requests
import pandas as pd
import matplotlib.pyplot as plt
from bs4 import BeautifulSoup
from datetime import datetime

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_EXPIRY = 60 * 60 * 6  # 6 hours

def cache_path(league):
    return os.path.join(CACHE_DIR, f"{league.lower()}_standings.csv")

def load_cached_standings(league):
    path = cache_path(league)
    if os.path.exists(path):
        if time.time() - os.path.getmtime(path) < CACHE_EXPIRY:
            return pd.read_csv(path)
    return None

def save_cached_standings(league, df):
    df.to_csv(cache_path(league), index=False)

def fetch_nba_standings():
    url = "https://www.espn.com/nba/standings"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        tables = soup.select("table.Table")
        standings = []
        for table in tables:
            for row in table.select("tbody tr"):
                cols = [c.get_text(strip=True) for c in row.select("td")]
                team = row.select_one("span.hide-mobile").get_text(strip=True) if row.select_one("span.hide-mobile") else None
                if team and len(cols) >= 10:
                    standings.append({
                        "Team": team,
                        "W": cols[0],
                        "L": cols[1],
                        "Win%": cols[2],
                        "GB": cols[3],
                        "PTS": cols[7] if len(cols) > 7 else None
                    })
        return pd.DataFrame(standings)
    except Exception as e:
        print(f"Error fetching NBA standings: {e}")
        return pd.DataFrame()

def fetch_euroleague_standings():
    url = "https://www.euroleaguebasketball.net/euroleague/standings/"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        standings = []
        for row in soup.select("table.standings-table tbody tr"):
            cols = [c.get_text(strip=True) for c in row.select("td")]
            if len(cols) >= 5:
                standings.append({
                    "Team": cols[1],
                    "W": cols[2],
                    "L": cols[3],
                    "Win%": None,
                    "GB": None,
                    "PTS": None
                })
        return pd.DataFrame(standings)
    except Exception as e:
        print(f"Error fetching EuroLeague standings: {e}")
        return pd.DataFrame()

def fetch_fiba_standings():
    url = "https://www.fiba.basketball/worldcup/2023/standings"
    try:
        r = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
        r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        standings = []
        for row in soup.select("table.standings tbody tr"):
            cols = [c.get_text(strip=True) for c in row.select("td")]
            if len(cols) >= 4:
                standings.append({
                    "Team": cols[1],
                    "W": cols[2],
                    "L": cols[3],
                    "Win%": None,
                    "GB": None,
                    "PTS": None
                })
        return pd.DataFrame(standings)
    except Exception as e:
        print(f"Error fetching FIBA standings: {e}")
        return pd.DataFrame()

def get_standings(league, refresh=False):
    league = league.upper()
    if not refresh:
        cached = load_cached_standings(league)
        if cached is not None:
            return cached

    if league == "NBA":
        df = fetch_nba_standings()
    elif league == "EUROLEAGUE":
        df = fetch_euroleague_standings()
    elif league == "FIBA":
        df = fetch_fiba_standings()
    else:
        raise ValueError(f"Unknown league: {league}")

    if not df.empty:
        save_cached_standings(league, df)
    return df

def analyze_standings(df, league):
    if df.empty:
        print("No standings data to analyze.")
        return

    print(f"\n--- {league} Standings Analysis ---")
    df["Win%"] = pd.to_numeric(df["Win%"], errors="coerce")
    df["W"] = pd.to_numeric(df["W"], errors="coerce")
    df["L"] = pd.to_numeric(df["L"], errors="coerce")

    # Top 5 teams by Win%
    top_teams = df.sort_values(by="Win%", ascending=False).head(5)
    print("\nTop 5 Teams by Win%:")
    print(top_teams[["Team", "W", "L", "Win%"]])

    # Plot standings
    plt.figure(figsize=(10, 6))
    plt.barh(top_teams["Team"], top_teams["Win%"], color="skyblue")
    plt.title(f"Top 5 {league} Teams by Win%")
    plt.xlabel("Win Percentage")
    plt.ylabel("Team")
    plt.tight_layout()
    plt.show()

if __name__ == "__main__":
    for lg in ["NBA", "EUROLEAGUE", "FIBA"]:
        print(f"\n{lg} Standings:")
        standings = get_standings(lg)
        print(standings.head(10))
        analyze_standings(standings, lg)