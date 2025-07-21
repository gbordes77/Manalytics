"""
Date Handler - Workaround #3 (CRITIQUE)

Reproduit fidèlement la gestion des dates nullable DateTime de C# avec fuseaux horaires
pour éliminer les erreurs de tri temporel et de classification par meta.

Impact: Élimine les erreurs de tri temporel et de classification par meta
"""

import logging
import re
from datetime import date, datetime, timezone
from typing import Optional, Union

import dateutil.parser

logger = logging.getLogger(__name__)


class DateHandler:
    """
    Reproduction fidèle de la gestion des dates C# DateTime nullable

    Le code C# original utilise:
    public DateTime? Date { get; set; }
    if (deck.Date == null) deck.Date = tournament.Information.Date;

    Cette classe reproduit exactement ce comportement en Python.
    """

    @staticmethod
    def parse_tournament_date(
        date_str: Union[str, datetime, None]
    ) -> Optional[datetime]:
        """
        Parse les dates avec la même logique que C# DateTime.Parse

        Reproduit la logique C#:
        DateTime.Parse(eventDate, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal).ToUniversalTime()

        Args:
            date_str: Chaîne de date, objet datetime, ou None

        Returns:
            Objet datetime ou None si parsing impossible
        """
        if date_str is None:
            return None

        # Si c'est déjà un datetime, le retourner tel quel
        if isinstance(date_str, datetime):
            return date_str

        # Si c'est un objet date, le convertir en datetime
        if isinstance(date_str, date):
            return datetime.combine(date_str, datetime.min.time())

        # Si ce n'est pas une chaîne, essayer de la convertir
        if not isinstance(date_str, str):
            date_str = str(date_str)

        if not date_str or date_str.strip() == "":
            return None

        try:
            # Gestion des formats ISO avec timezone (comme C#)
            if "T" in date_str:
                # Format ISO avec timezone
                if date_str.endswith("Z"):
                    # UTC timezone
                    date_str = date_str.replace("Z", "+00:00")

                # Parse avec timezone
                parsed_date = datetime.fromisoformat(date_str)

                # Conversion en UTC (comme ToUniversalTime() en C#)
                if parsed_date.tzinfo is None:
                    # Assume UTC si pas de timezone (comme AssumeUniversal en C#)
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)
                else:
                    # Convertir en UTC
                    parsed_date = parsed_date.astimezone(timezone.utc)

                return parsed_date
            else:
                # Format date simple - utiliser dateutil pour plus de flexibilité
                parsed_date = dateutil.parser.parse(date_str)

                # Si pas de timezone, assumer UTC (comme AssumeUniversal en C#)
                if parsed_date.tzinfo is None:
                    parsed_date = parsed_date.replace(tzinfo=timezone.utc)

                return parsed_date

        except Exception as e:
            logger.warning(f"Could not parse date '{date_str}': {e}")
            return None

    @staticmethod
    def extract_date_from_filename(filename: str) -> Optional[datetime]:
        """
        Extrait la date depuis un nom de fichier

        Reproduit la logique C#:
        private static DateTime ExtractDateFromName(string eventName)
        {
            string[] eventNameSegments = eventName.Split("-").Where(e => e.Length > 1).ToArray();
            string eventDate = String.Join("-", eventNameSegments.Skip(eventNameSegments.Length - 3).ToArray());
            return DateTime.Parse(eventDate, CultureInfo.InvariantCulture, DateTimeStyles.AssumeUniversal).ToUniversalTime();
        }

        Args:
            filename: Nom du fichier

        Returns:
            Date extraite ou None si extraction impossible
        """
        try:
            # Recherche de patterns de date dans le nom de fichier
            # Format YYYY-MM-DD
            date_pattern = r"(\d{4})-(\d{1,2})-(\d{1,2})"
            match = re.search(date_pattern, filename)

            if match:
                year, month, day = match.groups()
                date_str = f"{year}-{month.zfill(2)}-{day.zfill(2)}"
                return DateHandler.parse_tournament_date(date_str)

            # Reproduction de la logique C# originale
            segments = filename.split("-")
            segments = [s for s in segments if len(s) > 1]  # Where(e => e.Length > 1)

            if len(segments) >= 3:
                # Skip(segments.Length - 3) - prendre les 3 derniers segments
                date_segments = segments[-3:]
                event_date = "-".join(date_segments)
                return DateHandler.parse_tournament_date(event_date)

            return None

        except Exception as e:
            logger.warning(f"Could not extract date from filename '{filename}': {e}")
            return None

    @staticmethod
    def ensure_deck_date(
        deck_date: Optional[datetime], tournament_date: Optional[datetime]
    ) -> Optional[datetime]:
        """
        Reproduit la logique C# : if (deck.Date == null) deck.Date = tournament.Information.Date;

        Args:
            deck_date: Date du deck (peut être None)
            tournament_date: Date du tournoi (peut être None)

        Returns:
            Date du deck ou date du tournoi si deck_date est None
        """
        return deck_date if deck_date is not None else tournament_date

    @staticmethod
    def is_date_in_range(
        check_date: Optional[datetime], start_date: datetime, end_date: datetime
    ) -> bool:
        """
        Vérifie si une date est dans une plage donnée

        Reproduit la logique C#:
        if (not (start_date <= tournament_date <= end_date)) return [];

        Args:
            check_date: Date à vérifier
            start_date: Date de début
            end_date: Date de fin

        Returns:
            True si la date est dans la plage, False sinon
        """
        if check_date is None:
            return False

        # Conversion en date simple pour comparaison (ignore l'heure)
        check_date_only = (
            check_date.date() if isinstance(check_date, datetime) else check_date
        )
        start_date_only = (
            start_date.date() if isinstance(start_date, datetime) else start_date
        )
        end_date_only = end_date.date() if isinstance(end_date, datetime) else end_date

        return start_date_only <= check_date_only <= end_date_only

    @staticmethod
    def get_meta_week_reference_date(meta_start: datetime) -> datetime:
        """
        Reproduit la logique C# pour calculer la date de référence des semaines meta

        Reproduit la logique C#:
        // Note: I'm considering the meta weeks as starting on monday
        static DateTime GetMetaWeekReferenceDate(DateTime metaStart)
        {
            switch (metaStart.DayOfWeek)
            {
                case DayOfWeek.Sunday: return metaStart.AddDays(-6);
                case DayOfWeek.Monday: return metaStart;
                case DayOfWeek.Tuesday: return metaStart.AddDays(-1);
                // ...
            }
        }

        Args:
            meta_start: Date de début du meta

        Returns:
            Date de référence pour les semaines (lundi)
        """
        from datetime import timedelta

        # Mapping des jours de la semaine (Python: 0=lundi, 6=dimanche)
        # C#: Sunday=0, Monday=1, ..., Saturday=6
        weekday = meta_start.weekday()  # 0=lundi, 6=dimanche

        if weekday == 6:  # Dimanche
            return meta_start - timedelta(days=6)
        elif weekday == 0:  # Lundi
            return meta_start
        elif weekday == 1:  # Mardi
            return meta_start - timedelta(days=1)
        elif weekday == 2:  # Mercredi
            return meta_start - timedelta(days=2)
        elif weekday == 3:  # Jeudi
            return meta_start - timedelta(days=3)
        elif weekday == 4:  # Vendredi
            return meta_start - timedelta(days=4)
        elif weekday == 5:  # Samedi
            return meta_start - timedelta(days=5)
        else:
            raise ValueError("Invalid weekday for meta start date")

    @staticmethod
    def calculate_meta_week(tournament_date: datetime, meta_start: datetime) -> int:
        """
        Calcule le numéro de semaine meta

        Reproduit la logique C#:
        int weekID = ((int)Math.Floor((tournament.Decks.First().Date.Value - metaWeekReferenceDate).Days / 7.0)) + 1;

        Args:
            tournament_date: Date du tournoi
            meta_start: Date de début du meta

        Returns:
            Numéro de semaine meta (1-based)
        """
        meta_week_reference = DateHandler.get_meta_week_reference_date(meta_start)

        # Calcul des jours de différence
        days_diff = (tournament_date - meta_week_reference).days

        # Calcul de la semaine (1-based comme en C#)
        week_id = int(days_diff / 7.0) + 1

        return max(1, week_id)  # Au minimum semaine 1

    @staticmethod
    def format_date_for_output(date_obj: Optional[datetime]) -> str:
        """
        Formate une date pour la sortie (compatible avec le format C#)

        Args:
            date_obj: Objet datetime ou None

        Returns:
            Date formatée en chaîne YYYY-MM-DD ou "Unknown"
        """
        if date_obj is None:
            return "Unknown"

        if isinstance(date_obj, datetime):
            return date_obj.strftime("%Y-%m-%d")
        elif isinstance(date_obj, date):
            return date_obj.strftime("%Y-%m-%d")
        else:
            return str(date_obj)

    @staticmethod
    def parse_date_range(start_str: str, end_str: str) -> tuple[datetime, datetime]:
        """
        Parse une plage de dates

        Args:
            start_str: Date de début (chaîne)
            end_str: Date de fin (chaîne)

        Returns:
            Tuple (date_début, date_fin)

        Raises:
            ValueError: Si les dates ne peuvent pas être parsées
        """
        start_date = DateHandler.parse_tournament_date(start_str)
        end_date = DateHandler.parse_tournament_date(end_str)

        if start_date is None:
            raise ValueError(f"Could not parse start date: {start_str}")
        if end_date is None:
            raise ValueError(f"Could not parse end date: {end_str}")

        return start_date, end_date
