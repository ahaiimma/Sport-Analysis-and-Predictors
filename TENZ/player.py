import json

class Player:
    """A class to represent a tennis player and collect their key stats."""
    
    def __init__(self):
        print("--- Player Creation ---")
        self.name = input("Enter the player's name: ")
        self.home_location = input("Enter the player's home location (city/country): ")
        self.initial_number = self._get_float("Enter the player's initial number: ")
        self.final_number = self._get_float("Enter the player's final number: ")
        self.age = self._get_age()
        self.hand = self._select_player_hand()
        self.experience_surface = self._select_surface()
        
        # Serve statistics
        self.first_serve = self._get_avg_serve("firstServe")
        self.second_serve = self._get_avg_serve("secondServe")
        self.serve_speed = self._get_avg_serve("serveSpeed")
        
        # Physical attributes
        self.height, self.weight = self._input_height_weight()
        
        # Performance statistics
        self.break_points = self._avg_input("BPServed")
        self.rally_stats = self._avg_input("Rallied")
        self.rip = self._avg_input("RIP")
        self.ripw = self._avg_input("RIPW")
        self.ace = self._avg_input("Ace", float_values=True)
        
        # Calculated statistics
        self.points = self._calculate_points()
        self.rally_per_height = self._calculate_rally_per_height()
    
    @staticmethod
    def _get_float(prompt):
        """Helper method to get a float value with validation."""
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Invalid input. Please enter a numeric value.")
    
    def _get_age(self):
        """Prompts for and validates the player's age."""
        while True:
            try:
                age = int(input("Enter the player's age: "))
                if age >= 0:
                    return age
                print("Please enter a valid non-negative age.")
            except ValueError:
                print("Invalid input. Please enter a number.")
    
    def _select_player_hand(self):
        """Prompts for and validates the player's dominant hand."""
        while True:
            hand = input("Enter the player's dominant hand ('L' for Left, 'R' for Right): ").strip().upper()
            if hand in ['L', 'R']:
                return 'Left' if hand == 'L' else 'Right'
            print("Invalid input. Please enter 'L' or 'R'.")
    
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
    
    def _input_height_weight(self):
        """Prompts for and validates height and weight, converting to standard units."""
        # Height input
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
        
        # Weight input
        while True:
            weight_input = input("Enter the weight in kilograms: ").strip()
            try:
                weight_kg = float(weight_input)
                if weight_kg >= 0:
                    break
                print("Please enter a non-negative value for weight.")
            except ValueError:
                print("Invalid input. Please enter a numeric value for weight (integer or float).")
        
        print(f"Height: {height_in_meters:.2f} meters, Weight: {weight_kg:.1f} kg")
        return height_in_meters, weight_kg
    
    def _calculate_points(self):
        """Calculates the point difference."""
        difference = self.final_number - self.initial_number
        print(f"Points difference: {difference}")
        return difference
    
    def _calculate_rally_per_height(self):
        """Calculates a rally-to-height ratio."""
        divisor = self.height * 0.1
        if divisor == 0:
            return 0
        return self.rally_stats / divisor
    
    def _select_surface(self):
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
    
    def to_dict(self):
        """Converts player data to a dictionary for easy serialization."""
        return {
            "name": self.name,
            "home_location": self.home_location,
            "initial_number": self.initial_number,
            "final_number": self.final_number,
            "age": self.age,
            "hand": self.hand,
            "experience_surface": self.experience_surface,
            "first_serve": self.first_serve,
            "second_serve": self.second_serve,
            "serve_speed": self.serve_speed,
            "height": self.height,
            "weight": self.weight,
            "break_points": self.break_points,
            "rally_stats": self.rally_stats,
            "rip": self.rip,
            "ripw": self.ripw,
            "ace": self.ace,
            "points": self.points,
            "rally_per_height": self.rally_per_height
        }
    
    @classmethod
    def from_dict(cls, data):
        """Creates a Player instance from a dictionary."""
        player = cls.__new__(cls)
        for key, value in data.items():
            setattr(player, key, value)
        return player


def create_players():
    """Creates and returns two Player objects."""
    print("\n--- Creating Player 1 ---")
    player1 = Player()
    print("\n--- Creating Player 2 ---")
    player2 = Player()
    return player1, player2


def save_players(player1, player2, filename="players_data.json"):
    """Saves player data to a JSON file."""
    data = {
        "player1": player1.to_dict(),
        "player2": player2.to_dict()
    }
    
    with open(filename, 'w') as f:
        json.dump(data, f, indent=4)
    
    print(f"Player data saved to {filename}")


def load_players(filename="players_data.json"):
    """Loads player data from a JSON file."""
    try:
        with open(filename, 'r') as f:
            data = json.load(f)
        
        player1 = Player.from_dict(data["player1"])
        player2 = Player.from_dict(data["player2"])
        
        print(f"Player data loaded from {filename}")
        return player1, player2
    except FileNotFoundError:
        print(f"No saved data found at {filename}")
        return None, None


