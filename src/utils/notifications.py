"""
Notification utilities for pipeline completion
"""

import os
import logging
import subprocess
from pathlib import Path

logger = logging.getLogger(__name__)

class NotificationManager:
    """Handle notifications for pipeline events."""
    
    def __init__(self):
        self.sound_file = Path.home() / "finish.mp3"
        
    def play_sound(self):
        """Play notification sound if available."""
        if self.sound_file.exists():
            try:
                # macOS
                subprocess.run(["afplay", str(self.sound_file)], check=True)
                logger.debug("Played notification sound")
            except:
                try:
                    # Linux
                    subprocess.run(["mpg123", "-q", str(self.sound_file)], check=True)
                except:
                    logger.debug("Could not play notification sound")
        
    def notify_completion(self, message: str):
        """Send completion notification."""
        # Play sound
        self.play_sound()
        
        # macOS notification
        try:
            subprocess.run([
                "osascript", "-e",
                f'display notification "{message}" with title "Manalytics"'
            ])
        except:
            pass
            
        logger.info(f"✅ {message}")