# fetch_stats.py
import os
import re
import time
import difflib
import requests
import numpy as np
import pandas as pd
from bs4 import BeautifulSoup

CACHE_DIR = "cache"
os.makedirs(CACHE_DIR, exist_ok=True)
CACHE_EXPIRY = 60 * 60 * 6  # 6 hours

# Optional NBA API
try:
    from nba_api.stats.static import teams as nba_teams
    from nba_api.stats.endpoints import leaguedashplayerstats, commonteamroster
    NBA_AVAILABLE = True
except ImportError:
    NBA_AVAILABLE = False

EUROLEAGUE_KEYWORDS = ['fenerbahce', 'anadolu efes', 'real madrid', 'barcelona', 'maccabi']
FIBA_KEYWORDS = ['serbia', 'slovenia', 'spain']

def is_cache_fresh(path):
    return os.path.exists(path) and (time.time() - os.path.getmtime(path) < CACHE_EXPIRY)

def slugify(name):
    return re.sub(r'[^a-z0-9]+', '_', name.lower()).strip('_')

def detect_league(team_name):
    t = team_name.lower()
    if NBA_AVAILABLE:
        all_teams = nba_teams.get_teams()
        if any(team_name.lower() in tinfo['full_name'].lower() for tinfo in all_teams):
            return 'NBA'
    if any(k in t for k in EUROLEAGUE_KEYWORDS):
        return 'EUROLEAGUE'
    if any(k in t for k in FIBA_KEYWORDS):
        return 'FIBA'
    return 'AUTO'

# ------------------- NBA fetch -------------------
def fetch_nba_team(team_name, season=None):
    all_teams = nba_teams.get_teams()
    team_names = [t['full_name'] for t in all_teams]
    match = difflib.get_close_matches(team_name, team_names, n=1, cutoff=0.5)
    if not match:
        raise ValueError(f"No NBA team found matching '{team_name}'")
    team = next(t for t in all_teams if t['full_name'] == match[0])
    team_id = team['id']

    if not season:
        from datetime import datetime
        year = datetime.now().year
        month = datetime.now().month
        if month >= 10:
            season = f"{year}-{str(year+1)[-2:]}"
        else:
            season = f"{year-1}-{str(year)[-2:]}"

    try:
        roster = commonteamroster.CommonTeamRoster(team_id=team_id, season=season)
        roster_df = roster.get_data_frames()[0][['PLAYER', 'PLAYER_ID', 'POSITION']]
        stats = leaguedashplayerstats.LeagueDashPlayerStats(season=season, team_id_nullable=team_id)
        stats_df = stats.get_data_frames()[0]

        roster_df['PLAYER_norm'] = roster_df['PLAYER'].str.lower().str.replace(r'[^a-z ]', '', regex=True)
        stats_df['PLAYER_NAME_norm'] = stats_df['PLAYER_NAME'].str.lower().str.replace(r'[^a-z ]', '', regex=True)
        merged = pd.merge(roster_df, stats_df, left_on='PLAYER_norm', right_on='PLAYER_NAME_norm', how='left')

        rows = []
        for _, row in merged.iterrows():
            rows.append({
                'Player_Name': row['PLAYER'],
                'Team': team['full_name'],
                'Position': row['POSITION'],
                'PPG': row.get('PTS'),
                'APG': row.get('AST'),
                'RPG': row.get('REB'),
                'BPG': row.get('BLK'),
                'SPG': row.get('STL'),
                'FG_Pct': row.get('FG_PCT'),
                '3P_Pct': row.get('FG3_PCT'),
                'True_Shooting_Pct': row.get('TS_PCT', np.nan),
                'Usage_Rate': row.get('USG_PCT', np.nan),
                'PER': row.get('PLAYER_EFFICIENCY_RATING', np.nan),
                'Minutes_Played': row.get('MIN'),
                'Shots': row.get('FGA')
            })
        return pd.DataFrame(rows)
    except Exception as e:
        print(f"NBA fetch failed for {team_name}: {e}")
        return pd.DataFrame([])

# ------------------- EuroLeague fetch -------------------
def fetch_euroleague_team(team_name):
    search_url = f"https://www.google.com/search?q={team_name}+site:euroleaguebasketball.net"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        link = None
        for a in soup.select("a"):
            href = a.get('href', '')
            if 'euroleaguebasketball.net' in href and '/team' in href:
                m = re.search(r'(https?://[^&]+)', href)
                if m:
                    link = m.group(1)
                    break
        if not link:
            return pd.DataFrame([])

        r2 = requests.get(link, headers=headers, timeout=10)
        soup2 = BeautifulSoup(r2.text, "lxml")
        players = []
        table = soup2.find('table')
        if table:
            for tr in table.select('tbody tr'):
                cols = tr.find_all('td')
                if cols:
                    players.append({'Player_Name': cols[0].get_text(strip=True), 'Team': team_name})
        return pd.DataFrame(players)
    except Exception as e:
        print(f"EuroLeague fetch failed: {e}")
        return pd.DataFrame([])

# ------------------- FIBA fetch -------------------
def fetch_fiba_team(team_name):
    search_url = f"https://www.google.com/search?q={team_name}+site:fiba.basketball"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        r = requests.get(search_url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, "lxml")
        link = None
        for a in soup.select("a"):
            href = a.get('href', '')
            if 'fiba.basketball' in href and '/team' in href:
                m = re.search(r'(https?://[^&]+)', href)
                if m:
                    link = m.group(1)
                    break
        if not link:
            return pd.DataFrame([])
        r2 = requests.get(link, headers=headers, timeout=10)
        soup2 = BeautifulSoup(r2.text, "lxml")
        players = []
        for p in soup2.select(".player-name, .playerName, a.player"):
            name = p.get_text(strip=True)
            if name:
                players.append({'Player_Name': name, 'Team': team_name})
        return pd.DataFrame(players)
    except Exception as e:
        print(f"FIBA fetch failed: {e}")
        return pd.DataFrame([])

# ------------------- Wrapper with caching -------------------
def fetch_team_data(team_name, refresh=False):
    league = detect_league(team_name)
    cache_file = os.path.join(CACHE_DIR, f"{league.lower()}_{slugify(team_name)}.csv")

    if not refresh and is_cache_fresh(cache_file):
        return pd.read_csv(cache_file)

    if league == 'NBA' and NBA_AVAILABLE:
        df = fetch_nba_team(team_name)
    elif league == 'EUROLEAGUE':
        df = fetch_euroleague_team(team_name)
    elif league == 'FIBA':
        df = fetch_fiba_team(team_name)
    else:
        df = pd.DataFrame([])

    df.to_csv(cache_file, index=False)
    return df
