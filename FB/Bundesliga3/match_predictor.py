import pandas as pd
import math
from collections import defaultdict

# Actual betting odds data structure
BETTING_ODDS = {
    "1X2": {
        "Home": 3.67,
        "Draw": 3.76, 
        "Away": 1.96
    },
    "Over/Under 2.5": {
        "Over": 1.70,
        "Under": 2.15
    },
    "Over/Under 1.5": {
        "Over": 1.22,
        "Under": 4.20
    },
    "Over/Under 3.5": {
        "Over": 2.70,
        "Under": 1.45
    },
    "Double Chance": {
        "Home or Draw": 1.78,
        "Home or Away": 1.27,
        "Draw or Away": 1.28
    },
    "Both Teams to Score": {
        "Yes": 1.65,
        "No": 2.25
    },
    "Draw No Bet": {
        "Home": 2.70,
        "Away": 1.47
    },
    "Asian Handicap": {
        "Home +1.5": 1.31,
        "Away -1.5": 3.30
    },
    "First Goal": {
        "Home": 2.25,
        "Away": 1.63,
        "None": 13.50
    },
    "Correct Score": {
        "0-0": 13.50,
        "1-0": 12.50,
        "0-1": 8.90,
        "1-1": 6.90,
        "2-0": 21.00,
        "0-2": 10.50,
        "2-1": 12.50,
        "1-2": 8.60,
        "2-2": 13.00
    }
}

def calculate_value_bets(our_probabilities, odds_dict, threshold=0.05):
    """Calculate value bets based on our probabilities vs market odds"""
    value_bets = []
    
    for market, probabilities in our_probabilities.items():
        if market in odds_dict:
            for outcome, our_prob in probabilities.items():
                if outcome in odds_dict[market]:
                    odds = odds_dict[market][outcome]
                    if odds > 0:  # Avoid division by zero
                        implied_prob = 1 / odds
                        value = our_prob - implied_prob
                        
                        if value > threshold:
                            value_bets.append({
                                'market': market,
                                'outcome': outcome,
                                'our_probability': f"{our_prob:.1%}",
                                'implied_probability': f"{implied_prob:.1%}",
                                'odds': odds,
                                'value': f"+{value:.1%}",
                                'expected_value': (odds - 1) * our_prob - (1 - our_prob)
                            })
    
    return sorted(value_bets, key=lambda x: x['expected_value'], reverse=True)

def calculate_kelly_criterion(probability, odds, bankroll_fraction=0.25):
    """Calculate Kelly Criterion bet sizing"""
    if odds <= 1:
        return 0
    
    kelly_fraction = (probability * odds - 1) / (odds - 1)
    # Use fractional Kelly for safety
    return max(0, kelly_fraction * bankroll_fraction)

def compare_teams(team1_name, team2_name, team1_df=None, team2_df=None, player_df1=None, player_df2=None):
    """
    Compares two teams' overall strengths using both team and player data.
    Returns summaries for display and prediction correlation.
    """
    summary = {}

    if isinstance(player_df1, pd.DataFrame) and not player_df1.empty:
        s1 = analyze_team_strength(player_df1)
        s1_val = s1["Strength_Score"].sum()
        team1_style = analyze_team_style(player_df1)
        team1_xg_analysis = analyze_team_xg_profile(player_df1)
    else:
        s1_val = 0
        team1_style = {"style": "Unknown", "attack_strength": 0.5, "defense_strength": 0.5}
        team1_xg_analysis = {"xg_efficiency": 0.5, "penalty_reliance": 0.0, "creative_threat": 0.5}

    if isinstance(player_df2, pd.DataFrame) and not player_df2.empty:
        s2 = analyze_team_strength(player_df2)
        s2_val = s2["Strength_Score"].sum()
        team2_style = analyze_team_style(player_df2)
        team2_xg_analysis = analyze_team_xg_profile(player_df2)
    else:
        s2_val = 0
        team2_style = {"style": "Unknown", "attack_strength": 0.5, "defense_strength": 0.5}
        team2_xg_analysis = {"xg_efficiency": 0.5, "penalty_reliance": 0.0, "creative_threat": 0.5}

    summary["Team1_Strength"] = s1_val
    summary["Team2_Strength"] = s2_val
    summary["Team1_Style"] = team1_style["style"]
    summary["Team2_Style"] = team2_style["style"]
    summary["Team1_xG_Profile"] = team1_xg_analysis
    summary["Team2_xG_Profile"] = team2_xg_analysis
    summary["Predicted_Stronger_Team"] = team1_name if s1_val >= s2_val else team2_name

    print(f"\n[COMPARE] {team1_name} Strength: {s1_val:.2f} | Style: {team1_style['style']}")
    print(f"[COMPARE] {team2_name} Strength: {s2_val:.2f} | Style: {team2_style['style']}")
    print(f"[xG ANALYSIS] {team1_name}: Efficiency={team1_xg_analysis['xg_efficiency']:.2f}, PenaltyReliance={team1_xg_analysis['penalty_reliance']:.2f}")
    print(f"[xG ANALYSIS] {team2_name}: Efficiency={team2_xg_analysis['xg_efficiency']:.2f}, PenaltyReliance={team2_xg_analysis['penalty_reliance']:.2f}")
    print(f"Predicted Stronger Team: {summary['Predicted_Stronger_Team']}")
    return summary

