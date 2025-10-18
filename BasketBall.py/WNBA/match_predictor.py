import pandas as pd
import math
from collections import defaultdict

def analyze_basketball_team_strength(player_df):
    """Analyze basketball team strength based on player stats"""
    df = player_df.copy()
    
    # Ensure numeric columns
    for col in ["Points", "Rebounds", "Assists", "Scoring_Index", "Playmaking_Index", 
                "Defensive_Index", "Total_Score"]:
        df[col] = pd.to_numeric(df.get(col, 0), errors="coerce").fillna(0.0)
    
    strength = df.groupby("Team").agg(
        Total_Points=("Points", "sum"),
        Total_Rebounds=("Rebounds", "sum"),
        Total_Assists=("Assists", "sum"),
        Avg_Scoring=("Scoring_Index", "mean"),
        Avg_Playmaking=("Playmaking_Index", "mean"),
        Avg_Defense=("Defensive_Index", "mean"),
        Team_Total_Score=("Total_Score", "sum")
    ).reset_index()
    
    # Calculate comprehensive strength score
    strength["Strength_Score"] = (
        strength["Total_Points"] * 0.3 +          # Scoring ability
        strength["Total_Rebounds"] * 0.2 +        # Rebounding
        strength["Total_Assists"] * 0.2 +         # Playmaking
        strength["Avg_Scoring"] * 0.1 +           # Scoring efficiency
        strength["Avg_Playmaking"] * 0.1 +        # Playmaking efficiency  
        strength["Avg_Defense"] * 0.1             # Defensive capability
    )
    
    return strength.sort_values("Strength_Score", ascending=False).reset_index(drop=True)

def analyze_basketball_team_style(team_df):
    """Analyze basketball team playing style"""
    if team_df.empty:
        return {"style": "Balanced", "offense_strength": 0.5, "defense_strength": 0.5}
    
    # Analyze based on player positions and stats
    if "Position" in team_df.columns:
        positions = team_df["Position"].value_counts()
        
        # Count positions by type
        big_men = positions.get("C", 0) + positions.get("PF", 0)
        wings = positions.get("SF", 0) + positions.get("SG", 0)
        guards = positions.get("PG", 0)
        
        total_players = len(team_df)
        
        if total_players > 0:
            big_men_ratio = big_men / total_players
            wings_ratio = wings / total_players
            guards_ratio = guards / total_players
            
            # Determine style based on composition
            if big_men_ratio > 0.4:
                style = "Inside-Out"
            elif guards_ratio > 0.4:
                style = "Guard-Oriented"
            elif wings_ratio > 0.5:
                style = "Wing-Heavy"
            else:
                style = "Balanced"
        else:
            style = "Balanced"
    else:
        style = "Balanced"
    
    # Analyze offensive vs defensive strength from stats
    avg_scoring = team_df["Scoring_Index"].mean() if "Scoring_Index" in team_df.columns else 50
    avg_defense = team_df["Defensive_Index"].mean() if "Defensive_Index" in team_df.columns else 50
    
    offense_strength = min(avg_scoring / 100, 1.0) if avg_scoring > 0 else 0.5
    defense_strength = min(avg_defense / 100, 1.0) if avg_defense > 0 else 0.5
    
    return {
        "style": style,
        "offense_strength": offense_strength,
        "defense_strength": defense_strength
    }

