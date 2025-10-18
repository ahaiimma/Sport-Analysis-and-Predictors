# compare_teams.py
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.preprocessing import MinMaxScaler
from fetch_stats1 import fetch_team_data

sns.set(style="whitegrid")

def analyze_guards(df_guards):
    if df_guards.empty:
        print("No guard data to analyze.")
        return

    print("\n--- Guard Analysis (Playmaking & Scoring) ---")
    df = df_guards.copy()
    metrics = ['APG', 'PPG', 'SPG']
    scaler = MinMaxScaler()
    df_scaled = df.copy()
    df_scaled[metrics] = scaler.fit_transform(df[metrics].fillna(0))

    weights = {'APG': 0.4, 'PPG': 0.3, 'SPG': 0.2, 'TOV': -0.1}
    df_scaled['Playmaker_Score'] = (
        df_scaled['APG'] * weights['APG'] +
        df_scaled['PPG'] * weights['PPG'] +
        df_scaled['SPG'] * weights['SPG'] -
        (df['TOV'] / (df['APG'] + 1e-5)).fillna(0) * weights['TOV']
    )

    df_scaled = df_scaled.sort_values(by='Playmaker_Score', ascending=False)
    print(df_scaled[['Player_Name', 'Team', 'PPG', 'APG', 'Playmaker_Score']])

    plt.figure(figsize=(10, 6))
    sns.scatterplot(x='APG', y='PPG', hue='Team', style='Player_Name', data=df_guards, s=200, palette='viridis')
    plt.title('Guard Performance: PPG vs. APG')
    plt.xlabel('Assists Per Game (APG)')
    plt.ylabel('Points Per Game (PPG)')
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.show()

def analyze_forwards(df_forwards):
    if df_forwards.empty:
        print("No forward data to analyze.")
        return

    print("\n--- Forward Analysis (Versatility) ---")
    df = df_forwards.copy()
    df['Scoring_Efficiency'] = (df['True_Shooting_Pct'] / df['FG_Pct']).replace([np.inf, -np.inf], 0)
    df = df.sort_values(by='True_Shooting_Pct', ascending=False)
    print(df[['Player_Name', 'Team', 'PPG', 'RPG', 'True_Shooting_Pct']])

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Player_Name', y='RPG', hue='Team', data=df, palette='viridis')
    plt.title('Rebounds Per Game by Forward')
    plt.xlabel('Player')
    plt.ylabel('Rebounds Per Game (RPG)')
    plt.show()

def analyze_centers(df_centers):
    if df_centers.empty:
        print("No center data to analyze.")
        return

    print("\n--- Center Analysis (Rim Protection & Rebounding) ---")
    df = df_centers.copy()
    df['Dominance_Score'] = (df['PER'] * 0.4) + (df['TRB_Pct'] * 0.3) + (df['BLK_Pct'] * 0.3)
    df = df.sort_values(by='Dominance_Score', ascending=False)
    print(df[['Player_Name', 'Team', 'PER', 'TRB_Pct', 'Dominance_Score']])

    plt.figure(figsize=(10, 6))
    sns.barplot(x='Player_Name', y='BLK_Pct', hue='Team', data=df, palette='viridis')
    plt.title('Block Percentage (BLK%) by Center')
    plt.xlabel('Player')
    plt.ylabel('Block Percentage (BLK%)')
    plt.show()

def compare_teams(team_names, season_year="2025"):
    df_all = pd.DataFrame()
    for team in team_names:
        df_team = fetch_team_data(team, season_year)
        if not df_team.empty:
            df_team['Team'] = team  # Ensure team name is included
            df_all = pd.concat([df_all, df_team], ignore_index=True)

    if df_all.empty:
        print("No data fetched for the specified teams.")
        return

    df_guards = df_all[df_all['Role'] == 'Guard'].copy()
    df_forwards = df_all[df_all['Role'] == 'Forward'].copy()
    df_centers = df_all[df_all['Role'] == 'Center'].copy()

    analyze_guards(df_guards)
    analyze_forwards(df_forwards)
    analyze_centers(df_centers)

if __name__ == "__main__":
    # Example usage: Compare two teams
    teams_to_compare = ["Los Angeles Lakers", "Boston Celtics"]
    compare_teams(teams_to_compare)