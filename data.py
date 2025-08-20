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
        """Generate sample current property data with full details"""
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
        
        property_types = ['House', 'Unit/Apartment', 'Townhouse', 'Villa']
        street_names = ['Ocean St', 'Beach Rd', 'Park Ave', 'Hill St', 'Garden Way', 'Bay View Dr', 'Harbour St']
        
        current_data = []
        for suburb, info in suburbs_data.items():
            for i in range(np.random.randint(3, 6)):
                base_price = info['avg_price'] * 1.1
                price_variation = np.random.normal(0, info['price_range'] * 0.2)
                price = max(500000, base_price + price_variation)
                
                area = np.random.normal(200, 50)
                area = max(50, min(500, area))
                
                bedrooms = np.random.randint(1, 6)
                bathrooms = np.random.randint(1, min(bedrooms + 1, 4))
                parking = np.random.randint(0, 3)
                property_type = np.random.choice(property_types)
                street_name = np.random.choice(street_names)
                street_number = np.random.randint(1, 200)
                
                address = f"{street_number} {street_name}, {suburb} NSW {info['postcode']}"
                
                current_data.append({
                    'address': address,
                    'suburb': suburb,
                    'state': 'NSW',
                    'postcode': info['postcode'],
                    'price': int(price),
                    'price_display': f"${price:,.0f}",
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'parking': parking,
                    'square_meters': int(area),
                    'property_type': property_type,
                    'listing_date': pd.Timestamp.now().strftime('%Y-%m-%d'),
                    'source': 'sample_data',
                    'data_type': 'for_sale',
                    'Area': int(area),
                    'Property locality': suburb,
                    'Property street name': f"{street_number} {street_name}",
                    'Property post code': info['postcode']
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
    
    def get_property_insights(self, property_data: pd.Series) -> Dict:
        """Get insights for a specific property compared to historical data"""
        suburb = property_data.get('suburb', property_data.get('Property locality', ''))
        price = property_data.get('price', property_data.get('Purchase price', 0))
        area = property_data.get('Area', property_data.get('square_meters', 0))
        
        # Get historical data for the same suburb
        suburb_historical = self.historical_data[
            self.historical_data['Property locality'] == suburb
        ]
        
        insights = {
            'suburb_avg_price': 0,
            'suburb_median_price': 0,
            'price_percentile': 0,
            'price_vs_avg': 0,
            'area_comparison': 'Unknown',
            'suburb_sales_count': 0,
            'price_trend': 'Unknown'
        }
        
        if not suburb_historical.empty:
            insights['suburb_avg_price'] = suburb_historical['Purchase price'].mean()
            insights['suburb_median_price'] = suburb_historical['Purchase price'].median()
            insights['suburb_sales_count'] = len(suburb_historical)
            
            # Calculate price percentile
            if price > 0:
                percentile = (suburb_historical['Purchase price'] < price).mean() * 100
                insights['price_percentile'] = percentile
                insights['price_vs_avg'] = ((price - insights['suburb_avg_price']) / insights['suburb_avg_price']) * 100
            
            # Area comparison
            if area > 0 and 'Area' in suburb_historical.columns:
                avg_area = suburb_historical['Area'].mean()
                if not pd.isna(avg_area) and avg_area > 0:
                    area_diff = ((area - avg_area) / avg_area) * 100
                    if area_diff > 10:
                        insights['area_comparison'] = f"Larger than average (+{area_diff:.1f}%)"
                    elif area_diff < -10:
                        insights['area_comparison'] = f"Smaller than average ({area_diff:.1f}%)"
                    else:
                        insights['area_comparison'] = "Average size"
            
            # Price trend (last 2 years vs earlier)
            if len(suburb_historical) > 10:
                suburb_historical_sorted = suburb_historical.sort_values('Contract date')
                recent_date = suburb_historical_sorted['Contract date'].max()
                cutoff_date = recent_date - pd.DateOffset(years=2)
                
                recent_prices = suburb_historical_sorted[
                    suburb_historical_sorted['Contract date'] >= cutoff_date
                ]['Purchase price']
                
                older_prices = suburb_historical_sorted[
                    suburb_historical_sorted['Contract date'] < cutoff_date
                ]['Purchase price']
                
                if len(recent_prices) > 0 and len(older_prices) > 0:
                    recent_avg = recent_prices.mean()
                    older_avg = older_prices.mean()
                    trend_pct = ((recent_avg - older_avg) / older_avg) * 100
                    
                    if trend_pct > 5:
                        insights['price_trend'] = f"Rising (+{trend_pct:.1f}%)"
                    elif trend_pct < -5:
                        insights['price_trend'] = f"Declining ({trend_pct:.1f}%)"
                    else:
                        insights['price_trend'] = "Stable"
        
        return insights
    
    def get_similar_properties(self, property_data: pd.Series, limit: int = 5) -> pd.DataFrame:
        """Find similar properties in historical data"""
        suburb = property_data.get('suburb', property_data.get('Property locality', ''))
        price = property_data.get('price', property_data.get('Purchase price', 0))
        area = property_data.get('Area', property_data.get('square_meters', 0))
        
        # Filter historical data for same suburb
        suburb_data = self.historical_data[
            self.historical_data['Property locality'] == suburb
        ].copy()
        
        if suburb_data.empty:
            return pd.DataFrame()
        
        # Calculate similarity score based on price and area
        if price > 0:
            suburb_data['price_diff'] = abs(suburb_data['Purchase price'] - price) / price
        else:
            suburb_data['price_diff'] = 1.0
            
        if area > 0 and 'Area' in suburb_data.columns:
            suburb_data['area_diff'] = abs(suburb_data['Area'].fillna(area) - area) / area
        else:
            suburb_data['area_diff'] = 0.0
        
        # Combined similarity score (lower is better)
        suburb_data['similarity_score'] = suburb_data['price_diff'] + (suburb_data['area_diff'] * 0.5)
        
        # Return most similar properties
        similar = suburb_data.nsmallest(limit, 'similarity_score')[
            ['Contract date', 'Purchase price', 'Area', 'Property post code', 'similarity_score']
        ].copy()
        
        return similar