def analyze_team_xg_profile(team_df):
    """Analyze team's xG profile and efficiency"""
    if team_df.empty:
        return {"xg_efficiency": 0.5, "penalty_reliance": 0.0, "creative_threat": 0.5}
    
    # Calculate xG efficiency (goals vs expected goals)
    total_goals = team_df["Goals"].sum()
    total_xg = team_df["xG"].sum()
    
    if total_xg > 0:
        xg_efficiency = total_goals / total_xg
    else:
        xg_efficiency = 0.5
    
    # Calculate penalty reliance
    if "npxG" in team_df.columns and "xG" in team_df.columns:
        total_npxg = team_df["npxG"].sum()
        penalty_reliance = (total_xg - total_npxg) / max(total_xg, 1)
    else:
        penalty_reliance = 0.0
    
    # Calculate creative threat
    if "Creative_Threat" in team_df.columns:
        creative_threat = team_df["Creative_Threat"].sum() / max(len(team_df), 1)
    else:
        creative_threat = team_df["xA"].sum() / max(len(team_df), 1)
    
    return {
        "xg_efficiency": min(xg_efficiency, 2.0),  # Cap at 2.0 (200% efficiency)
        "penalty_reliance": min(max(penalty_reliance, 0), 1),  # Between 0 and 1
        "creative_threat": creative_threat / 10  # Normalize
    }

def analyze_team_strength(player_df):
    df = player_df.copy()
    for col in ["Goals", "Assists", "xG", "xA", "Total_Score", "Defense_Index", "Progression_Index", 
                "Creative_Threat", "Overall_Threat"]:
        df[col] = pd.to_numeric(df.get(col,0), errors="coerce").fillna(0.0)
    
    strength = df.groupby("Team").agg(
        Goals=("Goals","sum"),
        Assists=("Assists","sum"),
        xG=("xG","sum"),
        xA=("xA","sum"),
        Defense_Score=("Defense_Index","sum"),
        Progression_Score=("Progression_Index","sum"),
        Creative_Threat=("Creative_Threat","sum"),
        Overall_Threat=("Overall_Threat","sum"),
        Total_Score=("Total_Score","sum")
    ).reset_index()
    
    # ENHANCED strength score with advanced xG metrics
    strength["Strength_Score"] = (
        strength["Goals"] * 3 +           # Goals importance reduced slightly
        strength["Assists"] * 2.5 +       # Assists importance
        strength["xG"] * 2 +              # Expected goals
        strength["xA"] * 1.5 +            # Expected assists
        strength["Defense_Score"] * 2 +   # Defensive capability
        strength["Progression_Score"] * 1 + # Playing style/possession
        strength["Creative_Threat"] * 1.5 + # Creative threat
        strength["Overall_Threat"] * 1    # Overall threat rating
    )
    
    return strength.sort_values("Strength_Score", ascending=False).reset_index(drop=True)

def analyze_team_style(team_df):
    """Analyze team playing style based on player roles and stats"""
    if team_df.empty:
        return {"style": "Balanced", "attack_strength": 0.5, "defense_strength": 0.5}
    
    # Analyze player roles
    if "Role" in team_df.columns:
        roles = team_df["Role"].value_counts()
        
        # Count attacking vs defensive roles
        attacking_roles = ["FW", "LW", "RW", "AM", "WM", "LM", "RM"]
        defensive_roles = ["DF", "FB", "LB", "RB", "CB", "DM", "GK"]
        midfield_roles = ["MF", "CM"]
        
        attack_count = sum(roles.get(role, 0) for role in attacking_roles)
        defense_count = sum(roles.get(role, 0) for role in defensive_roles)
        midfield_count = sum(roles.get(role, 0) for role in midfield_roles)
        
        total_players = len(team_df)
        
        if total_players > 0:
            attack_ratio = attack_count / total_players
            defense_ratio = defense_count / total_players
            midfield_ratio = midfield_count / total_players
            
            # Determine playing style
            if attack_ratio > 0.4:
                style = "Attacking"
            elif defense_ratio > 0.4:
                style = "Defensive" 
            elif midfield_ratio > 0.4:
                style = "Possession-based"
            else:
                style = "Balanced"
        else:
            style = "Balanced"
            attack_ratio = 0.33
            defense_ratio = 0.33
    else:
        style = "Balanced"
        attack_ratio = 0.33
        defense_ratio = 0.33
    
    return {
        "style": style,
        "attack_strength": attack_ratio,
        "defense_strength": defense_ratio
    }

