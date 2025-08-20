#!/usr/bin/env python3
"""
AI-Powered Eastern Suburbs Property Chatbot
Uses OpenAI ChatGPT API for intelligent property data analysis
"""

import pandas as pd
import numpy as np
import re
import logging
import os
import time
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import openai

# Configure logging
logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                   handlers=[logging.FileHandler(os.path.join(logs_dir, "ai_chatbot.log")), logging.StreamHandler()])

class AIChatbot:
    """AI-powered chatbot using OpenAI ChatGPT API"""
    
    def __init__(self, use_cache=True, api_key=None):
        # Set up OpenAI
        if api_key:
            openai.api_key = api_key
        elif os.getenv('OPENAI_API_KEY'):
            openai.api_key = os.getenv('OPENAI_API_KEY')
        else:
            raise ValueError("OpenAI API key not found. Set OPENAI_API_KEY environment variable or pass api_key parameter.")
        
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
        
        # System prompt for the AI
        self.system_prompt = self._create_system_prompt()
        
        # Conversation history
        self.conversation_history = []
    
    def _create_system_prompt(self):
        """Create the system prompt for the AI"""
        return f"""You are an expert property analyst specializing in Eastern Suburbs of Sydney, Australia. You have access to comprehensive property data and can provide detailed insights about:

**Data Available:**
- Historical property sales data: {len(self.historical_df) if self.historical_df is not None else 0:,} records
- Current property listings: {len(self.current_df) if self.current_df is not None else 0:,} records
- Coverage: Eastern Suburbs postcodes 2021-2035 (Paddington, Bondi, Vaucluse, etc.)
- Time period: Past 5 years of sales data

**Your Capabilities:**
1. **Price Analysis**: Provide average, median, and price range statistics
2. **Market Trends**: Analyze price growth, market changes, and trends over time
3. **Suburb Comparisons**: Compare property prices between different Eastern Suburbs
4. **Property Search**: Find properties by price, bedrooms, bathrooms, location
5. **Market Insights**: Provide expert analysis and recommendations

**Eastern Suburbs Covered:**
- 2021: Paddington, Woollahra
- 2022: Bondi Junction  
- 2023: Bellevue Hill
- 2024: Bronte, Waverley
- 2025: Queens Park
- 2026: Bondi, Bondi Beach, North Bondi, Tamarama
- 2027: Edgecliff, Double Bay
- 2028: Rose Bay
- 2029: Vaucluse, Dover Heights
- 2030: Watsons Bay
- 2031: Clovelly, Coogee
- 2032: South Coogee
- 2033: Kensington
- 2034: Maroubra, Maroubra South, Pagewood
- 2035: Eastgardens, Chifley, Malabar, Little Bay, Phillip Bay

**Response Style:**
- Be conversational and friendly
- Use emojis to make responses engaging
- Provide specific data and statistics when available
- Give actionable insights and recommendations
- If you don't have specific data for a query, explain what you can help with instead

**Important Notes:**
- All prices are in Australian Dollars (AUD)
- Focus on Eastern Suburbs of Sydney only
- Be accurate with data and transparent about limitations
- Provide context and explanations for your analysis
"""

    def load_data(self):
        """Load historical and current property data"""
        logging.info("Loading property data for AI chatbot...")
        
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
    
    def _get_data_summary(self):
        """Get a summary of available data for the AI"""
        summary = {
            "historical_data": {
                "total_records": len(self.historical_df) if self.historical_df is not None else 0,
                "columns": list(self.historical_df.columns) if self.historical_df is not None else [],
                "date_range": None,
                "price_stats": None
            },
            "current_data": {
                "total_records": len(self.current_df) if self.current_df is not None else 0,
                "columns": list(self.current_df.columns) if self.current_df is not None else []
            }
        }
        
        # Add historical data stats
        if self.historical_df is not None and not self.historical_df.empty:
            if 'Contract date' in self.historical_df.columns:
                summary["historical_data"]["date_range"] = {
                    "earliest": self.historical_df['Contract date'].min().strftime('%Y-%m-%d'),
                    "latest": self.historical_df['Contract date'].max().strftime('%Y-%m-%d')
                }
            
            if 'Purchase price' in self.historical_df.columns:
                prices = self.historical_df['Purchase price'].dropna()
                if len(prices) > 0:
                    summary["historical_data"]["price_stats"] = {
                        "average": float(prices.mean()),
                        "median": float(prices.median()),
                        "min": float(prices.min()),
                        "max": float(prices.max())
                    }
        
        return summary
    
    def _get_relevant_data(self, query):
        """Extract relevant data based on the query"""
        relevant_data = {}
        
        # Extract suburb mentions
        eastern_suburbs = [
            'paddington', 'woollahra', 'bondi junction', 'bellevue hill', 'bronte',
            'waverley', 'queens park', 'bondi', 'bondi beach', 'north bondi',
            'tamarama', 'edgecliff', 'double bay', 'rose bay', 'vaucluse',
            'dover heights', 'watsons bay', 'clovelly', 'coogee', 'south coogee',
            'kensington', 'maroubra', 'maroubra south', 'pagewood', 'eastgardens',
            'chifley', 'malabar', 'little bay', 'phillip bay'
        ]
        
        mentioned_suburbs = []
        for suburb in eastern_suburbs:
            if suburb in query.lower():
                mentioned_suburbs.append(suburb.title())
        
        if mentioned_suburbs:
            relevant_data["mentioned_suburbs"] = mentioned_suburbs
            
            # Get data for mentioned suburbs
            if self.historical_df is not None and not self.historical_df.empty:
                suburb_data = {}
                for suburb in mentioned_suburbs:
                    suburb_records = self.historical_df[
                        self.historical_df['Property locality'].str.contains(suburb, case=False, na=False)
                    ]
                    if not suburb_records.empty:
                        suburb_data[suburb] = {
                            "count": len(suburb_records),
                            "avg_price": float(suburb_records['Purchase price'].mean()) if 'Purchase price' in suburb_records.columns else None,
                            "median_price": float(suburb_records['Purchase price'].median()) if 'Purchase price' in suburb_records.columns else None
                        }
                relevant_data["suburb_data"] = suburb_data
        
        # Extract price-related queries
        price_keywords = ['price', 'cost', 'value', 'expensive', 'cheap', 'affordable', 'million', 'dollars']
        if any(keyword in query.lower() for keyword in price_keywords):
            relevant_data["price_query"] = True
            
            # Get overall price statistics
            if self.historical_df is not None and not self.historical_df.empty and 'Purchase price' in self.historical_df.columns:
                prices = self.historical_df['Purchase price'].dropna()
                if len(prices) > 0:
                    relevant_data["overall_price_stats"] = {
                        "average": float(prices.mean()),
                        "median": float(prices.median()),
                        "min": float(prices.min()),
                        "max": float(prices.max())
                    }
        
        # Extract trend-related queries
        trend_keywords = ['trend', 'growth', 'increase', 'decrease', 'change', 'over time']
        if any(keyword in query.lower() for keyword in trend_keywords):
            relevant_data["trend_query"] = True
        
        return relevant_data
    
    def process_query(self, query: str) -> str:
        """Process user query using OpenAI ChatGPT API"""
        logging.info(f"Processing AI query: {query}")
        
        try:
            # Get relevant data for the query
            relevant_data = self._get_relevant_data(query)
            data_summary = self._get_data_summary()
            
            # Create the user message with context
            user_message = f"""User Query: {query}

Available Data Summary:
{json.dumps(data_summary, indent=2)}

Relevant Data for this Query:
{json.dumps(relevant_data, indent=2)}

Please provide a comprehensive, helpful response about Eastern Suburbs property data based on the user's query. Use the available data to provide specific insights and statistics when possible."""
            
            # Prepare messages for OpenAI
            messages = [
                {"role": "system", "content": self.system_prompt},
                {"role": "user", "content": user_message}
            ]
            
            # Add conversation history for context
            if self.conversation_history:
                messages = [{"role": "system", "content": self.system_prompt}] + self.conversation_history[-4:] + [{"role": "user", "content": user_message}]
            
            # Call OpenAI API
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=messages,
                max_tokens=1000,
                temperature=0.7,
                top_p=1,
                frequency_penalty=0,
                presence_penalty=0
            )
            
            ai_response = response.choices[0].message.content
            
            # Update conversation history
            self.conversation_history.append({"role": "user", "content": user_message})
            self.conversation_history.append({"role": "assistant", "content": ai_response})
            
            # Keep conversation history manageable
            if len(self.conversation_history) > 10:
                self.conversation_history = self.conversation_history[-10:]
            
            return ai_response
            
        except Exception as e:
            logging.error(f"Error processing AI query: {e}")
            return f"I apologize, but I encountered an error while processing your query. Please try again. Error: {str(e)}"
    
    def get_suggestions(self) -> List[str]:
        """Get suggested questions for the user"""
        return [
            "What's the current property market like in Bondi?",
            "How have property prices changed in Eastern Suburbs over the past 5 years?",
            "Which suburb in Eastern Suburbs offers the best value for money?",
            "What's the average price for a 3-bedroom house in Vaucluse?",
            "Compare property prices between Bondi and Coogee",
            "What are the most expensive suburbs in Eastern Suburbs?",
            "How does the current market compare to historical trends?",
            "What should I know about buying property in Eastern Suburbs?"
        ]
    
    def clear_conversation_history(self):
        """Clear the conversation history"""
        self.conversation_history = []
        logging.info("Conversation history cleared")
    
    def refresh_cache(self):
        """Force refresh the cache by reloading data"""
        logging.info("Refreshing cache...")
        self.load_data()
        self._save_cache()
        logging.info("Cache refreshed successfully")

if __name__ == "__main__":
    # Test the AI chatbot
    print("🤖 AI-Powered Eastern Suburbs Property Chatbot")
    print("=" * 60)
    print("This chatbot uses OpenAI ChatGPT API for intelligent responses!")
    print("Make sure you have set your OPENAI_API_KEY environment variable.")
    print("Type 'quit' to exit.\n")
    
    try:
        chatbot = AIChatbot()
        
        while True:
            try:
                user_input = input("You: ").strip()
                
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("👋 Thanks for using the AI Property Chatbot!")
                    break
                
                elif not user_input:
                    continue
                
                # Process query
                print("🤖 AI is thinking...")
                response = chatbot.process_query(user_input)
                print(f"\n🤖 **AI Chatbot:**\n{response}\n")
                
            except KeyboardInterrupt:
                print("\n👋 Thanks for using the AI Property Chatbot!")
                break
            except Exception as e:
                print(f"\n❌ Error: {e}")
                logging.error(f"Error in main loop: {e}")
                
    except Exception as e:
        print(f"❌ Failed to initialize AI chatbot: {e}")
        print("Make sure you have set your OPENAI_API_KEY environment variable.")
