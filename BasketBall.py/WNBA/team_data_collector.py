import pandas as pd
import os
import numpy as np

def load_basketball_team_data(filepath=None):
    """
    Load basketball team standings and sentiment data.
    """
    if filepath is None:
        filepath = "sentiment.xlsx"

    if not os.path.exists(filepath):
        raise FileNotFoundError(f"❌ Basketball team data file not found: {filepath}")

    try:
        print("📋 Loading basketball team data...")
        df = pd.read_excel(filepath, sheet_name='Sheet1')
        print("✅ Successfully read team data")
    except Exception as e:
        print(f"❌ Error reading basketball team data: {e}")
        raise

    print(f"📊 Loaded data shape: {df.shape}")
    print(f"🔍 Columns found: {list(df.columns)}")

    # Clean column names
    df.columns = [str(col).strip() for col in df.columns]
    print(f"🔍 Cleaned columns: {list(df.columns)}")

    # Find team column (usually first column)
    team_col = None
    for col in df.columns:
        if 'team' in col.lower() or df[col].dtype == 'object':
            team_col = col
            break
    
    if not team_col:
        team_col = df.columns[0]
        print(f"⚠️ Using first column as Team: {team_col}")

    # Create result dataframe
    result = pd.DataFrame()
    result['Team'] = df[team_col].astype(str).str.strip()
    
    # Remove empty rows and conference headers
    result = result[~result['Team'].str.contains('Conference', na=False)]
    result = result[result['Team'] != '']
    result = result[result['Team'] != 'TEAM']

    print(f"✅ Using '{team_col}' as Team column")

    # Map common basketball statistics
    column_mappings = {
        'Wins': ['w', 'win'],
        'Losses': ['l', 'loss'], 
        'Win_Pct': ['pct', 'win%'],
        'Games_Back': ['gb'],
        'Conference_Record': ['conf'],
        'Home_Record': ['home'],
        'Road_Record': ['road'],
        'Streak': ['streak'],
        'Last_10': ['l-10']
    }

    for new_col, keywords in column_mappings.items():
        for old_col in df.columns:
            if any(keyword in old_col.lower() for keyword in keywords):
                try:
                    # Handle record formats like "15-6"
                    if 'record' in new_col.lower() or 'last' in new_col.lower():
                        # Store as string for records
                        result[new_col] = df[old_col].astype(str)
                    else:
                        result[new_col] = pd.to_numeric(df[old_col], errors='coerce').fillna(0)
                    print(f"✅ Found {new_col}: {old_col}")
                    break
                except:
                    result[new_col] = 0 if 'record' not in new_col.lower() else "0-0"
                    print(f"⚠️ Could not convert {old_col} to {new_col}")

    # Set defaults for essential columns
    essential_cols = ['Wins', 'Losses', 'Win_Pct']
    for col in essential_cols:
        if col not in result.columns:
            result[col] = 0
            print(f"⚠️ Added default {col} column")

    # Calculate advanced metrics
    try:
        print("🔄 Calculating basketball team metrics...")
        
        # Ensure numeric types
        result['Wins'] = pd.to_numeric(result['Wins'], errors='coerce').fillna(0)
        result['Losses'] = pd.to_numeric(result['Losses'], errors='coerce').fillna(0)
        result['Win_Pct'] = pd.to_numeric(result['Win_Pct'], errors='coerce').fillna(0)
        
        # Calculate additional metrics if not provided
        if 'Win_Pct' not in result.columns or result['Win_Pct'].isna().all():
            total_games = result['Wins'] + result['Losses']
            result['Win_Pct'] = result['Wins'] / total_games.replace(0, 1)
        
        # Strength metrics
        result['Win_Strength'] = result['Wins'] * (1 + result['Win_Pct'])
        
        # Parse streak information
        def parse_streak(streak):
            if pd.isna(streak):
                return 0
            streak_str = str(streak).upper()
            if 'W' in streak_str:
                return int(streak_str.replace('W', '').strip())
            elif 'L' in streak_str:
                return -int(streak_str.replace('L', '').strip())
            return 0
        
        if 'Streak' in result.columns:
            result['Current_Streak'] = result['Streak'].apply(parse_streak)
        else:
            result['Current_Streak'] = 0
            
        # Parse last 10 games
        def parse_last_10(record):
            if pd.isna(record):
                return 0.5
            try:
                if '-' in str(record):
                    wins, losses = map(int, str(record).split('-'))
                    return wins / (wins + losses) if (wins + losses) > 0 else 0.5
            except:
                pass
            return 0.5
        
        if 'Last_10' in result.columns:
            result['Last_10_Pct'] = result['Last_10'].apply(parse_last_10)
        else:
            result['Last_10_Pct'] = 0.5

        # Calculate comprehensive sentiment score
        result['Sentiment_Score'] = (
            result['Win_Pct'] * 50 +                    # Overall performance
            result.get('Last_10_Pct', 0.5) * 30 +       # Recent form
            (result.get('Current_Streak', 0) * 2) +     # Momentum
            10                                          # Base score
        )
        
        # Normalize to 0-100 scale
        min_score = result['Sentiment_Score'].min()
        max_score = result['Sentiment_Score'].max()
        
        if max_score > min_score:
            result['Sentiment_Score'] = 100 * (result['Sentiment_Score'] - min_score) / (max_score - min_score)
        else:
            result['Sentiment_Score'] = 50.0
            
        print("✅ Basketball team metrics calculated")
    except Exception as e:
        print(f"❌ Error in basketball team metrics: {e}")
        result['Sentiment_Score'] = 50.0

    # Final cleaning
    result['Team'] = result['Team'].astype(str).str.strip()
    
    print(f"✅ Final basketball team data: {len(result)} teams loaded")
    print(f"✅ Final columns: {list(result.columns)}")
    
    return result