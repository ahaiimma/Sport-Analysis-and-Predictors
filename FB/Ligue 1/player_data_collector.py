import pandas as pd
import os
import re
import numpy as np

# Define stat categories for different player roles
stat_categories = {
    "Core": [
        "Player", 
        "Team", 
        "Role", 
        "Minutes"
    ],
    "Attackers": [
        "Goals", 
        "Assists", 
        "xG", 
        "xA",
        "npxG", 
        "xAG",
        "npxG_xA",
        "xG_xA",
        "Non_Penalty_Goals",
        "Progressive_Receptions"
    ],
    "Midfielders": [
        "Assists",
        "xA",
        "Progressive_Carries", 
        "Progressive_Passes", 
        "Progressive_Receptions",
        "Tackles",
        "Interceptions"
    ],
    "Defenders": [
        "Tackles", 
        "Interceptions", 
        "Clearances", 
        "Blocks",
        "Yellow_Cards",
        "Red_Cards",
        "Progressive_Passes" # Important for modern defenders
    ]
}

def classify_player_role(position):
    """Classifies a player's raw position into a general category."""
    
    position_mapping = {
        'Attackers': ['FW', 'ST', 'LW', 'RW', 'CF', 'WF', 'SS', 'AM', 'RAM', 'LAM', 'CAM'],
        'Midfielders': ['MF', 'CM', 'CAM', 'CDM', 'LM', 'RM', 'WM', 'LCM', 'RCM', 'DM', 'CMF', 'OMF', 'DMF'],
        'Defenders': ['DF', 'CB', 'LB', 'RB', 'LWB', 'RWB', 'FB', 'LCB', 'RCB', 'SW'],
        'Goalkeepers': ['GK', 'G']
    }
    
    # Normalize the input position to uppercase for consistent matching
    if pd.isna(position):
        return "Unknown"
    
    pos_upper = str(position).upper().strip()
    
    for category, positions in position_mapping.items():
        if pos_upper in positions:
            return category
            
    # Handle edge cases and partial matches
    if any(attacker in pos_upper for attacker in ['FORWARD', 'ATTACK', 'STRIKER', 'WINGER']):
        return "Attackers"
    elif any(midfielder in pos_upper for midfielder in ['MIDFIELD', 'CENTRE', 'CENTRAL']):
        return "Midfielders"
    elif any(defender in pos_upper for defender in ['DEFENSE', 'BACK', 'DEFENDER']):
        return "Defenders"
    elif any(goalkeeper in pos_upper for goalkeeper in ['GOALKEEPER', 'KEEPER']):
        return "Goalkeepers"
    
    return "Unknown"

def calculate_role_based_score(player_row, role_category):
    """Calculate specialized score based on player role"""
    score = 0
    
    if role_category == "Attackers":
        # Attackers: Emphasize goals, xG, and creative output
        score += player_row.get("Goals", 0) * 5
        score += player_row.get("xG", 0) * 4
        score += player_row.get("Assists", 0) * 4
        score += player_row.get("xA", 0) * 3
        score += player_row.get("Non_Penalty_Goals", 0) * 2
        score += player_row.get("Progressive_Receptions", 0) * 0.2
        
    elif role_category == "Midfielders":
        # Midfielders: Balanced approach with creativity, progression, and defensive work
        score += player_row.get("Assists", 0) * 4
        score += player_row.get("xA", 0) * 3
        score += player_row.get("Progressive_Passes", 0) * 0.3
        score += player_row.get("Progressive_Carries", 0) * 0.3
        score += player_row.get("Progressive_Receptions", 0) * 0.2
        score += player_row.get("Tackles", 0) * 2
        score += player_row.get("Interceptions", 0) * 2
        score += player_row.get("Goals", 0) * 3  # Goals still valuable for midfielders
        
    elif role_category == "Defenders":
        # Defenders: Focus on defensive actions and ball progression
        score += player_row.get("Tackles", 0) * 4
        score += player_row.get("Interceptions", 0) * 4
        score += player_row.get("Clearances", 0) * 3
        score += player_row.get("Blocks", 0) * 3
        score += player_row.get("Progressive_Passes", 0) * 0.5
        score -= player_row.get("Yellow_Cards", 0) * 1
        score -= player_row.get("Red_Cards", 0) * 5
        
    elif role_category == "Goalkeepers":
        # Goalkeepers: Simplified scoring (you might want to add GK-specific stats)
        score += player_row.get("Clearances", 0) * 2
        # Note: You might want to add saves, clean sheets etc. if available
    
    # Apply minutes adjustment (players with more minutes get higher scores)
    minutes = player_row.get("Minutes", 0)
    if minutes > 0:
        score *= min(minutes / 900, 1.5)  # Normalize to 10 games (900 mins)
    
    return max(score, 0)  # Ensure non-negative

