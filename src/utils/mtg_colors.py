"""
MTG Color mappings and gradient utilities for visualizations.
Maps archetype colors to actual MTG colors with gradient support.
"""

# Official MTG colors
MTG_COLORS = {
    "W": "#FFFBD5",  # White - Slightly off-white for visibility
    "U": "#0E68AB",  # Blue
    "B": "#1C1C1C",  # Black
    "R": "#F44336",  # Red
    "G": "#4CAF50",  # Green
    "C": "#9E9E9E",  # Colorless - Metallic gray
}

# Guild/Shard/Wedge color combinations
COLOR_COMBINATIONS = {
    # Guilds (2 colors)
    "Azorius": ["W", "U"],
    "Dimir": ["U", "B"],
    "Rakdos": ["B", "R"],
    "Gruul": ["R", "G"],
    "Selesnya": ["G", "W"],
    "Orzhov": ["W", "B"],
    "Izzet": ["U", "R"],
    "Golgari": ["B", "G"],
    "Boros": ["R", "W"],
    "Simic": ["G", "U"],
    
    # Shards (3 colors - allied)
    "Esper": ["W", "U", "B"],
    "Grixis": ["U", "B", "R"],
    "Jund": ["B", "R", "G"],
    "Naya": ["R", "G", "W"],
    "Bant": ["G", "W", "U"],
    
    # Wedges (3 colors - enemy)
    "Abzan": ["W", "B", "G"],
    "Jeskai": ["U", "R", "W"],
    "Sultai": ["B", "G", "U"],
    "Mardu": ["R", "W", "B"],
    "Temur": ["G", "U", "R"],
}


def get_archetype_colors(archetype_name: str) -> list:
    """
    Extract MTG colors from an archetype name.
    
    Args:
        archetype_name: Name like "Izzet Cauldron" or "Mono Red Aggro"
        
    Returns:
        List of color codes like ["U", "R"] for Izzet
    """
    # Check for mono colors first - be more specific
    mono_patterns = [
        ("Mono White", ["W"]),
        ("Mono Blue", ["U"]),
        ("Mono Black", ["B"]),
        ("Mono Red", ["R"]),
        ("Mono Green", ["G"]),
    ]
    
    for pattern, colors in mono_patterns:
        if pattern in archetype_name:
            return colors
    
    # Check for colorless
    if "Colorless" in archetype_name:
        return ["C"]
    
    # Check for known combinations - check these BEFORE generic patterns
    for combo_name, colors in COLOR_COMBINATIONS.items():
        if combo_name in archetype_name:
            return colors
    
    # Additional specific patterns that might not match guild names
    specific_patterns = {
        "Izzet Prowess": ["U", "R"],  # Explicitly handle Izzet Prowess
        "Gruul Aggro": ["R", "G"],    # Explicitly handle Gruul Aggro
        "Naya Yuna": ["R", "G", "W"], # Explicitly handle Naya Yuna
    }
    
    for pattern, colors in specific_patterns.items():
        if pattern in archetype_name:
            return colors
    
    # Check for 4c/5c
    if archetype_name.startswith("4c"):
        # Return WUBR (no green)
        return ["W", "U", "B", "R"]
    elif archetype_name.startswith("5c"):
        # All colors
        return ["W", "U", "B", "R", "G"]
    
    # Default fallback - try to guess from common patterns
    # This is a last resort
    return ["C"]  # Default to colorless if unknown


