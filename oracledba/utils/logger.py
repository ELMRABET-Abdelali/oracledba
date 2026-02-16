"""
Logger utility with automatic fallback
"""

import logging
import os
from pathlib import Path
from datetime import datetime

def setup_logger(name='oracledba', log_dir='/var/log/oracledba'):
    """
    Setup logger with automatic fallback to user directory
    
    Tries in order:
    1. /var/log/oracledba (system-wide)
    2. ~/.local/share/oracledba/logs (user-specific)
    3. Console only (if all fails)
    """
    handlers = [logging.StreamHandler()]  # Always have console output
    
    # Try multiple log locations
    log_locations = [
        Path(log_dir),
        Path.home() / '.local' / 'share' / 'oracledba' / 'logs',
        Path.home() / 'oracledba_logs'
    ]
    
    log_file = None
    for log_path in log_locations:
        try:
            log_path.mkdir(parents=True, exist_ok=True)
            log_file = log_path / f"oracledba_{datetime.now().strftime('%Y%m%d')}.log"
            
            # Test write access
            with open(log_file, 'a') as f:
                pass
            
            # Success! Add file handler
            handlers.append(logging.FileHandler(log_file))
            break
            
        except (PermissionError, OSError):
            # Try next location
            continue
    
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers,
        force=True  # Override any existing config
    )
    
    logger = logging.getLogger(name)
    if log_file:
        logger.info(f"Logging to: {log_file}")
    else:
        logger.warning("Could not create log file, logging to console only")
    
    return logger


logger = setup_logger()