def get_betting_suggestions_and_markets(team1_df, team2_df, team1_sentiment=None, team2_sentiment=None, home_team=None):
    if team1_df.empty or team2_df.empty:
        raise ValueError("One of the team datasets is empty.")

    # ENHANCED: Analyze team styles and xG profiles
    team1_style = analyze_team_style(team1_df)
    team2_style = analyze_team_style(team2_df)
    team1_xg = analyze_team_xg_profile(team1_df)
    team2_xg = analyze_team_xg_profile(team2_df)
    
    print(f"🎯 Team Styles: {team1_df['Team'].iloc[0]} = {team1_style['style']}, {team2_df['Team'].iloc[0]} = {team2_style['style']}")
    print(f"📊 xG Analysis: {team1_df['Team'].iloc[0]} (Eff: {team1_xg['xg_efficiency']:.2f}, Pen: {team1_xg['penalty_reliance']:.2f})")
    print(f"📊 xG Analysis: {team2_df['Team'].iloc[0]} (Eff: {team2_xg['xg_efficiency']:.2f}, Pen: {team2_xg['penalty_reliance']:.2f})")

    # Enhanced strength calculation with style and xG consideration
    a1 = (team1_df["Goals"].sum() + 0.8 * team1_df["xG"].sum()) * (1 + team1_style["attack_strength"] * 0.2)
    a2 = (team2_df["Goals"].sum() + 0.8 * team2_df["xG"].sum()) * (1 + team2_style["attack_strength"] * 0.2)
    
    # Apply xG efficiency adjustments
    a1 *= (1 + (team1_xg["xg_efficiency"] - 1) * 0.3)  # Teams with high efficiency overperform
    a2 *= (1 + (team2_xg["xg_efficiency"] - 1) * 0.3)
    
    # Defensive adjustments
    d1 = team1_style["defense_strength"] * 0.3
    d2 = team2_style["defense_strength"] * 0.3
    
    total = max(a1 + a2, 1e-6)
    
    # Enhanced lambda calculation with style and xG factors
    lambda_home = 1.6 * (a1 / total) * (1 - d2)  # Home attack vs away defense
    lambda_away = 1.2 * (a2 / total) * (1 - d1)  # Away attack vs home defense

    if home_team:
        lambda_home *= 1.05  # Home advantage

    if team1_sentiment is not None and team2_sentiment is not None:
        diff = team1_sentiment - team2_sentiment
        lambda_home *= (1 + diff * 0.004)
        lambda_away *= (1 - diff * 0.004)

    pm = score_prob_matrix(lambda_home, lambda_away, max_goals=6)
    derived = derive_match_probs_from_poisson(pm)

    probs = {
        "Home Win": derived["P_home"],
        "Draw": derived["P_draw"],
        "Away Win": derived["P_away"]
    }
    best = max(probs, key=probs.get)

    # Calculate additional probabilities for betting markets
    our_probabilities = {
        "1X2": probs,
        "Over/Under 2.5": {
            "Over": derived["Exp_goals"] > 2.5 and 0.65 or 0.35,
            "Under": derived["Exp_goals"] <= 2.5 and 0.65 or 0.35
        },
        "Both Teams to Score": {
            "Yes": min((team1_style["attack_strength"] + team2_style["attack_strength"]) * 0.8, 0.9),
            "No": max(0.1, 1 - (team1_style["attack_strength"] + team2_style["attack_strength"]) * 0.8)
        },
        "Draw No Bet": {
            "Home": probs["Home Win"] / (probs["Home Win"] + probs["Away Win"]) if (probs["Home Win"] + probs["Away Win"]) > 0 else 0.5,
            "Away": probs["Away Win"] / (probs["Home Win"] + probs["Away Win"]) if (probs["Home Win"] + probs["Away Win"]) > 0 else 0.5
        }
    }

    # Calculate value bets
    value_bets = calculate_value_bets(our_probabilities, BETTING_ODDS)

    suggestions = defaultdict(list)
    suggestions["Match Result"].append(f"Predicted: {best} (P={probs[best]:.2f})")
    suggestions["Over/Under 2.5"].append("Over 2.5" if derived["Exp_goals"] > 2.5 else "Under 2.5")
    
    # ENHANCED: Style and xG based suggestions
    if team1_style["style"] == "Defensive" and team2_style["style"] == "Defensive":
        suggestions["Match Analysis"].append("Both teams are defensively oriented - expect fewer goals")
    elif team1_style["style"] == "Attacking" and team2_style["style"] == "Attacking":
        suggestions["Match Analysis"].append("Both teams favor attacking football - expect more goals")
    elif team1_style["style"] == "Defensive" or team2_style["style"] == "Defensive":
        suggestions["Match Analysis"].append("One team plays defensively - could be a tight match")
    
    # xG based insights
    if team1_xg["xg_efficiency"] > 1.2 or team2_xg["xg_efficiency"] > 1.2:
        suggestions["xG Insights"].append("High xG efficiency detected - teams may overperform expectations")
    if team1_xg["penalty_reliance"] > 0.3 or team2_xg["penalty_reliance"] > 0.3:
        suggestions["xG Insights"].append("High penalty reliance - results may be volatile")

    # Top scorers with enhanced analysis
    top1 = sorted(estimate_player_goal_probs(team1_df).items(), key=lambda x: x[1], reverse=True)[:3]
    top2 = sorted(estimate_player_goal_probs(team2_df).items(), key=lambda x: x[1], reverse=True)[:3]
    suggestions["Top Scorers Home"] = [f"{p} ({prob:.2f})" for p, prob in top1]
    suggestions["Top Scorers Away"] = [f"{p} ({prob:.2f})" for p, prob in top2]

    # Correct score with style consideration
    top_scores = ", ".join([f"{i}-{j}" for (i,j), _ in derived["Top_scores"]])
    suggestions["Likely Scores"].append(top_scores)

    # Add value betting recommendations
    if value_bets:
        suggestions["🎯 VALUE BETS"] = []
        for bet in value_bets[:3]:  # Top 3 value bets
            kelly = calculate_kelly_criterion(float(bet['our_probability'].strip('%'))/100, bet['odds'])
            bet_suggestion = f"{bet['outcome']} in {bet['market']} @ {bet['odds']} (Value: {bet['value']}, Kelly: {kelly:.1%})"
            suggestions["🎯 VALUE BETS"].append(bet_suggestion)

    markets = {
        "P_home": derived["P_home"],
        "P_draw": derived["P_draw"],
        "P_away": derived["P_away"],
        "Expected Goals": derived["Exp_goals"]
    }

    conf = {
        "Confidence": abs(max(probs.values()) - sorted(probs.values())[-2]),
        "Exp Goals": derived["Exp_goals"],
        "Home Style": team1_style["style"],
        "Away Style": team2_style["style"],
        "Home xG Eff": f"{team1_xg['xg_efficiency']:.2f}",
        "Away xG Eff": f"{team2_xg['xg_efficiency']:.2f}",
        "Home Pen Rel": f"{team1_xg['penalty_reliance']:.2f}",
        "Away Pen Rel": f"{team2_xg['penalty_reliance']:.2f}"
    }

    return dict(suggestions), markets, conf, value_bets

