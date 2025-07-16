import matplotlib.pyplot as plt

class Player:
    def __init__(self):
        self.name = input("Enter the player's name: ")
        #self.number = input("Enter the player's number or ID: ")
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
        self.experience_surface = input("Enter experience surface (e.g., 'Clay', 'Grass', etc.): ")

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

    def rally(self):
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

    def rip(self):
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

    def ripW(self):
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

    def Ace(self):
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

    def point(self, number):
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


player1 = Player()
player2 = Player()

class PlayerEvaluator:  
    def __init__(self, player1, player2):  
        self.p1 = player1  
        self.p2 = player2  

        self.p1_points = 0
        self.p2_points = 0

    def evaluate(self):  
        experience_levels = ['Clay', 'Grass', 'Carpet', 'Hard']  
        p1_exp = getattr(self.p1, 'experience_surface', None)  
        p2_exp = getattr(self.p2, 'experience_surface', None)  

        p1_has_exp = p1_exp in experience_levels  
        p2_has_exp = p2_exp in experience_levels  

        # The nested decision logic:  
        if p1_has_exp and not p2_has_exp:  
            print(f"{self.p1.name} has surface experience advantage.")  
            advantage = self.p1  
            self.p1_points += 2
        else:  
            if p2_has_exp and not p1_has_exp:  
                print(f"{self.p2.name} has surface experience advantage.")  
                advantage = self.p2  
                self.p2_points += 2
            else:  
                # Both have or both lack experience, move to next condition  
                if self.p1.hand == 'Right' and self.p2.hand == 'Left':  
                    print(f"{self.p1.name} has hand advantage.")  
                    advantage = self.p1  
                    self.p1_points += 1
                elif self.p2.hand == 'Right' and self.p1.hand == 'Left':  
                    print(f"{self.p2.name} has hand advantage.")  
                    advantage = self.p2  
                    self.p2_points += 1
                else:  
                    # Younger age comparison  
                    if self.p1.age < self.p2.age:  
                        print(f"{self.p1.name} is younger; advantage.")  
                        advantage = self.p1  
                        self.p1_points += 1
                    elif self.p2.age < self.p1.age:  
                        print(f"{self.p2.name} is younger; advantage.")  
                        advantage = self.p2  
                        self.p2_points += 1
                    else:  
                        # 20s check  
                        p1_in_20s = 20 <= self.p1.age < 30  
                        p2_in_20s = 20 <= self.p2.age < 30  
                        if p1_in_20s and not p2_in_20s:  
                            print(f"{self.p1.name} in 20s; advantage.")  
                            advantage = self.p1  
                            self.p1_points += 1
                        elif p2_in_20s and not p1_in_20s:  
                            print(f"{self.p2.name} in 20s; advantage.")  
                            advantage = self.p2
                            self.p2_points += 1  
                        else:  
                            # First serve  
                            if self.p1.first_serve > self.p2.first_serve:  
                                print(f"{self.p1.name} has better first serve.")  
                                advantage = self.p1
                                self.p1_points += 1  
                            elif self.p2.first_serve > self.p1.first_serve:  
                                print(f"{self.p2.name} has better first serve.")  
                                advantage = self.p2
                                self.p2_points += 1  
                            else:  
                                # Second serve  
                                if self.p1.second_serve > self.p2.second_serve:  
                                    print(f"{self.p1.name} has better second serve.")  
                                    advantage = self.p1
                                    self.p1_points += 1  
                                elif self.p2.second_serve > self.p1.second_serve:  
                                    print(f"{self.p2.name} has better second serve.")  
                                    advantage = self.p2
                                    self.p2_points += 1  
                                else:  
                                    # Serve speed  
                                    if self.p1.serve_speed > self.p2.serve_speed:  
                                        print(f"{self.p1.name} has better serve speed.")  
                                        advantage = self.p1
                                        self.p1_points += 2  
                                    elif self.p2.serve_speed > self.p1.serve_speed:  
                                        print(f"{self.p2.name} has better serve speed.")  
                                        advantage = self.p2
                                        self.p2_points += 2  
                                    else:  
                                        # Rally stats  
                                        if self.p1.rally_stats > self.p2.rally_stats:  
                                            print(f"{self.p1.name} better rally stats.")  
                                            advantage = self.p1
                                            self.p1_points += 1  
                                        elif self.p2.rally_stats > self.p1.rally_stats:  
                                            print(f"{self.p2.name} better rally stats.")  
                                            advantage = self.p2
                                            self.p2_points += 1  
                                        else:  
                                            # Rip  
                                            if self.p1.rip > self.p2.rip:  
                                                print(f"{self.p1.name} better rip.")  
                                                advantage = self.p1
                                                self.p1_points += 1  
                                            elif self.p2.rip > self.p1.rip:
                                                print(f"{self.p2.name} better rip.")
                                                advantage = self.p2
                                                self.p2_points += 1
                                            else: 
                                                if self.p1.ripw > self.p2.ripw:
                                                    print(f"{self.p1.name} better ripw.")
                                                    advantage = self.p1
                                                    self.p1_points += 1
                                                elif self.p2.ripw > self.p1.ripw:
                                                    print(f"{self.p2.name} better ripw.")
                                                    advantage = self.p2
                                                    self.p2_points += 1
                                                else:
                                                     # 10. Points
                                                    if self.p1.points > self.p2.points:
                                                        print(f"{self.p1.name} is in better form based on points.")
                                                        advantage = self.p1
                                                    elif self.p2.points > self.p1.points:
                                                        print(f"{self.p2.name} is in better form based on points.")
                                                        advantage = self.p2
                                                        self.p2_points += 1
                                                    else:
                                                        # 11. Final consideration: ace, serve speed, experience
                                                        if self.p1.ace > self.p2.ace and self.p1.serve_speed > self.p2.serve_speed:
                                                            print(f"{self.p1.name} wins by ace and serve speed.")
                                                            advantage = self.p1
                                                            self.p1_points += 1
                                                        elif self.p2.ace > self.p1.ace and self.p2.serve_speed > self.p1.serve_speed:
                                                            print(f"{self.p2.name} wins by ace and serve speed.")
                                                            advantage = self.p2
                                                            self.p2_points += 1
        print(f"{self.p1.name} points: {self.p1_points}")
        print(f"{self.p2.name} points: {self.p2_points}")
        if advantage:
            print(f"Final advantage: {advantage.name}")
        else:
            print("Players are evenly matched.")     


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

    if __name__ == "__main__":
        match = Game()
        match.run_match()