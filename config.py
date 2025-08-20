"""
Configuration settings for the Property Analysis Application
"""

import os
import pandas as pd
import numpy as np
from pathlib import Path

# Project paths
PROJECT_ROOT = Path(__file__).parent
DATA_DIR = PROJECT_ROOT / "data"
SRC_DIR = PROJECT_ROOT / "src"
LOGS_DIR = PROJECT_ROOT / "logs"

# Data files
CURRENT_PROPERTY_DATA_FILE = SRC_DIR / "data" / "current_property_data.csv"
HISTORICAL_DATA_FILE = DATA_DIR / "extract-3-very-clean.csv"

# Eastern Suburbs configuration
EASTERN_SUBURBS = [
    'Bondi', 'Coogee', 'Double Bay', 'Vaucluse', 'Bronte', 'Rose Bay', 
    'Bellevue Hill', 'Paddington', 'Woollahra', 'Bondi Junction', 
    'Waverley', 'Queens Park', 'Bondi Beach', 'North Bondi', 'Tamarama', 
    'Edgecliff', 'Dover Heights', 'Watsons Bay', 'Clovelly', 'South Coogee', 
    'Kensington', 'Maroubra', 'Maroubra South', 'Pagewood', 'Eastgardens', 
    'Chifley', 'Malabar', 'Little Bay', 'Phillip Bay'
]

# Web scraping configuration
SCRAPING_CONFIG = {
    'timeout': 20,
    'rate_limit_wait': 60,
    'max_retries': 3,
    'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
}

# Streamlit configuration
STREAMLIT_CONFIG = {
    'page_title': "Sydney Eastern Suburbs Property Analysis",
    'page_icon': "🏠",
    'layout': "wide",
    'initial_sidebar_state': "expanded"
}

# Analysis configuration
ANALYSIS_CONFIG = {
    'historical_years': 5,  # Number of years of historical data to analyze
    'price_ranges': [
        (0, 1000000, "Under $1M"),
        (1000000, 2000000, "$1M - $2M"),
        (2000000, 3000000, "$2M - $3M"),
        (3000000, 5000000, "$3M - $5M"),
        (5000000, float('inf'), "Over $5M")
    ]
}

# Logging configuration
LOGGING_CONFIG = {
    'level': 'INFO',
    'format': '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    'file': LOGS_DIR / 'app.log'
}
