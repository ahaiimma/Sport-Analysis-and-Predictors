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
    },
    "Total Corners": {
        "Over 8.5": 1.95,
        "Under 8.5": 1.85,
        "Over 9.5": 2.20,
        "Under 9.5": 1.65
    },
    "Team Corners": {
        "Home Over 4.5": 2.10,
        "Home Under 4.5": 1.70,
        "Away Over 3.5": 2.30,
        "Away Under 3.5": 1.60
    },
    "First Half Corners": {
        "Over 4.5": 2.05,
        "Under 4.5": 1.75
    }
}

def poisson(k, lam):
    """Calculate Poisson probability"""
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

def analyze_team_corner_profile(team_df):
    """Analyze team's corner kick tendencies using existing metrics"""
    if team_df.empty:
        return {"avg_corners": 4.5, "corner_frequency": 0.5, "corner_threat": 0.5}
    
    # Calculate corner frequency based on attacking metrics you already have
    total_minutes = team_df["Minutes"].sum() if "Minutes" in team_df.columns else 90 * len(team_df)
    
    # Use existing attacking metrics to estimate corners
    attacking_pressure = (
        team_df["Goals"].sum() * 2 +                    # Goals indicate attacking pressure
        team_df["xG"].sum() * 3 +                       # xG indicates chance creation
        team_df.get("Progressive_Passes", pd.Series([0])).sum() * 0.1 +     # Progressive passes indicate attacking intent
        team_df.get("Progressive_Carries", pd.Series([0])).sum() * 0.1 +    # Progressive carries indicate forward movement
        team_df["Assists"].sum() * 1.5                  # Assists indicate creative output
    )
    
    # Normalize to per-90 minutes basis
    if total_minutes > 0:
        corner_frequency = attacking_pressure / (total_minutes / 90)
    else:
        corner_frequency = 5.0  # Default average
    
    # Convert to expected corners per match (typical range 3-7)
    avg_corners = max(3.0, min(7.0, corner_frequency * 0.25))
    
    # Corner threat based on set-piece proficiency (using goals as proxy)
    if "Goals" in team_df.columns and team_df["Goals"].sum() > 0:
        set_piece_threat = min(team_df["Goals"].sum() * 0.08, 1.0)
    else:
        set_piece_threat = 0.5
    
    return {
        "avg_corners": round(avg_corners, 1),
        "corner_frequency": min(corner_frequency / 12, 1.0),  # Normalize to 0-1
        "corner_threat": set_piece_threat
    }

def load_corner_data(filepath="Germany Corner.xlsx"):
    """Load actual corner statistics from the provided Excel file"""
    try:
        corner_df = pd.read_excel(filepath, sheet_name='Sheet1')
        
        # Clean column names and data
        corner_df.columns = [str(col).strip() for col in corner_df.columns]
        
        # Extract team names and corner statistics
        corner_data = {}
        for _, row in corner_df.iterrows():
            if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip() not in ['', 'Matches of…', 'League average']:
                team_name = str(row.iloc[0]).strip()
                
                # Get corner statistics
                corners_for = row.iloc[2] if pd.notna(row.iloc[2]) else 4.5
                corners_against = row.iloc[3] if pd.notna(row.iloc[3]) else 4.5
                total_corners = row.iloc[5] if pd.notna(row.iloc[5]) else 9.0
                
                # Get corner probabilities from the table
                over_85_prob = row.iloc[6] if pd.notna(row.iloc[6]) else 0.5
                over_95_prob = row.iloc[7] if pd.notna(row.iloc[7]) else 0.5
                over_105_prob = row.iloc[8] if pd.notna(row.iloc[8]) else 0.5
                
                corner_data[team_name] = {
                    'corners_for_per_match': float(corners_for),
                    'corners_against_per_match': float(corners_against),
                    'total_corners_per_match': float(total_corners),
                    'over_85_probability': float(over_85_prob),
                    'over_95_probability': float(over_95_prob),
                    'over_105_probability': float(over_105_prob)
                }
        
        print(f"✅ Loaded corner data for {len(corner_data)} teams")
        return corner_data
        
    except Exception as e:
        print(f"❌ Error loading corner data: {e}")
        return {}

def load_form_data(filepath="Germany Form.xlsx"):
    """Load and process the form data from Italy Form.xlsx"""
    try:
        form_df = pd.read_excel(filepath, sheet_name='Sheet1')
        
        # Clean the data - skip metadata rows and find the actual table
        form_data = {}
        for _, row in form_df.iterrows():
            # Look for rows that contain team data (numeric values in GP column)
            if pd.notna(row.iloc[0]) and str(row.iloc[0]).strip().isdigit():
                team_name = str(row.iloc[1]).strip()
                
                form_data[team_name] = {
                    'GP': int(row.iloc[2]),
                    'W': int(row.iloc[3]),
                    'D': int(row.iloc[4]),
                    'L': int(row.iloc[5]),
                    'GF': int(row.iloc[6]),
                    'GA': int(row.iloc[7]),
                    'GD': int(row.iloc[8]),
                    'Pts': int(row.iloc[9]),
                    'Opponents_PPG': float(row.iloc[10])
                }
        
        print(f"✅ Loaded form data for {len(form_data)} teams")
        return form_data
        
    except Exception as e:
        print(f"❌ Error loading form data: {e}")
        return {}

def analyze_team_form(team_name, form_data):
    """Analyze a team's recent form and strength of schedule"""
    if team_name not in form_data:
        return {
            "form_rating": 0.5,
            "attack_form": 0.5,
            "defense_form": 0.5,
            "strength_of_schedule": 0.5,
            "momentum": 0.5,
            "form_confidence": 0.0
        }
    
    team_form = form_data[team_name]
    
    # Calculate form rating (0-1 scale)
    max_possible_pts = team_form['GP'] * 3
    form_rating = team_form['Pts'] / max_possible_pts
    
    # Calculate attack form (goals per game normalized)
    attack_form = min(team_form['GF'] / team_form['GP'] / 3.0, 1.0)  # Cap at 3 goals per game
    
    # Calculate defense form (goals against per game normalized)
    defense_form = 1.0 - min(team_form['GA'] / team_form['GP'] / 3.0, 1.0)  # Inverse
    
    # Strength of schedule (Opponents PPG normalized)
    strength_of_schedule = min(team_form['Opponents_PPG'] / 3.0, 1.0)  # Cap at 3.0 PPG
    
    # Momentum (recent performance trend)
    momentum = form_rating * (1 + (team_form['GD'] / team_form['GP']) * 0.1)
    
    # Form confidence (how reliable is this form)
    form_confidence = min(team_form['GP'] / 4.0, 1.0)  # Based on number of games
    
    return {
        "form_rating": form_rating,
        "attack_form": attack_form,
        "defense_form": defense_form,
        "strength_of_schedule": strength_of_schedule,
        "momentum": momentum,
        "form_confidence": form_confidence
    }

