class Player:
    def __init__(self, name=None, age=None, hand=None, serve_avg=None):
        self.name = name
        self.age = age
        self.hand = hand
        self.serve_avg = serve_avg

    @staticmethod
    def get_float(prompt):
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

    def input_age(self):
        while True:
            try:
                age = int(input("Enter the player's age: "))
                if age >= 0:
                    self.age = age
                    return
                else:
                    print("Please enter a valid non-negative age.")
            except ValueError:
                print("Invalid input. Please enter a numerical value for age.")

    def select_hand(self):
        while True:
            hand = input("Enter the player's dominant hand ('L' for Left, 'R' for Right): ").strip().upper()
            if hand == 'L':
                self.hand = 'Left'
                return
            elif hand == 'R':
                self.hand = 'Right'
                return
            else:
                print("Invalid input. Please enter 'L' or 'R'.")

    def first_serve(self):
        """
        Collects between 3 and 5 serve speeds or success rates from user input
        and returns their average.
        """
        while True:
            user_input = input("Enter the firstServe between 3 and 5 integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    serve_values = [int(item) for item in items]
                    total = sum(serve_values)
                    print(f"The sum of the serve values is: {total}")
                    avg = total / len(serve_values)
                    print(f"The average First serve value is: {avg}")
                    self.serve_avg = avg
                    return
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")

# Example of creating a Player object and gathering info
player = Player()
player.input_age()
player.select_hand()
player.first_serve()

print(f"\nPlayer details:\nAge: {player.age}\nHand: {player.hand}\nAverage Serve: {player.serve_avg}")