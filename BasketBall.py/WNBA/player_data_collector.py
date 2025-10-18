import pandas as pd
import os
import re
import numpy as np

def load_basketball_player_data(filepath=None):
    """
    Load basketball player stats from Excel file.
    """
    if filepath is None:
        filepath = "basketball.xlsx"

    print(f"📂 Loading basketball player data from: {filepath}")
    
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Basketball player data file not found: {filepath}")

    try:
        print("📋 Trying to read 'Sheet1'...")
        df = pd.read_excel(filepath, sheet_name='Sheet1')
        print("✅ Successfully read 'Sheet1'")
    except Exception as e:
        print(f"❌ Error reading basketball data: {e}")
        raise

    print(f"📊 Loaded data shape: {df.shape}")
    print(f"🔍 Columns found: {list(df.columns)}")

    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]
    print(f"🔍 Cleaned columns: {list(df.columns)}")

    # Basketball-specific column mapping
    mapping = {}
    used_new_names = set()
    
    column_priority = [
        ("Player", ["player", "name"]),
        ("Team", ["team"]),
        ("Position", ["pos", "position"]),
        ("Games_Played", ["mp", "games", "gp"]),
        ("Points", ["pts", "points"]),
        ("Rebounds", ["trb", "rebounds"]),
        ("Assists", ["ast", "assists"]),
        ("Steals", ["stl", "steals"]),
        ("Blocks", ["blk", "blocks"]),
        ("Field_Goal_Pct", ["fg%", "field goal"]),
        ("Three_Point_Pct", ["3p%", "three point"]),
        ("Free_Throw_Pct", ["ft%", "free throw"]),
        ("Turnovers", ["tov", "turnovers"]),
        ("Usage_Rate", ["usg%", "usage"]),
        ("Offensive_Rating", ["ortg", "offensive rating"]),
        ("Defensive_Rating", ["drtg", "defensive rating"]),
        ("Win_Shares", ["ws", "win shares"]),
        ("Plus_Minus", ["+/-", "plus minus"])
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

    # Validate essential columns
    essential_cols = ["Player", "Team", "Points", "Rebounds", "Assists"]
    missing_essential = [col for col in essential_cols if col not in df.columns]
    if missing_essential:
        raise ValueError(f"Missing essential columns: {missing_essential}")

    # Convert numeric columns
    numeric_cols = ["Games_Played", "Points", "Rebounds", "Assists", "Steals", "Blocks", 
                   "Field_Goal_Pct", "Three_Point_Pct", "Free_Throw_Pct", "Turnovers",
                   "Usage_Rate", "Offensive_Rating", "Defensive_Rating", "Win_Shares"]
    
    for col in numeric_cols:
        if col in df.columns:
            try:
                df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0.0)
                print(f"✅ Converted {col} to numeric")
            except Exception as e:
                print(f"⚠️ Could not convert {col}: {e}")
                df[col] = 0.0

    # Set defaults for required columns
    for col in ["Points", "Rebounds", "Assists"]:
        if col not in df.columns:
            df[col] = 0.0
            print(f"⚠️ Added default {col} column")

    # Clean up strings
    df["Player"] = df["Player"].astype(str).str.strip()
    df["Team"] = df["Team"].astype(str).str.strip()
    
    if "Position" in df.columns:
        df["Position"] = df["Position"].astype(str).str.strip()
    else:
        df["Position"] = "Unknown"

    # Calculate basketball-specific derived metrics
    try:
        print("🔄 Calculating basketball derived metrics...")
        
        # Offensive metrics
        df["Scoring_Index"] = (
            df["Points"].fillna(0) * 1.5 +
            df.get("Field_Goal_Pct", 0).fillna(0) * 100 +
            df.get("Three_Point_Pct", 0).fillna(0) * 150 +
            df.get("Free_Throw_Pct", 0).fillna(0) * 50
        )
        
        # Playmaking metrics
        df["Playmaking_Index"] = (
            df["Assists"].fillna(0) * 2 +
            df.get("Usage_Rate", 0).fillna(0) * 1.5 -
            df.get("Turnovers", 0).fillna(0) * 1
        )
        
        # Defensive metrics
        defense_score = (
            df["Rebounds"].fillna(0) * 1.2 +
            df.get("Steals", 0).fillna(0) * 3 +
            df.get("Blocks", 0).fillna(0) * 3
        )
        if "Defensive_Rating" in df.columns:
            defense_score += (110 - df["Defensive_Rating"].fillna(110)) * 2  # Lower DRtg is better
        df["Defensive_Index"] = defense_score
        
        # Efficiency metrics
        if "Offensive_Rating" in df.columns and "Defensive_Rating" in df.columns:
            df["Net_Rating"] = df["Offensive_Rating"].fillna(100) - df["Defensive_Rating"].fillna(110)
        else:
            df["Net_Rating"] = 0
            
        # Overall player value
        df["Total_Score"] = (
            df["Scoring_Index"] * 0.4 +
            df["Playmaking_Index"] * 0.3 +
            df["Defensive_Index"] * 0.3 +
            df.get("Win_Shares", 0).fillna(0) * 10
        )
        
        print("✅ Basketball derived metrics calculated")
    except Exception as e:
        print(f"❌ Error in basketball derived metrics: {e}")
        # Set defaults
        df["Scoring_Index"] = 1.0
        df["Playmaking_Index"] = 0.0
        df["Defensive_Index"] = 0.0
        df["Net_Rating"] = 0.0
        df["Total_Score"] = 1.0

    print(f"✅ Final basketball data shape: {df.shape}")
    print(f"✅ Sample teams: {df['Team'].unique()[:5]}")
    print(f"✅ Total players loaded: {len(df)}")
    
    return df