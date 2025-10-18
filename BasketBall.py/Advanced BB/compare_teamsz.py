# compare_teams.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
import os

# Import the functionality from your two other scripts
# Assuming standings_scraper.py and fetch_stats.py are in the same directory
from standings_scraper import get_standings, apply_home_advantage
from fetch_stats import fetch_team_data, detect_league

sns.set(style="whitegrid")

# --- New Functionality: Team-wide Analysis ---
def compare_teams_overall(team_a_name, team_b_name, standings_df, home_team):
    """
    Compares two teams based on their win percentage and win probability.
    """
    print("\n--- Overall Team Comparison ---")
    
    # Get team win percentages
    team_a_stats = standings_df[standings_df['Team'].str.contains(team_a_name, case=False, na=False)]
    team_b_stats = standings_df[standings_df['Team'].str.contains(team_b_name, case=False, na=False)]

    if team_a_stats.empty or team_b_stats.empty:
        print("Could not find one or both teams in the standings.")
        return

    team_a_pct = team_a_stats['WinPct'].iloc[0]
    team_b_pct = team_b_stats['WinPct'].iloc[0]
    
    # Apply home advantage sentiment
    sentiment_a, sentiment_b = apply_home_advantage(team_a_name, team_b_name, standings_df, home_team)
    
    # Calculate a simple weighted win probability
    total_pct = team_a_pct * sentiment_a + team_b_pct * sentiment_b
    if total_pct > 0:
        win_prob_a = (team_a_pct * sentiment_a) / total_pct
        win_prob_b = (team_b_pct * sentiment_b) / total_pct
    else:
        win_prob_a = 0.5
        win_prob_b = 0.5

    print(f"{team_a_name} ({team_a_pct:.3f}) vs. {team_b_name} ({team_b_pct:.3f})")
    print(f"Home Team: {home_team}")
    print(f"Projected Win Probability:")
    print(f"  - {team_a_name}: {win_prob_a:.2%} (Sentiment: {sentiment_a:.2f})")
    print(f"  - {team_b_name}: {win_prob_b:.2%} (Sentiment: {sentiment_b:.2f})")

def analyze_positional_matchups(df_a, df_b):
    """
    Analyzes and visualizes player-by-player positional matchups.
    """
    print("\n--- Positional Matchup Analysis ---")
    df_all = pd.concat([df_a, df_b])
    
    # Find the top player in each role for each team
    top_players = {}
    for team in df_all['Team'].unique():
        team_df = df_all[df_all['Team'] == team]
        for role in team_df['Role'].unique():
            role_df = team_df[team_df['Role'] == role].sort_values('PPG', ascending=False)
            if not role_df.empty:
                top_players[(team, role)] = role_df.iloc[0]
    
    matchup_data = []
    for role in ['Guard', 'Forward', 'Center']:
        player_a = top_players.get((df_a['Team'].iloc[0], role))
        player_b = top_players.get((df_b['Team'].iloc[0], role))
        
        if player_a is not None and player_b is not None:
            matchup_data.append({
                'Role': role,
                f"{df_a['Team'].iloc[0]}_Player": player_a['Player_Name'],
                f"{df_b['Team'].iloc[0]}_Player": player_b['Player_Name'],
                f"{df_a['Team'].iloc[0]}_PPG": player_a['PPG'],
                f"{df_b['Team'].iloc[0]}_PPG": player_b['PPG']
            })
            
    matchup_df = pd.DataFrame(matchup_data)
    print(matchup_df)
    
    if not matchup_df.empty:
        plt.figure(figsize=(12, 7))
        matchup_df.set_index('Role').plot(kind='bar', figsize=(12, 7))
        plt.title('Top Players PPG Comparison by Role')
        plt.ylabel('Points Per Game')
        plt.xlabel('Position')
        plt.xticks(rotation=0)
        plt.show()

