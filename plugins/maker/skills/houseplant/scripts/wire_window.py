import datetime

def get_inspection_cadence(species: str, applied_date_str: str, season: str = "active") -> dict:
    """
    Returns the recommended wire inspection cadence and first check date
    based on species growth rate and current season.
    
    Args:
        species: e.g., 'Ficus benjamina', 'Jade', 'Pine'
        applied_date_str: 'YYYY-MM-DD'
        season: 'active' or 'dormant'
    """
    applied_date = datetime.datetime.strptime(applied_date_str, "%Y-%m-%d").date()
    
    # Simple growth rate dictionary
    # In a real scenario, this would be backed by a larger horticultural database.
    growth_rates = {
        'ficus': 'fast',
        'ficus benjamina': 'fast',
        'jade': 'medium',
        'pine': 'slow',
        'juniper': 'slow',
        'maple': 'medium'
    }
    
    species_lower = species.lower()
    rate = 'medium' # default
    for key in growth_rates:
        if key in species_lower:
            rate = growth_rates[key]
            break
            
    if season == "dormant":
        cadence_days = 60
        cadence_desc = "8 weeks"
    else:
        if rate == "fast":
            cadence_days = 14
            cadence_desc = "2 weeks"
        elif rate == "medium":
            cadence_days = 28
            cadence_desc = "4 weeks"
        else: # slow
            cadence_days = 42
            cadence_desc = "6 weeks"
            
    first_check = applied_date + datetime.timedelta(days=cadence_days)
    
    return {
        "species": species,
        "applied_date": applied_date_str,
        "growth_rate": rate,
        "season": season,
        "cadence_days": cadence_days,
        "cadence_description": cadence_desc,
        "first_check_date": first_check.strftime("%Y-%m-%d")
    }

if __name__ == "__main__":
    # Example usage
    today = datetime.date.today().strftime("%Y-%m-%d")
    res = get_inspection_cadence("Ficus benjamina", today, "active")
    print(f"Species: {res['species']} | Rate: {res['growth_rate']}")
    print(f"Applied: {res['applied_date']} | First check: {res['first_check_date']} ({res['cadence_description']})")
