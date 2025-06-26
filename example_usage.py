"""
Example usage of the SwimrankingsScraper package.

This script demonstrates how to use the refactored SwimrankingsScraper 
to retrieve athlete information and personal bests.
"""

from swimrankingsscraper import SwimrankingsScraper


def main():
    """
    Example usage of the SwimrankingsScraper.
    """
    # Create scraper instance
    scraper = SwimrankingsScraper()
    
    # Get a club and list its athletes
    print("Getting club information...")
    club = scraper.get_club('65929')
    swimmers = club.list_athletes()
    
    print(f"Found {len(swimmers)} swimmers in the club")
    
    # Get athlete information for the first few swimmers
    for i, swimmer in enumerate(swimmers[:3]):  # Limit to first 3 for demo
        print(f"\n--- Swimmer {i+1}: {swimmer['athlete_name']} ---")
        
        # Get athlete instance
        athlete = scraper.get_athlete(swimmer['athlete_id'])
        
        # Get personal bests
        personal_bests = athlete.list_personal_bests(season='2024')
        print(f"Personal bests for 2024: {len(personal_bests)} events")
        
        # Display some personal bests
        for pb in personal_bests[:5]:  # Show first 5 events
            print(f"  {pb['event_name']} ({pb['course_length']}): {pb['time']:.2f}s - {pb['FINA Points']} points")
        
        # Get athlete details
        details = athlete.list_personal_details()
        if details:
            for detail in details:
                print(f"  {list(detail.keys())[0]}: {list(detail.values())[0]}")


if __name__ == '__main__':
    main()