# --- Player-level Analysis (Original functions, now more robust) ---
def analyze_guards(df_guards):
    """Analyzes guard performance with a focus on playmaking and scoring."""
    if df_guards.empty:
        print("No guard data to analyze.")
        return

    print("\n--- Guard Analysis (Playmaking & Scoring) ---")
    df = df_guards.copy()
    
    # Handle missing values
    df['TOV'] = df['TOV'].fillna(0)
    df['APG'] = df['APG'].fillna(0)
    df['PPG'] = df['PPG'].fillna(0)
    df['SPG'] = df['SPG'].fillna(0)

    # Calculate a "Playmaker Score"
    metrics = ['APG', 'PPG', 'SPG']
    scaler = MinMaxScaler()
    df_scaled = df.copy()
    
    # Fit scaler only on columns that have non-zero variance
    valid_metrics = [m for m in metrics if df[m].var() > 0]
    if valid_metrics:
        df_scaled[valid_metrics] = scaler.fit_transform(df[valid_metrics])
    
    weights = {'APG': 0.4, 'PPG': 0.3, 'SPG': 0.2, 'TOV': -0.1} # TOV is negative
    
    df_scaled['Playmaker_Score'] = (
        df_scaled['APG'] * weights['APG'] +
        df_scaled['PPG'] * weights['PPG'] +
        df_scaled['SPG'] * weights['SPG']
    )
    # Add turnover adjustment if APG is not zero
    df_scaled['Playmaker_Score'] -= (df['TOV'] / df['APG']).fillna(0).replace([np.inf, -np.inf], 0) * weights['TOV']

    # Display and compare
    df_scaled = df_scaled.sort_values(by='Playmaker_Score', ascending=False)
    print(df_scaled[['Player_Name', 'Team', 'PPG', 'APG', 'Playmaker_Score']].head(10))

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='APG', y='PPG', hue='Team', style='Player_Name', data=df_guards.dropna(subset=['APG', 'PPG']), s=200, palette='viridis')
    plt.title('Guard Performance: PPG vs. APG')
    plt.xlabel('Assists Per Game (APG)')
    plt.ylabel('Points Per Game (PPG)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.show()

def analyze_forwards(df_forwards):
    """Analyzes forward performance with a focus on versatility."""
    if df_forwards.empty:
        print("No forward data to analyze.")
        return

    print("\n--- Forward Analysis (Versatility) ---")
    df = df_forwards.copy()
    
    # Handle missing values
    df['True_Shooting_Pct'] = df['True_Shooting_Pct'].fillna(0)
    df['FG_Pct'] = df['FG_Pct'].fillna(0)
    df['RPG'] = df['RPG'].fillna(0)
    df['PPG'] = df['PPG'].fillna(0)

    # Calculate Scoring Efficiency and handle division by zero
    df['Scoring_Efficiency'] = np.where(df['FG_Pct'] > 0, df['True_Shooting_Pct'] / df['FG_Pct'], 0)

    # Display and compare
    df = df.sort_values(by='True_Shooting_Pct', ascending=False)
    print(df[['Player_Name', 'Team', 'PPG', 'RPG', 'True_Shooting_Pct']].head(10))

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Player_Name', y='RPG', hue='Team', data=df.sort_values('RPG', ascending=False).head(10), palette='viridis')
    plt.title('Top 10 Rebounds Per Game by Forward')
    plt.xlabel('Player')
    plt.ylabel('Rebounds Per Game (RPG)')
    plt.xticks(rotation=45, ha='right')
    plt.show()

def analyze_centers(df_centers):
    """Analyzes center performance with a focus on rim protection and rebounding."""
    if df_centers.empty:
        print("No center data to analyze.")
        return

    print("\n--- Center Analysis (Rim Protection & Rebounding) ---")
    df = df_centers.copy()
    
    # Handle missing values with a default of 0
    df['PER'] = df['PER'].fillna(0)
    df['TRB_Pct'] = df['TRB_Pct'].fillna(0)
    df['BLK_Pct'] = df['BLK_Pct'].fillna(0)

    df['Dominance_Score'] = (df['PER'] * 0.4) + (df['TRB_Pct'] * 0.3) + (df['BLK_Pct'] * 0.3)

    # Display and compare
    df = df.sort_values(by='Dominance_Score', ascending=False)
    print(df[['Player_Name', 'Team', 'PER', 'TRB_Pct', 'Dominance_Score']].head(10))
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x='Player_Name', y='BLK_Pct', hue='Team', data=df.sort_values('BLK_Pct', ascending=False).head(10), palette='viridis')
    plt.title('Top 10 Block Percentage (BLK%) by Center')
    plt.xlabel('Player')
    plt.ylabel('Block Percentage (BLK%)')
    plt.xticks(rotation=45, ha='right')
    plt.show()

def main():
    """Main function to run the team comparison and analysis."""
    
    # --- User Input Section ---
    team_a_name = input("Enter the name of Team A: ")
    team_b_name = input("Enter the name of Team B: ")
    home_team = input("Enter the name of the Home Team: ")
    
    league_a = detect_league(team_a_name)
    league_b = detect_league(team_b_name)
    
    if league_a and league_a == league_b:
        league = league_a
        print(f"Detected league for both teams: {league}")
    else:
        league = input("Leagues do not match or could not be detected. Please manually enter a league (NBA, EuroLeague, FIBA): ").upper()

    # --- Data Collection ---
    try:
        print("\nFetching data...")
        
        # 1. Get standings for overall comparison
        standings_df = get_standings(league)
        if standings_df.empty:
            print("Failed to retrieve standings. Cannot perform overall team comparison.")
            
        # 2. Fetch player stats for each team
        df_a = fetch_team_data(team_a_name, prefer_league=league)
        df_b = fetch_team_data(team_b_name, prefer_league=league)
        
        if df_a.empty or df_b.empty:
            print("Failed to retrieve player stats for one or both teams. Exiting.")
            return

        df_all = pd.concat([df_a, df_b])
        
        print("\n--- Data Collected ---")
        print(f"{team_a_name} Players: {len(df_a)}")
        print(f"{team_b_name} Players: {len(df_b)}")
        
    except ValueError as e:
        print(e)
        return

    # --- Analysis and Visualization ---
    if not standings_df.empty:
        compare_teams_overall(team_a_name, team_b_name, standings_df, home_team)
        print("-" * 50)
        
    analyze_positional_matchups(df_a, df_b)
    print("-" * 50)

    # Separate players by position
    df_guards = df_all[df_all['Role'].str.contains('Guard', case=False, na=False)].copy()
    df_forwards = df_all[df_all['Role'].str.contains('Forward', case=False, na=False)].copy()
    df_centers = df_all[df_all['Role'].str.contains('Center', case=False, na=False)].copy()
    
    analyze_guards(df_guards)
    print("-" * 50)
    
    analyze_forwards(df_forwards)
    print("-" * 50)
    
    analyze_centers(df_centers)

if __name__ == "__main__":
    main()