def predict_corners_with_real_data(team1_name, team2_name, corner_data, home_advantage=True):
    """Predict corners using actual corner statistics"""
    
    # Get team data
    team1_corners = corner_data.get(team1_name, {
        'corners_for_per_match': 4.5,
        'corners_against_per_match': 4.5,
        'total_corners_per_match': 9.0,
        'over_85_probability': 0.5,
        'over_95_probability': 0.5,
        'over_105_probability': 0.5
    })
    
    team2_corners = corner_data.get(team2_name, {
        'corners_for_per_match': 4.5,
        'corners_against_per_match': 4.5,
        'total_corners_per_match': 9.0,
        'over_85_probability': 0.5,
        'over_95_probability': 0.5,
        'over_105_probability': 0.5
    })
    
    # Apply home advantage
    home_multiplier = 1.1 if home_advantage else 1.0
    away_multiplier = 0.95 if home_advantage else 1.0
    
    # Calculate expected corners
    home_expected = team1_corners['corners_for_per_match'] * home_multiplier
    away_expected = team2_corners['corners_for_per_match'] * away_multiplier
    
    total_expected = home_expected + away_expected
    
    # Use actual probabilities from the data when available
    over_85_prob = (team1_corners['over_85_probability'] + team2_corners['over_85_probability']) / 2
    over_95_prob = (team1_corners['over_95_probability'] + team2_corners['over_95_probability']) / 2
    over_105_prob = (team1_corners['over_105_probability'] + team2_corners['over_105_probability']) / 2
    
    # Adjust probabilities based on current matchup
    if total_expected > 10.5:
        over_85_prob = min(over_85_prob * 1.2, 0.95)
        over_95_prob = min(over_95_prob * 1.15, 0.85)
        over_105_prob = min(over_105_prob * 1.1, 0.75)
    elif total_expected < 8.0:
        over_85_prob = max(over_85_prob * 0.8, 0.05)
        over_95_prob = max(over_95_prob * 0.7, 0.05)
        over_105_prob = max(over_105_prob * 0.6, 0.05)
    
    # Team-specific corner probabilities
    home_over_45 = 0.5 + (home_expected - 4.5) * 0.15
    home_under_45 = 1 - home_over_45
    
    away_over_35 = 0.5 + (away_expected - 3.5) * 0.15
    away_under_35 = 1 - away_over_35
    
    corner_probabilities = {
        "Over 8.5 Corners": max(0.05, min(0.95, over_85_prob)),
        "Under 8.5 Corners": max(0.05, min(0.95, 1 - over_85_prob)),
        "Over 9.5 Corners": max(0.05, min(0.95, over_95_prob)),
        "Under 9.5 Corners": max(0.05, min(0.95, 1 - over_95_prob)),
        "Over 10.5 Corners": max(0.05, min(0.95, over_105_prob)),
        "Under 10.5 Corners": max(0.05, min(0.95, 1 - over_105_prob)),
        "Home Over 4.5": max(0.05, min(0.95, home_over_45)),
        "Home Under 4.5": max(0.05, min(0.95, home_under_45)),
        "Away Over 3.5": max(0.05, min(0.95, away_over_35)),
        "Away Under 3.5": max(0.05, min(0.95, away_under_35))
    }
    
    return {
        "expected_total_corners": round(total_expected, 1),
        "expected_home_corners": round(home_expected, 1),
        "expected_away_corners": round(away_expected, 1),
        "probabilities": corner_probabilities,
        "data_quality": "REAL_STATS"
    }

def predict_corners(team1_corner_profile, team2_corner_profile, home_advantage=True):
    """Predict total corners and corner-based betting markets"""
    
    # Base corner prediction from team profiles
    home_corners = team1_corner_profile["avg_corners"]
    away_corners = team2_corner_profile["avg_corners"]
    
    # Apply home advantage adjustment
    if home_advantage:
        home_corners *= 1.15  # Home teams typically get more corners
        away_corners *= 0.9
    
    # Adjust based on attacking style
    home_corners *= (1 + team1_corner_profile["corner_frequency"] * 0.15)
    away_corners *= (1 + team2_corner_profile["corner_frequency"] * 0.15)
    
    total_corners = home_corners + away_corners
    
    # Calculate probabilities for corner markets
    corner_probabilities = {
        "Over 8.5 Corners": max(0.1, min(0.9, (total_corners - 8.5) * 0.25 + 0.5)),
        "Under 8.5 Corners": max(0.1, min(0.9, 1 - ((total_corners - 8.5) * 0.25 + 0.5))),
        "Over 9.5 Corners": max(0.1, min(0.9, (total_corners - 9.5) * 0.3 + 0.5)),
        "Under 9.5 Corners": max(0.1, min(0.9, 1 - ((total_corners - 9.5) * 0.3 + 0.5))),
        "Home Over 4.5": max(0.1, min(0.9, (home_corners - 4.5) * 0.3 + 0.5)),
        "Home Under 4.5": max(0.1, min(0.9, 1 - ((home_corners - 4.5) * 0.3 + 0.5))),
        "Away Over 3.5": max(0.1, min(0.9, (away_corners - 3.5) * 0.3 + 0.5)),
        "Away Under 3.5": max(0.1, min(0.9, 1 - ((away_corners - 3.5) * 0.3 + 0.5)))
    }
    
    return {
        "expected_total_corners": round(total_corners, 1),
        "expected_home_corners": round(home_corners, 1),
        "expected_away_corners": round(away_corners, 1),
        "probabilities": corner_probabilities
    }