def calculate_role_specific_strength(player_row, role_category):
    """Calculate a descriptive strength for each player based on their role"""
    strengths = []
    
    if role_category == "Attackers":
        if player_row.get("Goals", 0) > 5:
            strengths.append("Clinical Finisher")
        if player_row.get("Assists", 0) > 3:
            strengths.append("Creative Playmaker")
        if player_row.get("xG", 0) > player_row.get("Goals", 0):
            strengths.append("Chance Creator")
        if player_row.get("Progressive_Receptions", 0) > 20:
            strengths.append("Advanced Threat")
            
    elif role_category == "Midfielders":
        if player_row.get("Assists", 0) > 2:
            strengths.append("Creative Engine")
        if player_row.get("Progressive_Passes", 0) > 30:
            strengths.append("Progressor")
        if player_row.get("Tackles", 0) > 10:
            strengths.append("Defensive Presence")
        if player_row.get("Progressive_Carries", 0) > 15:
            strengths.append("Ball Carrier")
            
    elif role_category == "Defenders":
        if player_row.get("Tackles", 0) > 15:
            strengths.append("Tackling Machine")
        if player_row.get("Interceptions", 0) > 10:
            strengths.append("Reading Game")
        if player_row.get("Clearances", 0) > 20:
            strengths.append("Aerial Dominance")
        if player_row.get("Progressive_Passes", 0) > 20:
            strengths.append("Ball Playing")
    
    return ", ".join(strengths) if strengths else "Solid Performer"

