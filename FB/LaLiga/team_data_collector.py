import pandas as pd
import os
import re
import numpy as np

def load_team_data(filepath=None):
    if filepath is None:
        filepath = "LaLiga Sentiment table.xlsx"

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

    # Ensure Position column exists
    if 'Position' not in result.columns:
        result['Position'] = range(1, len(result) + 1)
        print("⚠️ Added default Position column")

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

    # ENHANCED: Calculate sentiment score with relegation AND European qualification pressure
    try:
        print("🔄 Calculating ENHANCED sentiment scores with EUROPEAN QUALIFICATION analysis...")
        
        total_teams = len(result)
        games_in_season = 38  # EPL has 38 games
        
        # Calculate current performance metrics
        performance_score = (result['Win_Rate'] * 50) + (result['Goal_Diff_per_Match'] * 10) + (result['Points'] / result['Played'])
        
        # ENHANCED: European qualification and relegation pressure analysis
        result['Champions_League_Zone'] = result['Position'] <= 4  # Top 4 - Champions League
        result['Europa_League_Zone'] = (result['Position'] >= 5) & (result['Position'] <= 7)  # 5th-7th - Europa League
        result['European_Qualification'] = result['Position'] <= 7  # Any European qualification
        result['Mid_Table_Safety'] = (result['Position'] >= 8) & (result['Position'] <= (total_teams - 6))  # Safe mid-table
        result['Relegation_Threat'] = result['Position'] >= (total_teams - 5)  # Last 5 positions (danger zone)
        result['Relegation_Zone'] = result['Position'] >= (total_teams - 2)  # Last 3 positions (automatic relegation)
        
        # Calculate European qualification pressure factor
        # Teams chasing Champions League have highest positive pressure
        # Teams chasing Europa League have moderate positive pressure
        european_pressure = np.where(
            result['Champions_League_Zone'], 
            25,  # High positive pressure for Champions League
            np.where(
                result['Europa_League_Zone'],
                15,  # Moderate positive pressure for Europa League
                np.where(
                    (result['Position'] >= 8) & (result['Position'] <= 10),
                    5,   # Slight pressure for teams close to European spots
                    0    # No European pressure
                )
            )
        )
        
        # Calculate relegation pressure factor
        relegation_pressure = np.where(
            result['Relegation_Zone'], 
            -30,  # High negative pressure for relegation zone
            np.where(
                result['Relegation_Threat'],
                -15,  # Moderate negative pressure for relegation threat
                0     # No relegation pressure
            )
        )
        
        # Form factor (recent performance)
        games_played = result['Played'].clip(upper=games_in_season)
        season_progress = games_played / games_in_season
        
        # Teams with strong form late in season get European push boost
        form_pressure = np.where(
            (result['Win_Rate'] > 0.6) & (season_progress > 0.6) & result['European_Qualification'],
            20,  # Strong form late in season for European spots
            np.where(
                (result['Loss_Rate'] > 0.6) & (season_progress > 0.6) & result['Relegation_Threat'],
                -20,  # Poor form late in season for relegation teams
                0     # Neutral otherwise
            )
        )
        
        # Points from European spots calculation
        if 'Points' in result.columns:
            # Points needed for Champions League (4th place)
            cl_points = result[result['Position'] == 4]['Points'].iloc[0] if len(result[result['Position'] == 4]) > 0 else 60
            # Points needed for Europa League (7th place)
            el_points = result[result['Position'] == 7]['Points'].iloc[0] if len(result[result['Position'] == 7]) > 0 else 50
            
            result['Points_From_UCL'] = cl_points - result['Points']
            result['Points_From_UEFA'] = el_points - result['Points']
            
            european_points_pressure = np.where(
                (result['Position'] >= 5) & (result['Position'] <= 8) & (result['Points_From_UCL'] <= 6),
                15,  # Close to Champions League
                np.where(
                    (result['Position'] >= 8) & (result['Position'] <= 10) & (result['Points_From_UEFA'] <= 4),
                    10,  # Close to Europa League
                    0    # No points pressure
                )
            )
        else:
            european_points_pressure = 0
        
        # Points from safety calculation (for relegation-threatened teams)
        if 'Points' in result.columns:
            safe_points = result[result['Position'] == (total_teams - 3)]['Points'].iloc[0] if len(result[result['Position'] == (total_teams - 3)]) > 0 else 30
            result['Points_From_Safety'] = safe_points - result['Points']
            points_pressure = np.where(
                result['Relegation_Threat'] & (result['Points_From_Safety'] > 6),
                -25,  # Far from safety
                np.where(
                    result['Relegation_Threat'] & (result['Points_From_Safety'] <= 3),
                    -5,   # Close to safety
                    0     # No points pressure
                )
            )
        else:
            points_pressure = 0
        
        # Combine all pressure factors
        total_pressure = european_pressure + relegation_pressure + form_pressure + european_points_pressure + points_pressure
        
        # Calculate final sentiment score with pressure adjustments
        base_sentiment = performance_score
        adjusted_sentiment = base_sentiment + total_pressure
        
        # Normalize to 0-100 scale
        min_score = adjusted_sentiment.min()
        max_score = adjusted_sentiment.max()
        
        if max_score > min_score:
            result['Sentiment_Score'] = 100 * (adjusted_sentiment - min_score) / (max_score - min_score)
        else:
            result['Sentiment_Score'] = 50.0
        
        # Add pressure indicators for analysis
        result['European_Pressure'] = european_pressure
        result['Relegation_Pressure'] = relegation_pressure
        result['Total_Pressure'] = total_pressure
        result['Pressure_Level'] = np.where(
            total_pressure < -20, 'CRITICAL_RELEGATION',
            np.where(
                total_pressure < -10, 'HIGH_RELEGATION',
                np.where(
                    total_pressure > 20, 'HIGH_EUROPEAN',
                    np.where(
                        total_pressure > 10, 'MODERATE_EUROPEAN',
                        np.where(
                            total_pressure < 0, 'LOW_RELEGATION',
                            'NEUTRAL'
                        )
                    )
                )
            )
        )
        
        print("✅ ENHANCED sentiment scores with EUROPEAN qualification analysis calculated")
        print(f"🏆 Champions League Teams: {list(result[result['Champions_League_Zone']]['Team'])}")
        print(f"🌍 Europa League Teams: {list(result[result['Europa_League_Zone']]['Team'])}")
        print(f"📊 European Qualification Teams: {list(result[result['European_Qualification']]['Team'])}")
        print(f"🚨 Relegation Zone Teams: {list(result[result['Relegation_Zone']]['Team'])}")
        print(f"⚠️ Relegation Threat Teams: {list(result[result['Relegation_Threat']]['Team'])}")
        
    except Exception as e:
        print(f"❌ Error in enhanced sentiment calculation: {e}")
        # Fallback to basic sentiment calculation
        result['Sentiment_Score'] = (result['Win_Rate'] * 50) + (result['Goal_Diff_per_Match'] * 10) + (result['Points'] / result['Played'])
        min_score = result['Sentiment_Score'].min()
        max_score = result['Sentiment_Score'].max()
        if max_score > min_score:
            result['Sentiment_Score'] = 100 * (result['Sentiment_Score'] - min_score) / (max_score - min_score)
        else:
            result['Sentiment_Score'] = 50.0

    # Final cleaning
    result['Team'] = result['Team'].astype(str).str.strip()
    
    print(f"✅ Final team data: {len(result)} teams loaded")
    print(f"✅ Final columns: {list(result.columns)}")
    
    # Display pressure analysis summary
    print("\n🎯 EUROPEAN & RELEGATION PRESSURE ANALYSIS:")
    pressure_summary = result.groupby('Pressure_Level').agg({
        'Team': 'count',
        'Position': 'mean',
        'Sentiment_Score': 'mean'
    }).round(1)
    print(pressure_summary)
    
    # Display European qualification summary
    print("\n🏆 EUROPEAN QUALIFICATION STATUS:")
    european_teams = result[result['European_Qualification']].sort_values('Position')
    for _, team in european_teams.iterrows():
        if team['Champions_League_Zone']:
            print(f"  🥇 {team['Team']} (Position {team['Position']}) - CHAMPIONS LEAGUE")
        elif team['Europa_League_Zone']:
            print(f"  🥈 {team['Team']} (Position {team['Position']}) - EUROPA LEAGUE")
    
    return result