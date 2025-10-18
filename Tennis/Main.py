from compare2 import create_players
#from ntn import create_players
import pandas as pd
import matplotlib.pyplot as plt

class PlayerEvaluator:
    def __init__(self, p1, p2, match_surface):
        self.p1 = p1
        self.p2 = p2
        self.match_surface = match_surface
        self.p1_points = 0
        self.p2_points = 0
        self.results = {}

    def _apply_home_advantage(self):
        """
        Calculates and adds a home advantage bonus of 10% of the first player's total stats.
        """
        # Sum up all relevant numerical stats for player 1.
        total_stats_p1 = (
            self.p1.first_serve + self.p1.second_serve + self.p1.serve_speed + 
            self.p1.rally_stats + self.p1.rip + self.p1.ripw + self.p1.points + 
            self.p1.ace + self.p1.rally_per_height + self.p1.age
        )
        
        # Calculate 10% of the total stats.
        home_advantage_points = total_stats_p1 * 0.10
        self.p1_points += home_advantage_points
        self.p1_home_advantage_bonus = home_advantage_points
        print(f"\n🏠 {self.p1.name} gains {home_advantage_points:.2f} points from home advantage (10% of total stats).")

    def experience(self):
        match_surface = self.match_surface.lower()
        p1_exp = getattr(self.p1, 'experience_surface', '').lower()
        p2_exp = getattr(self.p2, 'experience_surface', '').lower()

        p1_has_exp = p1_exp == match_surface
        p2_has_exp = p2_exp == match_surface

        if p1_has_exp and not p2_has_exp:
            print(f"{self.p1.name} has advantage on {self.match_surface}.")
            self.p1_points += 2
            advantage = self.p1
        elif p2_has_exp and not p1_has_exp:
            print(f"{self.p2.name} has advantage on {self.match_surface}.")
            self.p2_points += 2
            advantage = self.p2
        else:
            advantage = self._tie_breaker()

        # Final output
        print(f"\n🎯 Points Summary:")
        print(f"{self.p1.name} points: {self.p1_points}")
        print(f"{self.p2.name} points: {self.p2_points}")
        if advantage:
            print(f"Final advantage: {advantage.name}")
        else:
            print("Players are evenly matched.")

        # Run pandas/matplotlib comparison

    def _tie_breaker(self):
        # Full nested decision logic
        advantage = None

        if self.p1.hand == 'Right' and self.p2.hand == 'Left':
            print(f"{self.p1.name} has hand advantage.")
            advantage = self.p1
            self.p1_points += 1
        elif self.p2.hand == 'Right' and self.p1.hand == 'Left':
            print(f"{self.p2.name} has hand advantage.")
            advantage = self.p2
            self.p2_points += 1
        elif self.p1.age < self.p2.age:
            print(f"{self.p1.name} is younger; advantage.")
            advantage = self.p1
            self.p1_points += 1
        elif self.p2.age < self.p1.age:
            print(f"{self.p2.name} is younger; advantage.")
            advantage = self.p2
            self.p2_points += 1
        elif (20 <= self.p1.age < 30) and not (20 <= self.p2.age < 30):
            print(f"{self.p1.name} in 20s; advantage.")
            advantage = self.p1
            self.p1_points += 1
        elif (20 <= self.p2.age < 30) and not (20 <= self.p1.age < 30):
            print(f"{self.p2.name} in 20s; advantage.")
            advantage = self.p2
            self.p2_points += 1
        elif self.p1.first_serve > self.p2.first_serve:
            print(f"{self.p1.name} has better first serve.")
            advantage = self.p1
            self.p1_points += 1
        elif self.p2.first_serve > self.p1.first_serve:
            print(f"{self.p2.name} has better first serve.")
            advantage = self.p2
            self.p2_points += 1
        elif self.p1.second_serve > self.p2.second_serve:
            print(f"{self.p1.name} has better second serve.")
            advantage = self.p1
            self.p1_points += 1
        elif self.p2.second_serve > self.p1.second_serve:
            print(f"{self.p2.name} has better second serve.")
            advantage = self.p2
            self.p2_points += 1
        elif self.p1.serve_speed > self.p2.serve_speed:
            print(f"{self.p1.name} has better serve speed.")
            advantage = self.p1
            self.p1_points += 2
        elif self.p2.serve_speed > self.p1.serve_speed:
            print(f"{self.p2.name} has better serve speed.")
            advantage = self.p2
            self.p2_points += 2
        elif self.p1.rally_stats > self.p2.rally_stats:
            print(f"{self.p1.name} better rally stats.")
            advantage = self.p1
            self.p1_points += 1
        elif self.p2.rally_stats > self.p1.rally_stats:
            print(f"{self.p2.name} better rally stats.")
            advantage = self.p2
            self.p2_points += 1
        elif self.p1.rip > self.p2.rip:
            print(f"{self.p1.name} better rip.")
            advantage = self.p1
            self.p1_points += 1
        elif self.p2.rip > self.p1.rip:
            print(f"{self.p2.name} better rip.")
            advantage = self.p2
            self.p2_points += 1
        elif self.p1.ripw > self.p2.ripw:
            print(f"{self.p1.name} better ripw.")
            advantage = self.p1
            self.p1_points += 1
        elif self.p2.ripw > self.p1.ripw:
            print(f"{self.p2.name} better ripw.")
            advantage = self.p2
            self.p2_points += 1
        elif self.p1.points > self.p2.points:
            print(f"{self.p1.name} is in better form based on points.")
            advantage = self.p1
            self.p1_points += 1
        elif self.p2.points > self.p1.points:
            print(f"{self.p2.name} is in better form based on points.")
            advantage = self.p2
            self.p2_points += 1
        elif (self.p1.ace > self.p2.ace) and (self.p1.serve_speed > self.p2.serve_speed):
            print(f"{self.p1.name} wins by ace and serve speed.")
            advantage = self.p1
            self.p1_points += 1
        elif (self.p2.ace > self.p1.ace) and (self.p2.serve_speed > self.p1.serve_speed):
            print(f"{self.p2.name} wins by ace and serve speed.")
            advantage = self.p2
            self.p2_points += 1
        elif hasattr(self.p1, 'rally_per_height') and hasattr(self.p2, 'rally_per_height'):
            if self.p1.rally_per_height > self.p2.rally_per_height:
                print(f"{self.p1.name} has a better rally per height ratio.")
                advantage = self.p1
                self.p1_points += 2
            elif self.p2.rally_per_height > self.p1.rally_per_height:
                print(f"{self.p2.name} has a better rally per height ratio.")
                advantage = self.p2
                self.p2_points += 2
            else:
                print("Both players have equal rally per height ratios.")

        return advantage

    def compare_metrics(self):
        # Build metrics dictionary
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
            "Home Advantage": [self.p1_home_advantage_bonus, 0],
        }

        df = pd.DataFrame(metrics, index=[self.p1.name, self.p2.name]).T

        print("\n📊 Detailed Comparison Table:")
        print(df)

        # Advantage summary
        summary = {}
        p1_wins, p2_wins, ties = 0, 0, 0
        for metric, values in metrics.items():
            if values[0] > values[1]:
                summary[metric] = self.p1.name
                p1_wins += 1
            elif values[1] > values[0]:
                summary[metric] = self.p2.name
                p2_wins += 1
            else:
                summary[metric] = "Tie"
                ties += 1

        summary_df = pd.DataFrame.from_dict(summary, orient="index", columns=["Advantage"])
        print("\n✅ Metric by Metric Advantage:")
        print(summary_df)

        print("\n🏆 Final Decision:")
        if p1_wins > p2_wins:
            print(f"{self.p1.name} wins overall ({p1_wins} metrics vs {p2_wins})")
        elif p2_wins > p1_wins:
            print(f"{self.p2.name} wins overall ({p2_wins} metrics vs {p1_wins})")
        else:
            print(f"It's a tie! ({p1_wins} each, {ties} tied metrics)")

        # Visualization
        self.plot_results(df)

    def plot_results(self, df):
        ax = df.plot(kind="bar", figsize=(10, 6))
        plt.title(f"Comparison Analysis: {self.p1.name} vs {self.p2.name} on {self.match_surface}")
        plt.ylabel("Values")
        plt.xticks(rotation=45, ha="right")

        for container in ax.containers:
            ax.bar_label(container, fmt="%.1f", label_type="edge", fontsize=8)

        plt.tight_layout()
        plt.show()


if __name__ == "__main__":
    player1, player2 = create_players()
    match_surface = input("Enter match surface (Grass/Clay/Carpet/Hard): ")
    evaluator = PlayerEvaluator(player1, player2, match_surface)
    evaluator.experience()
