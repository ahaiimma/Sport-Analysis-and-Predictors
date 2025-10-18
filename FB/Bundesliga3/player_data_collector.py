import pandas as pd
import os
import re
import numpy as np

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

    # ENHANCED derived metrics with advanced xG analysis
    try:
        print("🔄 Calculating enhanced derived metrics with advanced xG analysis...")
        
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
        
        # ENHANCED Overall score with advanced metrics
        df["Total_Score"] = (
            df["Attack_Index"] * 0.4 + 
            df["Defense_Index"] * 0.25 + 
            df["Progression_Index"] * 0.15 + 
            df["Creative_Threat"] * 0.1 +
            df["Overall_Threat"] * 0.05 +
            df["Discipline_Index"] * 0.05
        )
        
        print("✅ Enhanced derived metrics with advanced xG analysis calculated")
    except Exception as e:
        print(f"❌ Error in enhanced derived metrics: {e}")
        df["Attack_Index"] = 1.0
        df["Defense_Index"] = 0.0
        df["Progression_Index"] = 0.0
        df["Discipline_Index"] = 0.0
        df["Creative_Threat"] = 0.0
        df["Overall_Threat"] = 0.0
        df["Penalty_Reliance"] = 0.0
        df["Total_Score"] = 1.0

    print(f"✅ Final data shape: {df.shape}")
    print(f"✅ Sample teams: {df['Team'].unique()[:5]}")
    print(f"✅ Total players loaded: {len(df)}")
    
    return df