def calculate_halftime_probabilities(lambda_home, lambda_away, team1_style, team2_style):
    """Calculate probabilities for scoring in each half"""
    # First half typically has 40-45% of total goals, second half 55-60%
    first_half_ratio = 0.43
    second_half_ratio = 0.57
    
    # Adjust based on team styles
    if team1_style["style"] == "Attacking":
        first_half_ratio += 0.05  # Attacking teams start strong
    if team2_style["style"] == "Defensive":
        first_half_ratio -= 0.03  # Defensive teams may hold out early
    
    # Calculate expected goals per half
    home_first_half = lambda_home * first_half_ratio
    home_second_half = lambda_home * second_half_ratio
    away_first_half = lambda_away * first_half_ratio
    away_second_half = lambda_away * second_half_ratio
    
    # Probability of scoring at least one goal in each half
    home_score_first_half = 1 - poisson(0, home_first_half)
    home_score_second_half = 1 - poisson(0, home_second_half)
    away_score_first_half = 1 - poisson(0, away_first_half)
    away_score_second_half = 1 - poisson(0, away_second_half)
    
    return {
        "home_first_half_goal_prob": home_score_first_half,
        "home_second_half_goal_prob": home_score_second_half,
        "away_first_half_goal_prob": away_score_first_half,
        "away_second_half_goal_prob": away_score_second_half,
        "home_first_half_goals": home_first_half,
        "home_second_half_goals": home_second_half,
        "away_first_half_goals": away_first_half,
        "away_second_half_goals": away_second_half
    }

def calculate_key_score_probabilities(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg):
    """Calculate probabilities for key scorelines with explanations"""
    score_probs = {}
    explanations = {}
    
    # Calculate probabilities using Poisson distribution
    score_probs["1-0"] = poisson(1, lambda_home) * poisson(0, lambda_away)
    score_probs["0-0"] = poisson(0, lambda_home) * poisson(0, lambda_away)
    score_probs["2-0"] = poisson(2, lambda_home) * poisson(0, lambda_away)
    score_probs["1-1"] = poisson(1, lambda_home) * poisson(1, lambda_away)
    score_probs["0-1"] = poisson(0, lambda_home) * poisson(1, lambda_away)
    
    # Generate explanations based on stats
    explanations["1-0"] = generate_1_0_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg)
    explanations["0-0"] = generate_0_0_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg)
    explanations["2-0"] = generate_2_0_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg)
    explanations["1-1"] = generate_1_1_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg)
    explanations["0-1"] = generate_0_1_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg)
    
    return score_probs, explanations

def generate_1_0_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg):
    """Generate explanation for 1-0 scoreline"""
    reasons = []
    if lambda_home > lambda_away:
        reasons.append(f"{team1_name} has stronger attack ({lambda_home:.2f} expected goals vs {lambda_away:.2f})")
    if team2_xg["xg_efficiency"] < 0.9:
        reasons.append(f"{team2_name} poor finishing (xG efficiency: {team2_xg['xg_efficiency']:.2f})")
    if lambda_away < 0.8:
        reasons.append(f"{team2_name} limited attacking threat")
    if team1_xg["xg_efficiency"] > 1.1:
        reasons.append(f"{team1_name} clinical finishing (xG efficiency: {team1_xg['xg_efficiency']:.2f})")
    
    return " | ".join(reasons) if reasons else "Balanced match with home edge"

def generate_0_0_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg):
    """Generate explanation for 0-0 scoreline"""
    reasons = []
    if lambda_home < 1.0 and lambda_away < 1.0:
        reasons.append("Both teams have low expected goals")
    if team1_xg["xg_efficiency"] < 0.9 and team2_xg["xg_efficiency"] < 0.9:
        reasons.append("Both teams inefficient in front of goal")
    if lambda_home + lambda_away < 1.5:
        reasons.append("Very low total expected goals")
    
    return " | ".join(reasons) if reasons else "Defensive stalemate"

def generate_2_0_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg):
    """Generate explanation for 2-0 scoreline"""
    reasons = []
    if lambda_home > 1.5:
        reasons.append(f"{team1_name} strong attacking performance expected")
    if lambda_away < 0.5:
        reasons.append(f"{team2_name} very limited attacking threat")
    if team1_xg["xg_efficiency"] > 1.2:
        reasons.append(f"{team1_name} excellent finishing quality")
    if team2_xg["xg_efficiency"] < 0.8:
        reasons.append(f"{team2_name} wasteful in front of goal")
    
    return " | ".join(reasons) if reasons else "Home dominance expected"

def generate_1_1_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg):
    """Generate explanation for 1-1 scoreline"""
    reasons = []
    if abs(lambda_home - lambda_away) < 0.3:
        reasons.append("Evenly matched teams")
    if lambda_home > 1.0 and lambda_away > 1.0:
        reasons.append("Both teams have decent attacking threat")
    if team1_xg["xg_efficiency"] > 1.0 and team2_xg["xg_efficiency"] > 1.0:
        reasons.append("Both teams efficient finishers")
    
    return " | ".join(reasons) if reasons else "Balanced match with goals both ends"

def generate_0_1_explanation(lambda_home, lambda_away, team1_name, team2_name, team1_xg, team2_xg):
    """Generate explanation for 0-1 scoreline"""
    reasons = []
    if lambda_away > lambda_home:
        reasons.append(f"{team2_name} has stronger attack ({lambda_away:.2f} expected goals vs {lambda_home:.2f})")
    if team1_xg["xg_efficiency"] < 0.9:
        reasons.append(f"{team1_name} poor finishing (xG efficiency: {team1_xg['xg_efficiency']:.2f})")
    if lambda_home < 0.8:
        reasons.append(f"{team1_name} limited attacking threat")
    if team2_xg["xg_efficiency"] > 1.1:
        reasons.append(f"{team2_name} clinical finishing (xG efficiency: {team2_xg['xg_efficiency']:.2f})")
    
    return " | ".join(reasons) if reasons else "Away team advantage"

def get_xg_efficiency_advantage(eff1, eff2, team1_name, team2_name):
    """Explain which team has the xG efficiency advantage"""
    if eff1 > eff2 and eff1 > 1.1:
        advantage = eff1 - eff2
        if advantage > 0.3:
            return f"STRONG advantage to {team1_name} - much more clinical finishing"
        elif advantage > 0.15:
            return f"Moderate advantage to {team1_name} - better finishing quality"
        else:
            return f"Slight advantage to {team1_name} - marginally better finishing"
    
    elif eff2 > eff1 and eff2 > 1.1:
        advantage = eff2 - eff1
        if advantage > 0.3:
            return f"STRONG advantage to {team2_name} - much more clinical finishing"
        elif advantage > 0.15:
            return f"Moderate advantage to {team2_name} - better finishing quality"
        else:
            return f"Slight advantage to {team2_name} - marginally better finishing"
    
    elif eff1 > 1.1 and eff2 > 1.1:
        return "Both teams efficient - expect clinical finishing from both sides"
    elif eff1 < 0.9 and eff2 < 0.9:
        return "Both teams inefficient - may waste scoring opportunities"
    else:
        return "Similar finishing efficiency - no clear advantage"

