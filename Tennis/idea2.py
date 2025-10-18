import pandas as pd
import matplotlib.pyplot as plt
import json

class Player:
    """
    A class to represent a tennis player and collect their key stats.
    The user is prompted for various data points which are then used to
    calculate additional performance metrics.
    """
    def __init__(self):
        print("--- Player Creation ---")
        self.name = input("Enter the player's name: ")
        self.home_location = input("Enter the player's home location (city/country): ")
        self.initial_number = input("Enter the player's initial number: ")
        self.final_number = input("Enter the player's final number: ")
        self.age = self.get_age()
        self.hand = self.select_player_hand()
        self.experience_surface = self.select_surface()
        
        # Call methods to collect data
        self.first_serve = self._get_avg_serve("firstServe")
        self.second_serve = self._get_avg_serve("secondServe")
        self.serve_speed = self._get_avg_serve("serveSpeed")
        
        self.height, self.weight = self.input_height_weight()
        
        # Stats based on average input
        self.break_points = self._avg_input("BPServed")
        self.rally_stats = self._avg_input("Rallied")
        self.rip = self._avg_input("RIP")
        self.ripw = self._avg_input("RIPW")
        self.ace = self._avg_input("Ace", float_values=True)
        
        # Point difference and calculated stats
        self.points = self.calculate_points()
        self.rally_per_height = self.calculate_rally_per_height()
    
    def _get_avg_serve(self, serve_type):
        """Helper method to get and average serve values."""
        while True:
            user_input = input(f"Enter the {serve_type} between 3 and 5 integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    serve_values = [int(item) for item in items]
                    avg = sum(serve_values) / len(serve_values)
                    print(f"The average {serve_type} value is: {avg}")
                    return avg
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")

    def _avg_input(self, label, float_values=False):
        """Helper method to get and average various stat values."""
        while True:
            user_input = input(f"Enter between 3 and 5 {label} values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    values = [float(item) if float_values else int(item) for item in items]
                    avg = sum(values) / len(values)
                    print(f"The average {label} value is: {avg}")
                    return avg
                except ValueError:
                    print("Invalid input. Please enter only numeric values.")
            else:
                print("Please enter between 3 and 5 values.")
    
    def get_age(self):
        """Prompts for and validates the player's age."""
        while True:
            try:
                age = int(input("Enter the player's age: "))
                if age >= 0:
                    return age
                else:
                    print("Please enter a valid non-negative age.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def select_player_hand(self):
        """Prompts for and validates the player's dominant hand."""
        while True:
            hand = input("Enter the player's dominant hand ('L' for Left, 'R' for Right): ").strip().upper()
            if hand in ['L', 'R']:
                return 'Left' if hand == 'L' else 'Right'
            else:
                print("Invalid input. Please enter 'L' or 'R'.")

    def input_height_weight(self):
        """Prompts for and validates height and weight, converting to standard units."""
        while True:
            height_input = input("Enter the height (e.g., 180 or 1.80): ").strip()
            unit = input("Is this in centimeters or meters? (Enter 'cm' or 'm'): ").strip().lower()
            try:
                height_value = float(height_input)
                if unit == 'cm':
                    height_in_meters = height_value / 100
                    break
                elif unit == 'm':
                    height_in_meters = height_value
                    break
                else:
                    print("Please enter 'cm' or 'm' for the unit.")
            except ValueError:
                print("Invalid input. Please enter a numeric value for height (integer or float).")
        
        while True:
            weight_input = input("Enter the weight in kilograms: ").strip()
            try:
                weight_kg = float(weight_input)
                if weight_kg >= 0:
                    break
                else:
                    print("Please enter a non-negative value for weight.")
            except ValueError:
                print("Invalid input. Please enter a numeric value for weight (integer or float).")
        
        print(f"Height: {height_in_meters:.2f} meters, Weight: {weight_kg:.1f} kg")
        return height_in_meters, weight_kg

    def calculate_points(self):
        """Calculates the point difference."""
        initial = float(self.initial_number)
        final = float(self.final_number)
        difference = final - initial
        print(f"Points difference: {difference}")
        return difference

    def calculate_rally_per_height(self):
        """Calculates a rally-to-height ratio."""
        divisor = self.height * 0.1
        if divisor == 0:
            return 0
        return self.rally_stats / divisor

    def select_surface(self):
        """Prompts for and validates the player's surface experience."""
        print("Are Most tournaments and awards are on Grass, Clay, Carpet, or Hard courts.?")
        print("If you have experience on any of these surfaces, please select one to indicate your experience.")
        while True:
            surface = input(f"Player {self.name} surface experience (Grass/Clay/Carpet/Hard): ").strip().lower()
            if surface in ['grass', 'clay', 'carpet', 'hard']:
                print("Great! Your experience on this surface will be noted.")
                return surface.capitalize()
            print("Invalid input. Please enter one of: Grass, Clay, Carpet, or Hard.")

    def display_stats(self):
        """Prints all collected and calculated player stats."""
        print(f"\n--- Stats for {self.name} ---")
        print(f"Age: {self.age}")
        print(f"Hand: {self.hand}")
        print(f"Surface: {self.experience_surface}")
        print(f"Height: {self.height:.2f} m, Weight: {self.weight:.1f} kg")
        print(f"First Serve Avg: {self.first_serve:.2f}")
        print(f"Second Serve Avg: {self.second_serve:.2f}")
        print(f"Serve Speed Avg: {self.serve_speed:.2f}")
        print(f"Break Points Avg: {self.break_points:.2f}")
        print(f"Rally Avg: {self.rally_stats:.2f}")
        print(f"RIP: {self.rip:.2f}, RIPW: {self.ripw:.2f}")
        print(f"Ace Avg: {self.ace:.2f}")
        print(f"Points Difference: {self.points:.2f}")
        print(f"Rally to Height Ratio: {self.rally_per_height:.2f}\n")


class PlayerEvaluator:
    """
    A class to evaluate two players against each other based on their stats
    and match conditions.
    """
    def __init__(self, p1, p2, match_location):
        self.p1 = p1
        self.p2 = p2
        self.match_location = match_location
        self.p1_points = 0
        self.p2_points = 0
        self.p1_home_advantage_bonus = 0
        self.p2_home_advantage_bonus = 0

    def _apply_home_advantage(self, home_player):
        """
        Applies a performance boost for the home player based on specific stat multipliers.
        This provides a more significant advantage than a simple point bonus.
        """
        boost_factors = {
            "first_serve": 1.05,
            "second_serve": 1.03,
            "serve_speed": 1.05,
            "rally_stats": 1.04,
            "rip": 1.02,
            "ripw": 1.03,
            "ace": 1.05,
        }

        print(f"--- Applying home advantage boost to {home_player.name} ---")
        for stat, boost in boost_factors.items():
            original_value = getattr(home_player, stat)
            boosted_value = original_value * boost
            setattr(home_player, stat, boosted_value)
            print(f"- {stat.replace('_', ' ').capitalize()}: {original_value:.2f} -> {boosted_value:.2f}")
        print("---------------------------------------------------\n")


    def experience_advantage(self):
        """Assigns points based on surface experience."""
        match_surface = self.match_location.lower()
        p1_exp = getattr(self.p1, 'experience_surface', '').lower()
        p2_exp = getattr(self.p2, 'experience_surface', '').lower()

        p1_has_exp = p1_exp == match_surface
        p2_has_exp = p2_exp == match_surface

        if p1_has_exp and not p2_has_exp:
            print(f"{self.p1.name} has a surface advantage on {self.match_location}.")
            self.p1_points += 2
        elif p2_has_exp and not p1_has_exp:
            print(f"{self.p2.name} has a surface advantage on {self.match_location}.")
            self.p2_points += 2
        else:
            self._tie_breaker()

    def _tie_breaker(self):
        """Evaluates additional metrics for a tie-break."""
        p1_stats = [self.p1.first_serve, self.p1.second_serve, self.p1.serve_speed, self.p1.rally_stats, self.p1.rip, self.p1.ripw, self.p1.points, self.p1.ace, self.p1.rally_per_height, self.p1.age]
        p2_stats = [self.p2.first_serve, self.p2.second_serve, self.p2.serve_speed, self.p2.rally_stats, self.p2.rip, self.p2.ripw, self.p2.points, self.p2.ace, self.p2.rally_per_height, self.p2.age]
        
        p1_wins = sum(1 for p1_s, p2_s in zip(p1_stats, p2_stats) if p1_s > p2_s)
        p2_wins = sum(1 for p1_s, p2_s in zip(p1_stats, p2_stats) if p2_s > p1_s)

        if p1_wins > p2_wins:
            self.p1_points += 1
            print(f"{self.p1.name} wins the tie-breaker by a margin of {p1_wins} to {p2_wins}.")
        elif p2_wins > p1_wins:
            self.p2_points += 1
            print(f"{self.p2.name} wins the tie-breaker by a margin of {p2_wins} to {p1_wins}.")
        else:
            print("The tie-breaker also results in a tie.")

    def _create_data_dict(self):
        """Creates and returns the data dictionary from player objects."""
        return {
            "First Serve": [self.p1.first_serve, self.p2.first_serve],
            "Second Serve": [self.p1.second_serve, self.p2.second_serve],
            "Serve Speed": [self.p1.serve_speed, self.p2.serve_speed],
            "Rally": [self.p1.rally_stats, self.p2.rally_stats],
            "RIP": [self.p1.rip, self.p2.rip],
            "RIPW": [self.p1.ripw, self.p2.ripw],
            "Points": [self.p1.points, self.p2.points],
            "Ace": [self.p1.ace, self.p2.ace],
            "Rally/Height": [self.p1.rally_per_height, self.p2.rally_per_height],
            "Age": [self.p1.age, self.p2.age],
        }

    def compare_metrics(self):
        """Displays a detailed comparison table and plot using pandas."""
        metrics = self._create_data_dict()
        df = pd.DataFrame(metrics, index=[self.p1.name, self.p2.name]).T

        print("\n📊 Detailed Comparison Table:")
        print(df)
        
        # Determine the winner based on total points
        print("\n🏆 Final Result:")
        if self.p1_points > self.p2_points:
            print(f"After all considerations, {self.p1.name} wins with {self.p1_points} points vs {self.p2_points} points!")
        elif self.p2_points > self.p1_points:
            print(f"After all considerations, {self.p2.name} wins with {self.p2_points} points vs {self.p1_points} points!")
        else:
            print("It's a tie! Both players are equally matched.")

        self.plot_results(df)
        
    def evaluate_match(self):
        """Main method to run the evaluation process."""
        home_player_name = input(f"\nWhich player has the home advantage? ({self.p1.name} or {self.p2.name}): ").strip()
        if home_player_name.lower() == self.p1.name.lower():
            self._apply_home_advantage(self.p1)
        elif home_player_name.lower() == self.p2.name.lower():
            self._apply_home_advantage(self.p2)
        else:
            print("No valid home player selected. No home advantage will be applied.")

        self.experience_advantage()
        self.compare_metrics()
        
        # Get the data dictionary
        provided_data = self._create_data_dict()
        
        # Pass the data to the betting suggestions function
        betting_suggestions = get_betting_suggestions(provided_data)
        print("\n--- Betting Suggestions ---")
        print(betting_suggestions)

    def plot_results(self, df):
        """Generates and displays a bar chart of the player stats."""
        ax = df.plot(kind="bar", figsize=(10, 6))
        plt.title(f"Comparison Analysis: {self.p1.name} vs {self.p2.name} on {self.match_location}")
        plt.ylabel("Values")
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Player")

        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f", label_type="edge", fontsize=8)

        plt.tight_layout()
        plt.show()


def get_betting_suggestions(player_data):
    """
    Analyzes player data and generates betting suggestions based on a more robust statistical advantage,
    covering various markets like those on sporty.com.
    """
    if not isinstance(player_data, dict) or not player_data:
        return "Error: Invalid input data. Please provide a dictionary with player stats."
    
    player1_name = "Player 1"
    player2_name = "Player 2"

    suggestions = {
        "Match Winner (1x2)": [],
        "Set Winner (1st & 2nd)": [],
        "Set Handicap (-1.5 / +1.5)": [],
        "Game Handicap": [],
        "Correct Score": [],
        "Total Games (Over/Under)": [],
        "Player Props (Total Aces)": []
    }

    # --- Match Winner (1x2) ---
    # Determine the statistical favorite based on a composite score
    p1_stats = [player_data["First Serve"][0], player_data["Serve Speed"][0], player_data["RIPW"][0]]
    p2_stats = [player_data["First Serve"][1], player_data["Serve Speed"][1], player_data["RIPW"][1]]
    p1_score = sum(1 for p1_s, p2_s in zip(p1_stats, p2_stats) if p1_s > p2_s)
    p2_score = sum(1 for p1_s, p2_s in zip(p1_stats, p2_stats) if p2_s > p1_s)

    if p1_score >= 2 and p1_score > p2_score:
        suggestions["Match Winner (1x2)"].append(f"Based on superior serving and return stats, bet on **{player1_name}** to win the match outright.")
    elif p2_score >= 2 and p2_score > p1_score:
        suggestions["Match Winner (1x2)"].append(f"Based on superior serving and return stats, bet on **{player2_name}** to win the match outright.")
    else:
        suggestions["Match Winner (1x2)"].append("The players are statistically very close. This is a risky bet. It's advisable to look for a different market.")

    # --- Set Winner (1st & 2nd) ---
    # Base first set winner on serve strength, as the first set is often dominated by serves.
    if player_data["Serve Speed"][0] > player_data["Serve Speed"][1] * 1.05 and player_data["First Serve"][0] > player_data["First Serve"][1]:
        suggestions["Set Winner (1st & 2nd)"].append(f"Bet on **{player1_name}** to win the 1st set. Their superior serve speed and first serve percentage give them an early advantage.")
    elif player_data["Serve Speed"][1] > player_data["Serve Speed"][0] * 1.05 and player_data["First Serve"][1] > player_data["First Serve"][0]:
        suggestions["Set Winner (1st & 2nd)"].append(f"Bet on **{player2_name}** to win the 1st set. Their superior serve speed and first serve percentage give them an early advantage.")
    else:
        suggestions["Set Winner (1st & 2nd)"].append("The players are evenly matched on serve. It is difficult to predict the winner of the first set based on this data.")

    # --- Set Handicap (-1.5 / +1.5) ---
    # Suggest a -1.5 handicap only if there's a strong, clear statistical favorite.
    # The logic here is more robust and checks for multiple conditions.
    p1_serve_advantage = player_data["First Serve"][0] > player_data["First Serve"][1] * 1.1 or player_data["Serve Speed"][0] > player_data["Serve Speed"][1] * 1.05
    p1_return_advantage = player_data["RIPW"][0] > player_data["RIPW"][1]
    p2_serve_advantage = player_data["First Serve"][1] > player_data["First Serve"][0] * 1.1 or player_data["Serve Speed"][1] > player_data["Serve Speed"][0] * 1.05
    p2_return_advantage = player_data["RIPW"][1] > player_data["RIPW"][0]
    
    # Condition for betting on Player 1 with -1.5 handicap
    if p1_serve_advantage and p1_return_advantage and player_data["Rally"][0] > player_data["Rally"][1]:
        suggestions["Set Handicap (-1.5 / +1.5)"].append(f"Bet on **{player1_name} with a -1.5 set handicap**. Their significant advantage in both serving and returning suggests a high probability of a 2-0 (straight sets) victory.")
    # Condition for betting on Player 2 with -1.5 handicap
    elif p2_serve_advantage and p2_return_advantage and player_data["Rally"][1] > player_data["Rally"][0]:
        suggestions["Set Handicap (-1.5 / +1.5)"].append(f"Bet on **{player2_name} with a -1.5 set handicap**. Their significant advantage in both serving and returning suggests a high probability of a 2-0 (straight sets) victory.")
    # Condition for betting on the underdog with +1.5 handicap
    else:
        underdog = player2_name if p1_score > p2_score else player1_name
        suggestions["Set Handicap (-1.5 / +1.5)"].append(f"The match is likely to be competitive. Bet on **{underdog} with a +1.5 set handicap**. This means they are likely to win at least one set, as neither player has a clear enough advantage for a 2-0 win.")

    # --- Game Handicap ---
    # Base game handicap on the ability to break serve and win rallies.
    p1_rally_advantage = player_data["Rally"][0] > player_data["Rally"][1]
    p1_ripw_advantage = player_data["RIPW"][0] > player_data["RIPW"][1]
    
    if p1_rally_advantage and p1_ripw_advantage and player_data["Serve Speed"][0] > player_data["Serve Speed"][1]:
        suggestions["Game Handicap"].append(f"Bet on **{player1_name} with a -3.5 game handicap**. Their superior rally and return game suggests they will win by a comfortable margin.")
    elif not p1_rally_advantage and not p1_ripw_advantage and player_data["Serve Speed"][1] > player_data["Serve Speed"][0]:
        suggestions["Game Handicap"].append(f"Bet on **{player2_name} with a -3.5 game handicap**. Their superior rally and return game suggests they will win by a comfortable margin.")
    else:
        underdog = player2_name if p1_score > p2_score else player1_name
        suggestions["Game Handicap"].append(f"The game stats are too close. Consider betting on the underdog, **{underdog} with a +2.5 game handicap**, as they are likely to keep the game count tight.")

    # --- Correct Score ---
    if p1_score >= 3:
        suggestions["Correct Score"].append(f"For a high-risk, high-reward bet, consider **{player1_name} to win 2-0**.")
    elif p2_score >= 3:
        suggestions["Correct Score"].append(f"For a high-risk, high-reward bet, consider **{player2_name} to win 2-0**.")
    else:
        suggestions["Correct Score"].append("The most likely correct score is **2-1** in favor of the statistical favorite. A 2-0 outcome is less probable.")

    # --- Total Games (Over/Under) ---
    # If rally stats are close, it suggests a long match
    rally_diff = abs(player_data["Rally"][0] - player_data["Rally"][1])
    if rally_diff < 5:
        suggestions["Total Games (Over/Under)"].append("Bet on **Total Games: Over**. The players' similar rally capabilities suggest a long, competitive match with many games.")
    else:
        suggestions["Total Games (Over/Under)"].append("Bet on **Total Games: Under**. The difference in rally stats suggests a shorter match with a decisive winner.")

    # --- Player Props (Total Aces) ---
    p1_aces, p2_aces = player_data.get("Ace", [0, 0])
    if p1_aces > p2_aces * 1.5:
        suggestions["Player Props (Total Aces)"].append(f"Bet on **{player1_name} to have more aces**. Their average ace count is significantly higher.")
    elif p2_aces > p1_aces * 1.5:
        suggestions["Player Props (Total Aces)"].append(f"Bet on **{player2_name} to have more aces**. Their average ace count is significantly higher.")
    else:
        suggestions["Player Props (Total Aces)"].append("The average ace counts are too similar to confidently bet on one player over the other.")

    # Format the final output string
    output = "Here are the betting suggestions based on your data and sporty.com market types:\n\n"
    for market, tips in suggestions.items():
        output += f"--- {market} ---\n"
        for tip in tips:
            output += f"- {tip}\n"
        output += "\n"

    return output


def create_players():
    """Creates and returns two Player objects."""
    print("\n--- Creating Player 1 ---")
    player1 = Player()

    print("\n--- Creating Player 2 ---")
    player2 = Player()

    return player1, player2

if __name__ == "__main__":
    p1, p2 = create_players()
    p1.display_stats()
    p2.display_stats()
    match_location = input("\nEnter the match location (city/country/surface): ")
    evaluator = PlayerEvaluator(p1, p2, match_location)
    evaluator.evaluate_match()
