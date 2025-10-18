import pandas as pd
import os
import re
import numpy as np

def load_team_data(filepath=None):
    if filepath is None:
        filepath = "Bundesliga Sentiment table.xlsx"

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"The team data file was not found at: {filepath}")

    try:
        print("📋 Trying to read 'Sheet1'...")
        df = pd.read_excel(filepath, sheet_name='Sheet1')
        print("✅ Successfully read 'Sheet1'")
    except Exception as e1:
        print(f"⚠️ Could not read 'Sheet1': {e1}")
        try:
            df = pd.read_excel(filepath, sheet_name=0, header=0)
            print("✅ Successfully read with default header")
        except Exception as e3:
            raise ValueError(f"Could not read Excel file: {e3}")

    print(f"📊 Loaded data shape: {df.shape}")
    print(f"🔍 Original columns: {list(df.columns)}")

    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]
    print(f"🔍 Cleaned columns: {list(df.columns)}")

    # FIXED: Find the team column more robustly
    team_col = None
    for col in df.columns:
        col_lower = col.lower()
        if 'team' in col_lower or 'squad' in col_lower or 'club' in col_lower:
            team_col = col
            break
    
    # If no team column found, use first column
    if not team_col:
        team_col = df.columns[0]
        print(f"⚠️ No 'Team' column found, using first column: {team_col}")

    # Create result dataframe with Team column
    result = pd.DataFrame()
    result['Team'] = df[team_col].astype(str).str.strip()
    
    print(f"✅ Using '{team_col}' as Team column")

    # Try to find numeric columns and map them
    column_mappings = {
        'Position': ['position', 'pos'],
        'Played': ['played', 'pl', 'mp'], 
        'Won': ['won', 'w'],
        'Drawn': ['drawn', 'd'],
        'Lost': ['lost', 'l'],
        'Goals_For': ['goals for', 'gf', 'f'],
        'Goals_Against': ['goals against', 'ga', 'a'],
        'Goal_Difference': ['goal difference', 'gd'],
        'Points': ['points', 'pts']
    }

    for new_col, keywords in column_mappings.items():
        for old_col in df.columns:
            if any(keyword in old_col.lower() for keyword in keywords):
                try:
                    result[new_col] = pd.to_numeric(df[old_col], errors='coerce').fillna(0)
                    print(f"✅ Found {new_col}: {old_col}")
                    break
                except:
                    result[new_col] = 0
                    print(f"⚠️ Could not convert {old_col} to {new_col}")

    # Set defaults for essential columns
    essential_cols = ['Played', 'Won', 'Drawn', 'Lost', 'Goals_For', 'Goals_Against', 'Points']
    for col in essential_cols:
        if col not in result.columns:
            result[col] = 0
            print(f"⚠️ Added default {col} column")

    # Calculate derived metrics
    try:
        print("🔄 Calculating rates and averages...")
        
        # Handle division by zero
        result['Played'] = result['Played'].replace(0, 1)
        
        result['Win_Rate'] = (result['Won'] / result['Played']).fillna(0).round(3)
        result['Draw_Rate'] = (result['Drawn'] / result['Played']).fillna(0).round(3)
        result['Loss_Rate'] = (result['Lost'] / result['Played']).fillna(0).round(3)
        result['Avg_Goals_For'] = (result['Goals_For'] / result['Played']).fillna(0).round(2)
        result['Avg_Goals_Against'] = (result['Goals_Against'] / result['Played']).fillna(0).round(2)
        
        # Calculate Goal Difference if not present
        if 'Goal_Difference' not in result.columns:
            result['Goal_Difference'] = result['Goals_For'] - result['Goals_Against']
            
        result['Goal_Diff_per_Match'] = (result['Goal_Difference'] / result['Played']).fillna(0).round(2)
        
        print("✅ Rates and averages calculated")
    except Exception as e:
        print(f"❌ Error in rate calculations: {e}")

    # Calculate sentiment score
    try:
        print("🔄 Calculating sentiment scores...")
        result['Sentiment_Score'] = (result['Win_Rate'] * 50) + (result['Goal_Diff_per_Match'] * 10) + (result['Points'] / result['Played'])
        
        # Normalize
        min_score = result['Sentiment_Score'].min()
        max_score = result['Sentiment_Score'].max()
        
        if max_score > min_score:
            result['Sentiment_Score'] = 100 * (result['Sentiment_Score'] - min_score) / (max_score - min_score)
        else:
            result['Sentiment_Score'] = 50.0
            
        print("✅ Sentiment scores calculated")
    except Exception as e:
        print(f"❌ Error in sentiment calculation: {e}")
        result['Sentiment_Score'] = 50.0

    # Final cleaning
    result['Team'] = result['Team'].astype(str).str.strip()
    
    print(f"✅ Final team data: {len(result)} teams loaded")
    print(f"✅ Final columns: {list(result.columns)}")
    
    return result