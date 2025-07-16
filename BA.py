class Player:
    def __init__(self, name):
        self.name = name
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



    def ServeSpeed():
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

    def input_height_weight():
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


    def break_point_served():
        """
        Collects between 3 and 5 BPServed from user input
        and returns their average.

        Returns:
            float: The average of the entered serve values.
        """
        while True:
            user_input = input("Enter between BPServed 3 and 5 integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    BPServed = [int(item) for item in items]
                    total = sum(BPServed)
                    print(f"The sum of the BPServed values is: {total}")
                    break
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")
        
    
        total = sum(BPServed)
        avg = total / len(BPServed)
        print(f"The average BreakPointServed value is: {avg}")
        return avg


        self.average = break_point_served()

    def rally():
        """
        Collects between 3 and 5 rallies from user input
        and returns their average.

        Returns:
            float: The average of the entered rallied values.
        """
        while True:
            user_input = input("Enter between 3 and 5 Rallied integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    Rally = [int(item) for item in items]
                    total = sum(Rally)
                    print(f"The sum of the Rallied values is: {total}")
                    break
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")
        
    
        total = sum(Rally)
        avg = total / len(Rally)
        print(f"The average rally value is: {avg}")
        return avg


        self.average = rally()

    def rip():
        """
        Collects between 3 and 5 serve speeds or success rates from user input
        and returns their average.
        Returns: float: The average of the entered serve values.
        """
        while True:
            user_input = input("Enter between 3 and 5 RIP integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    Rip = [int(item) for item in items]
                    total = sum(Rip)
                    print(f"The sum of the Rip values is: {total}")
                    break
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")
        
    
        total = sum(Rip)
        avg = total / len(Rip)
        print(f"The average ReturnInPlay value is: {avg}")
        return avg

        self.average = rip()

    def ripW():
        """
        Collects between 3 and 5 serve speeds or success rates from user input
        and returns their average.
        Returns: float: The average of the entered serve values.
        """
        while True:
            user_input = input("Enter between 3 and 5 RIPW integer values, separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    RipW = [int(item) for item in items]
                    total = sum(RipW)
                    print(f"The sum of the RIPW values is: {total}")
                    break
                except ValueError:
                    print("Invalid input. Please enter only integer values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")
        
    
        total = sum(RipW)
        avg = total / len(RipW)
        print(f"The average ReturnInPlayWIN value is: {avg}")
        return avg

        self.average = ripW()

    def Ace():
        """
        Collects between 3 and 5 ace rates from user input (as float values)
        and returns their average.
        """
        while True:
            user_input = input("Enter between 3 and 5 ace values (numbers), separated by commas: ")
            items = [item.strip() for item in user_input.split(",")]
            if 3 <= len(items) <= 5:
                try:
                    ace = [(float(item) or int(item)) for item in items]
                    total = sum(ace)
                    print(f"The sum of the ace values is: {total}")
                    break
                except ValueError:
                    print("Invalid input. Please enter only numeric values separated by commas.")
            else:
                print("Please enter between 3 and 5 values.")
        
        avg = sum(ace) / len(ace)
        print(f"The average Ace value is: {avg}")
        return avg
    
        self.average = Ace()

    def point(self):
        initial = float(input(f"Player {self.number} initial points: "))
        final = float(input(f"Player {self.number} final points: "))
        difference = final - initial
        
        if difference > 0:
            print(f"The difference is positive: {difference}")
        elif difference < 0:
            print(f"The difference is negative: {difference}")
        else:
            print("There is no difference (difference is zero).")
        return difference


    def select_surface(self):
        print("Are Most tournaments and awards are on Grass, Clay, Carpet, or Hard courts.?")
        print("If you have experience on any of these surfaces, please select one to indicate your experience.")
        while True:
            surface = input(f"Player {self.name} surface experience (Grass/Clay/Carpet/Hard): ").strip().lower()
            if surface in ['grass', 'clay', 'carpet', 'hard']:
                print("Great! Your experience on this surface will be noted.")
                return surface.capitalize()
            print("Invalid input. Please enter one of: Grass, Clay, Carpet, or Hard.")
pass


class Game:
    def __init__(self):
        name1 = input("Enter the name of Player 1: ")
        name2 = input("Enter the name of Player 2: ")
        self.player1 = Player(name1)
        self.player2 = Player(name2)
        pass


        
    
    def analyze_players(self):
        # Nested logic based on your description
        if self.player1.get_age < self.player2.get_age:
            print(f"{self.player1.name} is younger than {self.player2.name}.")
            
            # Check dominant hand
            if self.player1.hand in ["Right", "Left"]:
                print(f"{self.player1.name} uses their {self.player1.hand} hand.")
                
                # Check serve speed difference
                speed_diff = self.player1.serve_speed - self.player2.serve_speed
                print(f"Serve speed difference: {speed_diff}")
                
                # Check if this difference exceeds any value in the list
                compare_values = [3, 4, 5, 6, 7, 8, 9, 10]
                if any(speed_diff >= val for val in compare_values):
                    print("Serve speed difference exceeds at least one of the threshold values.")
                else:
                    print("Serve speed difference does not exceed the threshold values.")
        else:
            print(f"{self.player2.name} is older or equal in age to {self.player1.name}.")

# Usage example:
# Create players with all necessary attributes properly initialized
# Then create a game instance and call analyze_players()