import pandas as pd
import matplotlib.pyplot as plt
from test import Player, create_players

class PlayerEvaluator:
    def __init__(self, p1, p2, match_location):
        self.p1 = p1
        self.p2 = p2
        self.match_location = match_location
        self.p1_points = 0
        self.p2_points = 0
        self.p1_home_advantage_bonus = 0
        self.p2_home_advantage_bonus = 0

    def _apply_home_advantage(self):
        """Calculates and applies home advantage points if applicable."""
        # Calculate bonus based on home location matching match location
        if self.p1.home_location.strip().lower() == self.match_location.strip().lower():
            self.p1_home_advantage_bonus = 20
            self.p1_points += self.p1_home_advantage_bonus
            print(f"🏠 {self.p1.name} gains {self.p1_home_advantage_bonus} points from home advantage.")
        
        if self.p2.home_location.strip().lower() == self.match_location.strip().lower():
            self.p2_home_advantage_bonus = 20
            self.p2_points += self.p2_home_advantage_bonus
            print(f"🏠 {self.p2.name} gains {self.p2_home_advantage_bonus} points from home advantage.")

    def evaluate_match(self):
        """Main method to run the evaluation process."""
        self._apply_home_advantage()
        self.experience_advantage()
        self.compare_metrics()

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

    def compare_metrics(self):
        """Displays a detailed comparison table and plot using pandas."""
        metrics = {
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

if __name__ == "__main__":
    player1, player2 = create_players()
    match_location = input("\nEnter the match location (city/country/surface): ")
    evaluator = PlayerEvaluator(player1, player2, match_location)
    evaluator.evaluate_match()