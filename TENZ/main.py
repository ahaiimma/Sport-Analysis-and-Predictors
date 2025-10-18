from player import create_players, save_players, load_players
from evaluator import PlayerEvaluator

def main():
    """Main function to run the complete system."""
    print("Tennis Player Comparison System")
    print("===============================")
    
    # Check if user wants to load saved data
    load_option = input("Load saved player data? (y/n): ").strip().lower()
    
    # Initialize p1 and p2 to None to handle the case where no data is loaded
    p1, p2 = None, None
    if load_option == 'y':
        p1, p2 = load_players()
    
    # If no saved data or user doesn't want to load, create new players
    if p1 is None or p2 is None:
        p1, p2 = create_players()
        save_option = input("Save player data for future use? (y/n): ").strip().lower()
        if save_option == 'y':
            save_players(p1, p2)
    
    p1.display_stats()
    p2.display_stats()
    
    match_location = input("\nEnter the match location (city/country/surface): ")
    evaluator = PlayerEvaluator(p1, p2, match_location)
    evaluator.evaluate_match()
    evaluator.get_betting_suggestions()

if __name__ == "__main__":
    main()
