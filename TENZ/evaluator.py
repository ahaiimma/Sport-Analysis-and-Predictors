import pandas as pd
import matplotlib.pyplot as plt
from player import Player


class PlayerEvaluator:
    """A class to evaluate two players against each other based on their stats and match conditions."""
    
    def __init__(self, p1, p2, match_location):
        self.p1 = p1
        self.p2 = p2
        self.match_location = match_location
        self.p1_points = 0
        self.p2_points = 0
        self.p1_home_advantage_bonus = 0
        self.p2_home_advantage_bonus = 0
    
    def apply_home_advantage(self, home_player):
        """
        Apply a significant performance boost for the home player based on specific stat multipliers.
        This follows the pattern you requested with specific boosts for different stats.
        """
        boost_factors = {
            "first_serve": 1.10,        # +10% first serve
            "second_serve": 1.08,       # +8% second serve
            "serve_speed": 1.10,        # +10% serve speed
            "rally_stats": 1.08,        # +8% rally stats
            "rip": 1.07,                # +7% rip
            "ripw": 1.07,               # +7% ripw
            "ace": 1.10,                # +10% ace
            "break_points": 1.08,       # +8% break points
            "points": 1.05,             # +5% points
            "rally_per_height": 1.05    # +5% rally per height
        }
        
        print(f"--- Applying HOME ADVANTAGE boost to {home_player.name} ---")
        
        # Apply boosts to all relevant stats
        for stat, boost in boost_factors.items():
            if hasattr(home_player, stat):
                original_value = getattr(home_player, stat)
                boosted_value = original_value * boost
                setattr(home_player, stat, boosted_value)
                print(f"- {stat.replace('_', ' ').capitalize()}: {original_value:.2f} -> {boosted_value:.2f} (+{int((boost-1)*100)}%)")
        
        print("---------------------------------------------------\n")
        
        # Add a significant point bonus for home advantage
        home_advantage_points = 25
        if home_player == self.p1:
            self.p1_points += home_advantage_points
            self.p1_home_advantage_bonus = home_advantage_points
        else:
            self.p2_points += home_advantage_points
            self.p2_home_advantage_bonus = home_advantage_points
        
        print(f"🏠 {home_player.name} gains {home_advantage_points} additional points for home advantage!")
    
    def experience_advantage(self):
        """Assigns points based on surface experience."""
        match_surface = self.match_location.lower()
        p1_exp = getattr(self.p1, 'experience_surface', '').lower()
        p2_exp = getattr(self.p2, 'experience_surface', '').lower()
        
        p1_has_exp = p1_exp == match_surface
        p2_has_exp = p2_exp == match_surface
        
        if p1_has_exp and not p2_has_exp:
            print(f"{self.p1.name} has a surface advantage on {self.match_location}.")
            self.p1_points += 5  # Reduced from previous value since home advantage is now more significant
        elif p2_has_exp and not p1_has_exp:
            print(f"{self.p2.name} has a surface advantage on {self.match_location}.")
            self.p2_points += 5  # Reduced from previous value since home advantage is now more significant
        else:
            self._tie_breaker()
    
    def _tie_breaker(self):
        """Evaluates additional metrics for a tie-break."""
        p1_stats = [
            self.p1.first_serve, self.p1.second_serve, self.p1.serve_speed,
            self.p1.rally_stats, self.p1.rip, self.p1.ripw, self.p1.points,
            self.p1.ace, self.p1.rally_per_height, self.p1.age
        ]
        
        p2_stats = [
            self.p2.first_serve, self.p2.second_serve, self.p2.serve_speed,
            self.p2.rally_stats, self.p2.rip, self.p2.ripw, self.p2.points,
            self.p2.ace, self.p2.rally_per_height, self.p2.age
        ]
        
        p1_wins = sum(1 for p1_s, p2_s in zip(p1_stats, p2_stats) if p1_s > p2_s)
        p2_wins = sum(1 for p1_s, p2_s in zip(p1_stats, p2_stats) if p2_s > p1_s)
        
        if p1_wins > p2_wins:
            self.p1_points += 3
            print(f"{self.p1.name} wins the tie-breaker by a margin of {p1_wins} to {p2_wins}.")
        elif p2_wins > p1_wins:
            self.p2_points += 3
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
            "Home Advantage": [self.p1_home_advantage_bonus, self.p2_home_advantage_bonus],
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
        home_player_name = input(f"\nWhich player has the HOME ADVANTAGE? ({self.p1.name} or {self.p2.name}): ").strip()
        
        if home_player_name.lower() == self.p1.name.lower():
            self.apply_home_advantage(self.p1)
        elif home_player_name.lower() == self.p2.name.lower():
            self.apply_home_advantage(self.p2)
        else:
            print("No valid home player selected. No home advantage will be applied.")
        
        self.experience_advantage()
        self.compare_metrics()
        
        # Get betting suggestions
        betting_suggestions = self.get_betting_suggestions()
        print("\n--- Betting Suggestions ---")
        print(betting_suggestions)
    
    def plot_results(self, df):
        """Generates and displays a bar chart of the player stats."""
        ax = df.plot(kind="bar", figsize=(12, 7))
        plt.title(f"Comparison Analysis: {self.p1.name} vs {self.p2.name} on {self.match_location}")
        plt.ylabel("Values")
        plt.xticks(rotation=45, ha="right")
        plt.legend(title="Player")
        
        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f", label_type="edge", fontsize=8)
        
        plt.tight_layout()
        plt.show()
    
    def get_betting_suggestions(self):
        """
        Analyzes player data and generates betting suggestions based on a more robust statistical advantage,
        covering various markets like those on sporty.com.
        """
        player_data = self._create_data_dict()
        player1_name = self.p1.name.lower()
        player2_name = self.p2.name.lower()
        
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
        
        # Consider home advantage points in the final decision
        p1_total = p1_score + (self.p1_points / 10)  # Scale down points to make them comparable
        p2_total = p2_score + (self.p2_points / 10)  # Scale down points to make them comparable
        
        if p1_total > p2_total:
            suggestions["Match Winner (1x2)"].append(f"Based on superior stats and home advantage, bet on **{player1_name}** to win the match outright.")
        elif p2_total > p1_total:
            suggestions["Match Winner (1x2)"].append(f"Based on superior stats and home advantage, bet on **{player2_name}** to win the match outright.")
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
            underdog = player2_name if p1_total > p2_total else player1_name
            suggestions["Set Handicap (-1.5 / +1.5)"].append(f"The match is likely to be competitive. Bet on **{underdog} with a +1.5 set handicap**. This means they are likely to win at least one set, as neither player has a clear enough advantage for a 2-0 win.")
        
        # --- Game Handicap ---
        # --- Game Handicap ---
        # Base game handicap on a tiered system of statistical advantage.
        difference = abs(p1_total - p2_total)
        
        if p1_total > p2_total:
            favorite, underdog = self.p1.name, self.p2.name
        else:
            favorite, underdog = self.p2.name, self.p1.name
            
        if difference >= 6:
            suggestions["Game Handicap"].append(f"This is a massive statistical mismatch. Bet on **{favorite} with a -7.5 game handicap**. They are likely to dominate the match.")
        elif difference >= 4:
            suggestions["Game Handicap"].append(f"There is a significant advantage for one player. Bet on **{favorite} with a -5.5 game handicap**. They should win by a comfortable margin.")
        elif difference >= 2:
            suggestions["Game Handicap"].append(f"One player has a clear advantage. Bet on **{favorite} with a -3.5 game handicap**. They are likely to win and cover this margin.")
        elif difference >= 1:
            suggestions["Game Handicap"].append(f"The stats are moderately in favor of one player. Consider **{favorite} with a -2.5 game handicap**, but be cautious.")
        else:
            suggestions["Game Handicap"].append(f"The game stats are too close. Consider betting on the underdog, **{underdog} with a +2.5 game handicap**, as they are likely to keep the game count tight.")
        

        
        # --- Correct Score ---
        if p1_total >= p2_total + 3:  # Clear favorite
            suggestions["Correct Score"].append(f"For a high-risk, high-reward bet, consider **{player1_name} to win 2-0**.")
        elif p2_total >= p1_total + 3:  # Clear favorite
            suggestions["Correct Score"].append(f"For a high-risk, high-reward bet, consider **{player2_name} to win 2-0**.")
        else:
            favorite = player1_name if p1_total > p2_total else player2_name
            suggestions["Correct Score"].append(f"The most likely correct score is **2-1** in favor of {favorite}. A 2-0 outcome is less probable.")
        
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


