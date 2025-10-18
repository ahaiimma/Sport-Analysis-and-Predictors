import os
import sys
import pandas as pd
from player_data_collector import load_basketball_player_data
from team_data_collector import load_basketball_team_data
from match_predictor import analyze_basketball_team_strength, compare_basketball_teams, get_basketball_predictions

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def normalize_team_name(team_name):
    """Normalize basketball team names"""
    if pd.isna(team_name):
        return ""
    team_str = str(team_name).lower().strip()
    team_str = ''.join(char for char in team_str if char.isalnum() or char.isspace())
    return ' '.join(team_str.split())

def find_basketball_team_match(user_input, available_teams):
    """Find matching basketball team"""
    user_normalized = normalize_team_name(user_input)
    
    for team in available_teams:
        if normalize_team_name(team) == user_normalized:
            return team
        if user_normalized in normalize_team_name(team):
            return team
    
    return None

def main():
    print("======================================")
    print(" 🏀 Basketball Prediction System")
    print("======================================\n")

    team_file = os.path.join(BASE_DIR, "sentiment.xlsx")
    player_file = os.path.join(BASE_DIR, "basketball.xlsx")

    # Load data
    try:
        team_df = load_basketball_team_data(team_file)
        player_df = load_basketball_player_data(player_file)
    except Exception as e:
        print("❌ Failed to load basketball data:", e)
        sys.exit(1)

    print("\n--- Team Standings (Top 10) ---")
    print(team_df.sort_values("Sentiment_Score", ascending=False)[["Team", "Wins", "Losses", "Win_Pct", "Sentiment_Score"]].head(10).to_string(index=False))

    print("\n--- Team Strength Rankings ---")
    ts = analyze_basketball_team_strength(player_df)
    print(ts.head(10).to_string(index=False))

    # Get available teams
    all_team_names = set(team_df['Team'].dropna().unique())
    all_player_teams = set(player_df['Team'].dropna().unique())
    all_available_teams = all_team_names.union(all_player_teams)
    
    print(f"\n✅ Available teams ({len(all_available_teams)} teams):")
    for team in sorted(all_available_teams):
        print(f"  - {team}")

    # Interactive loop
    while True:
        print(f"\nEnter two teams to compare (or 'q' to quit).")
        print("You can use any team name variation")
        
        t1_input = input("Home team: ").strip()
        if t1_input.lower() in ("q", "quit"):
            break
        t2_input = input("Away team: ").strip()
        if t2_input.lower() in ("q", "quit"):
            break

        # Find matches
        t1_matched = find_basketball_team_match(t1_input, all_player_teams)
        t2_matched = find_basketball_team_match(t2_input, all_player_teams)

        if not t1_matched or not t2_matched:
            print("❌ Could not find one or both teams in player data.")
            continue

        print(f"🔍 Found: '{t1_input}' -> '{t1_matched}'")
        print(f"🔍 Found: '{t2_input}' -> '{t2_matched}'")

        # Get data
        t1_players = player_df[player_df["Team"] == t1_matched]
        t2_players = player_df[player_df["Team"] == t2_matched]
        t1_sent = team_df[team_df["Team"] == t1_matched]
        t2_sent = team_df[team_df["Team"] == t2_matched]

        if t1_players.empty or t2_players.empty:
            print("❌ Could not find player data for matched teams.")
            continue

        team1_sentiment = float(t1_sent["Sentiment_Score"].iloc[0]) if not t1_sent.empty else None
        team2_sentiment = float(t2_sent["Sentiment_Score"].iloc[0]) if not t2_sent.empty else None

        print(f"\nComparing {t1_matched} vs {t2_matched}\n")

        # Show comparison
        compare_basketball_teams(t1_matched, t2_matched, t1_players, t2_players)

        # Get predictions
        suggestions, markets, confidence = get_basketball_predictions(
            t1_players, t2_players, team1_sentiment, team2_sentiment, t1_matched
        )

        print("\n=========================")
        print("📈 BASKETBALL PREDICTIONS")
        for category, tips in suggestions.items():
            print(f"\n--- {category} ---")
            for tip in tips:
                print(" •", tip)

        print("\n--- Market Probabilities ---")
        for market, value in markets.items():
            if isinstance(value, float):
                print(f"{market}: {value:.3f}")
            else:
                print(f"{market}: {value}")

        print("\n--- Confidence Metrics ---")
        for metric, value in confidence.items():
            if isinstance(value, float):
                print(f"{metric}: {value:.2f}")
            else:
                print(f"{metric}: {value}")

    print("\nGoodbye!")
    sys.exit(0)

if __name__ == "__main__":
    main()