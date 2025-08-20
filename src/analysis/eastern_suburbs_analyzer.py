#!/usr/bin/env python3
"""
Eastern Suburbs Sydney Property Analysis
Specialized analysis for Eastern Suburbs property market
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from datetime import datetime
import os
import logging

# Configure logging
logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                   handlers=[logging.FileHandler(os.path.join(logs_dir, "eastern_suburbs_analysis.log")), logging.StreamHandler()])

# Eastern Suburbs postcodes and suburbs
EASTERN_SUBURBS = {
    '2021': ['Paddington', 'Woollahra'],
    '2022': ['Bondi Junction'],
    '2023': ['Bellevue Hill'],
    '2024': ['Bronte', 'Waverley'],
    '2025': ['Queens Park'],
    '2026': ['Bondi', 'Bondi Beach', 'North Bondi', 'Tamarama'],
    '2027': ['Edgecliff', 'Double Bay'],
    '2028': ['Rose Bay'],
    '2029': ['Vaucluse', 'Dover Heights'],
    '2030': ['Watsons Bay', 'Vaucluse'],
    '2031': ['Clovelly', 'Coogee'],
    '2032': ['South Coogee'],
    '2033': ['Kensington'],
    '2034': ['Maroubra', 'Maroubra South', 'Pagewood'],
    '2035': ['Eastgardens', 'Chifley', 'Malabar', 'Little Bay', 'Phillip Bay']
}

EASTERN_POSTCODES = list(EASTERN_SUBURBS.keys())

class EasternSuburbsAnalyzer:
    """Specialized analyzer for Eastern Suburbs Sydney property market"""
    
    def __init__(self):
        # Ensure data directory exists
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        # Historical data is in the root data directory
        root_data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        self.historical_file = os.path.join(root_data_dir, "extract-3-very-clean.csv")
        self.current_file = os.path.join(data_dir, "current_property_data.csv")
        self.output_dir = os.path.join(data_dir, "eastern_suburbs_analysis")
        
        # Create output directory
        os.makedirs(self.output_dir, exist_ok=True)
        
        self.historical_df = None
        self.current_df = None
        
    def load_eastern_suburbs_data(self):
        """Load and filter data for Eastern Suburbs only"""
        logging.info("Loading Eastern Suburbs property data...")
        
        # Load historical data
        if os.path.exists(self.historical_file):
            logging.info(f"Loading historical data from {self.historical_file}")
            df = pd.read_csv(self.historical_file, low_memory=False)
            
            # Filter for Eastern Suburbs postcodes
            df['Property post code'] = df['Property post code'].astype(str)
            # Remove decimal points from postcodes (e.g., "2021.0" -> "2021")
            df['Property post code'] = df['Property post code'].str.replace('.0', '', regex=False)
            self.historical_df = df[df['Property post code'].isin(EASTERN_POSTCODES)]
            
            logging.info(f"Found {len(self.historical_df)} Eastern Suburbs historical records")
        else:
            logging.warning("Historical data file not found")
            self.historical_df = pd.DataFrame()
            
        # Load current data
        if os.path.exists(self.current_file):
            logging.info(f"Loading current data from {self.current_file}")
            self.current_df = pd.read_csv(self.current_file)
            logging.info(f"Found {len(self.current_df)} current records")
        else:
            logging.warning("Current data file not found")
            self.current_df = pd.DataFrame()
            
    def analyze_price_trends(self):
        """Analyze price trends by suburb and postcode"""
        if self.historical_df.empty:
            logging.warning("No historical data available for price trend analysis")
            return
            
        print("\n=== EASTERN SUBURBS PRICE ANALYSIS (PAST 5 YEARS) ===")
        
        # Convert date column
        self.historical_df['Contract date'] = pd.to_datetime(self.historical_df['Contract date'], errors='coerce')
        
        # Remove rows with invalid dates or prices
        valid_data = self.historical_df.dropna(subset=['Contract date', 'Purchase price'])
        valid_data = valid_data[valid_data['Purchase price'] > 0]
        
        # Filter for past 5 years only
        five_years_ago = datetime.now() - pd.DateOffset(years=5)
        valid_data = valid_data[valid_data['Contract date'] >= five_years_ago]
        
        print(f"Analyzing {len(valid_data)} valid sales records")
        
        # Calculate price per square meter if Area data is available
        if 'Area' in valid_data.columns:
            # Filter for properties with valid area data
            area_data = valid_data.dropna(subset=['Area'])
            area_data = area_data[area_data['Area'] > 0]
            
            if len(area_data) > 0:
                area_data['Price_per_sqm'] = area_data['Purchase price'] / area_data['Area']
                
                print(f"\n📏 PRICE PER SQUARE METER ANALYSIS:")
                print(f"📊 Properties with area data: {len(area_data):,} ({len(area_data)/len(valid_data)*100:.1f}% of total)")
                print(f"💰 Average Price/sq.m: ${area_data['Price_per_sqm'].mean():,.0f}")
                print(f"📈 Median Price/sq.m: ${area_data['Price_per_sqm'].median():,.0f}")
                print(f"📊 Price/sq.m Range: ${area_data['Price_per_sqm'].min():,.0f} - ${area_data['Price_per_sqm'].max():,.0f}")
                
                # Price per sqm by postcode
                print(f"\nPrice per Square Meter by Postcode:")
                sqm_stats = area_data.groupby('Property post code')['Price_per_sqm'].agg([
                    'count', 'mean', 'median', 'min', 'max'
                ]).round(0)
                
                sqm_stats.columns = ['Sales Count', 'Avg Price/sq.m', 'Median Price/sq.m', 'Min Price/sq.m', 'Max Price/sq.m']
                sqm_stats = sqm_stats.sort_values('Median Price/sq.m', ascending=False)
                
                print(sqm_stats.head(10))
                
                # Save price per sqm analysis
                sqm_stats.to_csv(os.path.join(self.output_dir, "price_per_sqm_analysis.csv"))
                
                # Monthly price per sqm trends
                monthly_sqm = area_data.groupby(area_data['Contract date'].dt.to_period('M'))['Price_per_sqm'].median()
                if len(monthly_sqm) > 1:
                    print(f"\n📈 Monthly Median Price/sq.m Trends:")
                    print(f"   Latest (3 months): ${monthly_sqm.tail(3).mean():,.0f}")
                    print(f"   Previous (3 months): ${monthly_sqm.tail(6).head(3).mean():,.0f}")
                    if len(monthly_sqm) >= 6:
                        growth = ((monthly_sqm.tail(3).mean() - monthly_sqm.tail(6).head(3).mean()) / monthly_sqm.tail(6).head(3).mean()) * 100
                        print(f"   Growth: {growth:+.1f}%")
        
        # Overall statistics
        # Calculate time range
        date_range = f"{valid_data['Contract date'].min().strftime('%Y-%m')} to {valid_data['Contract date'].max().strftime('%Y-%m')}"
        
        print(f"\nOverall Eastern Suburbs Statistics:")
        print(f"📊 Analysis Period: {date_range}")
        print(f"🏠 Total Properties Analyzed: {len(valid_data):,}")
        print(f"💰 Average Price: ${valid_data['Purchase price'].mean():,.0f}")
        print(f"📈 Median Price: ${valid_data['Purchase price'].median():,.0f}")
        print(f"📊 Price Range: ${valid_data['Purchase price'].min():,.0f} - ${valid_data['Purchase price'].max():,.0f}")
        
        # By postcode
        print(f"\nPrice Statistics by Postcode:")
        postcode_stats = valid_data.groupby('Property post code')['Purchase price'].agg([
            'count', 'mean', 'median', 'min', 'max'
        ]).round(0)
        
        postcode_stats.columns = ['Sales Count', 'Average Price', 'Median Price', 'Min Price', 'Max Price']
        postcode_stats = postcode_stats.sort_values('Average Price', ascending=False)
        
        print(postcode_stats.head(10))
        
        # Save detailed postcode analysis
        postcode_stats.to_csv(os.path.join(self.output_dir, "postcode_analysis.csv"))
        
        return postcode_stats
        
    def analyze_by_suburb(self):
        """Analyze property data by specific suburb"""
        if self.historical_df.empty:
            logging.warning("No historical data available for suburb analysis")
            return
            
        print("\n=== SUBURB ANALYSIS (PAST 5 YEARS) ===")
        
        # Get unique suburbs in Eastern Suburbs data and filter for past 5 years
        eastern_suburbs_data = self.historical_df.copy()
        eastern_suburbs_data['Contract date'] = pd.to_datetime(eastern_suburbs_data['Contract date'], errors='coerce')
        five_years_ago = datetime.now() - pd.DateOffset(years=5)
        eastern_suburbs_data = eastern_suburbs_data[eastern_suburbs_data['Contract date'] >= five_years_ago]
        
        suburb_stats = eastern_suburbs_data.groupby('Property locality')['Purchase price'].agg([
            'count', 'mean', 'median', 'min', 'max'
        ]).round(0)
        
        suburb_stats.columns = ['Sales Count', 'Average Price', 'Median Price', 'Min Price', 'Max Price']
        suburb_stats = suburb_stats.sort_values('Average Price', ascending=False)
        
        print("🏆 Top 15 Most Expensive Eastern Suburbs:")
        print(suburb_stats.head(15))
        
        # Save suburb analysis
        suburb_stats.to_csv(os.path.join(self.output_dir, "suburb_analysis.csv"))
        
        return suburb_stats
        
    def create_visualizations(self):
        """Create visualizations for Eastern Suburbs analysis"""
        if self.historical_df.empty:
            logging.warning("No data available for visualizations")
            return
            
        print("\nCreating visualizations (Past 5 Years)...")
        
        # Filter for Eastern Suburbs and valid data (past 5 years only)
        eastern_data = self.historical_df.copy()
        eastern_data['Contract date'] = pd.to_datetime(eastern_data['Contract date'], errors='coerce')
        eastern_data = eastern_data.dropna(subset=['Purchase price', 'Contract date'])
        eastern_data = eastern_data[eastern_data['Purchase price'] > 0]
        
        # Filter for past 5 years
        five_years_ago = datetime.now() - pd.DateOffset(years=5)
        eastern_data = eastern_data[eastern_data['Contract date'] >= five_years_ago]
        
        # 1. Price distribution by postcode
        plt.figure(figsize=(15, 8))
        postcode_prices = [eastern_data[eastern_data['Property post code'] == pc]['Purchase price'] 
                          for pc in EASTERN_POSTCODES if pc in eastern_data['Property post code'].values]
        postcode_labels = [pc for pc in EASTERN_POSTCODES if pc in eastern_data['Property post code'].values]
        
        plt.boxplot(postcode_prices, labels=postcode_labels)
        plt.title('Property Price Distribution by Eastern Suburbs Postcode (Past 5 Years)')
        plt.xlabel('Postcode')
        plt.ylabel('Price ($)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "price_distribution_by_postcode.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 2. Average price by postcode
        avg_prices = eastern_data.groupby('Property post code')['Purchase price'].mean().sort_values(ascending=False)
        
        plt.figure(figsize=(12, 6))
        avg_prices.plot(kind='bar')
        plt.title('Average Property Prices by Eastern Suburbs Postcode (Past 5 Years)')
        plt.xlabel('Postcode')
        plt.ylabel('Average Price ($)')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "average_prices_by_postcode.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        # 3. Sales volume by postcode
        sales_volume = eastern_data.groupby('Property post code').size().sort_values(ascending=False)
        
        plt.figure(figsize=(12, 6))
        sales_volume.plot(kind='bar')
        plt.title('Property Sales Volume by Eastern Suburbs Postcode (Past 5 Years)')
        plt.xlabel('Postcode')
        plt.ylabel('Number of Sales')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig(os.path.join(self.output_dir, "sales_volume_by_postcode.png"), dpi=300, bbox_inches='tight')
        plt.close()
        
        print(f"Visualizations saved to {self.output_dir}/")
        
    def generate_market_insights(self):
        """Generate market insights for Eastern Suburbs"""
        if self.historical_df.empty:
            logging.warning("No data available for market insights")
            return
            
        print("\n=== EASTERN SUBURBS MARKET INSIGHTS (PAST 5 YEARS) ===")
        
        eastern_data = self.historical_df.copy()
        eastern_data = eastern_data.dropna(subset=['Purchase price'])
        eastern_data = eastern_data[eastern_data['Purchase price'] > 0]
        
        # Convert dates
        eastern_data['Contract date'] = pd.to_datetime(eastern_data['Contract date'], errors='coerce')
        eastern_data = eastern_data.dropna(subset=['Contract date'])
        
        # Filter for past 5 years
        five_years_ago = datetime.now() - pd.DateOffset(years=5)
        eastern_data = eastern_data[eastern_data['Contract date'] >= five_years_ago]
        
        # Recent data (last 2 years)
        recent_date = datetime.now() - pd.DateOffset(years=2)
        recent_data = eastern_data[eastern_data['Contract date'] >= recent_date]
        
        print(f"📅 Analysis Period: {eastern_data['Contract date'].min().strftime('%Y-%m')} to {eastern_data['Contract date'].max().strftime('%Y-%m')}")
        print(f"🏠 Total Properties Analyzed (Past 5 Years): {len(eastern_data):,}")
        print(f"💰 Average Price (Past 5 Years): ${eastern_data['Purchase price'].mean():,.0f}")
        
        print(f"📅 Recent Analysis Period (Last 2 Years): {recent_data['Contract date'].min().strftime('%Y-%m')} to {recent_data['Contract date'].max().strftime('%Y-%m')}")
        print(f"🏠 Recent Properties Analyzed: {len(recent_data):,}")
        print(f"💰 Recent Average Price: ${recent_data['Purchase price'].mean():,.0f}")
        
        # Price growth analysis
        if len(recent_data) > 0 and len(eastern_data) > len(recent_data):
            older_data = eastern_data[eastern_data['Contract date'] < recent_date]
            if len(older_data) > 0:
                recent_avg = recent_data['Purchase price'].mean()
                older_avg = older_data['Purchase price'].mean()
                growth_pct = ((recent_avg - older_avg) / older_avg) * 100
                
                print(f"Price growth (last 2 years vs previous 3 years): {growth_pct:.1f}%")
                
                if growth_pct > 10:
                    print("📈 Strong price growth in Eastern Suburbs")
                elif growth_pct > 5:
                    print("📊 Moderate price growth in Eastern Suburbs")
                elif growth_pct > 0:
                    print("📉 Slight price growth in Eastern Suburbs")
                else:
                    print("📉 Price decline in Eastern Suburbs")
        
        # Price per square meter insights
        if 'Area' in eastern_data.columns:
            area_data = eastern_data.dropna(subset=['Area'])
            area_data = area_data[area_data['Area'] > 0]
            
            if len(area_data) > 0:
                area_data['Price_per_sqm'] = area_data['Purchase price'] / area_data['Area']
                
                # Recent vs older price per sqm
                recent_area_data = area_data[area_data['Contract date'] >= recent_date]
                older_area_data = area_data[area_data['Contract date'] < recent_date]
                
                if len(recent_area_data) > 0 and len(older_area_data) > 0:
                    recent_sqm_median = recent_area_data['Price_per_sqm'].median()
                    older_sqm_median = older_area_data['Price_per_sqm'].median()
                    sqm_growth = ((recent_sqm_median - older_sqm_median) / older_sqm_median) * 100
                    
                    print(f"\n📏 PRICE PER SQUARE METER INSIGHTS:")
                    print(f"   Recent median price/sq.m: ${recent_sqm_median:,.0f}")
                    print(f"   Previous median price/sq.m: ${older_sqm_median:,.0f}")
                    print(f"   Price/sq.m growth: {sqm_growth:+.1f}%")
                    
                    # Compare with current listings if available
                    if not self.current_df.empty and 'Area' in self.current_df.columns:
                        current_area_data = self.current_df.dropna(subset=['Area'])
                        current_area_data = current_area_data[current_area_data['Area'] > 0]
                        
                        if len(current_area_data) > 0:
                            current_area_data['Price_per_sqm'] = current_area_data['price'] / current_area_data['Area']
                            current_sqm_median = current_area_data['Price_per_sqm'].median()
                            
                            print(f"\n🏠 CURRENT LISTINGS vs HISTORICAL SALES:")
                            print(f"   Current listings median price/sq.m: ${current_sqm_median:,.0f}")
                            print(f"   Recent sales median price/sq.m: ${recent_sqm_median:,.0f}")
                            
                            current_vs_recent = ((current_sqm_median - recent_sqm_median) / recent_sqm_median) * 100
                            print(f"   Current vs Recent sales: {current_vs_recent:+.1f}%")
                            
                            if current_vs_recent > 10:
                                print("   📈 Current listings are significantly higher than recent sales")
                            elif current_vs_recent > 5:
                                print("   📊 Current listings are moderately higher than recent sales")
                            elif current_vs_recent > -5:
                                print("   📉 Current listings are in line with recent sales")
                            else:
                                print("   📉 Current listings are below recent sales - potential opportunity")
        
        # Most expensive suburbs
        top_suburbs = eastern_data.groupby('Property locality')['Purchase price'].mean().sort_values(ascending=False).head(5)
        print(f"\n🏆 Top 5 Most Expensive Eastern Suburbs:")
        for suburb, price in top_suburbs.items():
            print(f"  💰 {suburb}: ${price:,.0f}")
            
        # Most active suburbs
        active_suburbs = eastern_data.groupby('Property locality').size().sort_values(ascending=False).head(5)
        print(f"\n📊 Top 5 Most Active Eastern Suburbs (by sales volume):")
        for suburb, count in active_suburbs.items():
            print(f"  🏠 {suburb}: {count:,} properties sold")
            
    def run_full_analysis(self):
        """Run complete Eastern Suburbs analysis"""
        print("🏠 EASTERN SUBURBS SYDNEY PROPERTY ANALYSIS")
        print("=" * 50)
        
        # Load data
        self.load_eastern_suburbs_data()
        
        # Run analyses
        self.analyze_price_trends()
        self.analyze_by_suburb()
        self.create_visualizations()
        self.generate_market_insights()
        
        # Run price per square meter comparison
        self.compare_current_vs_historical_price_per_sqm()
        
        # Run general price comparison (works with any data)
        self.compare_current_vs_historical_prices()
        
        print(f"\n✅ Analysis complete! Results saved to {self.output_dir}/")
        print(f"📊 Generated files:")
        print(f"   - postcode_analysis.csv")
        print(f"   - suburb_analysis.csv")
        print(f"   - price_distribution_by_postcode.png")
        print(f"   - average_prices_by_postcode.png")
        print(f"   - sales_volume_by_postcode.png")
        print(f"   - price_per_sqm_comparison.csv")
        print(f"   - price_per_sqm_comparison.png")
        print(f"   - price_comparison.csv")

    def compare_current_vs_historical_price_per_sqm(self):
        """Comprehensive comparison of current listings vs historical sales price per square meter"""
        print("\n=== CURRENT vs HISTORICAL PRICE PER SQUARE METER COMPARISON ===")
        
        # Check if we have both current and historical data
        if self.current_df.empty:
            print("❌ No current listings data available for comparison")
            return None
            
        if self.historical_df.empty:
            print("❌ No historical sales data available for comparison")
            return None
            
        # Prepare historical data
        historical_data = self.historical_df.copy()
        historical_data['Contract date'] = pd.to_datetime(historical_data['Contract date'], errors='coerce')
        
        # Check if Area data is available in historical data
        if 'Area' not in historical_data.columns:
            print("ℹ️  No Area data available in historical dataset - skipping square meter comparison")
            return None
            
        # Filter for properties with valid area data
        historical_area_data = historical_data.dropna(subset=['Area', 'Purchase price'])
        historical_area_data = historical_area_data[historical_area_data['Area'] > 0]
        historical_area_data = historical_area_data[historical_area_data['Purchase price'] > 0]
        
        if len(historical_area_data) == 0:
            print("ℹ️  No historical data with valid area information available")
            return None
            
        # Calculate historical price per sqm
        historical_area_data['Price_per_sqm'] = historical_area_data['Purchase price'] / historical_area_data['Area']
        
        # Prepare current data
        current_data = self.current_df.copy()
        
        # Check if Area data is available in current data
        if 'Area' not in current_data.columns:
            print("ℹ️  No Area data available in current dataset - skipping square meter comparison")
            return None
            
        current_area_data = current_data.dropna(subset=['Area', 'price'])
        current_area_data = current_area_data[current_area_data['Area'] > 0]
        current_area_data = current_area_data[current_area_data['price'] > 0]
        
        if len(current_area_data) == 0:
            print("ℹ️  No current listings with valid area information available")
            return None
            
        # Calculate current price per sqm
        current_area_data['Price_per_sqm'] = current_area_data['price'] / current_area_data['Area']
        
        print(f"📊 Data Summary:")
        print(f"   Historical sales with area data: {len(historical_area_data):,}")
        print(f"   Current listings with area data: {len(current_area_data):,}")
        
        # Overall comparison
        historical_median = historical_area_data['Price_per_sqm'].median()
        current_median = current_area_data['Price_per_sqm'].median()
        historical_mean = historical_area_data['Price_per_sqm'].mean()
        current_mean = current_area_data['Price_per_sqm'].mean()
        
        print(f"\n💰 OVERALL PRICE PER SQUARE METER COMPARISON:")
        print(f"   Historical Sales (Median): ${historical_median:,.0f}/sqm")
        print(f"   Current Listings (Median): ${current_median:,.0f}/sqm")
        print(f"   Difference: {((current_median - historical_median) / historical_median * 100):+.1f}%")
        
        print(f"\n   Historical Sales (Mean): ${historical_mean:,.0f}/sqm")
        print(f"   Current Listings (Mean): ${current_mean:,.0f}/sqm")
        print(f"   Difference: {((current_mean - historical_mean) / historical_mean * 100):+.1f}%")
        
        # Recent historical comparison (last 2 years)
        two_years_ago = datetime.now() - pd.DateOffset(years=2)
        recent_historical = historical_area_data[historical_area_data['Contract date'] >= two_years_ago]
        
        if len(recent_historical) > 0:
            recent_median = recent_historical['Price_per_sqm'].median()
            recent_mean = recent_historical['Price_per_sqm'].mean()
            
            print(f"\n📈 RECENT SALES COMPARISON (Last 2 Years):")
            print(f"   Recent Sales (Median): ${recent_median:,.0f}/sqm")
            print(f"   Current Listings (Median): ${current_median:,.0f}/sqm")
            print(f"   Difference: {((current_median - recent_median) / recent_median * 100):+.1f}%")
            
            print(f"\n   Recent Sales (Mean): ${recent_mean:,.0f}/sqm")
            print(f"   Current Listings (Mean): ${current_mean:,.0f}/sqm")
            print(f"   Difference: {((current_mean - recent_mean) / recent_mean * 100):+.1f}%")
        
        # Comparison by postcode
        print(f"\n🏘️ PRICE PER SQUARE METER BY POSTCODE:")
        
        comparison_data = []
        
        # Get unique postcodes from both datasets and ensure they're strings
        hist_postcodes = set(historical_area_data['Property post code'].astype(str).unique())
        current_postcodes = set(current_area_data['postcode'].astype(str).unique())
        all_postcodes = hist_postcodes | current_postcodes
        
        for postcode in sorted(all_postcodes):
            # Historical data for this postcode
            hist_postcode_data = historical_area_data[historical_area_data['Property post code'] == str(postcode)]
            current_postcode_data = current_area_data[current_area_data['postcode'] == str(postcode)]
            
            if len(hist_postcode_data) > 0 and len(current_postcode_data) > 0:
                hist_median = hist_postcode_data['Price_per_sqm'].median()
                current_median = current_postcode_data['Price_per_sqm'].median()
                difference_pct = ((current_median - hist_median) / hist_median * 100)
                
                # Get suburb name
                suburb = current_postcode_data['suburb'].iloc[0] if len(current_postcode_data) > 0 else "Unknown"
                
                print(f"   {suburb} ({postcode}):")
                print(f"     Historical: ${hist_median:,.0f}/sqm ({len(hist_postcode_data)} sales)")
                print(f"     Current: ${current_median:,.0f}/sqm ({len(current_postcode_data)} listings)")
                print(f"     Difference: {difference_pct:+.1f}%")
                
                comparison_data.append({
                    'postcode': postcode,
                    'suburb': suburb,
                    'historical_median_price_per_sqm': hist_median,
                    'current_median_price_per_sqm': current_median,
                    'difference_percentage': difference_pct,
                    'historical_sales_count': len(hist_postcode_data),
                    'current_listings_count': len(current_postcode_data)
                })
        
        # Save comparison data
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df = comparison_df.sort_values('difference_percentage', ascending=False)
            comparison_file = os.path.join(self.output_dir, "price_per_sqm_comparison.csv")
            comparison_df.to_csv(comparison_file, index=False)
            
            print(f"\n📊 COMPARISON SUMMARY:")
            print(f"   Postcodes with current listings: {len(comparison_data)}")
            print(f"   Average difference: {comparison_df['difference_percentage'].mean():+.1f}%")
            print(f"   Median difference: {comparison_df['difference_percentage'].median():+.1f}%")
            
            # Market insights
            positive_diff = comparison_df[comparison_df['difference_percentage'] > 0]
            negative_diff = comparison_df[comparison_df['difference_percentage'] < 0]
            
            print(f"\n💡 MARKET INSIGHTS:")
            print(f"   Postcodes where current listings > historical sales: {len(positive_diff)}")
            print(f"   Postcodes where current listings < historical sales: {len(negative_diff)}")
            
            if len(positive_diff) > 0:
                top_overvalued = positive_diff.head(3)
                print(f"\n   📈 Top 3 'Overvalued' Postcodes (Current > Historical):")
                for _, row in top_overvalued.iterrows():
                    print(f"     {row['suburb']} ({row['postcode']}): +{row['difference_percentage']:.1f}%")
            
            if len(negative_diff) > 0:
                top_undervalued = negative_diff.head(3)
                print(f"\n   📉 Top 3 'Undervalued' Postcodes (Current < Historical):")
                for _, row in top_undervalued.iterrows():
                    print(f"     {row['suburb']} ({row['postcode']}): {row['difference_percentage']:.1f}%")
            
            # Create visualization
            self._create_price_per_sqm_comparison_chart(comparison_df)
            
            return comparison_df
        
        return None
    
    def _create_price_per_sqm_comparison_chart(self, comparison_df):
        """Create visualization for price per square meter comparison"""
        try:
            plt.figure(figsize=(14, 8))
            
            # Create bar chart
            x = range(len(comparison_df))
            bars = plt.bar(x, comparison_df['difference_percentage'], 
                          color=['red' if x < 0 else 'green' for x in comparison_df['difference_percentage']])
            
            plt.xlabel('Postcode')
            plt.ylabel('Difference (%)')
            plt.title('Current Listings vs Historical Sales: Price per Square Meter Comparison')
            plt.xticks(x, [f"{row['suburb']}\n({row['postcode']})" for _, row in comparison_df.iterrows()], rotation=45, ha='right')
            
            # Add horizontal line at 0
            plt.axhline(y=0, color='black', linestyle='-', alpha=0.3)
            
            # Add value labels on bars
            for i, bar in enumerate(bars):
                height = bar.get_height()
                plt.text(bar.get_x() + bar.get_width()/2., height + (0.5 if height > 0 else -1),
                        f'{height:+.1f}%', ha='center', va='bottom' if height > 0 else 'top')
            
            plt.tight_layout()
            
            # Save chart
            chart_file = os.path.join(self.output_dir, "price_per_sqm_comparison.png")
            plt.savefig(chart_file, dpi=300, bbox_inches='tight')
            plt.close()
            
            print(f"   📊 Chart saved: price_per_sqm_comparison.png")
            
        except Exception as e:
            logging.error(f"Error creating price per sqm comparison chart: {e}")

    def compare_current_vs_historical_prices(self):
        """General comparison of current listings vs historical sales prices (works with any data)"""
        print("\n=== CURRENT vs HISTORICAL PRICE COMPARISON ===")
        
        # Check if we have both current and historical data
        if self.current_df.empty:
            print("❌ No current listings data available for comparison")
            return None
            
        if self.historical_df.empty:
            print("❌ No historical sales data available for comparison")
            return None
            
        # Prepare historical data
        historical_data = self.historical_df.copy()
        historical_data['Contract date'] = pd.to_datetime(historical_data['Contract date'], errors='coerce')
        
        # Filter for properties with valid price data
        historical_price_data = historical_data.dropna(subset=['Purchase price'])
        historical_price_data = historical_price_data[historical_price_data['Purchase price'] > 0]
        
        if len(historical_price_data) == 0:
            print("ℹ️  No historical data with valid price information available")
            return None
            
        # Prepare current data
        current_data = self.current_df.copy()
        current_price_data = current_data.dropna(subset=['price'])
        current_price_data = current_price_data[current_price_data['price'] > 0]
        
        if len(current_price_data) == 0:
            print("ℹ️  No current listings with valid price information available")
            return None
            
        print(f"📊 Data Summary:")
        print(f"   Historical sales with price data: {len(historical_price_data):,}")
        print(f"   Current listings with price data: {len(current_price_data):,}")
        
        # Overall comparison
        historical_median = historical_price_data['Purchase price'].median()
        current_median = current_price_data['price'].median()
        historical_mean = historical_price_data['Purchase price'].mean()
        current_mean = current_price_data['price'].mean()
        
        print(f"\n💰 OVERALL PRICE COMPARISON:")
        print(f"   Historical Sales (Median): ${historical_median:,.0f}")
        print(f"   Current Listings (Median): ${current_median:,.0f}")
        print(f"   Difference: {((current_median - historical_median) / historical_median * 100):+.1f}%")
        
        print(f"\n   Historical Sales (Mean): ${historical_mean:,.0f}")
        print(f"   Current Listings (Mean): ${current_mean:,.0f}")
        print(f"   Difference: {((current_mean - historical_mean) / historical_mean * 100):+.1f}%")
        
        # Recent historical comparison (last 2 years)
        two_years_ago = datetime.now() - pd.DateOffset(years=2)
        recent_historical = historical_price_data[historical_price_data['Contract date'] >= two_years_ago]
        
        if len(recent_historical) > 0:
            recent_median = recent_historical['Purchase price'].median()
            recent_mean = recent_historical['Purchase price'].mean()
            
            print(f"\n📈 RECENT SALES COMPARISON (Last 2 Years):")
            print(f"   Recent Sales (Median): ${recent_median:,.0f}")
            print(f"   Current Listings (Median): ${current_median:,.0f}")
            print(f"   Difference: {((current_median - recent_median) / recent_median * 100):+.1f}%")
            
            print(f"\n   Recent Sales (Mean): ${recent_mean:,.0f}")
            print(f"   Current Listings (Mean): ${current_mean:,.0f}")
            print(f"   Difference: {((current_mean - recent_mean) / recent_mean * 100):+.1f}%")
        
        # Comparison by postcode (if postcodes match)
        print(f"\n🏘️ PRICE COMPARISON BY POSTCODE:")
        
        comparison_data = []
        
        # Get unique postcodes from both datasets and ensure they're strings
        hist_postcodes = set(historical_price_data['Property post code'].astype(str).unique())
        current_postcodes = set(current_price_data['postcode'].astype(str).unique())
        matching_postcodes = hist_postcodes & current_postcodes  # Only postcodes that exist in both datasets
        
        if len(matching_postcodes) == 0:
            print("ℹ️  No matching postcodes between historical and current data")
            return None
        
        for postcode in sorted(matching_postcodes):
            # Historical data for this postcode
            hist_postcode_data = historical_price_data[historical_price_data['Property post code'] == str(postcode)]
            current_postcode_data = current_price_data[current_price_data['postcode'] == str(postcode)]
            
            if len(hist_postcode_data) > 0 and len(current_postcode_data) > 0:
                hist_median = hist_postcode_data['Purchase price'].median()
                current_median = current_postcode_data['price'].median()
                difference_pct = ((current_median - hist_median) / hist_median * 100)
                
                # Get suburb name
                suburb = current_postcode_data['suburb'].iloc[0] if len(current_postcode_data) > 0 else "Unknown"
                
                print(f"   {suburb} ({postcode}):")
                print(f"     Historical: ${hist_median:,.0f} ({len(hist_postcode_data)} sales)")
                print(f"     Current: ${current_median:,.0f} ({len(current_postcode_data)} listings)")
                print(f"     Difference: {difference_pct:+.1f}%")
                
                comparison_data.append({
                    'postcode': postcode,
                    'suburb': suburb,
                    'historical_median_price': hist_median,
                    'current_median_price': current_median,
                    'difference_percentage': difference_pct,
                    'historical_sales_count': len(hist_postcode_data),
                    'current_listings_count': len(current_postcode_data)
                })
        
        # Save comparison data
        if comparison_data:
            comparison_df = pd.DataFrame(comparison_data)
            comparison_df = comparison_df.sort_values('difference_percentage', ascending=False)
            comparison_file = os.path.join(self.output_dir, "price_comparison.csv")
            comparison_df.to_csv(comparison_file, index=False)
            
            print(f"\n📊 COMPARISON SUMMARY:")
            print(f"   Postcodes with matching data: {len(comparison_data)}")
            print(f"   Average difference: {comparison_df['difference_percentage'].mean():+.1f}%")
            print(f"   Median difference: {comparison_df['difference_percentage'].median():+.1f}%")
            
            # Market insights
            positive_diff = comparison_df[comparison_df['difference_percentage'] > 0]
            negative_diff = comparison_df[comparison_df['difference_percentage'] < 0]
            
            print(f"\n💡 MARKET INSIGHTS:")
            print(f"   Postcodes where current listings > historical sales: {len(positive_diff)}")
            print(f"   Postcodes where current listings < historical sales: {len(negative_diff)}")
            
            if len(positive_diff) > 0:
                top_overvalued = positive_diff.head(3)
                print(f"\n   📈 Top 3 'Overvalued' Postcodes (Current > Historical):")
                for _, row in top_overvalued.iterrows():
                    print(f"     {row['suburb']} ({row['postcode']}): +{row['difference_percentage']:.1f}%")
            
            if len(negative_diff) > 0:
                top_undervalued = negative_diff.head(3)
                print(f"\n   📉 Top 3 'Undervalued' Postcodes (Current < Historical):")
                for _, row in top_undervalued.iterrows():
                    print(f"     {row['suburb']} ({row['postcode']}): {row['difference_percentage']:.1f}%")
            
            return comparison_df
        
        return None

if __name__ == "__main__":
    analyzer = EasternSuburbsAnalyzer()
    analyzer.run_full_analysis()
