class Player:
    def __init__(self, number):
        self.number = number
        self.age = self.get_age()
        self.hand = self.select_hand()
        self.first_serve = self.get_serve("first")
        self.second_serve = self.get_serve("second")
        self.serve_speed = self.get_serve_speed()
        self.height, self.weight = self.get_height_weight()
        self.break_points = self.get_break_points()
        self.rally_stats = self.get_rally()
        self.rip = self.get_rip()
        self.ripw = self.get_ripw()
        self.ace = self.get_ace()
        self.points = self.get_points()

    def get_age(self):
        while True:
            try:
                age = int(input(f"Enter Player {self.number}'s age: "))
                if age >= 0:
                    return age
                print("Please enter a valid non-negative age.")
            except ValueError:
                print("Invalid input. Please enter a numerical value.")

    def select_hand(self):
        while True:
            hand = input(f"Player {self.number} dominant hand (L/R): ").strip().upper()
            if hand == 'L': return 'Left'
            if hand == 'R': return 'Right'
            print("Invalid input. Please enter 'L' or 'R'.")

    def get_serve(self, serve_type):
        while True:
            user_input = input(f"Enter Player {self.number}'s {serve_type} serve (3-5 values, comma-separated): ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    values = [int(item) for item in items]
                    return sum(values) / len(values)
                except ValueError:
                    print("Please enter integer values only.")
            print("Please enter 3-5 values.")

    def get_serve_speed(self):
        return self.get_serve("speed")

    def get_height_weight(self):
        while True:
            height = input(f"Enter Player {self.number}'s height (e.g., 180 or 1.80): ")
            unit = input("Centimeters or meters? (cm/m): ").lower()
            try:
                h_val = float(height)
                if unit == 'cm': h_val /= 100
                elif unit != 'm': raise ValueError
                weight = float(input(f"Player {self.number} weight (kg): "))
                if h_val > 0 and weight > 0:
                    return h_val, weight
                print("Values must be positive.")
            except ValueError:
                print("Invalid input. Please enter numeric values.")

    def get_break_points(self):
        return self.get_serve("break points")

    def get_rally(self):
        return self.get_serve("rally")

    def get_rip(self):
        return self.get_serve("return in play")

    def get_ripw(self):
        return self.get_serve("return in play wins")

    def get_ace(self):
        return self.get_serve("ace")

    def get_points(self):
        initial = float(input(f"Player {self.number} initial points: "))
        final = float(input(f"Player {self.number} final points: "))
        return final - initial

    def total_score(self):
        return (self.first_serve + self.second_serve + self.serve_speed +
                self.break_points + self.rally_stats + self.rip +
                self.ripw + self.ace + self.points)

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
        # Create result table
        fig, ax = plt.subplots(figsize=(6, 2))
        ax.axis('off')
        result_text = []
        result_text.append(["Player 1 Total", f"{p1_score:.1f}"])
        result_text.append(["Player 2 Total", f"{p2_score:.1f}"])
        result_text.append(["\nResult:",
            "Player 1 Wins!" if p1_score > p2_score else
            "Player 2 Wins!" if p2_score > p1_score else
            "It's a Tie!"])

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

if __name__ == "__main__":
    match = Game()
    match.run_match()