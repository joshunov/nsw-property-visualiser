"""
Data management module for property analysis
"""

import pandas as pd
import numpy as np
from pathlib import Path
from typing import Dict, Optional, Tuple, List
import logging

from config import (
    CURRENT_PROPERTY_DATA_FILE, 
    HISTORICAL_DATA_FILE, 
    EASTERN_SUBURBS,
    ANALYSIS_CONFIG
)

logger = logging.getLogger(__name__)


class DataLoader:
    """Handles loading and caching of property data"""
    
    def __init__(self):
        self._current_data: Optional[pd.DataFrame] = None
        self._historical_data: Optional[pd.DataFrame] = None
    
    def load_current_data(self) -> pd.DataFrame:
        """Load current property listings data"""
        if self._current_data is not None:
            return self._current_data
            
        try:
            if CURRENT_PROPERTY_DATA_FILE.exists():
                logger.info(f"Loading current data from {CURRENT_PROPERTY_DATA_FILE}")
                self._current_data = pd.read_csv(CURRENT_PROPERTY_DATA_FILE)
                logger.info(f"Loaded {len(self._current_data)} current properties")
            else:
                logger.warning("Current data file not found, generating sample data")
                self._current_data = self._generate_sample_current_data()
        except Exception as e:
            logger.error(f"Error loading current data: {e}")
            self._current_data = self._generate_sample_current_data()
            
        return self._current_data
    
    def load_historical_data(self) -> pd.DataFrame:
        """Load historical property sales data"""
        if self._historical_data is not None:
            return self._historical_data
            
        try:
            if HISTORICAL_DATA_FILE.exists():
                logger.info(f"Loading historical data from {HISTORICAL_DATA_FILE}")
                full_data = pd.read_csv(HISTORICAL_DATA_FILE, low_memory=False)
                
                # Filter for Eastern Suburbs
                self._historical_data = full_data[
                    full_data['Property locality'].isin(EASTERN_SUBURBS)
                ].copy()
                
                # Convert and clean dates
                self._historical_data['Contract date'] = pd.to_datetime(
                    self._historical_data['Contract date'], errors='coerce'
                )
                self._historical_data = self._historical_data.dropna(subset=['Contract date'])
                
                # Filter for recent data
                years_back = ANALYSIS_CONFIG['historical_years']
                cutoff_date = pd.Timestamp.now() - pd.DateOffset(years=years_back)
                self._historical_data = self._historical_data[
                    self._historical_data['Contract date'] >= cutoff_date
                ]
                
                logger.info(f"Loaded {len(self._historical_data):,} historical properties")
            else:
                logger.warning("Historical data file not found, generating sample data")
                self._historical_data = self._generate_sample_historical_data()
        except Exception as e:
            logger.error(f"Error loading historical data: {e}")
            self._historical_data = self._generate_sample_historical_data()
            
        return self._historical_data
    
    def load_all_data(self) -> Dict[str, pd.DataFrame]:
        """Load both current and historical data"""
        return {
            'current_data': self.load_current_data(),
            'historical_data': self.load_historical_data()
        }
    
    def _generate_sample_current_data(self) -> pd.DataFrame:
        """Generate sample current property data"""
        suburbs_data = {
            'Bondi': {'postcode': '2026', 'avg_price': 2500000, 'price_range': 500000},
            'Coogee': {'postcode': '2031', 'avg_price': 2200000, 'price_range': 400000},
            'Double Bay': {'postcode': '2027', 'avg_price': 3500000, 'price_range': 800000},
            'Vaucluse': {'postcode': '2029', 'avg_price': 4500000, 'price_range': 1000000},
            'Bronte': {'postcode': '2024', 'avg_price': 2800000, 'price_range': 600000},
            'Rose Bay': {'postcode': '2028', 'avg_price': 3200000, 'price_range': 700000},
            'Bellevue Hill': {'postcode': '2023', 'avg_price': 3800000, 'price_range': 900000},
            'Paddington': {'postcode': '2021', 'avg_price': 2000000, 'price_range': 400000}
        }
        
        current_data = []
        for suburb, info in suburbs_data.items():
            for _ in range(np.random.randint(2, 5)):
                base_price = info['avg_price'] * 1.1
                price_variation = np.random.normal(0, info['price_range'] * 0.2)
                price = max(500000, base_price + price_variation)
                
                area = np.random.normal(200, 50)
                area = max(50, min(500, area))
                
                current_data.append({
                    'price': int(price),
                    'postcode': info['postcode'],
                    'suburb': suburb,
                    'Area': int(area)
                })
        
        return pd.DataFrame(current_data)
    
    def _generate_sample_historical_data(self) -> pd.DataFrame:
        """Generate sample historical property data"""
        suburbs_data = {
            'Bondi': {'postcode': '2026', 'avg_price': 2500000, 'price_range': 500000},
            'Coogee': {'postcode': '2031', 'avg_price': 2200000, 'price_range': 400000},
            'Double Bay': {'postcode': '2027', 'avg_price': 3500000, 'price_range': 800000},
            'Vaucluse': {'postcode': '2029', 'avg_price': 4500000, 'price_range': 1000000},
            'Bronte': {'postcode': '2024', 'avg_price': 2800000, 'price_range': 600000},
            'Rose Bay': {'postcode': '2028', 'avg_price': 3200000, 'price_range': 700000},
            'Bellevue Hill': {'postcode': '2023', 'avg_price': 3800000, 'price_range': 900000},
            'Paddington': {'postcode': '2021', 'avg_price': 2000000, 'price_range': 400000}
        }
        
        sample_historical = pd.DataFrame({
            'Contract date': pd.date_range('2020-01-01', periods=1000, freq='D'),
            'Purchase price': np.random.normal(1500000, 500000, 1000),
            'Property post code': np.random.choice(['2026', '2031', '2027', '2029'], 1000),
            'Property locality': np.random.choice(['Bondi', 'Coogee', 'Double Bay', 'Vaucluse'], 1000),
            'Area': np.random.normal(200, 50, 1000)
        })
        
        sample_historical['Purchase price'] = sample_historical['Purchase price'].abs()
        sample_historical['Area'] = sample_historical['Area'].abs()
        
        return sample_historical