def load_player_data(filepath=None):
    if filepath is None:
        filepath = "FutBall.xlsx"

    print(f"📂 Loading player data from: {filepath}")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Player data file not found: {filepath}")

    try:
        print("📋 Trying to read 'Sheet1' directly...")
        df = pd.read_excel(filepath, sheet_name='Sheet1')
        print("✅ Successfully read 'Sheet1' directly")
    except Exception as e1:
        print(f"⚠️ Could not read 'Sheet1' directly: {e1}")
        try:
            df = pd.read_excel(filepath, sheet_name=0, header=0)
            print("✅ Successfully read first sheet")
        except Exception as e3:
            raise ValueError(f"❌ All reading methods failed: {e3}")

    print(f"🔍 Final columns found: {list(df.columns)}")
    print(f"📊 Final data shape: {df.shape}")

    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]
    print(f"🔍 Columns after cleaning: {list(df.columns)}")

    # ENHANCED COLUMN MAPPING - including advanced xG metrics
    mapping = {}
    used_new_names = set()
    
    column_priority = [
        ("Player", ["player", "name"]),
        ("Team", ["squad", "team"]),
        ("Role", ["pos", "position"]),
        ("Goals", ["gls", "goals"]),
        ("Assists", ["ast", "assists"]),
        ("xG", ["xg", "expected goals"]),
        ("xA", ["xag", "expected assists"]),
        ("npxG", ["npxg", "non-penalty xg"]),
        ("xAG", ["xag", "expected assisted goals"]),
        ("npxG_xA", ["npxg+xag", "npxg xag"]),
        ("xG_xA", ["xg+xag", "xg xag"]),
        ("Minutes", ["min", "minutes"]),
        ("Yellow_Cards", ["crdy", "yellow"]),
        ("Red_Cards", ["crdr", "red"]),
        ("Non_Penalty_Goals", ["g-pk", "non-penalty goals"]),
        ("Progressive_Carries", ["prgc", "progressive carries"]),
        ("Progressive_Passes", ["prgp", "progressive passes"]),
        ("Progressive_Receptions", ["prgr", "progressive receptions"]),
        ("Tackles", ["tkl", "tackles"]),
        ("Interceptions", ["int", "interceptions"]),
        ("Clearances", ["clr", "clearances"]),
        ("Blocks", ["blocks", "blocked"]),
    ]
    
    for new_name, keywords in column_priority:
        for orig_col in df.columns:
            if new_name not in used_new_names:
                col_lower = orig_col.lower()
                if any(keyword in col_lower for keyword in keywords):
                    mapping[orig_col] = new_name
                    used_new_names.add(new_name)
                    print(f"✅ Mapped '{orig_col}' -> '{new_name}'")
                    break

    # Apply renaming
    df = df.rename(columns=mapping)
    print(f"🔍 Columns after mapping: {list(df.columns)}")

    # Validate minimal existence
    if "Player" not in df.columns:
        raise ValueError(f"Player file must contain Player column. Found: {list(df.columns)}")
    if "Team" not in df.columns:
        raise ValueError(f"Player file must contain Team column. Found: {list(df.columns)}")

    print("✅ Basic validation passed")

    # Numeric conversion - enhanced with advanced xG metrics
    numeric_cols = ["Goals", "Assists", "xG", "xA", "Minutes", "Yellow_Cards", "Red_Cards",
                   "Non_Penalty_Goals", "Progressive_Carries", "Progressive_Passes", 
                   "Progressive_Receptions", "Tackles", "Interceptions", "Clearances", "Blocks",
                   "npxG", "xAG", "npxG_xA", "xG_xA"]  # Added advanced xG metrics
    
    for col in numeric_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col].astype(str), errors='coerce').fillna(0.0)
                print(f"✅ Converted {col} to numeric")
            except Exception as e:
                print(f"⚠️ Could not convert {col}: {e}")
                df[col] = 0.0

    # Set defaults for required columns
    required_cols = ["Goals", "Assists", "xG", "xA"]
    for col in required_cols:
        if col not in df.columns:
            df[col] = 0.0
            print(f"⚠️ Added default {col} column")

    # Clean up strings
    df["Player"] = df["Player"].astype(str).str.strip()
    df["Team"] = df["Team"].astype(str).str.strip()
    
    if "Role" in df.columns:
        df["Role"] = df["Role"].astype(str).str.strip()
    else:
        df["Role"] = "Unknown"

    # ENHANCED: Classify player roles
    print("🎯 Classifying player roles...")
    df["Role_Category"] = df["Role"].apply(classify_player_role)
    
    # Show role distribution
    role_distribution = df["Role_Category"].value_counts()
    print("📊 Role Distribution:")
    for role, count in role_distribution.items():
        print(f"   {role}: {count} players")

    # ENHANCED derived metrics with role-based analysis
    try:
        print("🔄 Calculating enhanced derived metrics with role-based analysis...")
        
        # Calculate role-based scores
        df["Role_Based_Score"] = df.apply(
            lambda row: calculate_role_based_score(row, row["Role_Category"]), 
            axis=1
        )
        
        # Attack metrics with advanced xG
        df["Attack_Index"] = (
            df["Goals"].fillna(0) * 4 + 
            df["Assists"].fillna(0) * 3 + 
            df["xG"].fillna(0) * 2 + 
            df["xA"].fillna(0) * 2
        )
        
        # Advanced xG metrics analysis
        # Penalty reliance: high xG but low npxG suggests penalty reliance
        if "npxG" in df.columns and "xG" in df.columns:
            df["Penalty_Reliance"] = (df["xG"] - df["npxG"]).fillna(0)
        else:
            df["Penalty_Reliance"] = 0.0
            
        # Creative threat: combination of xA and progressive actions
        creative_threat = df["xA"].fillna(0) * 2
        if "Progressive_Passes" in df.columns:
            creative_threat += df["Progressive_Passes"].fillna(0) * 0.1
        if "Progressive_Carries" in df.columns:
            creative_threat += df["Progressive_Carries"].fillna(0) * 0.1
        df["Creative_Threat"] = creative_threat
        
        # Overall threat: combination of scoring and creating
        if "npxG_xA" in df.columns:
            df["Overall_Threat"] = df["npxG_xA"].fillna(0) * 1.5
        elif "xG_xA" in df.columns:
            df["Overall_Threat"] = df["xG_xA"].fillna(0) * 1.5
        else:
            df["Overall_Threat"] = (df["xG"].fillna(0) + df["xA"].fillna(0)) * 1.5
        
        # Defense metrics (if available)
        defense_score = 0
        if "Tackles" in df.columns:
            defense_score += df["Tackles"].fillna(0) * 2
        if "Interceptions" in df.columns:
            defense_score += df["Interceptions"].fillna(0) * 2
        if "Clearances" in df.columns:
            defense_score += df["Clearances"].fillna(0) * 1.5
        if "Blocks" in df.columns:
            defense_score += df["Blocks"].fillna(0) * 1.5
        
        df["Defense_Index"] = defense_score
        
        # Discipline metrics (negative impact)
        df["Discipline_Index"] = -(df["Yellow_Cards"].fillna(0) * 0.5 + df["Red_Cards"].fillna(0) * 2)
        
        # Progression metrics (playing style)
        progression_score = 0
        if "Progressive_Carries" in df.columns:
            progression_score += df["Progressive_Carries"].fillna(0) * 0.1
        if "Progressive_Passes" in df.columns:
            progression_score += df["Progressive_Passes"].fillna(0) * 0.1
        if "Progressive_Receptions" in df.columns:
            progression_score += df["Progressive_Receptions"].fillna(0) * 0.1
            
        df["Progression_Index"] = progression_score
        
        # ENHANCED Overall score with role-based weighting
        df["Total_Score"] = (
            df["Role_Based_Score"] * 0.6 +  # Primary weight to role-based score
            df["Attack_Index"] * 0.15 + 
            df["Defense_Index"] * 0.1 + 
            df["Progression_Index"] * 0.1 +
            df["Creative_Threat"] * 0.03 +
            df["Overall_Threat"] * 0.01 +
            df["Discipline_Index"] * 0.01
        )
        
        # Calculate role-specific strengths
        df["Role_Specific_Strength"] = df.apply(
            lambda row: calculate_role_specific_strength(row, row["Role_Category"]), 
            axis=1
        )
        
        print("✅ Enhanced role-based metrics calculated")
        
    except Exception as e:
        print(f"❌ Error in enhanced derived metrics: {e}")
        df["Attack_Index"] = 1.0
        df["Defense_Index"] = 0.0
        df["Progression_Index"] = 0.0
        df["Discipline_Index"] = 0.0
        df["Creative_Threat"] = 0.0
        df["Overall_Threat"] = 0.0
        df["Penalty_Reliance"] = 0.0
        df["Role_Based_Score"] = 1.0
        df["Total_Score"] = 1.0
        df["Role_Specific_Strength"] = "Unknown"

    print(f"✅ Final data shape: {df.shape}")
    print(f"✅ Sample teams: {df['Team'].unique()[:5]}")
    print(f"✅ Total players loaded: {len(df)}")
    
    # Show top players by role
    print("\n🏆 Top Players by Role Category:")
    for role in df["Role_Category"].unique():
        top_players = df[df["Role_Category"] == role].nlargest(3, "Role_Based_Score")[["Player", "Team", "Role_Based_Score"]]
        print(f"\n{role}:")
        for _, player in top_players.iterrows():
            print(f"   {player['Player']} ({player['Team']}): {player['Role_Based_Score']:.1f}")
    
    return df