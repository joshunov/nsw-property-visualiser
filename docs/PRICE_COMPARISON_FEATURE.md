# Price Comparison Feature Implementation

## Overview

The property analysis system now includes comprehensive comparison functionality between current property listings and historical sales data. This feature provides valuable insights into market trends and helps identify potential opportunities or overvalued properties.

## Features Implemented

### 1. Square Meter Price Comparison

#### `compare_current_vs_historical_price_per_sqm()`
- **Purpose**: Compares price per square meter between current listings and historical sales
- **Data Requirements**: Both datasets must have valid Area and price data
- **Graceful Handling**: Skips comparison if square meter data is not available
- **Output**: Detailed analysis with median/mean comparisons and postcode breakdown

#### Key Features:
- **Overall Comparison**: Compares median and mean price per square meter
- **Recent Sales Comparison**: Focuses on last 2 years of historical data
- **Postcode Analysis**: Breaks down comparison by postcode
- **Market Insights**: Identifies overvalued and undervalued areas
- **Visualization**: Generates comparison charts
- **Data Export**: Saves results to CSV files

### 2. General Price Comparison

#### `compare_current_vs_historical_prices()`
- **Purpose**: Compares overall property prices between current listings and historical sales
- **Data Requirements**: Only requires price data (no square meter data needed)
- **Robust**: Works with any dataset that has price information
- **Output**: Comprehensive price analysis and market insights

#### Key Features:
- **Overall Comparison**: Compares median and mean prices
- **Recent Sales Focus**: Analyzes last 2 years vs. older data
- **Postcode Matching**: Only compares postcodes that exist in both datasets
- **Market Insights**: Identifies price trends and opportunities
- **Data Export**: Saves comparison results to CSV

## Usage Examples

### Basic Usage

```python
from src.analysis.eastern_suburbs_analyzer import EasternSuburbsAnalyzer

# Create analyzer
analyzer = EasternSuburbsAnalyzer()

# Load data
analyzer.load_eastern_suburbs_data()

# Run square meter comparison (if data available)
sqm_result = analyzer.compare_current_vs_historical_price_per_sqm()

# Run general price comparison (always works)
price_result = analyzer.compare_current_vs_historical_prices()
```

### Full Analysis Pipeline

```python
# Run complete analysis including comparisons
analyzer.run_full_analysis()
```

## Output Format

### Square Meter Comparison Output

```
=== CURRENT vs HISTORICAL PRICE PER SQUARE METER COMPARISON ===
📊 Data Summary:
   Historical sales with area data: 75,369
   Current listings with area data: 4

💰 OVERALL PRICE PER SQUARE METER COMPARISON:
   Historical Sales (Median): $6,028/sqm
   Current Listings (Median): $5,369/sqm
   Difference: -10.9%

📈 RECENT SALES COMPARISON (Last 2 Years):
   Recent Sales (Median): $15,000/sqm
   Current Listings (Median): $5,369/sqm
   Difference: -64.2%

💡 MARKET INSIGHTS:
   Postcodes where current listings > historical sales: 0
   Postcodes where current listings < historical sales: 0
```

### General Price Comparison Output

```
=== CURRENT vs HISTORICAL PRICE COMPARISON ===
📊 Data Summary:
   Historical sales with price data: 157,358
   Current listings with price data: 4

💰 OVERALL PRICE COMPARISON:
   Historical Sales (Median): $731,000
   Current Listings (Median): $1,690,154
   Difference: +131.2%

📈 RECENT SALES COMPARISON (Last 2 Years):
   Recent Sales (Median): $1,902,500
   Current Listings (Median): $1,690,154
   Difference: -11.2%
```

## Generated Files

The comparison analysis generates several output files:

1. **`price_per_sqm_comparison.csv`**: Detailed square meter comparison by postcode
2. **`price_per_sqm_comparison.png`**: Visualization of square meter price differences
3. **`price_comparison.csv`**: General price comparison by postcode

### CSV File Structure

#### Square Meter Comparison CSV:
```csv
postcode,suburb,historical_median_price_per_sqm,current_median_price_per_sqm,difference_percentage,historical_sales_count,current_listings_count
2026,Bondi,15000,5369,-64.2,150,2
2031,Coogee,12000,5875,-51.0,200,2
```

#### General Price Comparison CSV:
```csv
postcode,suburb,historical_median_price,current_median_price,difference_percentage,historical_sales_count,current_listings_count
2026,Bondi,1500000,1690154,+12.7,150,2
2031,Coogee,1200000,1615250,+34.6,200,2
```

## Data Requirements

### Square Meter Comparison
- **Historical Data**: Requires `Area` and `Purchase price` columns
- **Current Data**: Requires `Area` and `price` columns
- **Graceful Degradation**: Skips comparison if area data is missing

### General Price Comparison
- **Historical Data**: Requires `Purchase price` column
- **Current Data**: Requires `price` column
- **Postcode Matching**: Only compares postcodes present in both datasets

## Market Insights

The comparison provides several types of market insights:

### 1. Price Trends
- **Overvalued Areas**: Current listings significantly higher than historical sales
- **Undervalued Areas**: Current listings below historical sales (potential opportunities)
- **Market Alignment**: Current listings in line with historical trends

### 2. Temporal Analysis
- **Recent vs. Historical**: Compares last 2 years with older data
- **Growth Patterns**: Identifies areas with strong price growth
- **Market Cycles**: Helps understand current market position

### 3. Geographic Analysis
- **Postcode Breakdown**: Detailed analysis by location
- **Suburb Comparison**: Identifies best and worst performing areas
- **Regional Trends**: Understands broader market patterns

## Error Handling

The comparison methods include robust error handling:

1. **Missing Data**: Gracefully handles missing square meter or price data
2. **No Matching Postcodes**: Continues analysis even if no postcodes match
3. **Empty Datasets**: Provides informative messages for empty data
4. **Invalid Data**: Filters out invalid prices or areas

## Benefits

1. **Market Intelligence**: Provides data-driven market insights
2. **Investment Decisions**: Helps identify undervalued properties
3. **Risk Assessment**: Identifies potentially overvalued areas
4. **Trend Analysis**: Understands market direction and timing
5. **Geographic Focus**: Provides location-specific analysis

## Future Enhancements

1. **More Data Sources**: Extend to additional property websites
2. **Advanced Analytics**: Add statistical significance testing
3. **Predictive Modeling**: Forecast future price trends
4. **Seasonal Analysis**: Account for seasonal price variations
5. **Property Type Filtering**: Compare similar property types

## Integration

The comparison functionality is fully integrated into the existing analysis pipeline:

- **Automatic Execution**: Runs as part of the full analysis
- **Standalone Usage**: Can be run independently
- **Data Compatibility**: Works with existing data formats
- **Output Integration**: Results saved to standard output directory

The price comparison feature provides comprehensive market analysis capabilities while maintaining flexibility to work with whatever data is available.
