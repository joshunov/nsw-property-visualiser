#!/usr/bin/env python3
"""
Eastern Suburbs Property AI Chatbot
Natural language interface for querying property data
"""

import pandas as pd
import numpy as np
import re
import logging
import os
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import json

# Configure logging
logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                   handlers=[logging.FileHandler(os.path.join(logs_dir, "property_chatbot.log")), logging.StreamHandler()])

class PropertyChatbot:
    """AI Chatbot for Eastern Suburbs property queries"""
    
    def __init__(self, use_cache=True):
        # Ensure data directory exists
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Data file paths
        root_data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        self.historical_file = os.path.join(root_data_dir, "extract-3-very-clean.csv")
        self.current_file = os.path.join(data_dir, "current_property_data.csv")
        
        # Cache file paths
        self.cache_dir = os.path.join(os.path.dirname(__file__), '..', 'cache')
        os.makedirs(self.cache_dir, exist_ok=True)
        self.historical_cache_file = os.path.join(self.cache_dir, "historical_data_cache.pkl")
        self.current_cache_file = os.path.join(self.cache_dir, "current_data_cache.pkl")
        
        # Eastern Suburbs postcodes
        self.eastern_postcodes = ['2021', '2022', '2023', '2024', '2025', '2026', '2027', '2028', '2029', '2030', '2031', '2032', '2033', '2034', '2035']
        
        # Load data
        self.historical_df = None
        self.current_df = None
        
        if use_cache:
            self.load_cached_data()
        else:
            self.load_data()
        
        # Common property terms and synonyms
        self.property_terms = {
            'price': ['price', 'cost', 'value', 'amount', 'dollars', '$', 'expensive', 'cheap', 'affordable'],
            'bedrooms': ['bedroom', 'bed', 'beds', 'sleeping'],
            'bathrooms': ['bathroom', 'bath', 'baths', 'shower'],
            'area': ['area', 'size', 'square meters', 'sqm', 'm2', 'land size'],
            'suburb': ['suburb', 'location', 'area', 'neighborhood', 'postcode'],
            'date': ['date', 'when', 'recent', 'latest', 'old', 'new', 'sold', 'listed'],
            'type': ['type', 'house', 'unit', 'apartment', 'townhouse', 'property']
        }
        
        # Query patterns
        self.query_patterns = {
            'price_range': r'(price|cost|value).*(between|from|to|range)',
            'suburb_query': r'(in|at|near|around)\s+([a-zA-Z\s]+)',
            'bedroom_query': r'(\d+)\s*(bedroom|bed|beds)',
            'bathroom_query': r'(\d+)\s*(bathroom|bath|baths)',
            'comparison': r'(compare|vs|versus|difference)',
            'trend': r'(trend|growth|increase|decrease|change)',
            'average': r'(average|mean|median|typical)',
            'expensive': r'(most expensive|highest price|top price)',
            'cheap': r'(cheapest|lowest price|affordable)',
            'recent': r'(recent|latest|new|current)',
            'area_query': r'(\d+)\s*(sqm|square meters|m2)'
        }
        
    def load_data(self):
        """Load historical and current property data"""
        logging.info("Loading property data for chatbot...")
        
        # Load historical data
        if os.path.exists(self.historical_file):
            self.historical_df = pd.read_csv(self.historical_file, low_memory=False)
            # Filter for Eastern Suburbs
            self.historical_df['Property post code'] = self.historical_df['Property post code'].astype(str)
            self.historical_df['Property post code'] = self.historical_df['Property post code'].str.replace('.0', '', regex=False)
            self.historical_df = self.historical_df[self.historical_df['Property post code'].isin(self.eastern_postcodes)]
            
            # Filter for past 5 years
            self.historical_df['Contract date'] = pd.to_datetime(self.historical_df['Contract date'], errors='coerce')
            five_years_ago = datetime.now() - timedelta(days=5*365)
            self.historical_df = self.historical_df[self.historical_df['Contract date'] >= five_years_ago]
            
            logging.info(f"Loaded {len(self.historical_df)} historical Eastern Suburbs records")
        else:
            logging.warning("Historical data file not found")
            self.historical_df = pd.DataFrame()
            
        # Load current data
        if os.path.exists(self.current_file):
            self.current_df = pd.read_csv(self.current_file)
            logging.info(f"Loaded {len(self.current_df)} current listings")
        else:
            logging.warning("Current data file not found")
            self.current_df = pd.DataFrame()
    
    def load_cached_data(self):
        """Load data from cache if available, otherwise load and cache"""
        logging.info("Checking for cached data...")
        
        # Check if cache files exist and are recent (less than 24 hours old)
        cache_valid = self._is_cache_valid()
        
        if cache_valid:
            try:
                logging.info("Loading data from cache...")
                self.historical_df = pd.read_pickle(self.historical_cache_file)
                self.current_df = pd.read_pickle(self.current_cache_file)
                logging.info(f"Loaded {len(self.historical_df)} historical and {len(self.current_df)} current records from cache")
                return
            except Exception as e:
                logging.warning(f"Failed to load cache: {e}")
        
        # Load data normally and cache it
        logging.info("Cache not available or invalid, loading fresh data...")
        self.load_data()
        self._save_cache()
    
    def _is_cache_valid(self):
        """Check if cache files exist and are recent"""
        try:
            if not os.path.exists(self.historical_cache_file) or not os.path.exists(self.current_cache_file):
                return False
            
            # Check if cache is less than 24 hours old
            cache_time = os.path.getmtime(self.historical_cache_file)
            current_time = time.time()
            cache_age_hours = (current_time - cache_time) / 3600
            
            return cache_age_hours < 24
        except Exception:
            return False
    
    def _save_cache(self):
        """Save processed data to cache"""
        try:
            logging.info("Saving data to cache...")
            self.historical_df.to_pickle(self.historical_cache_file)
            self.current_df.to_pickle(self.current_cache_file)
            logging.info("Cache saved successfully")
        except Exception as e:
            logging.error(f"Failed to save cache: {e}")
    
    def refresh_cache(self):
        """Force refresh the cache by reloading data"""
        logging.info("Refreshing cache...")
        self.load_data()
        self._save_cache()
        logging.info("Cache refreshed successfully")
    
    def preprocess_query(self, query: str) -> str:
        """Preprocess and normalize user query"""
        query = query.lower().strip()
        # Remove extra whitespace
        query = re.sub(r'\s+', ' ', query)
        return query
    
    def extract_keywords(self, query: str) -> Dict[str, List[str]]:
        """Extract relevant keywords from query"""
        keywords = {}
        
        for category, terms in self.property_terms.items():
            found_terms = []
            for term in terms:
                if term in query:
                    found_terms.append(term)
            if found_terms:
                keywords[category] = found_terms
        
        return keywords
    
    def extract_patterns(self, query: str) -> Dict[str, str]:
        """Extract patterns from query"""
        patterns = {}
        
        for pattern_name, pattern in self.query_patterns.items():
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                patterns[pattern_name] = match.group(0)
        
        return patterns
    
    def get_suburb_from_query(self, query: str) -> Optional[str]:
        """Extract suburb name from query"""
        # Common Eastern Suburbs
        eastern_suburbs = [
            'paddington', 'woollahra', 'bondi junction', 'bellevue hill', 'bronte',
            'waverley', 'queens park', 'bondi', 'bondi beach', 'north bondi',
            'tamarama', 'edgecliff', 'double bay', 'rose bay', 'vaucluse',
            'dover heights', 'watsons bay', 'clovelly', 'coogee', 'south coogee',
            'kensington', 'maroubra', 'maroubra south', 'pagewood', 'eastgardens',
            'chifley', 'malabar', 'little bay', 'phillip bay'
        ]
        
        for suburb in eastern_suburbs:
            if suburb in query.lower():
                return suburb.title()
        
        return None
    
    def get_price_range_from_query(self, query: str) -> Optional[Tuple[float, float]]:
        """Extract price range from query"""
        # Look for price patterns like "$1.5M to $2M" or "1.5 million to 2 million"
        price_patterns = [
            r'\$?(\d+(?:\.\d+)?)\s*(?:million|m|mil).*?\$?(\d+(?:\.\d+)?)\s*(?:million|m|mil)',
            r'\$?(\d+(?:\.\d+)?)\s*(?:million|m|mil).*?(\d+(?:\.\d+)?)\s*(?:million|m|mil)',
            r'\$(\d{1,3}(?:,\d{3})*).*?\$(\d{1,3}(?:,\d{3})*)',
        ]
        
        for pattern in price_patterns:
            match = re.search(pattern, query, re.IGNORECASE)
            if match:
                try:
                    min_price = float(match.group(1).replace(',', ''))
                    max_price = float(match.group(2).replace(',', ''))
                    
                    # Convert millions to actual price
                    if 'million' in query.lower() or 'm' in query.lower() or 'mil' in query.lower():
                        min_price *= 1000000
                        max_price *= 1000000
                    
                    return (min_price, max_price)
                except ValueError:
                    continue
        
        return None
    
    def get_bedroom_count_from_query(self, query: str) -> Optional[int]:
        """Extract bedroom count from query"""
        match = re.search(r'(\d+)\s*(?:bedroom|bed|beds)', query, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def get_bathroom_count_from_query(self, query: str) -> Optional[int]:
        """Extract bathroom count from query"""
        match = re.search(r'(\d+)\s*(?:bathroom|bath|baths)', query, re.IGNORECASE)
        if match:
            return int(match.group(1))
        return None
    
    def query_historical_data(self, filters: Dict) -> pd.DataFrame:
        """Query historical data with filters"""
        df = self.historical_df.copy()
        
        if df.empty:
            return df
        
        # Apply filters
        if 'suburb' in filters and filters['suburb']:
            df = df[df['Property locality'].str.contains(filters['suburb'], case=False, na=False)]
        
        if 'postcode' in filters and filters['postcode']:
            df = df[df['Property post code'] == filters['postcode']]
        
        if 'min_price' in filters and filters['min_price']:
            df = df[df['Purchase price'] >= filters['min_price']]
        
        if 'max_price' in filters and filters['max_price']:
            df = df[df['Purchase price'] <= filters['max_price']]
        
        if 'bedrooms' in filters and filters['bedrooms']:
            if 'Bedrooms' in df.columns:
                df = df[df['Bedrooms'] >= filters['bedrooms']]
        
        if 'bathrooms' in filters and filters['bathrooms']:
            if 'Bathrooms' in df.columns:
                df = df[df['Bathrooms'] >= filters['bathrooms']]
        
        return df
    
    def query_current_data(self, filters: Dict) -> pd.DataFrame:
        """Query current data with filters"""
        df = self.current_df.copy()
        
        if df.empty:
            return df
        
        # Apply filters
        if 'suburb' in filters and filters['suburb']:
            df = df[df['suburb'].str.contains(filters['suburb'], case=False, na=False)]
        
        if 'postcode' in filters and filters['postcode']:
            df = df[df['postcode'] == filters['postcode']]
        
        if 'min_price' in filters and filters['min_price']:
            df = df[df['price'] >= filters['min_price']]
        
        if 'max_price' in filters and filters['max_price']:
            df = df[df['price'] <= filters['max_price']]
        
        if 'bedrooms' in filters and filters['bedrooms']:
            df = df[df['bedrooms'] >= filters['bedrooms']]
        
        if 'bathrooms' in filters and filters['bathrooms']:
            df = df[df['bathrooms'] >= filters['bathrooms']]
        
        return df
    
    def generate_price_analysis(self, df: pd.DataFrame, data_type: str = "historical") -> str:
        """Generate price analysis for the filtered data"""
        if df.empty:
            return f"No {data_type} data found matching your criteria."
        
        if data_type == "historical":
            price_col = 'Purchase price'
        else:
            price_col = 'price'
        
        if price_col not in df.columns:
            return f"No price data available in {data_type} data."
        
        prices = df[price_col].dropna()
        if len(prices) == 0:
            return f"No valid price data found in {data_type} data."
        
        avg_price = prices.mean()
        median_price = prices.median()
        min_price = prices.min()
        max_price = prices.max()
        count = len(prices)
        
        response = f"📊 **{data_type.title()} Price Analysis:**\n"
        response += f"🏠 **Properties found:** {count:,}\n"
        response += f"💰 **Average price:** ${avg_price:,.0f}\n"
        response += f"📈 **Median price:** ${median_price:,.0f}\n"
        response += f"📊 **Price range:** ${min_price:,.0f} - ${max_price:,.0f}\n"
        
        return response
    
    def generate_suburb_comparison(self, suburb1: str, suburb2: str) -> str:
        """Compare two suburbs"""
        df1 = self.query_historical_data({'suburb': suburb1})
        df2 = self.query_historical_data({'suburb': suburb2})
        
        if df1.empty and df2.empty:
            return f"No data found for {suburb1} or {suburb2}."
        
        response = f"🏘️ **Suburb Comparison: {suburb1} vs {suburb2}**\n\n"
        
        if not df1.empty:
            avg1 = df1['Purchase price'].mean()
            median1 = df1['Purchase price'].median()
            count1 = len(df1)
            response += f"**{suburb1}:**\n"
            response += f"  📊 Properties: {count1:,}\n"
            response += f"  💰 Average: ${avg1:,.0f}\n"
            response += f"  📈 Median: ${median1:,.0f}\n\n"
        
        if not df2.empty:
            avg2 = df2['Purchase price'].mean()
            median2 = df2['Purchase price'].median()
            count2 = len(df2)
            response += f"**{suburb2}:**\n"
            response += f"  📊 Properties: {count2:,}\n"
            response += f"  💰 Average: ${avg2:,.0f}\n"
            response += f"  📈 Median: ${median2:,.0f}\n\n"
        
        if not df1.empty and not df2.empty:
            price_diff = avg2 - avg1
            price_diff_pct = (price_diff / avg1) * 100
            response += f"**Price Difference:**\n"
            response += f"  💵 {suburb2} is ${price_diff:+,.0f} ({price_diff_pct:+.1f}%) different from {suburb1}\n"
        
        return response
    
    def generate_trend_analysis(self, suburb: str = None) -> str:
        """Generate trend analysis"""
        df = self.historical_df.copy()
        
        if suburb:
            df = df[df['Property locality'].str.contains(suburb, case=False, na=False)]
        
        if df.empty:
            return "No data available for trend analysis."
        
        # Group by year and calculate average prices
        df['year'] = df['Contract date'].dt.year
        yearly_avg = df.groupby('year')['Purchase price'].mean().sort_index()
        
        if len(yearly_avg) < 2:
            return "Insufficient data for trend analysis."
        
        response = "📈 **Price Trend Analysis**\n\n"
        
        # Calculate growth
        first_year = yearly_avg.index[0]
        last_year = yearly_avg.index[-1]
        first_price = yearly_avg.iloc[0]
        last_price = yearly_avg.iloc[-1]
        
        total_growth = ((last_price - first_price) / first_price) * 100
        annual_growth = total_growth / (last_year - first_year)
        
        response += f"📅 **Period:** {first_year} to {last_year}\n"
        response += f"💰 **Price change:** ${first_price:,.0f} → ${last_price:,.0f}\n"
        response += f"📊 **Total growth:** {total_growth:+.1f}%\n"
        response += f"📈 **Annual growth:** {annual_growth:+.1f}%\n\n"
        
        # Recent trend (last 2 years)
        if len(yearly_avg) >= 2:
            recent_avg = yearly_avg.tail(2).mean()
            older_avg = yearly_avg.head(len(yearly_avg)-2).mean()
            recent_growth = ((recent_avg - older_avg) / older_avg) * 100
            
            response += f"🕒 **Recent Trend (Last 2 Years):**\n"
            response += f"  📊 Recent average: ${recent_avg:,.0f}\n"
            response += f"  📊 Previous average: ${older_avg:,.0f}\n"
            response += f"  📈 Growth: {recent_growth:+.1f}%\n"
        
        return response
    
    def process_query(self, query: str) -> str:
        """Main method to process user query and generate response"""
        logging.info(f"Processing query: {query}")
        
        # Preprocess query
        processed_query = self.preprocess_query(query)
        
        # Extract information
        keywords = self.extract_keywords(processed_query)
        patterns = self.extract_patterns(processed_query)
        suburb = self.get_suburb_from_query(processed_query)
        price_range = self.get_price_range_from_query(processed_query)
        bedrooms = self.get_bedroom_count_from_query(processed_query)
        bathrooms = self.get_bathroom_count_from_query(processed_query)
        
        # Build filters
        filters = {}
        if suburb:
            filters['suburb'] = suburb
        if price_range:
            filters['min_price'] = price_range[0]
            filters['max_price'] = price_range[1]
        if bedrooms:
            filters['bedrooms'] = bedrooms
        if bathrooms:
            filters['bathrooms'] = bathrooms
        
        # Determine query type and generate response
        response = ""
        
        # Comparison queries
        if 'comparison' in patterns or 'vs' in processed_query or 'versus' in processed_query:
            if suburb:
                # Find another suburb to compare with
                all_suburbs = self.historical_df['Property locality'].unique()
                other_suburbs = [s for s in all_suburbs if s.lower() != suburb.lower()]
                if other_suburbs:
                    other_suburb = other_suburbs[0]
                    response = self.generate_suburb_comparison(suburb, other_suburb)
                else:
                    response = f"No other suburbs found to compare with {suburb}."
            else:
                response = "Please specify which suburbs you'd like to compare."
        
        # Trend queries
        elif 'trend' in patterns or 'growth' in processed_query or 'change' in processed_query:
            response = self.generate_trend_analysis(suburb)
        
        # Price analysis queries
        elif 'price' in keywords or 'cost' in keywords or 'value' in keywords:
            if 'current' in processed_query or 'listing' in processed_query:
                current_data = self.query_current_data(filters)
                response = self.generate_price_analysis(current_data, "current")
            else:
                historical_data = self.query_historical_data(filters)
                response = self.generate_price_analysis(historical_data, "historical")
        
        # General property queries
        else:
            # Default to historical data analysis
            historical_data = self.query_historical_data(filters)
            current_data = self.query_current_data(filters)
            
            if not historical_data.empty:
                response += self.generate_price_analysis(historical_data, "historical") + "\n\n"
            
            if not current_data.empty:
                response += self.generate_price_analysis(current_data, "current")
            
            if historical_data.empty and current_data.empty:
                response = "I couldn't find any property data matching your criteria. Please try rephrasing your question or specify a different suburb."
        
        # Add context if filters were applied
        if filters:
            context = "🔍 **Applied Filters:**\n"
            for key, value in filters.items():
                context += f"  • {key.title()}: {value}\n"
            response = context + "\n" + response
        
        return response
    
    def get_suggestions(self) -> List[str]:
        """Get suggested questions for the user"""
        return [
            "What's the average price in Bondi?",
            "Show me properties in Paddington under $2M",
            "Compare Bondi vs Coogee prices",
            "What's the price trend in Eastern Suburbs?",
            "Find 3-bedroom properties in Vaucluse",
            "What are the most expensive suburbs?",
            "Show me recent sales in Double Bay",
            "What's the price range for 2-bedroom apartments?"
        ]

if __name__ == "__main__":
    # Test the chatbot
    chatbot = PropertyChatbot()
    
    print("🏠 Eastern Suburbs Property AI Chatbot")
    print("=" * 50)
    print("Ask me anything about Eastern Suburbs property data!")
    print("Type 'quit' to exit, 'suggestions' for example questions.\n")
    
    while True:
        try:
            user_input = input("You: ").strip()
            
            if user_input.lower() in ['quit', 'exit', 'bye']:
                print("👋 Thanks for using the Property Chatbot!")
                break
            
            elif user_input.lower() == 'suggestions':
                print("\n💡 **Suggested Questions:**")
                for i, suggestion in enumerate(chatbot.get_suggestions(), 1):
                    print(f"{i}. {suggestion}")
                print()
                continue
            
            elif not user_input:
                continue
            
            # Process query
            response = chatbot.process_query(user_input)
            print(f"\n🤖 **Chatbot:**\n{response}\n")
            
        except KeyboardInterrupt:
            print("\n👋 Thanks for using the Property Chatbot!")
            break
        except Exception as e:
            print(f"\n❌ Error: {e}")
            logging.error(f"Error processing query: {e}")
