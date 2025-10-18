# basketball_data_collector.py
import pandas as pd
import numpy as np
from fetch_stats import fetch_team_data
#from basketball_data_collector_manual import collect_players_manual  # fallback if you prefer full manual

# We'll implement a function that tries to fetch team data; if not enough data, fallback to prompting manually.
def collect_players_auto_or_manual():
    teams = []
    for side in ['A', 'B']:
        team_name = input(f"Enter Team {side} name: ")
        print(f"Fetching data for {team_name} ...")
        df_team = fetch_team_data(team_name)
        if df_team.empty:
            print(f"No automatic data found for '{team_name}'. Falling back to manual entry.")
            # call your previous manual collector for that team (you must have `basketball_data_collector_manual.py`)
            # If you don't have that file, we prompt minimally here
            # For simplicity we will ask for 3 players manually (Guard/Forward/Center)
            manual_rows = []
            for role in ['guard', 'forward', 'center']:
                name = input(f"Enter {role} name for {team_name}: ")
                # minimal required columns for the analyzer; they can be filled later
                manual_rows.append({
                    'Player_Name': name, 'Team': team_name, 'Role': role.capitalize(),
                    'PPG': np.nan, 'APG': np.nan, 'RPG': np.nan, 'BPG': np.nan,
                    'SPG': np.nan, 'FG_Pct': np.nan, '3P_Pct': np.nan, 'PER': np.nan,
                    'Minutes_Played': np.nan
                })
            df_team = pd.DataFrame(manual_rows)
        else:
            # ensure necessary columns exist (fill with NaN if missing)
            expected = ['Player_Name','Team','Role','PPG','APG','RPG','BPG','SPG','FG_Pct','3P_Pct','PER','Minutes_Played']
            for c in expected:
                if c not in df_team.columns:
                    df_team[c] = np.nan
            # Some scraped sources may not include Role; try to map from Position or set default
            if 'Role' not in df_team.columns:
                df_team['Role'] = df_team.get('Position', 'Forward').fillna('Forward')
        teams.append(df_team)
    # combine both teams into single df
    df_all = pd.concat(teams, ignore_index=True, sort=False)
    return df_all

# If you prefer the previous manual collector, import and call collect_players_manual()
# def collect_players():
#     return collect_players_manual()
