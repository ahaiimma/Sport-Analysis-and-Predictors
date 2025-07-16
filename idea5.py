class PlayerEvaluator:
    def __init__(self, player1, player2):
        self.p1 = player1
        self.p2 = player2

    def evaluate(self):
        advantage = None

        # 1. Experience (surface experience)
        experience_levels = ['Clay', 'Grass', 'Carpet', 'Hard']
        p1_exp = getattr(self.p1, 'experience_surface', None)
        p2_exp = getattr(self.p2, 'experience_surface', None)

        p1_has_exp = p1_exp in experience_levels
        p2_has_exp = p2_exp in experience_levels

        if p1_has_exp and not p2_has_exp:
            print(f"{self.p1.name} has surface experience advantage.")
            advantage = self.p1
        else:
            if p2_has_exp and not p1_has_exp:
                print(f"{self.p2.name} has surface experience advantage.")
                advantage = self.p2
            else:
                # 2. Hand dominance
                if self.p1.hand == 'Right' and self.p2.hand == 'Left':
                    print(f"{self.p1.name} has hand advantage.")
                    advantage = self.p1
                else:
                    if self.p2.hand == 'Right' and self.p1.hand == 'Left':
                        print(f"{self.p2.name} has hand advantage.")
                        advantage = self.p2
                    else:
                        # 3. Younger advantage
                        if self.p1.age < self.p2.age:
                            print(f"{self.p1.name} is younger; advantage.")
                            advantage = self.p1
                        else:
                            if self.p2.age < self.p1.age:
                                print(f"{self.p2.name} is younger; advantage.")
                                advantage = self.p2
                            else:
                                # check if in 20s
                                p1_in_20s = 20 <= self.p1.age < 30
                                p2_in_20s = 20 <= self.p2.age < 30
                                if p1_in_20s and not p2_in_20s:
                                    print(f"{self.p1.name} in 20s; advantage.")
                                    advantage = self.p1
                                else:
                                    if p2_in_20s and not p1_in_20s:
                                        print(f"{self.p2.name} in 20s; advantage.")
                                        advantage = self.p2
                                    else:
                                        # 4. First Serve
                                        if self.p1.first_serve > self.p2.first_serve:
                                            print(f"{self.p1.name} has better first serve.")
                                            advantage = self.p1
                                        else:
                                            if self.p2.first_serve > self.p1.first_serve:
                                                print(f"{self.p2.name} has better first serve.")
                                                advantage = self.p2
                                            else:
                                                # 5. Second Serve if tie
                                                if self.p1.second_serve > self.p2.second_serve:
                                                    print(f"{self.p1.name} has better second serve.")
                                                    advantage = self.p1
                                                else:
                                                    if self.p2.second_serve > self.p1.second_serve:
                                                        print(f"{self.p2.name} has better second serve.")
                                                        advantage = self.p2
                                                    else:
                                                        # 6. Serve speed
                                                        if self.p1.serve_speed > self.p2.serve_speed:
                                                            print(f"{self.p1.name} has better serve speed.")
                                                            advantage = self.p1
                                                        else:
                                                            if self.p2.serve_speed > self.p1.serve_speed:
                                                                print(f"{self.p2.name} has better serve speed.")
                                                                advantage = self.p2
                                                            else:
                                                                # 7. Rally stats
                                                                if self.p1.rally_stats > self.p2.rally_stats:
                                                                    print(f"{self.p1.name} better rally stats.")
                                                                    advantage = self.p1
                                                                else:
                                                                    if self.p2.rally_stats > self.p1.rally_stats:
                                                                        print(f"{self.p2.name} better rally stats.")
                                                                        advantage = self.p2
                                                                    else:
                                                                        # 8. Rip
                                                                        if self.p1.rip > self.p2.rip:
                                                                            print(f"{self.p1.name} better rip.")
                                                                            advantage = self.p1
                                                                        else:
                                                                            if self.p2.rip > self.p1.rip:
                                                                                print(f"{self.p2.name} better rip.")
                                                                                advantage = self.p2
                                                                            else:
                                                                                # 9. Ripw
                                                                                if self.p1.ripw > self.p2.ripw:
                                                                                    print(f"{self.p1.name} better ripw.")
                                                                                    advantage = self.p1
                                                                                else:
                                                                                    if self.p2.ripw > self.p1.ripw:
                                                                                        print(f"{self.p2.name} better ripw.")
                                                                                        advantage = self.p2
                                                                                    else:
                                                                                        # 10. Points
                                                                                        if self.p1.points > self.p2.points:
                                                                                            print(f"{self.p1.name} is in better form based on points.")
                                                                                            advantage = self.p1
                                                                                        elif self.p2.points > self.p1.points:
                                                                                            print(f"{self.p2.name} is in better form based on points.")
                                                                                            advantage = self.p2
                                                                                        else:
                                                                                            # 11. Final consideration: ace, serve speed, experience
                                                                                            if self.p1.ace > self.p2.ace and self.p1.serve_speed > self.p2.serve_speed:
                                                                                                print(f"{self.p1.name} wins by ace and serve speed.")
                                                                                                advantage = self.p1
                                                                                            elif self.p2.ace > self.p1.ace and self.p2.serve_speed > self.p1.serve_speed:
                                                                                                print(f"{self.p2.name} wins by ace and serve speed.")
                                                                                                advantage = self.p2
        if advantage:
            print(f"Final advantage: {advantage.name}")
        else:
            print("Players are evenly matched.")