def get_basketball_predictions(team1_df, team2_df, team1_sentiment=None, team2_sentiment=None, home_team=None):
    """Generate basketball predictions and betting suggestions"""
    if team1_df.empty or team2_df.empty:
        raise ValueError("One of the team datasets is empty.")

    # Analyze team styles
    team1_style = analyze_basketball_team_style(team1_df)
    team2_style = analyze_basketball_team_style(team2_df)
    
    print(f"🎯 Team Styles: {team1_df['Team'].iloc[0]} = {team1_style['style']}")
    print(f"🎯 Team Styles: {team2_df['Team'].iloc[0]} = {team2_style['style']}")

    # Calculate team strengths
    team1_strength = (
        team1_df["Total_Score"].sum() * 0.6 +
        team1_style["offense_strength"] * 30 +
        team1_style["defense_strength"] * 10
    )
    
    team2_strength = (
        team2_df["Total_Score"].sum() * 0.6 +
        team2_style["offense_strength"] * 30 +
        team2_style["defense_strength"] * 10
    )

    # Apply sentiment adjustments
    if team1_sentiment:
        team1_strength *= (1 + (team1_sentiment - 50) / 200)
    if team2_sentiment:
        team2_strength *= (1 + (team2_sentiment - 50) / 200)

    # Home court advantage
    if home_team and team1_df['Team'].iloc[0] == home_team:
        team1_strength *= 1.05

    # Calculate win probabilities
    total_strength = team1_strength + team2_strength
    if total_strength > 0:
        team1_win_prob = team1_strength / total_strength
        team2_win_prob = team2_strength / total_strength
    else:
        team1_win_prob = team2_win_prob = 0.5

    # Adjust for style matchups
    style_adjustment = calculate_style_matchup(team1_style, team2_style)
    team1_win_prob += style_adjustment
    team2_win_prob -= style_adjustment

    # Ensure probabilities are valid
    team1_win_prob = max(0.1, min(0.9, team1_win_prob))
    team2_win_prob = 1 - team1_win_prob

    # Calculate expected score (basketball points)
    avg_team_points = 85  # Average NBA team points per game
    expected_margin = (team1_win_prob - 0.5) * 20  # Scale margin based on probability difference
    expected_total = avg_team_points * 2
    
    team1_expected_score = (expected_total / 2) + expected_margin
    team2_expected_score = (expected_total / 2) - expected_margin

    # Generate predictions
    suggestions = defaultdict(list)
    
    # Winner prediction
    if team1_win_prob > 0.6:
        suggestions["Match Result"].append(f"Strong favorite: {team1_df['Team'].iloc[0]} (P={team1_win_prob:.2f})")
    elif team2_win_prob > 0.6:
        suggestions["Match Result"].append(f"Strong favorite: {team2_df['Team'].iloc[0]} (P={team2_win_prob:.2f})")
    else:
        suggestions["Match Result"].append(f"Close game: {team1_df['Team'].iloc[0]} (P={team1_win_prob:.2f}) vs {team2_df['Team'].iloc[0]} (P={team2_win_prob:.2f})")

    # Over/Under prediction
    if expected_total > 220:
        suggestions["Total Points"].append(f"High-scoring game expected: Over {expected_total:.0f}")
    elif expected_total < 200:
        suggestions["Total Points"].append(f"Low-scoring game expected: Under {expected_total:.0f}")
    else:
        suggestions["Total Points"].append(f"Average scoring expected: Around {expected_total:.0f} total points")

    # Style-based insights
    if team1_style["style"] == "Inside-Out" and team2_style["style"] == "Guard-Oriented":
        suggestions["Matchup Analysis"].append("Inside game vs perimeter game - watch paint battle")
    elif team1_style["offense_strength"] > 0.7 and team2_style["defense_strength"] > 0.7:
        suggestions["Matchup Analysis"].append("Elite offense vs elite defense - key matchup")

    # Top performers
    top1 = team1_df.nlargest(3, "Total_Score")[["Player", "Points", "Rebounds", "Assists"]]
    top2 = team2_df.nlargest(3, "Total_Score")[["Player", "Points", "Rebounds", "Assists"]]
    
    suggestions["Key Players - Home"] = [
        f"{row['Player']} ({row['Points']} pts, {row['Rebounds']} reb, {row['Assists']} ast)" 
        for _, row in top1.iterrows()
    ]
    suggestions["Key Players - Away"] = [
        f"{row['Player']} ({row['Points']} pts, {row['Rebounds']} reb, {row['Assists']} ast)" 
        for _, row in top2.iterrows()
    ]

    # Expected score
    suggestions["Expected Score"].append(f"{team1_df['Team'].iloc[0]} {team1_expected_score:.1f} - {team2_expected_score:.1f} {team2_df['Team'].iloc[0]}")

    markets = {
        "Home Win Probability": team1_win_prob,
        "Away Win Probability": team2_win_prob,
        "Expected Total Points": expected_total,
        "Expected Margin": expected_margin
    }

    confidence = {
        "Confidence": abs(team1_win_prob - 0.5) * 2,  # 0-1 scale
        "Home Offense Rating": team1_style["offense_strength"],
        "Away Offense Rating": team2_style["offense_strength"],
        "Home Defense Rating": team1_style["defense_strength"],
        "Away Defense Rating": team2_style["defense_strength"]
    }

    return dict(suggestions), markets, confidence

def calculate_style_matchup(style1, style2):
    """Calculate style matchup advantage"""
    matchup_bonus = 0
    
    # Inside-Out teams have advantage against Guard-Oriented teams
    if style1["style"] == "Inside-Out" and style2["style"] == "Guard-Oriented":
        matchup_bonus = 0.05
    elif style1["style"] == "Guard-Oriented" and style2["style"] == "Inside-Out":
        matchup_bonus = -0.05
    
    # Defensive teams can neutralize offensive teams
    if style1["defense_strength"] > 0.7 and style2["offense_strength"] > 0.7:
        matchup_bonus += 0.03
    
    return matchup_bonus

def compare_basketball_teams(team1_name, team2_name, player_df1, player_df2):
    """Compare two basketball teams"""
    summary = {}

    if not player_df1.empty:
        strength1 = analyze_basketball_team_strength(player_df1)
        strength1_val = strength1["Strength_Score"].sum() if not strength1.empty else 0
        style1 = analyze_basketball_team_style(player_df1)
    else:
        strength1_val = 0
        style1 = {"style": "Unknown", "offense_strength": 0.5, "defense_strength": 0.5}

    if not player_df2.empty:
        strength2 = analyze_basketball_team_strength(player_df2)
        strength2_val = strength2["Strength_Score"].sum() if not strength2.empty else 0
        style2 = analyze_basketball_team_style(player_df2)
    else:
        strength2_val = 0
        style2 = {"style": "Unknown", "offense_strength": 0.5, "defense_strength": 0.5}

    summary["Team1_Strength"] = strength1_val
    summary["Team2_Strength"] = strength2_val
    summary["Team1_Style"] = style1["style"]
    summary["Team2_Style"] = style2["style"]
    summary["Predicted_Stronger_Team"] = team1_name if strength1_val >= strength2_val else team2_name

    print(f"\n[COMPARE] {team1_name} Strength: {strength1_val:.2f} | Style: {style1['style']}")
    print(f"[COMPARE] {team2_name} Strength: {strength2_val:.2f} | Style: {style2['style']}")
    print(f"Predicted Stronger Team: {summary['Predicted_Stronger_Team']}")
    
    return summary