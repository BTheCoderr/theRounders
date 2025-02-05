from datetime import datetime

def get_current_season(sport: str) -> str:
    """
    Get current season based on sport and date.
    
    Args:
        sport: String indicating sport ('NBA', 'NHL', 'NFL', 'NCAAB', 'NCAAF')
    
    Returns:
        String representing current season (e.g., '2023-24' or '2023')
    """
    current_date = datetime.now()
    current_year = current_date.year
    
    # Sports that use YYYY-YY format (spans two years)
    two_year_sports = ['NBA', 'NHL', 'NCAAB']
    
    # Sports that use YYYY format (single year)
    single_year_sports = ['NFL', 'NCAAF']
    
    if sport in two_year_sports:
        # For NBA/NHL/NCAAB: Season starts in previous year if before July
        if current_date.month < 7:
            return f"{current_year-1}-{str(current_year)[2:]}"
        else:
            return f"{current_year}-{str(current_year+1)[2:]}"
            
    elif sport in single_year_sports:
        # For NFL/NCAAF: Season is current year if after July, previous year if before
        if current_date.month < 7:
            return str(current_year - 1)
        else:
            return str(current_year)
            
    else:
        raise ValueError(f"Unsupported sport: {sport}") 