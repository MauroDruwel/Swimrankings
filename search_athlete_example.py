"""
Example usage of the athlete search functionality.

This script demonstrates how to search for athletes by name
and then retrieve their information.
"""

from swimrankingsscraper import SwimrankingsScraper
from swimrankingsscraper.athlete import Athlete


def main():
    """
    Example usage of the athlete search functionality.
    """
    # Create scraper instance
    scraper = SwimrankingsScraper()
    
    # Search for athletes by name
    search_name = "Mauro Druwel"
    print(f"Searching for athletes with name: {search_name}")
    
    # Use the static method to search for athletes
    search_results = Athlete.search_athletes(search_name, scraper.sessionManager)
    
    if not search_results:
        print("No athletes found with that name.")
        return
    
    print(f"Found {len(search_results)} athlete(s):")
    
    # Display search results
    for i, athlete_data in enumerate(search_results):
        print(f"\n--- Result {i+1} ---")
        print(f"Name: {athlete_data['name']}")
        print(f"Athlete ID: {athlete_data['athlete_id']}")
        print(f"Birth Year: {athlete_data['birth_year']}")
        print(f"Gender: {athlete_data['gender']}")
        print(f"Country: {athlete_data['country_code']}")
        print(f"Club: {athlete_data['club_name']}")
        
        # Create an Athlete instance for the first result
        if i == 0:
            print(f"\n--- Getting detailed information for {athlete_data['name']} ---")
            athlete = scraper.get_athlete(str(athlete_data['athlete_id']))
            
            # Get personal bests
            personal_bests = athlete.list_personal_bests(season='2024')
            print(f"Personal bests for 2024: {len(personal_bests)} events")
            
            # Display first few personal bests
            for pb in personal_bests[:5]:  # Show first 5 events
                print(f"  {pb['event_name']} ({pb['course_length']}): {pb['time']:.2f}s - {pb['FINA Points']} points")
            
            # Get athlete details
            details = athlete.list_personal_details()
            if details:
                print("\nDetailed information:")
                for detail in details:
                    key = list(detail.keys())[0]
                    value = list(detail.values())[0]
                    print(f"  {key}: {value}")
            
            # Get meets
            meets = athlete.list_meets()
            print(f"\nParticipated in {len(meets)} meets")
            for meet in meets[:3]:  # Show first 3 meets
                print(f"  {meet['meet_date']}: {meet['meet_name']} in {meet['meet_city']}")


def search_with_filters_example():
    """
    Example showing how to search with gender and club filters.
    """
    scraper = SwimrankingsScraper()
    
    print("\n" + "="*50)
    print("EXAMPLE WITH FILTERS")
    print("="*50)
    
    # Search with gender filter (1 = male, 2 = female, -1 = all)
    search_name = "Druwel"
    print(f"Searching for male athletes with name: {search_name}")
    
    male_results = Athlete.search_athletes(search_name, scraper.sessionManager, gender=1)
    
    print(f"Found {len(male_results)} male athlete(s):")
    for athlete_data in male_results:
        print(f"  {athlete_data['name']} ({athlete_data['birth_year']}) - {athlete_data['club_name']}")


if __name__ == '__main__':
    main()
    search_with_filters_example()
