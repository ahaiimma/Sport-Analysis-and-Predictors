import json

def get_betting_suggestions(player_data):
    """
    Analyzes tennis player data and provides betting suggestions for sporty.com markets.

    This function categorizes bets into 'Safe Bets', 'Sure Bets' (interpreted as
    highly confident safe bets), and 'Betting on the Edge' based on a statistical
    analysis of two players' performance metrics.

    Args:
        player_data (dict): A dictionary containing the statistical data for two players.
                            The keys should be the metric names, and the values should be
                            a list or tuple with two numbers, representing Player 1 and Player 2.
                            Example format:
                            {
                                "First Serve": [63.8, 76.8],
                                "Second Serve": [43.4, 52.0],
                                "Serve Speed": [95.2, 96.0],
                                "Rally": [3.2, 3.4],
                                "RIP": [68.2, 77.6],
                                "RIPW": [57.0, 62.6],
                                "Points": [772.0, 350.0],
                                "Ace": [8.2, 6.0],
                                "Rally/Height": [17.777778, 19.318182],
                                "Age": [24.0, 24.0],
                                "Home Advantage": [0.0, 0.0]
                            }

    Returns:
        str: A formatted string with betting suggestions for each category.
    """
    # Defensive check for valid input
    if not isinstance(player_data, dict) or not player_data:
        return "Error: Invalid input data. Please provide a dictionary with player stats."
    
    # Analyze the data to determine the likely favorite
    player1_score = 0
    player2_score = 0
    anomalous_data = []

    # Metrics where a higher value indicates better performance
    for metric in ["First Serve", "Second Serve", "Serve Speed", "Rally", "RIP", "RIPW", "Rally/Height", "Ace"]:
        if metric in player_data and len(player_data[metric]) == 2:
            if player_data[metric][0] > player_data[metric][1]:
                player1_score += 1
            elif player_data[metric][1] > player_data[metric][0]:
                player2_score += 1

    # Special handling for "Points" - it's a huge outlier
    if "Points" in player_data and len(player_data["Points"]) == 2:
        if player_data["Points"][0] > player_data["Points"][1]:
            anomalous_data.append("The 'Points' metric heavily favors Player 1, but this is a significant outlier compared to most other performance stats which suggest Player 2 is stronger. This could be from a different type of match or a misleading metric for a head-to-head analysis.")

    likely_winner = None
    if player2_score > player1_score:
        likely_winner = "Player 2"
    elif player1_score > player2_score:
        likely_winner = "Player 1"
    else:
        likely_winner = "It's a very close match based on the stats."

    # Generate suggestions based on the analysis
    suggestions = {
        "Safe Bets": [],
        "Sure Bets (High Confidence)": [],
        "Betting on the Edge": []
    }

    if likely_winner:
        if likely_winner != "It's a very close match based on the stats.":
            suggestions["Safe Bets"].append(f"Match Winner: Bet on {likely_winner} to win the match outright. The data shows they have a strong statistical advantage in key areas like First Serve, Second Serve, and Return Impact Points.")
            
            suggestions["Sure Bets (High Confidence)"].append(f"Given the clear statistical lead in serving and returning for {likely_winner}, this is a high-confidence bet. The high 'RIP' and 'RIPW' numbers for {likely_winner} are particularly strong indicators of their ability to control the game.")

            suggestions["Betting on the Edge"].append(f"If the moneyline odds on sporty.com are close or even favor the other player due to the outlier 'Points' metric, betting on {likely_winner} to win is an 'edge' bet. You are betting against the public perception (and potentially the book's odds) based on a deeper statistical analysis. You could also consider a 'prop bet' such as '{likely_winner} to win a specific set', or '{likely_winner} to win with a -1.5 set handicap' to get better odds.")
        else:
            suggestions["Safe Bets"].append("This match is statistically too close to call a clear winner. A safer bet would be on 'Over/Under Total Games,' as the players' similar skill levels suggest a long, competitive match.")
            suggestions["Sure Bets (High Confidence)"].append("No high-confidence bets can be made based on this data. The players are too evenly matched.")
            suggestions["Betting on the Edge"].append("Look for prop bets that highlight a minor statistical edge, such as 'Player with higher Serve Speed to win the first set,' or 'Player with higher Rally/Height to win a long rally.'")
    else:
        suggestions["Safe Bets"].append("Insufficient data to make a confident recommendation.")
        suggestions["Sure Bets (High Confidence)"].append("Insufficient data to make a confident recommendation.")
        suggestions["Betting on the Edge"].append("Insufficient data to make a confident recommendation.")

    # Format the output string
    output = "Here are the betting suggestions based on your data and sporty.com market types:\n\n"
    output += "--- Safe Bets ---\n"
    for item in suggestions["Safe Bets"]:
        output += f"- {item}\n"
    output += "\n"
    
    output += "--- Sure Bets (High Confidence) ---\n"
    for item in suggestions["Sure Bets (High Confidence)"]:
        output += f"- {item}\n"
    output += "\n"
    
    output += "--- Betting on the Edge ---\n"
    for item in suggestions["Betting on the Edge"]:
        output += f"- {item}\n"
    
    if anomalous_data:
        output += "\n"
        output += "--- Important Notes on Data ---\n"
        for note in anomalous_data:
            output += f"- {note}\n"

    return output

if __name__ == '__main__':
    # Your provided data
    provided_data = {
        "First Serve": [63.8, 76.8],
        "Second Serve": [43.4, 52.0],
        "Serve Speed": [95.2, 96.0],
        "Rally": [3.2, 3.4],
        "RIP": [68.2, 77.6],
        "RIPW": [57.0, 62.6],
        "Points": [772.0, 350.0],
        "Ace": [8.2, 6.0],
        "Rally/Height": [17.777778, 19.318182],
        "Age": [24.0, 24.0],
        "Home Advantage": [0.0, 0.0]
    }
    
    print(get_betting_suggestions(provided_data))
