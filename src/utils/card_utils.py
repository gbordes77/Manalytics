import re
import unidecode

def normalize_card_name(name: str) -> str:
    """
    Normalizes a card name to handle inconsistencies like split cards, accents, etc.
    """
    if not isinstance(name, str):
        return ""
        
    if " // " in name:
        name = name.split(" // ")[0]
    
    name = unidecode.unidecode(name).lower()
    name = re.sub(r"[.,:;!?']", "", name)
    
    return name.strip()