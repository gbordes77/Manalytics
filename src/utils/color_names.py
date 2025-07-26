"""
Color combination names for Magic: The Gathering.
Maps color codes to their full names (guilds, shards, wedges, etc.)
"""

# Single colors
MONO_COLORS = {
    "W": "Mono White",
    "U": "Mono Blue",
    "B": "Mono Black",
    "R": "Mono Red",
    "G": "Mono Green",
    "C": "Colorless"
}

# Two-color combinations (Guilds)
GUILDS = {
    "WU": "Azorius",
    "UW": "Azorius",
    "UB": "Dimir",
    "BU": "Dimir",
    "BR": "Rakdos",
    "RB": "Rakdos",
    "RG": "Gruul",
    "GR": "Gruul",
    "GW": "Selesnya",
    "WG": "Selesnya",
    "WB": "Orzhov",
    "BW": "Orzhov",
    "UR": "Izzet",
    "RU": "Izzet",
    "BG": "Golgari",
    "GB": "Golgari",
    "RW": "Boros",
    "WR": "Boros",
    "GU": "Simic",
    "UG": "Simic"
}

# Three-color combinations (Shards and Wedges)
THREE_COLOR = {
    # Shards (allied colors)
    "WUB": "Esper",
    "UBR": "Grixis",
    "BRG": "Jund",
    "RGW": "Naya",
    "GWU": "Bant",
    # Wedges (enemy colors)
    "WBG": "Abzan",
    "URW": "Jeskai",
    "BGU": "Sultai",
    "RWB": "Mardu",
    "GUR": "Temur",
    # Alternative orderings (WUBRG order)
    "WRG": "Naya",
    "WUR": "Jeskai",
    "WUG": "Bant",
    "UBG": "Sultai",
    "UWB": "Esper",
    "RUB": "Grixis",
    "RGB": "Jund",
    "WBR": "Mardu",
    "GBW": "Abzan",
    "RGU": "Temur",
    "URG": "Temur"
}

# Four and five color
MULTI_COLOR = {
    "WUBR": "4c",
    "WURG": "4c",
    "WBRG": "4c",
    "UBRG": "4c",
    "WUBG": "4c",
    "WUBRG": "5c"
}


def get_color_name(color_code: str) -> str:
    """
    Get the full name for a color combination code.
    
    Args:
        color_code: Color code like "UR", "WUB", etc.
        
    Returns:
        Full name like "Izzet", "Esper", etc.
    """
    if not color_code:
        return "Colorless"
    
    # Check each mapping in order
    if color_code in MONO_COLORS:
        return MONO_COLORS[color_code]
    elif color_code in GUILDS:
        return GUILDS[color_code]
    elif color_code in THREE_COLOR:
        return THREE_COLOR[color_code]
    elif color_code in MULTI_COLOR:
        return MULTI_COLOR[color_code]
    elif len(color_code) == 4:
        return "4c"
    elif len(color_code) == 5:
        return "5c"
    else:
        # Return as-is if no mapping found
        return color_code


def format_archetype_name(archetype: str, color_code: str = None) -> str:
    """
    Format an archetype name with proper color names.
    
    Args:
        archetype: Archetype name like "UR Prowess"
        color_code: Optional color code if not in archetype name
        
    Returns:
        Formatted name like "Izzet Prowess"
    """
    if not archetype:
        return "Unknown"
    
    # Fix duplicate names in parentheses pattern
    # e.g. "Mono White Caretaker (Mono White Caretaker)" -> "Mono White Caretaker"
    # Also handle "Orzhov Caretaker (Mono White Caretaker)" -> keep as is but clean display
    import re
    pattern = r'^(.+?)\s*\(\1\)$'
    match = re.match(pattern, archetype)
    if match:
        archetype = match.group(1)
    
    # For now, remove all parenthetical content for cleaner display
    # This handles cases like "Orzhov Caretaker (Mono White Caretaker)"
    archetype = re.sub(r'\s*\([^)]+\)', '', archetype)
    
    # Check all possible color codes in the name
    all_color_codes = list(MONO_COLORS.keys()) + list(GUILDS.keys()) + list(THREE_COLOR.keys()) + list(MULTI_COLOR.keys())
    
    # If archetype already contains color code at the beginning
    parts = archetype.split()
    if len(parts) > 1:
        # Check if first part is a color code
        if parts[0] in all_color_codes:
            color_name = get_color_name(parts[0])
            remaining = ' '.join(parts[1:])
            # Avoid double color names (e.g., "WRG WRG Yuna" -> "Naya Yuna")
            if not remaining.startswith(parts[0]):
                return f"{color_name} {remaining}"
            else:
                # Skip redundant color code
                remaining_parts = remaining.split()
                if len(remaining_parts) > 1 and remaining_parts[0] == parts[0]:
                    return f"{color_name} {' '.join(remaining_parts[1:])}"
                return f"{color_name} {remaining}"
    
    # If color code provided separately
    if color_code:
        color_name = get_color_name(color_code)
        # Check if archetype already starts with the color code to avoid duplication
        if not archetype.startswith(color_code + " "):
            return f"{color_name} {archetype}"
        else:
            # Remove the color code from archetype name
            return f"{color_name} {archetype[len(color_code)+1:]}"
    
    return archetype