class DataProcessor:
    """Handles data processing and analysis calculations"""
    
    def __init__(self, historical_data: pd.DataFrame, current_data: pd.DataFrame):
        self.historical_data = historical_data
        self.current_data = current_data
    
    def get_basic_stats(self) -> Dict:
        """Get basic statistics for both datasets"""
        return {
            'historical_count': len(self.historical_data),
            'current_count': len(self.current_data),
            'historical_avg_price': self.historical_data['Purchase price'].mean(),
            'current_avg_price': self.current_data['price'].mean(),
            'historical_median_price': self.historical_data['Purchase price'].median(),
            'current_median_price': self.current_data['price'].median(),
            'historical_date_range': (
                self.historical_data['Contract date'].min(),
                self.historical_data['Contract date'].max()
            ),
            'historical_suburbs': self.historical_data['Property locality'].nunique(),
            'current_suburbs': self.current_data['suburb'].nunique()
        }
    
    def get_price_growth(self) -> Dict:
        """Calculate price growth between historical and current data"""
        hist_median = self.historical_data['Purchase price'].median()
        current_median = self.current_data['price'].median()
        growth_percentage = ((current_median - hist_median) / hist_median) * 100
        
        return {
            'historical_median': hist_median,
            'current_median': current_median,
            'growth_percentage': growth_percentage,
            'growth_absolute': current_median - hist_median
        }
    
    def get_suburb_performance(self, top_n: int = 10) -> pd.DataFrame:
        """Get top performing suburbs by average price"""
        suburb_stats = self.historical_data.groupby('Property locality')['Purchase price'].agg([
            'count', 'mean', 'median'
        ]).round(0)
        
        suburb_stats.columns = ['Sales Count', 'Average Price', 'Median Price']
        return suburb_stats.sort_values('Average Price', ascending=False).head(top_n)
    
    def get_price_distribution(self) -> List[Dict]:
        """Get price distribution breakdown"""
        price_ranges = ANALYSIS_CONFIG['price_ranges']
        distribution = []
        
        for min_price, max_price, label in price_ranges:
            if max_price == float('inf'):
                count = len(self.historical_data[
                    self.historical_data['Purchase price'] >= min_price
                ])
            else:
                count = len(self.historical_data[
                    (self.historical_data['Purchase price'] >= min_price) & 
                    (self.historical_data['Purchase price'] < max_price)
                ])
            
            percentage = (count / len(self.historical_data)) * 100
            distribution.append({
                'range': label,
                'count': count,
                'percentage': percentage
            })
        
        return distribution
    
    def get_monthly_trends(self) -> pd.DataFrame:
        """Get monthly price and volume trends"""
        monthly_data = self.historical_data.groupby(
            self.historical_data['Contract date'].dt.to_period('M')
        )['Purchase price'].agg(['mean', 'median', 'count'])
        
        monthly_data.index = monthly_data.index.astype(str)
        monthly_data.columns = ['Average Price', 'Median Price', 'Sales Volume']
        
        return monthly_data
    
    def get_suburb_comparison(self) -> pd.DataFrame:
        """Get suburb-level comparison between historical and current data"""
        hist_suburbs = set(self.historical_data['Property locality'].unique())
        current_suburbs = set(self.current_data['suburb'].unique())
        matching_suburbs = hist_suburbs & current_suburbs
        
        if not matching_suburbs:
            return pd.DataFrame()
        
        comparison_data = []
        for suburb in matching_suburbs:
            hist_median = self.historical_data[
                self.historical_data['Property locality'] == suburb
            ]['Purchase price'].median()
            
            current_median = self.current_data[
                self.current_data['suburb'] == suburb
            ]['price'].median()
            
            difference = ((current_median - hist_median) / hist_median) * 100
            
            comparison_data.append({
                'Suburb': suburb,
                'Historical Median': hist_median,
                'Current Median': current_median,
                'Difference (%)': difference
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        return comparison_df.sort_values('Difference (%)', ascending=False)
    
    def get_top_suburbs_by_listings(self, top_n: int = 5) -> pd.Series:
        """Get top suburbs by number of current listings"""
        return self.current_data['suburb'].value_counts().head(top_n)
