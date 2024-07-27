import logging
from typing import Optional

logger = logging.getLogger(__name__)

def setup_logger(log_level: str = 'WARN', log_file: Optional[str] = None) -> None:
    """Create a configured instance of logger."""
    fmt = '%(asctime)s [%(levelname)s] - %(message)s'
    date_fmt='%d/%m/%Y %H:%M:%S'
    formatter = logging.Formatter(fmt=fmt, datefmt=date_fmt)

    logger = logging.getLogger()
    logger.setLevel(log_level)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)
    logger.addHandler(stream_handler)

    if log_file is not None:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

def convert_to_float(frac_str: str) -> float:
    try:
        return float(frac_str)
    except ValueError:
        num, denom = frac_str.split('/')
        try:
            leading, num = num.split(' ')
            whole = float(leading)
        except ValueError:
            whole = 0
        frac = float(num) / float(denom)
        return whole - frac if whole < 0 else whole + frac

REPLACE_KEYWORD = ['@atk', '@hit' , '@damage', '@h', '@condition', '@dc', '@dice', '@sense', '@skill', '@spell']
ATK_REPLACE = {'mw': 'melee weapon', 'ms': 'melee spell', 'rw': 'range weapon', 'rs': "range spell"}
