class Player:
    def __init__(self):
        self.name = input("Enter the player's name: ")
        self.home_location = input("Enter the player's home location (city/country): ")
        self.number1 = input("Enter the player's initial number: ")
        self.number2 = input("Enter the player's final number: ")
        self.age = self.get_age()
        self.hand = self.select_player_hand()
        self.first_serve = self.firstServe()
        self.second_serve = self.secondServe()
        self.serve_speed = self.ServeSpeed()
        self.height, self.weight = self.input_height_weight()
        self.break_points = self.break_point_served()
        self.rally_stats = self.rally()
        self.rip = self.rip()
        self.ripw = self.ripW()
        self.ace = self.Ace()
        self.points = self.point()
        self.rally_per_height = self.rally_per_height()
        self.experience_surface = self.select_surface()
        #self.home_Advantage = self.home_advantage(self, self.home_location)   


    @staticmethod
    def get_float(prompt):
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a numeric value.")

    def get_age(self):
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
        while True:
            hand = input("Enter the player's dominant hand ('L' for Left, 'R' for Right): ").strip().upper()
            if hand == 'L':
                return 'Left'
            elif hand == 'R':
                return 'Right'
            else:
                print("Invalid input. Please enter 'L' or 'R'.")

    def firstServe(self):
        while True:
            user_input = input("Enter the firstServe between 3 and 5 integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    serve_values = [int(item) for item in items]
                    total = sum(serve_values)
                    avg = total / len(serve_values)
                    print(f"The average First serve value is: {avg}")
                    return avg
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")

        self.average = firstServe()

    def secondServe(self):
        """
        Collects between 3 and 5 serve speeds or success rates from user input
        and returns their average.

        Returns:
            float: The average of the entered serve values.
        """
        while True:
            user_input = input("Enter the secondServe between 3 and 5 integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    serve_values = [int(item) for item in items]
                    total = sum(serve_values)
                    print(f"The sum of the values is: {total}")
                    break
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")
        
    
        total = sum(serve_values)
        avg = total / len(serve_values)
        print(f"The average Last serve value is: {avg}")
        return avg


        self.average = secondServe()



    def ServeSpeed(self):
        """
        Collects between 3 and 5 serve speeds or success rates from user input
        and returns their average.

        Returns:
            float: The average of the entered serve values.
        """
        while True:
            user_input = input("Enter the serveSpeed between 3 and 5 integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    serveSpeed = [int(item) for item in items]
                    total = sum(serveSpeed)
                    print(f"The sum of the  serveSpeed values is: {total}")
                    break
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")
        
    
        total = sum(serveSpeed)
        avg = total / len(serveSpeed)
        print(f"The average Serve Speed value is: {avg}")
        return avg


        self.average = ServeSpeed()

    def input_height_weight(self):
        """
        Prompts the user to input height (in centimeters or meters) and weight.
        Height can be entered in centimeters or meters.
        Ensures that the inputs are either integers or floats.
        
        Returns:
            tuple: (height_in_meters, weight_in_kg)
        """
        # Input height with unit option
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
        
        # Input weight in kg
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
        
        print(f"Height: {height_in_meters} meters, Weight: {weight_kg} kg")
        return height_in_meters, weight_kg

        # Example usage
        self.height, self.weight = input_height_weight()


    def break_point_served(self):
        return self._avg_input("BPServed")

    def rally(self):
        return self._avg_input("Rallied")

    def rip(self):
        return self._avg_input("RIP")

    def ripW(self):
        return self._avg_input("RIPW")

    def Ace(self):
        return self._avg_input("Ace", float_values=True)

    def _avg_input(self, label, float_values=False):
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

    def point(self):
        initial = float(input(f"Player {self.number1} initial points: "))
        final = float(input(f"Player {self.number2} final points: "))
        difference = final - initial
        
        if difference > 0:
            print(f"The difference is positive: {difference}")
        elif difference < 0:
            print(f"The difference is negative: {difference}")
        else:
            print("There is no difference (difference is zero).")
        return difference
        
        self.points = point()    

    
    def rally_per_height(self):
        height = getattr(self, 'height', None)
        rally_stats = getattr(self, 'rally_stats', None)
        if height is None or rally_stats is None:
            return None
        divisor = height * 0.1
        return rally_stats / divisor
    
        self.rally_per_height = rally_per_height()



    def select_surface(self):
        print("Are Most tournaments and awards are on Grass, Clay, Carpet, or Hard courts.?")
        print("If you have experience on any of these surfaces, please select one to indicate your experience.")
        while True:
            surface = input(f"Player {self.name} surface experience (Grass/Clay/Carpet/Hard): ").strip().lower()
            if surface in ['grass', 'clay', 'carpet', 'hard']:
                print("Great! Your experience on this surface will be noted.")
                return surface.capitalize()
            print("Invalid input. Please enter one of: Grass, Clay, Carpet, or Hard.")


    # The home_advantage function should be defined outside the Player class.
    def home_advantage(self, player, match_location):
        """
        Calculate a home advantage score for a player.

        Args:
        player (Player): The player object
        match_location (str): Location of the match (city/country/surface)

        Returns:
        int: Bonus points from home advantage
        """
        # Check if the player has a home_location attribute and if it matches the match location
        if hasattr(player, "home_location") and player.home_location.strip().lower() == match_location.strip().lower():
            print(f"{player.name} has home advantage at {match_location}! (+20 points)")
            return 20
        
        # No advantage if the location doesn't match
        return 0


    def display_stats(self):
        print(f"\n--- Stats for {self.name} ---")
        print(f"Age: {self.age}")
        print(f"Hand: {self.hand}")
        print(f"Surface: {self.experience_surface}")
        print(f"Height: {self.height:.2f} m, Weight: {self.weight:.1f} kg")
        print(f"First Serve Avg: {self.first_serve}")
        print(f"Second Serve Avg: {self.second_serve}")
        print(f"Serve Speed Avg: {self.serve_speed}")
        print(f"Break Points Avg: {self.break_points}")
        print(f"Rally Avg: {self.rally_stats}")
        print(f"RIP: {self.rip}, RIPW: {self.ripw}")
        print(f"Ace Avg: {self.ace}")
        print(f"Points Difference: {self.points}")
        print(f"Experienced on {self.experience_surface} surface.\n")
        print(f"rally to height ratio on {self.rally_per_height} .\n")
        print(f"Experienced on {self.experience_surface} surface.\n")
        #print(f"Home Advantage Points: {self.home_Advantage}\n")

def create_players():
    """
    Creates and returns two Player objects.
    Only runs interactively when explicitly called.
    """
    print("\n--- Creating Player 1 ---")
    player1 = Player()

    print("\n--- Creating Player 2 ---")
    player2 = Player()

    return player1, player2


# Prevent auto-execution on import
if __name__ == "__main__":
    p1, p2 = create_players()
    p1.display_stats()
    p2.display_stats()