def get_goal_expectation_analysis(eff1, eff2):
    """Analyze what xG efficiency means for goal expectations"""
    analyses = []
    
    if eff1 > 1.2:
        analyses.append("Home team OVERPERFORMING xG by 20%+ (clinical finishers)")
    elif eff1 > 1.1:
        analyses.append("Home team slightly overperforming xG (efficient finishing)")
    elif eff1 < 0.9:
        analyses.append("Home team UNDERPERFORMING xG (wasteful in front of goal)")
    elif eff1 < 0.8:
        analyses.append("Home team significantly underperforming xG (poor finishing)")
    
    if eff2 > 1.2:
        analyses.append("Away team OVERPERFORMING xG by 20%+ (clinical finishers)")
    elif eff2 > 1.1:
        analyses.append("Away team slightly overperforming xG (efficient finishing)")
    elif eff2 < 0.9:
        analyses.append("Away team UNDERPERFORMING xG (wasteful in front of goal)")
    elif eff2 < 0.8:
        analyses.append("Away team significantly underperforming xG (poor finishing)")
    
    if not analyses:
        analyses.append("Both teams converting chances as expected")
    
    return " | ".join(analyses)

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

def analyze_team_role_composition(team_df):
    """Analyze team composition and role-based strengths"""
    if team_df.empty:
        return {
            "role_distribution": {},
            "primary_strength": "Unknown",
            "weakness": "Unknown",
            "playing_style": "Balanced",
            "attacker_strength": 0,
            "midfielder_strength": 0,
            "defender_strength": 0
        }
    
    # Get role distribution - handle missing columns
    if "Role_Category" not in team_df.columns:
        # Fallback: create basic role categories from existing data
        role_distribution = {"Attackers": 0.33, "Midfielders": 0.33, "Defenders": 0.33}
    else:
        role_counts = team_df["Role_Category"].value_counts()
        total_players = len(team_df)
        
        role_distribution = {}
        for role, count in role_counts.items():
            role_distribution[role] = count / total_players
    
    # Calculate role-based strengths with fallbacks
    if "Role_Category" in team_df.columns and "Role_Based_Score" in team_df.columns:
        attacker_strength = team_df[team_df["Role_Category"] == "Attackers"]["Role_Based_Score"].sum()
        midfielder_strength = team_df[team_df["Role_Category"] == "Midfielders"]["Role_Based_Score"].sum()
        defender_strength = team_df[team_df["Role_Category"] == "Defenders"]["Role_Based_Score"].sum()
    else:
        # Fallback: estimate from goals and assists
        attacker_strength = team_df["Goals"].sum() + team_df["Assists"].sum()
        midfielder_strength = team_df["xA"].sum() + team_df.get("Progressive_Passes", pd.Series([0])).sum() * 0.1
        defender_strength = team_df.get("Defense_Index", pd.Series([0])).sum()
    
    # Determine primary strength
    strengths = {
        "Attacking": attacker_strength,
        "Midfield Control": midfielder_strength,
        "Defensive Solidarity": defender_strength
    }
    
    primary_strength = max(strengths, key=strengths.get) if any(strengths.values()) else "Unknown"
    
    # Determine weakness
    weakness = min(strengths, key=strengths.get) if any(strengths.values()) else "Unknown"
    
    # Determine playing style based on role distribution
    if role_distribution.get("Attackers", 0) > 0.35:
        playing_style = "Attacking"
    elif role_distribution.get("Defenders", 0) > 0.35:
        playing_style = "Defensive"
    elif role_distribution.get("Midfielders", 0) > 0.35:
        playing_style = "Possession-based"
    else:
        playing_style = "Balanced"
    
    return {
        "role_distribution": role_distribution,
        "primary_strength": primary_strength,
        "weakness": weakness,
        "playing_style": playing_style,
        "attacker_strength": attacker_strength,
        "midfielder_strength": midfielder_strength,
        "defender_strength": defender_strength
    }

def get_role_based_matchup_analysis(team1_roles, team2_roles, team1_name, team2_name):
    """Generate matchup analysis based on role compositions"""
    analysis = []
    
    # Attacking matchup
    if team1_roles["attacker_strength"] > team2_roles["attacker_strength"] * 1.2:
        analysis.append(f"⚡ {team1_name} has significantly stronger attacking threat")
    elif team2_roles["attacker_strength"] > team1_roles["attacker_strength"] * 1.2:
        analysis.append(f"⚡ {team2_name} has significantly stronger attacking threat")
    
    # Midfield matchup
    if team1_roles["midfielder_strength"] > team2_roles["midfielder_strength"] * 1.2:
        analysis.append(f"🎯 {team1_name} should dominate midfield possession")
    elif team2_roles["midfielder_strength"] > team1_roles["midfielder_strength"] * 1.2:
        analysis.append(f"🎯 {team2_name} should dominate midfield possession")
    
    # Defensive matchup
    if team1_roles["defender_strength"] > team2_roles["defender_strength"] * 1.2:
        analysis.append(f"🛡️ {team1_name} has stronger defensive organization")
    elif team2_roles["defender_strength"] > team1_roles["defender_strength"] * 1.2:
        analysis.append(f"🛡️ {team2_name} has stronger defensive organization")
    
    # Style matchup
    if team1_roles["playing_style"] == "Attacking" and team2_roles["playing_style"] == "Defensive":
        analysis.append("⚔️ Classic attack vs defense matchup expected")
    elif team1_roles["playing_style"] == "Defensive" and team2_roles["playing_style"] == "Attacking":
        analysis.append("⚔️ Classic defense vs attack matchup expected")
    elif team1_roles["playing_style"] == "Attacking" and team2_roles["playing_style"] == "Attacking":
        analysis.append("🔥 Both teams favor attacking football - expect goals")
    elif team1_roles["playing_style"] == "Defensive" and team2_roles["playing_style"] == "Defensive":
        analysis.append("🔒 Both teams defensively oriented - low scoring likely")
    
    return analysis if analysis else ["⚖️ Teams are evenly matched across all areas"]

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