def create_plotly_gradient(colors: list) -> dict:
    """
    Create a Plotly gradient colorscale for given MTG colors.
    
    Args:
        colors: List of MTG color codes like ["U", "R"]
        
    Returns:
        Dict with Plotly gradient configuration
    """
    if len(colors) == 1:
        # Single color - return solid color
        return {
            "color": MTG_COLORS[colors[0]],
            "line": {"color": adjust_brightness(MTG_COLORS[colors[0]], 0.8), "width": 2}
        }
    
    # Multi-color gradient
    color_values = [MTG_COLORS[c] for c in colors]
    
    # Create gradient stops
    if len(colors) == 2:
        colorscale = [[0, color_values[0]], [1, color_values[1]]]
    elif len(colors) == 3:
        colorscale = [[0, color_values[0]], [0.5, color_values[1]], [1, color_values[2]]]
    elif len(colors) == 4:
        colorscale = [[0, color_values[0]], [0.33, color_values[1]], 
                      [0.66, color_values[2]], [1, color_values[3]]]
    else:  # 5 colors
        colorscale = [[0, color_values[0]], [0.25, color_values[1]], 
                      [0.5, color_values[2]], [0.75, color_values[3]], [1, color_values[4]]]
    
    return {
        "colorscale": colorscale,
        "showscale": False,
        "line": {"color": color_values[0], "width": 2}
    }


def get_pie_colors(archetypes: list) -> list:
    """
    Get colors for pie chart slices based on archetype names.
    
    Args:
        archetypes: List of archetype names
        
    Returns:
        List of color values for Plotly
    """
    colors = []
    for archetype in archetypes:
        arch_colors = get_archetype_colors(archetype)
        
        if len(arch_colors) == 1:
            # Single color
            colors.append(MTG_COLORS[arch_colors[0]])
        else:
            # For multi-color in pie chart, use the first color as dominant
            # with a slight blend of the second
            primary = MTG_COLORS[arch_colors[0]]
            secondary = MTG_COLORS[arch_colors[1]]
            blended = blend_colors(primary, secondary, 0.7)  # 70% primary, 30% secondary
            colors.append(blended)
    
    return colors


def blend_colors(color1: str, color2: str, ratio: float = 0.5) -> str:
    """
    Blend two hex colors together.
    
    Args:
        color1: First hex color
        color2: Second hex color  
        ratio: Blend ratio (0 = all color2, 1 = all color1)
        
    Returns:
        Blended hex color
    """
    # Convert hex to RGB
    c1_rgb = tuple(int(color1[i:i+2], 16) for i in (1, 3, 5))
    c2_rgb = tuple(int(color2[i:i+2], 16) for i in (1, 3, 5))
    
    # Blend
    blended = tuple(int(c1_rgb[i] * ratio + c2_rgb[i] * (1 - ratio)) for i in range(3))
    
    # Convert back to hex
    return f"#{blended[0]:02x}{blended[1]:02x}{blended[2]:02x}"


def adjust_brightness(color: str, factor: float) -> str:
    """
    Adjust brightness of a hex color.
    
    Args:
        color: Hex color string
        factor: Brightness factor (< 1 = darker, > 1 = lighter)
        
    Returns:
        Adjusted hex color
    """
    # Convert hex to RGB
    rgb = tuple(int(color[i:i+2], 16) for i in (1, 3, 5))
    
    # Adjust brightness
    adjusted = tuple(min(255, max(0, int(c * factor))) for c in rgb)
    
    # Convert back to hex
    return f"#{adjusted[0]:02x}{adjusted[1]:02x}{adjusted[2]:02x}"


def create_bar_gradient_marker(archetype: str) -> dict:
    """
    Create a gradient marker configuration for bar charts.
    
    Args:
        archetype: Archetype name
        
    Returns:
        Plotly marker configuration with gradient
    """
    colors = get_archetype_colors(archetype)
    
    if len(colors) == 1:
        # Solid color with slight gradient effect
        base_color = MTG_COLORS[colors[0]]
        return {
            "color": base_color,
            "line": {"color": adjust_brightness(base_color, 0.8), "width": 1}
        }
    
    # For gradients in bar charts, we'll use a pattern approach
    # since Plotly bars don't support true gradients easily
    # We'll use the primary color with a pattern effect
    primary = MTG_COLORS[colors[0]]
    secondary = MTG_COLORS[colors[1]] if len(colors) > 1 else primary
    
    # Create a blended color for multi-color archetypes
    blended = blend_colors(primary, secondary, 0.6)
    
    return {
        "color": blended,
        "line": {"color": primary, "width": 2},
        "opacity": 0.9
    }