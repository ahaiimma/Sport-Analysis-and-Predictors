import matplotlib.pyplot as plt

class Player:
    def __init__(self, number):
        self.number = number
        # Initialize attributes, optionally prompt the user for input
        self.age = None
        self.hand = None
        self.height = None
        self.weight = None
        self.first_serve = 0.0
        self.second_serve = 0.0
        # You can extend this to gather the actual data on creation
        self.gather_stats()

    def gather_stats(self):
        # Example prompts for each attribute:
        self.age = int(input(f"Enter age for Player {self.number}: "))
        self.hand = input(f"Enter preferred hand for Player {self.number} ('L' or 'R'): ").strip().upper()
        self.height = self.get_float(f"Enter height in meters for Player {self.number}: ")
        self.weight = self.get_float(f"Enter weight in kg for Player {self.number}: ")
        self.first_serve = self.get_float("Enter average first serve percentage: ")
        self.second_serve = self.get_float("Enter average second serve percentage: ")

    @staticmethod
    def get_float(prompt):
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

    def total_score(self):
        # Example combining stats into a total score, can be customized
        return self.first_serve * 0.6 + self.second_serve * 0.4

    def display_stats(self):
        print(f"\nPlayer {self.number} Stats:")
        print(f"Age: {self.age}  Dominant Hand: {self.hand}")
        print(f"Height: {self.height:.2f}m  Weight: {self.weight}kg")
        print(f"First Serve Avg: {self.first_serve:.1f}")
        print(f"Second Serve Avg: {self.second_serve:.1f}")
        print(f"Total Score: {self.total_score():.1f}")

class Game:
    def __init__(self):
        self.player1 = Player(1)
        self.player2 = Player(2)

    def compare_stats(self):
        print("\n=== MATCH COMPARISON ===")
        print(f"{'Stat':<20} | Player 1 | Player 2")
        print(f"{'Age':<20} | {self.player1.age:7} | {self.player2.age}")
        print(f"{'Dominant Hand':<20} | {self.player1.hand:7} | {self.player2.hand}")
        print(f"{'First Serve Avg':<20} | {self.player1.first_serve:7.1f} | {self.player2.first_serve:.1f}")
        print(f"{'Total Score':<20} | {self.player1.total_score():7.1f} | {self.player2.total_score():.1f}")

    def determine_winner(self):
        p1_score = self.player1.total_score()
        p2_score = self.player2.total_score()
        # Plot table for the result
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.axis('off')
        result_text = []
        result_text.append(["Player 1 Total", f"{p1_score:.1f}"])
        result_text.append(["Player 2 Total", f"{p2_score:.1f}"])
        if p1_score > p2_score:
            result_text.append(["\nResult:", "Player 1 Wins!"])
        elif p2_score > p1_score:
            result_text.append(["\nResult:", "Player 2 Wins!"])
        else:
            result_text.append(["\nResult:", "It's a Tie!"])

        result_table = ax.table(cellText=result_text,
                                colWidths=[0.4, 0.6],
                                cellLoc='center',
                                loc='center')
        result_table.auto_set_font_size(False)
        result_table.set_fontsize(14)
        result_table.scale(1, 2)
        plt.title("Match Result", pad=20)
        plt.show()

    def run_match(self):
        self.player1.display_stats()
        self.player2.display_stats()
        self.compare_stats()
        self.determine_winner()

# Run the game
if __name__ == "__main__":
    match = Game()
    match.run_match()