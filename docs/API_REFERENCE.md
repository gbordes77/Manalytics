# 📚 API Reference Manalytics

## Core Modules

### `run_full_pipeline`

```python
def main(args: argparse.Namespace) -> None:
    """
    Orchestrate complete pipeline execution.
    
    Args:
        args: CLI arguments with format, start_date, end_date
        
    Raises:
        ScrapingError: If data fetching fails
        ClassificationError: If archetype detection fails
        VisualizationError: If chart generation fails
    """
```

### `scraper.BaseScraper`

```python
class BaseScraper(ABC):
    """Abstract base class for all scrapers."""
    
    @abstractmethod
    def fetch_tournaments(
        self,
        format: str,
        start_date: datetime,
        end_date: datetime
    ) -> List[Tournament]:
        """Fetch tournaments for given parameters."""
        pass
    
    def validate_response(self, response: Response) -> bool:
        """Validate HTTP response."""
        return response.status_code == 200
```

### `classifier.Classifier`

```python
class Classifier:
    """Classify decks into archetypes using rule engine."""
    
    def __init__(self, rules_path: str = "archetype_rules.json"):
        """Initialize with rules file."""
        self.rules = self._load_rules(rules_path)
    
    def classify(self, deck: List[str]) -> str:
        """
        Classify a deck based on card list.
        
        Args:
            deck: List of card names
            
        Returns:
            Archetype name or "Other"
        """
```

### `analyzer.StatsCalculator`

```python
class StatsCalculator:
    """Calculate statistical metrics for metagame."""
    
    def calculate_winrate(
        self,
        matches: List[Match],
        archetype: str
    ) -> WinrateResult:
        """Calculate winrate with confidence interval."""
    
    def generate_matchup_matrix(
        self,
        matches: List[Match]
    ) -> pd.DataFrame:
        """Generate archetype vs archetype winrate matrix."""
    
    def classify_tiers(
        self,
        archetypes: List[ArchetypeStats],
        method: str = "kmeans"
    ) -> Dict[str, int]:
        """Classify archetypes into tiers (1-3)."""
```

### `visualizer.ChartGenerator`

```python
class ChartGenerator:
    """Generate Plotly charts for metagame data."""
    
    def create_metagame_pie(
        self,
        archetype_shares: Dict[str, float]
    ) -> go.Figure:
        """Create pie chart of metagame distribution."""
    
    def create_matchup_heatmap(
        self,
        matchup_matrix: pd.DataFrame
    ) -> go.Figure:
        """Create heatmap of matchup winrates."""
    
    def create_evolution_timeline(
        self,
        daily_shares: pd.DataFrame
    ) -> go.Figure:
        """Create line chart of archetype evolution."""
```

## Data Models

### Tournament

```python
@dataclass
class Tournament:
    id: str
    date: datetime
    format: str
    source: str  # "MTGO", "Melee", etc.
    decks: List[Deck]
```

### Deck

```python
@dataclass
class Deck:
    id: str
    player: str
    archetype: Optional[str]  # Set by classifier
    mainboard: List[Card]
    sideboard: List[Card]
    record: Record
```

### Match

```python
@dataclass
class Match:
    deck_id: str
    opponent_archetype: str
    won: bool
    game_wins: int
    game_losses: int
```

## Configuration

### Settings Schema

```python
# config/settings.py
SETTINGS = {
    "scraping": {
        "timeout": 30,
        "max_retries": 3,
        "delay_between_requests": 1.0,
        "user_agent": "Manalytics/1.0"
    },
    "classification": {
        "min_cards_for_archetype": 10,
        "confidence_threshold": 0.8
    },
    "analysis": {
        "min_matches_for_stats": 20,
        "confidence_level": 0.95
    },
    "visualization": {
        "theme": "plotly_dark",
        "figure_height": 600,
        "figure_width": 1000
    }
}
```

## Error Handling

### Custom Exceptions

```python
class ManalyticsError(Exception):
    """Base exception for all Manalytics errors."""

class ScrapingError(ManalyticsError):
    """Raised when data fetching fails."""

class ClassificationError(ManalyticsError):
    """Raised when deck classification fails."""

class AnalysisError(ManalyticsError):
    """Raised when statistical analysis fails."""

class VisualizationError(ManalyticsError):
    """Raised when chart generation fails."""
```

### Error Codes

| Code | Description | Recovery |
|------|-------------|----------|
| E001 | Network timeout | Retry with backoff |
| E002 | Invalid date format | Check input format |
| E003 | No data found | Try different dates |
| E004 | Classification failed | Check rules file |
| E005 | Insufficient data | Expand date range |

## Utils

### `cache.LRUCache`

```python
class LRUCache:
    """Least Recently Used cache implementation."""
    
    def __init__(self, capacity: int = 1000):
        """Initialize with max capacity."""
    
    def get(self, key: str) -> Optional[Any]:
        """Retrieve from cache."""
    
    def put(self, key: str, value: Any) -> None:
        """Store in cache."""
```

### `retry.exponential_backoff`

```python
@exponential_backoff(max_retries=3, base_delay=1.0)
def fetch_with_retry(url: str) -> Response:
    """Fetch URL with exponential backoff retry."""
``` 