def poisson(k, lam):
    return lam**k * math.exp(-lam) / math.factorial(k)

def score_prob_matrix(lambda_home, lambda_away, max_goals=6):
    return [[poisson(i, lambda_home) * poisson(j, lambda_away)
             for j in range(max_goals+1)] for i in range(max_goals+1)]

def derive_match_probs_from_poisson(pm):
    n = len(pm)
    home_win = draw = away_win = exp_goals = 0.0
    for i in range(n):
        for j in range(n):
            p = pm[i][j]
            exp_goals += (i + j) * p
            if i > j:
                home_win += p
            elif i == j:
                draw += p
            else:
                away_win += p
    flat = [((i,j), pm[i][j]) for i in range(n) for j in range(n)]
    flat.sort(key=lambda x: x[1], reverse=True)
    return {
        "P_home": home_win,
        "P_draw": draw,
        "P_away": away_win,
        "Exp_goals": exp_goals,
        "Top_scores": flat[:5],
    }

def estimate_player_goal_probs(team_df):
    results = {}
    total_xg = team_df["xG"].sum() or team_df["Goals"].sum() or 1
    for _, r in team_df.iterrows():
        score = r.get("xG", 0) + 0.5 * r.get("Goals", 0)
        results[r["Player"]] = score
    total = sum(results.values()) or 1
    scale = total_xg / total
    for k in results:
        results[k] *= scale
    return results