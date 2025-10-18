import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


class Player:
    def __init__(self):
        self.name = input("Enter the player's name: ")
        self.home_location = input("Enter the player's home location (city/country): ")
        self.number1 = input("Enter the player's initial number: ")
        self.number2 = input("Enter the player's final number: ")
        self.age = self.get_age()
        self.hand = self.select_player_hand()
        self.first_serve = self.collect_values("First Serve")
        self.second_serve = self.collect_values("Second Serve")
        self.serve_speed = self.collect_values("Serve Speed")
        self.height, self.weight = self.input_height_weight()
        self.break_points = self.collect_values("Break Points")
        self.rally_stats = self.collect_values("Rally")
        self.rip = self.collect_values("RIP")
        self.ripw = self.collect_values("RIPW")
        self.ace = self.collect_values("Ace", float_values=True)
        self.points = self.point()
        self.rally_per_height = self.calc_rally_per_height()
        self.experience_surface = self.select_surface()

    # =====================
    # Data collection
    # =====================
    @staticmethod
    def get_age():
        while True:
            try:
                age = int(input("Enter the player's age: "))
                if age >= 0:
                    return age
            except ValueError:
                pass
            print("Invalid input. Please enter a valid age.")

    @staticmethod
    def select_player_hand():
        while True:
            hand = input("Enter the player's dominant hand (L/R): ").strip().upper()
            if hand in ["L", "R"]:
                return "Left" if hand == "L" else "Right"
            print("Invalid input. Please enter 'L' or 'R'.")

    @staticmethod
    def collect_values(label, float_values=False):
        """Collect 3–5 values and return their NumPy average"""
        while True:
            try:
                values = input(f"Enter between 3 and 5 {label} values (comma-separated): ")
                arr = np.array([float(v) if float_values else int(v) for v in values.split(",")])
                if 3 <= len(arr) <= 5:
                    avg = np.mean(arr)
                    print(f"{label} average = {avg:.2f}")
                    return avg
            except ValueError:
                pass
            print("Invalid input. Please enter numbers separated by commas (3–5 values).")

    @staticmethod
    def input_height_weight():
        while True:
            try:
                height_input = float(input("Enter height (in cm if > 3, else in meters): "))
                if height_input > 3:
                    height = height_input / 100
                else:
                    height = height_input
                weight = float(input("Enter weight in kg: "))
                return height, weight
            except ValueError:
                print("Invalid input. Try again.")

    def point(self):
        try:
            initial = float(input(f"Player {self.number1} initial points: "))
            final = float(input(f"Player {self.number2} final points: "))
            return final - initial
        except ValueError:
            return 0

    def calc_rally_per_height(self):
        if self.height and self.rally_stats:
            return self.rally_stats / (self.height * 0.1)
        return None

    @staticmethod
    def select_surface():
        while True:
            surface = input("Surface experience (Grass/Clay/Carpet/Hard): ").strip().capitalize()
            if surface in ["Grass", "Clay", "Carpet", "Hard"]:
                return surface
            print("Invalid input. Try again.")

    # =====================
    # Data Export
    # =====================
    def to_dataframe(self):
        """Return player's stats as a Pandas DataFrame row"""
        data = {
            "Name": self.name,
            "Location": self.home_location,
            "Age": self.age,
            "Hand": self.hand,
            "Surface": self.experience_surface,
            "Height(m)": self.height,
            "Weight(kg)": self.weight,
            "First Serve": self.first_serve,
            "Second Serve": self.second_serve,
            "Serve Speed": self.serve_speed,
            "Break Points": self.break_points,
            "Rally": self.rally_stats,
            "RIP": self.rip,
            "RIPW": self.ripw,
            "Ace": self.ace,
            "Points": self.points,
            "Rally/Height": self.rally_per_height
        }
        return pd.DataFrame([data])

    # =====================
    # Visualization
    # =====================
    def plot_stats(self):
        df = self.to_dataframe().set_index("Name")
        numeric_stats = df.select_dtypes(include=[np.number]).T  # Transpose for plotting
        numeric_stats.plot(kind="bar", legend=False, figsize=(8, 6))
        plt.title(f"Performance Stats for {self.name}")
        plt.ylabel("Values")
        plt.xticks(rotation=45, ha="right")
        plt.tight_layout()
        plt.show()


# =====================
# Example usage
# =====================
if __name__ == "__main__":
    player1 = Player()
    player2 = Player()

    # Compare with pandas
    df = pd.concat([player1.to_dataframe(), player2.to_dataframe()], ignore_index=True)
    print("\n=== Player Comparison Table ===")
    print(df)

    # Plot comparison side by side
    df_numeric = df.drop(columns=["Name", "Location", "Hand", "Surface"])
    df_numeric.set_index(df["Name"]).T.plot(kind="bar", figsize=(10, 6))
    plt.title("Player Comparison")
    plt.ylabel("Values")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()
