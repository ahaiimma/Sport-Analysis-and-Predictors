import os, sys
import pandas as pd
from team_data_collector import load_team_data
from player_data_collector import load_player_data
from match_predictor import (
    analyze_team_strength, 
    compare_teams, 
    get_betting_suggestions_and_markets,
    load_corner_data,  # ADD THIS LINE
    load_form_data     # ADD THIS LINE
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def normalize_team_name(team_name):
    """Normalize team name for comparison - handle case, spaces, punctuation"""
    if pd.isna(team_name):
        return ""
    # Convert to string, lowercase, remove extra spaces and punctuation
    team_str = str(team_name).lower().strip()
    # Remove common punctuation and extra spaces
    team_str = ''.join(char for char in team_str if char.isalnum() or char.isspace())
    # Normalize spaces
    team_str = ' '.join(team_str.split())
    return team_str

def find_team_match(user_input, available_teams):
    """Find the best matching team name from available teams"""
    user_normalized = normalize_team_name(user_input)
    
    # First: Exact normalized match
    for team in available_teams:
        if normalize_team_name(team) == user_normalized:
            return team
    
    # Second: Contains match (user input is part of team name)
    for team in available_teams:
        team_normalized = normalize_team_name(team)
        if user_normalized in team_normalized or team_normalized in user_normalized:
            return team
    
    # Third: Word-based matching
    user_words = set(user_normalized.split())
    for team in available_teams:
        team_normalized = normalize_team_name(team)
        team_words = set(team_normalized.split())
        
        # If most words match
        common_words = user_words & team_words
        if len(common_words) > 0 and len(common_words) >= min(len(user_words), len(team_words)) * 0.5:
            return team
    
    return None

def main():
    print("======================================")
    print(" ⚽ Seria A Prediction System")
    print("======================================\n")

    team_file = os.path.join(BASE_DIR, "Laliga Sentiment table.xlsx")
    player_file = os.path.join(BASE_DIR, "FutBall.xlsx")
    corner_file = os.path.join(BASE_DIR, "Laliga Corner.xlsx")
    form_file = os.path.join(BASE_DIR, "Laliga Form.xlsx")  # ADD THIS LINE

    # load all data
    try:
        team_df = load_team_data(team_file)
        player_df = load_player_data(player_file)
        corner_data = load_corner_data(corner_file)
        form_data = load_form_data(form_file)
    except Exception as e:
        print("❌ Failed to load data:", e)
        sys.exit(1)

    print("\n--- Team sentiment (top 10) ---")
    print(team_df.sort_values("Sentiment_Score", ascending=False)[["Team", "Sentiment_Score"]].head(10).to_string(index=False))

    print("\n--- Player strength (top teams) ---")
    ts = analyze_team_strength(player_df)
    print(ts.head(10).to_string(index=False))

    # Get all available teams from both datasets
    all_team_names = set(team_df['Team'].dropna().unique())
    all_player_teams = set(player_df['Team'].dropna().unique())
    
    # Combine all possible team names
    all_available_teams = all_team_names.union(all_player_teams)
    
    print(f"\n✅ All available teams ({len(all_available_teams)} teams):")
    for team in sorted(all_available_teams):
        print(f"  - {team}")

    # interactive loop
    while True:
        print(f"\nEnter two teams to compare (or 'q' to quit).")
        print("You can use any team name variation (case doesn't matter)")
        
        t1_input = input("Home team: ").strip()
        if t1_input.lower() in ("q", "quit"):
            break
        t2_input = input("Away team: ").strip()
        if t2_input.lower() in ("q", "quit"):
            break

        # Find best matches in player data (since we need player stats)
        t1_matched = find_team_match(t1_input, all_player_teams)
        t2_matched = find_team_match(t2_input, all_player_teams)

        if not t1_matched:
            print(f"❌ Could not find '{t1_input}' in player data.")
            print("   Close matches:")
            for team in all_player_teams:
                if t1_input.lower() in team.lower():
                    print(f"   - {team}")
            continue
            
        if not t2_matched:
            print(f"❌ Could not find '{t2_input}' in player data.")
            print("   Close matches:")
            for team in all_player_teams:
                if t2_input.lower() in team.lower():
                    print(f"   - {team}")
            continue

        print(f"🔍 Found: '{t1_input}' -> '{t1_matched}'")
        print(f"🔍 Found: '{t2_input}' -> '{t2_matched}'")

        # Get player data using matched names
        t1_players = player_df[player_df["Team"] == t1_matched]
        t2_players = player_df[player_df["Team"] == t2_matched]

        # Get sentiment data using flexible matching
        t1_sent = team_df[team_df["Team"].apply(lambda x: find_team_match(x, [t1_matched]) == t1_matched)]
        t2_sent = team_df[team_df["Team"].apply(lambda x: find_team_match(x, [t2_matched]) == t2_matched)]

        if t1_players.empty or t2_players.empty:
            print("❌ Could not find player data for the matched teams.")
            continue

        team1_sentiment = float(t1_sent["Sentiment_Score"].iloc[0]) if not t1_sent.empty else None
        team2_sentiment = float(t2_sent["Sentiment_Score"].iloc[0]) if not t2_sent.empty else None

        print(f"\nComparing {t1_matched} vs {t2_matched}\n")

        # Show strength tables
        s = analyze_team_strength(pd.concat([t1_players, t2_players]))
        print(s[s["Team"].isin([t1_matched, t2_matched])].to_string(index=False))

        # Get pressure data for both teams
        team1_pressure = team_df[team_df['Team'] == t1_matched].iloc[0].to_dict() if not team_df[team_df['Team'] == t1_matched].empty else None
        team2_pressure = team_df[team_df['Team'] == t2_matched].iloc[0].to_dict() if not team_df[team_df['Team'] == t2_matched].empty else None

        # Get predictions & betting suggestions with ALL data
        suggestions, markets, confidence, value_bets = get_betting_suggestions_and_markets(
            t1_players, t2_players,
            team1_sentiment=team1_sentiment,
            team2_sentiment=team2_sentiment,
            home_team=t1_matched,
            team1_pressure_data=team1_pressure,
            team2_pressure_data=team2_pressure,
            corner_data=corner_data,
            form_data=form_data
        )
        
        print("\n=========================")
        print("📈 BETTING SUGGESTIONS")
        for market, tips in suggestions.items():
            print(f"\n--- {market} ---")
            for t in tips:
                print(" •", t)

        print("\n--- Market probabilities ---")
        for m, v in markets.items():
            print(f"{m}: {v}")

        print("\n--- Confidence metrics ---")
        for c, v in confidence.items():
            if isinstance(v, (int, float)):
                print(f"{c}: {v:.2f}")
            else:
                print(f"{c}: {v}")

        # Display value bets if any
        if value_bets:
            print("\n--- 🎯 VALUE BETS (Top 5) ---")
            for i, bet in enumerate(value_bets[:5], 1):
                print(f"{i}. {bet['market']} - {bet['outcome']} @ {bet['odds']}")
                print(f"   Our Probability: {bet['our_probability']} | Implied: {bet['implied_probability']}")
                print(f"   Value: {bet['value']} | Expected Value: {bet['expected_value']:.3f}")

    print("\nGoodbye.")
    sys.exit(0)

if __name__ == "__main__":
    main()