def get_betting_suggestions_and_markets(team1_df, team2_df, team1_sentiment=None, team2_sentiment=None, home_team=None, team1_pressure_data=None, team2_pressure_data=None, corner_data=None, form_data=None):
    if team1_df.empty or team2_df.empty:
        raise ValueError("One of the team datasets is empty.")

    # Get team names
    team1_name = team1_df['Team'].iloc[0]
    team2_name = team2_df['Team'].iloc[0]

    # ENHANCED: Analyze team styles and xG profiles
    team1_style = analyze_team_style(team1_df)
    team2_style = analyze_team_style(team2_df)
    team1_xg = analyze_team_xg_profile(team1_df)
    team2_xg = analyze_team_xg_profile(team2_df)
    
    # NEW: Role-based team analysis
    team1_roles = analyze_team_role_composition(team1_df)
    team2_roles = analyze_team_role_composition(team2_df)
    
    # NEW: Form analysis
    team1_form = analyze_team_form(team1_name, form_data) if form_data else None
    team2_form = analyze_team_form(team2_name, form_data) if form_data else None
    
    # Print form analysis if available
    if team1_form and team2_form:
        print(f"📈 FORM ANALYSIS:")
        print(f"   {team1_name}: {team1_form['form_rating']:.1%} form, {team1_form['strength_of_schedule']:.1%} SOS, Momentum: {team1_form['momentum']:.2f}")
        print(f"   {team2_name}: {team2_form['form_rating']:.1%} form, {team2_form['strength_of_schedule']:.1%} SOS, Momentum: {team2_form['momentum']:.2f}")
    
    # Use REAL corner data instead of estimates
    if corner_data is not None:
        corner_prediction = predict_corners_with_real_data(team1_name, team2_name, corner_data, home_advantage=True)
        print(f"📊 USING REAL CORNER DATA:")
        print(f"   {team1_name}: {corner_prediction['expected_home_corners']:.1f} corners expected")
        print(f"   {team2_name}: {corner_prediction['expected_away_corners']:.1f} corners expected")
        print(f"   Total: {corner_prediction['expected_total_corners']:.1f} corners expected")
        print(f"   Data Quality: {corner_prediction['data_quality']}")
    else:
        # Fallback to estimated corner data
        team1_corners = analyze_team_corner_profile(team1_df)
        team2_corners = analyze_team_corner_profile(team2_df)
        corner_prediction = predict_corners(team1_corners, team2_corners, home_advantage=True)
        print(f"⚠️ Using ESTIMATED corner data (fallback)")
    
    print(f"🎯 Team Styles: {team1_df['Team'].iloc[0]} = {team1_style['style']}, {team2_df['Team'].iloc[0]} = {team2_style['style']}")
    print(f"📊 xG Analysis: {team1_df['Team'].iloc[0]} (Eff: {team1_xg['xg_efficiency']:.2f}, Pen: {team1_xg['penalty_reliance']:.2f})")
    print(f"📊 xG Analysis: {team2_df['Team'].iloc[0]} (Eff: {team2_xg['xg_efficiency']:.2f}, Pen: {team2_xg['penalty_reliance']:.2f})")
    
    # NEW: Print role-based analysis
    print(f"👥 {team1_df['Team'].iloc[0]} Role Analysis: {team1_roles['playing_style']} style, Primary: {team1_roles['primary_strength']}")
    print(f"👥 {team2_df['Team'].iloc[0]} Role Analysis: {team2_roles['playing_style']} style, Primary: {team2_roles['primary_strength']}")

    # Enhanced strength calculation with role-based consideration AND FORM DATA
    a1 = (team1_df["Goals"].sum() + 0.8 * team1_df["xG"].sum()) * (1 + team1_style["attack_strength"] * 0.2)
    a2 = (team2_df["Goals"].sum() + 0.8 * team2_df["xG"].sum()) * (1 + team2_style["attack_strength"] * 0.2)
    
    # Apply form adjustments if available
    if team1_form:
        a1 *= (1 + (team1_form["form_rating"] - 0.5) * 0.3)  # ±30% based on form
        a1 *= (1 + (team1_form["momentum"] - 1.0) * 0.2)     # ±20% based on momentum
    if team2_form:
        a2 *= (1 + (team2_form["form_rating"] - 0.5) * 0.3)
        a2 *= (1 + (team2_form["momentum"] - 1.0) * 0.2)
    
    # Apply role-based adjustments
    total_strength_1 = max(team1_roles["attacker_strength"] + team1_roles["midfielder_strength"] + team1_roles["defender_strength"], 1)
    total_strength_2 = max(team2_roles["attacker_strength"] + team2_roles["midfielder_strength"] + team2_roles["defender_strength"], 1)
    
    role_factor_1 = 1 + (team1_roles["attacker_strength"] / total_strength_1) * 0.3
    role_factor_2 = 1 + (team2_roles["attacker_strength"] / total_strength_2) * 0.3
    
    a1 *= role_factor_1
    a2 *= role_factor_2
    
    # Apply xG efficiency adjustments
    a1 *= (1 + (team1_xg["xg_efficiency"] - 1) * 0.3)
    a2 *= (1 + (team2_xg["xg_efficiency"] - 1) * 0.3)
    
    # Defensive adjustments with role-based consideration AND FORM DATA
    d1 = team1_style["defense_strength"] * 0.3 * (1 + team1_roles["defender_strength"] / total_strength_1 * 0.5)
    d2 = team2_style["defense_strength"] * 0.3 * (1 + team2_roles["defender_strength"] / total_strength_2 * 0.5)
    
    # Apply defensive form adjustments
    if team1_form:
        d1 *= (1 + (team1_form["defense_form"] - 0.5) * 0.4)  # ±40% based on defensive form
    if team2_form:
        d2 *= (1 + (team2_form["defense_form"] - 0.5) * 0.4)
    
    total = max(a1 + a2, 1e-6)
    
    # Enhanced lambda calculation with style, xG, role, and form factors
    lambda_home = 1.6 * (a1 / total) * (1 - d2)
    lambda_away = 1.2 * (a2 / total) * (1 - d1)

    # ENHANCED: Apply European qualification and relegation pressure adjustments
    european_boost = 1.0
    relegation_boost = 1.0
    
    if team1_pressure_data is not None:
        pressure_level = team1_pressure_data.get('Pressure_Level', 'NEUTRAL')
        total_pressure = team1_pressure_data.get('Total_Pressure', 0)
        champions_league = team1_pressure_data.get('Champions_League_Zone', False)
        europa_league = team1_pressure_data.get('Europa_League_Zone', False)
        
        print(f"🎯 {team1_df['Team'].iloc[0]} Pressure Analysis: {pressure_level} (Pressure Score: {total_pressure})")
        
        # European qualification motivation boosts
        if pressure_level in ['HIGH_EUROPEAN', 'MODERATE_EUROPEAN']:
            if champions_league:
                european_boost = 1.20  # 20% boost for Champions League chase
                print(f"   🏆 CHAMPIONS LEAGUE BOOST: {team1_df['Team'].iloc[0]} gets 20% motivation boost (UCL qualification)")
            elif europa_league:
                european_boost = 1.15  # 15% boost for Europa League chase
                print(f"   🌍 EUROPA LEAGUE BOOST: {team1_df['Team'].iloc[0]} gets 15% motivation boost (UEFA qualification)")
        
        # Relegation battle motivation boosts
        elif pressure_level in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']:
            relegation_boost = 1.15  # 15% boost due to desperation
            print(f"   ⚡ RELEGATION BOOST: {team1_df['Team'].iloc[0]} gets 15% motivation boost (fighting for survival)")
    
    if team2_pressure_data is not None:
        pressure_level = team2_pressure_data.get('Pressure_Level', 'NEUTRAL')
        total_pressure = team2_pressure_data.get('Total_Pressure', 0)
        champions_league = team2_pressure_data.get('Champions_League_Zone', False)
        europa_league = team2_pressure_data.get('Europa_League_Zone', False)
        
        print(f"🎯 {team2_df['Team'].iloc[0]} Pressure Analysis: {pressure_level} (Pressure Score: {total_pressure})")
        
        if pressure_level in ['HIGH_EUROPEAN', 'MODERATE_EUROPEAN']:
            if champions_league:
                european_boost = 1.20
                print(f"   🏆 CHAMPIONS LEAGUE BOOST: {team2_df['Team'].iloc[0]} gets 20% motivation boost (UCL qualification)")
            elif europa_league:
                european_boost = 1.15
                print(f"   🌍 EUROPA LEAGUE BOOST: {team2_df['Team'].iloc[0]} gets 15% motivation boost (UEFA qualification)")
        
        elif pressure_level in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']:
            relegation_boost = 1.15
            print(f"   ⚡ RELEGATION BOOST: {team2_df['Team'].iloc[0]} gets 15% motivation boost (fighting for survival)")

    # Apply home advantage with European/relegation consideration
    if home_team:
        lambda_home *= 1.05  # Base home advantage
        
        # Home teams in European/relegation battles get extra boosts
        if team1_pressure_data:
            pressure_level = team1_pressure_data.get('Pressure_Level', 'NEUTRAL')
            if pressure_level in ['HIGH_EUROPEAN', 'MODERATE_EUROPEAN']:
                lambda_home *= 1.10  # Additional 5% for home teams chasing Europe
                print(f"   🏠 HOME EUROPEAN BOOST: Extra 5% for home team chasing European qualification")
            elif pressure_level in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']:
                lambda_home *= 1.08  # Additional 3% for home teams in relegation battle
                print(f"   🏠 HOME RELEGATION BOOST: Extra 3% for home team in relegation battle")

    # Apply sentiment adjustments with relegation consideration
    if team1_sentiment is not None and team2_sentiment is not None:
        diff = team1_sentiment - team2_sentiment
        # Teams under relegation pressure get amplified sentiment effects
        sentiment_multiplier = 1.5 if (team1_pressure_data and team1_pressure_data.get('Pressure_Level') in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']) else 1.0
        sentiment_multiplier = 1.5 if (team2_pressure_data and team2_pressure_data.get('Pressure_Level') in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']) else sentiment_multiplier
        
        lambda_home *= (1 + diff * 0.004 * sentiment_multiplier)
        lambda_away *= (1 - diff * 0.004 * sentiment_multiplier)

    # Apply European motivation boosts
    if team1_pressure_data and team1_pressure_data.get('Pressure_Level') in ['HIGH_EUROPEAN', 'MODERATE_EUROPEAN']:
        lambda_home *= european_boost
    if team2_pressure_data and team2_pressure_data.get('Pressure_Level') in ['HIGH_EUROPEAN', 'MODERATE_EUROPEAN']:
        lambda_away *= european_boost

    # Apply relegation motivation boosts
    if team1_pressure_data and team1_pressure_data.get('Pressure_Level') in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']:
        lambda_home *= relegation_boost
    if team2_pressure_data and team2_pressure_data.get('Pressure_Level') in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']:
        lambda_away *= relegation_boost

    pm = score_prob_matrix(lambda_home, lambda_away, max_goals=6)
    derived = derive_match_probs_from_poisson(pm)

    # Calculate half-time scoring probabilities
    halftime_probs = calculate_halftime_probabilities(lambda_home, lambda_away, team1_style, team2_style)
    
    # Calculate key score probabilities with explanations
    key_scores, score_explanations = calculate_key_score_probabilities(
        lambda_home, lambda_away, 
        team1_df['Team'].iloc[0], team2_df['Team'].iloc[0],
        team1_xg, team2_xg
    )

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
        },
        "Total Corners": {
            "Over 8.5": corner_prediction["probabilities"]["Over 8.5 Corners"],
            "Under 8.5": corner_prediction["probabilities"]["Under 8.5 Corners"],
            "Over 9.5": corner_prediction["probabilities"]["Over 9.5 Corners"],
            "Under 9.5": corner_prediction["probabilities"]["Under 9.5 Corners"],
            "Over 10.5": corner_prediction["probabilities"]["Over 10.5 Corners"],
            "Under 10.5": corner_prediction["probabilities"]["Under 10.5 Corners"]
        },
        "Team Corners": {
            "Home Over 4.5": corner_prediction["probabilities"]["Home Over 4.5"],
            "Home Under 4.5": corner_prediction["probabilities"]["Home Under 4.5"],
            "Away Over 3.5": corner_prediction["probabilities"]["Away Over 3.5"],
            "Away Under 3.5": corner_prediction["probabilities"]["Away Under 3.5"]
        }
    }

    # Calculate value bets
    value_bets = calculate_value_bets(our_probabilities, BETTING_ODDS)

    suggestions = defaultdict(list)
    suggestions["Match Result"].append(f"Predicted: {best} (P={probs[best]:.2f})")
    suggestions["Over/Under 2.5"].append("Over 2.5" if derived["Exp_goals"] > 2.5 else "Under 2.5")
    
    # NEW: Role-based matchup analysis
    matchup_analysis = get_role_based_matchup_analysis(team1_roles, team2_roles, team1_df['Team'].iloc[0], team2_df['Team'].iloc[0])
    suggestions["Role-Based Matchup"] = matchup_analysis
    
    # FORM-BASED SUGGESTIONS
    if team1_form and team2_form:
        suggestions["Form Analysis"] = []
        
        # Strong form vs weak form
        if team1_form["form_rating"] > 0.7 and team2_form["form_rating"] < 0.4:
            suggestions["Form Analysis"].append(f"🔥 {team1_name} in EXCELLENT form vs {team2_name} in POOR form")
        elif team2_form["form_rating"] > 0.7 and team1_form["form_rating"] < 0.4:
            suggestions["Form Analysis"].append(f"🔥 {team2_name} in EXCELLENT form vs {team1_name} in POOR form")
        
        # Strength of schedule insights
        if team1_form["strength_of_schedule"] > 0.7 and team1_form["form_rating"] > 0.6:
            suggestions["Form Analysis"].append(f"💪 {team1_name}'s strong form came against TOUGH opponents")
        if team2_form["strength_of_schedule"] > 0.7 and team2_form["form_rating"] > 0.6:
            suggestions["Form Analysis"].append(f"💪 {team2_name}'s strong form came against TOUGH opponents")
        
        # Momentum insights
        if team1_form["momentum"] > 1.2:
            suggestions["Form Analysis"].append(f"📈 {team1_name} has STRONG positive momentum")
        if team2_form["momentum"] > 1.2:
            suggestions["Form Analysis"].append(f"📈 {team2_name} has STRONG positive momentum")
    
    # ENHANCED: European qualification insights
    suggestions["European Qualification Analysis"] = []
    if team1_pressure_data:
        champions_league = team1_pressure_data.get('Champions_League_Zone', False)
        europa_league = team1_pressure_data.get('Europa_League_Zone', False)
        pressure_level = team1_pressure_data.get('Pressure_Level', 'NEUTRAL')
        
        if champions_league:
            suggestions["European Qualification Analysis"].append(f"🏆 {team1_df['Team'].iloc[0]} in CHAMPIONS LEAGUE spots - high motivation")
        elif europa_league:
            suggestions["European Qualification Analysis"].append(f"🌍 {team1_df['Team'].iloc[0]} in EUROPA LEAGUE spots - strong motivation")
        elif pressure_level in ['HIGH_EUROPEAN', 'MODERATE_EUROPEAN']:
            suggestions["European Qualification Analysis"].append(f"📈 {team1_df['Team'].iloc[0]} chasing EUROPEAN qualification - motivated")
    
    if team2_pressure_data:
        champions_league = team2_pressure_data.get('Champions_League_Zone', False)
        europa_league = team2_pressure_data.get('Europa_League_Zone', False)
        pressure_level = team2_pressure_data.get('Pressure_Level', 'NEUTRAL')
        
        if champions_league:
            suggestions["European Qualification Analysis"].append(f"🏆 {team2_df['Team'].iloc[0]} in CHAMPIONS LEAGUE spots - high motivation")
        elif europa_league:
            suggestions["European Qualification Analysis"].append(f"🌍 {team2_df['Team'].iloc[0]} in EUROPA LEAGUE spots - strong motivation")
        elif pressure_level in ['HIGH_EUROPEAN', 'MODERATE_EUROPEAN']:
            suggestions["European Qualification Analysis"].append(f"📈 {team2_df['Team'].iloc[0]} chasing EUROPEAN qualification - motivated")

    # ENHANCED: Relegation pressure insights
    suggestions["Relegation Pressure Analysis"] = []
    if team1_pressure_data:
        pressure_level = team1_pressure_data.get('Pressure_Level', 'NEUTRAL')
        relegation_zone = team1_pressure_data.get('Relegation_Zone', False)
        if pressure_level in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']:
            if relegation_zone:
                suggestions["Relegation Pressure Analysis"].append(f"🚨 {team1_df['Team'].iloc[0]} in RELEGATION ZONE - fighting for survival")
            else:
                suggestions["Relegation Pressure Analysis"].append(f"⚠️ {team1_df['Team'].iloc[0]} under HIGH pressure - need points")
    
    if team2_pressure_data:
        pressure_level = team2_pressure_data.get('Pressure_Level', 'NEUTRAL')
        relegation_zone = team2_pressure_data.get('Relegation_Zone', False)
        if pressure_level in ['CRITICAL_RELEGATION', 'HIGH_RELEGATION']:
            if relegation_zone:
                suggestions["Relegation Pressure Analysis"].append(f"🚨 {team2_df['Team'].iloc[0]} in RELEGATION ZONE - fighting for survival")
            else:
                suggestions["Relegation Pressure Analysis"].append(f"⚠️ {team2_df['Team'].iloc[0]} under HIGH pressure - need points")
    
    # ENHANCED: Style and xG based suggestions with pressure context
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

    # CORNER SUGGESTIONS
    total_corners = corner_prediction['expected_total_corners']
    home_corners = corner_prediction['expected_home_corners']
    away_corners = corner_prediction['expected_away_corners']
    
    suggestions["Corner Markets"] = []
    
    # Enhanced corner suggestions with real data
    if corner_data is not None:
        suggestions["Corner Markets"].append(f"📊 REAL CORNER DATA ANALYSIS:")
        suggestions["Corner Markets"].append(f"Expected Total: {total_corners:.1f} corners")
        suggestions["Corner Markets"].append(f"Home ({team1_name}): {home_corners:.1f} corners")
        suggestions["Corner Markets"].append(f"Away ({team2_name}): {away_corners:.1f} corners")
    else:
        suggestions["Corner Markets"].append(f"📊 ESTIMATED CORNER DATA:")
        suggestions["Corner Markets"].append(f"Expected Total: {total_corners:.1f} corners")
    
    # Strong recommendations based on real data
    over_85_prob = corner_prediction["probabilities"]["Over 8.5 Corners"]
    over_95_prob = corner_prediction["probabilities"]["Over 9.5 Corners"]
    over_105_prob = corner_prediction["probabilities"]["Over 10.5 Corners"]
    
    if over_85_prob > 0.7:
        suggestions["Corner Markets"].append(f"🎯 STRONG OVER 8.5: {over_85_prob:.1%} probability")
    elif over_85_prob < 0.3:
        suggestions["Corner Markets"].append(f"🎯 STRONG UNDER 8.5: {1-over_85_prob:.1%} probability")
    
    if over_95_prob > 0.65:
        suggestions["Corner Markets"].append(f"🎯 GOOD OVER 9.5: {over_95_prob:.1%} probability")
    elif over_95_prob < 0.35:
        suggestions["Corner Markets"].append(f"🎯 GOOD UNDER 9.5: {1-over_95_prob:.1%} probability")
    
    # Team-specific insights from real data
    if home_corners > 5.5:
        suggestions["Corner Markets"].append(f"⚡ {team1_name} HIGH corners: {home_corners:.1f} expected")
    if away_corners > 4.5:
        suggestions["Corner Markets"].append(f"⚡ {team2_name} HIGH corners: {away_corners:.1f} expected")

    # Half-time scoring insights
    suggestions["Half-Time Scoring"] = []
    if halftime_probs["home_first_half_goal_prob"] > 0.5:
        suggestions["Half-Time Scoring"].append(f"Home team likely to score in 1st half ({halftime_probs['home_first_half_goal_prob']:.1%})")
    if halftime_probs["home_second_half_goal_prob"] > 0.6:
        suggestions["Half-Time Scoring"].append(f"Home team very likely to score in 2nd half ({halftime_probs['home_second_half_goal_prob']:.1%})")
    if halftime_probs["away_first_half_goal_prob"] > 0.4:
        suggestions["Half-Time Scoring"].append(f"Away team may score in 1st half ({halftime_probs['away_first_half_goal_prob']:.1%})")
    if halftime_probs["away_second_half_goal_prob"] > 0.5:
        suggestions["Half-Time Scoring"].append(f"Away team likely to score in 2nd half ({halftime_probs['away_second_half_goal_prob']:.1%})")

    # Key score predictions with explanations
    suggestions["Key Score Probabilities"] = []
    for score in ["1-0", "0-0", "2-0", "1-1", "0-1"]:
        prob = key_scores.get(score, 0)
        explanation = score_explanations.get(score, "No specific factors")
        suggestions["Key Score Probabilities"].append(
            f"{score}: {prob:.1%} - {explanation}"
        )

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

    # ENHANCED: Clearer market probabilities with explanations
    markets = {
        "Home Win Probability": f"{derived['P_home']:.1%}",
        "Draw Probability": f"{derived['P_draw']:.1%}",
        "Away Win Probability": f"{derived['P_away']:.1%}",
        "Expected Total Goals": f"{derived['Exp_goals']:.2f}",
        "Both Teams Score Probability": f"{our_probabilities['Both Teams to Score']['Yes']:.1%}",
        "Over 2.5 Goals Probability": f"{our_probabilities['Over/Under 2.5']['Over']:.1%}",
        "Total Corners Expected": f"{corner_prediction['expected_total_corners']:.1f}",
        "Home Corners Expected": f"{corner_prediction['expected_home_corners']:.1f}",
        "Away Corners Expected": f"{corner_prediction['expected_away_corners']:.1f}",
        # Half-time scoring probabilities
        "Home Score in 1st Half": f"{halftime_probs['home_first_half_goal_prob']:.1%}",
        "Home Score in 2nd Half": f"{halftime_probs['home_second_half_goal_prob']:.1%}",
        "Away Score in 1st Half": f"{halftime_probs['away_first_half_goal_prob']:.1%}",
        "Away Score in 2nd Half": f"{halftime_probs['away_second_half_goal_prob']:.1%}"
    }

    # ENHANCED: Detailed confidence metrics with role-based insights
    conf = {
        "Prediction Confidence": f"{abs(max(probs.values()) - sorted(probs.values())[-2]):.1%}",
        "Expected Total Goals": f"{derived['Exp_goals']:.2f}",
        "Match Type": "Low-Scoring" if derived["Exp_goals"] < 2.0 else "High-Scoring" if derived["Exp_goals"] > 2.8 else "Average-Scoring",
        "Home Team Style": team1_style["style"],
        "Away Team Style": team2_style["style"],
        "Home Role Composition": team1_roles["playing_style"],
        "Away Role Composition": team2_roles["playing_style"],
        "xG Efficiency Analysis": f"{team1_df['Team'].iloc[0]}: {team1_xg['xg_efficiency']:.2f}, {team2_df['Team'].iloc[0]}: {team2_xg['xg_efficiency']:.2f}",
        "xG Efficiency Advantage": get_xg_efficiency_advantage(team1_xg['xg_efficiency'], team2_xg['xg_efficiency'], team1_df['Team'].iloc[0], team2_df['Team'].iloc[0]),
        "Penalty Reliance": f"{team1_df['Team'].iloc[0]}: {team1_xg['penalty_reliance']:.1%}, {team2_df['Team'].iloc[0]}: {team2_xg['penalty_reliance']:.1%}",
        "Goal Expectation vs Reality": get_goal_expectation_analysis(team1_xg['xg_efficiency'], team2_xg['xg_efficiency'])
    }

    # Add form analysis to confidence metrics
    if team1_form:
        conf["Home Form Rating"] = f"{team1_form['form_rating']:.1%}"
        conf["Home Strength of Schedule"] = f"{team1_form['strength_of_schedule']:.1%}"
    if team2_form:
        conf["Away Form Rating"] = f"{team2_form['form_rating']:.1%}"
        conf["Away Strength of Schedule"] = f"{team2_form['strength_of_schedule']:.1%}"

    # Add pressure analysis to confidence metrics
    if team1_pressure_data:
        conf["Home Pressure Level"] = team1_pressure_data.get('Pressure_Level', 'UNKNOWN')
        conf["Home Relegation Pressure"] = team1_pressure_data.get('Total_Pressure', 0)
    if team2_pressure_data:
        conf["Away Pressure Level"] = team2_pressure_data.get('Pressure_Level', 'UNKNOWN')
        conf["Away Relegation Pressure"] = team2_pressure_data.get('Total_Pressure', 0)

    return dict(suggestions), markets, conf, value_bets