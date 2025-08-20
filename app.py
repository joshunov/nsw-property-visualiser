#!/usr/bin/env python3
"""
Sydney Eastern Suburbs Property Analysis - Streamlit Application

A clean, well-organized property market analysis tool with real data
and interactive visualizations.
"""

import streamlit as st
import pandas as pd
from datetime import datetime
import logging
import sys
from pathlib import Path

# Add the current directory to Python path for imports
sys.path.append(str(Path(__file__).parent))

# Import configuration and modules
try:
    from app.config import STREAMLIT_CONFIG
    from app.data import DataLoader, DataProcessor
    from app.visualization import ChartGenerator
except ImportError:
    # Fallback for Streamlit Cloud deployment
    import config
    from data import DataLoader, DataProcessor
    from visualization import ChartGenerator
    STREAMLIT_CONFIG = config.STREAMLIT_CONFIG

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration
st.set_page_config(**STREAMLIT_CONFIG)

# Custom CSS for theme-aware styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: var(--primary-color);
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: var(--background-color);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--primary-color);
        border: 1px solid var(--border-color);
    }
    .insight-box {
        background-color: var(--background-color);
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid var(--accent-color);
        border: 1px solid var(--border-color);
    }
    .data-source-success {
        background-color: rgba(0, 255, 0, 0.1);
        padding: 0.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #00ff00;
        margin-bottom: 1rem;
    }
    .data-source-warning {
        background-color: rgba(255, 165, 0, 0.1);
        padding: 0.5rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ffa500;
        margin-bottom: 1rem;
    }
    .suburb-list {
        background-color: var(--background-color);
        padding: 0.5rem;
        border-radius: 0.5rem;
        border: 1px solid var(--border-color);
        margin-top: 0.5rem;
    }
    .price-highlight {
        color: var(--primary-color);
        font-weight: bold;
    }
    .growth-positive {
        color: #00ff00;
        font-weight: bold;
    }
    .growth-negative {
        color: #ff4444;
        font-weight: bold;
    }
    
    /* Ensure charts work well in both themes */
    .js-plotly-plot .plotly .main-svg {
        background-color: transparent !important;
    }
    
    /* Improve readability in dark mode */
    @media (prefers-color-scheme: dark) {
        .data-source-success {
            background-color: rgba(0, 255, 0, 0.2);
        }
        .data-source-warning {
            background-color: rgba(255, 165, 0, 0.2);
        }
    }
    
    /* Ensure text is readable in both themes */
    .stMarkdown, .stText {
        color: var(--text-color);
    }
</style>
""", unsafe_allow_html=True)


@st.cache_data(ttl=60)  # Cache for 1 minute to prevent stale data
def load_data():
    """Load property data with caching"""
    loader = DataLoader()
    data = loader.load_all_data()
    
    # Debug logging
    print(f"🔍 Data loaded: {len(data['current_data'])} current, {len(data['historical_data'])} historical")
    if len(data['current_data']) > 0:
        print(f"🔍 Sample address: {data['current_data']['address'].iloc[0]}")
    
    return data


def show_dashboard(data_processor: DataProcessor, data_loader: DataLoader):
    """Display the main dashboard"""
    st.header("📊 Property Market Dashboard")
    
    # Data source indicator
    current_file = data_loader._current_data is not None and hasattr(data_loader, '_current_data')
    historical_file = data_loader._historical_data is not None and hasattr(data_loader, '_historical_data')
    
    if current_file and historical_file:
        st.markdown(f"""
        <div class="data-source-success">
            <strong>✅ Real Data Loaded</strong><br>
            {len(data_processor.current_data)} current properties + {len(data_processor.historical_data):,} historical properties
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div class="data-source-warning">
            <strong>⚠️ Sample Data</strong><br>
            Using generated sample data (run the extractor to get real data)
        </div>
        """, unsafe_allow_html=True)
    
    # Key metrics
    stats = data_processor.get_basic_stats()
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Historical Sales",
            value=f"{stats['historical_count']:,}",
            help="Total number of historical property sales"
        )
    
    with col2:
        st.metric(
            label="Current Listings",
            value=f"{stats['current_count']:,}",
            help="Total number of current property listings"
        )
    
    with col3:
        st.metric(
            label="Historical Sales",
            value=f"{stats['historical_suburbs']}",
            help="Number of suburbs with historical data"
        )
    
    with col4:
        st.metric(
            label="Current Listings",
            value=f"{stats['current_suburbs']}",
            help="Number of suburbs with current listings"
        )
    
    # Data overview
    st.subheader("📋 Data Overview")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.write("**Historical Sales Data**")
        st.write(f"- **Records**: {stats['historical_count']:,}")
        st.write(f"- **Date Range**: {stats['historical_date_range'][0].strftime('%Y-%m-%d')} to {stats['historical_date_range'][1].strftime('%Y-%m-%d')}")
        st.write(f"- **Suburbs**: {stats['historical_suburbs']}")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.write("**Current Listings Data**")
        st.write(f"- **Records**: {stats['current_count']:,}")
        st.write(f"- **Suburbs**: {stats['current_suburbs']}")
        
        # Show top suburbs by listings
        top_suburbs = data_processor.get_top_suburbs_by_listings()
        if not top_suburbs.empty:
            st.markdown('<div class="suburb-list">', unsafe_allow_html=True)
            st.write("**Top 5 Suburbs by Listings:**")
            for suburb, count in top_suburbs.items():
                st.write(f"- {suburb}: {count} properties")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Market insights
    st.subheader("💡 Market Insights")
    growth_data = data_processor.get_price_growth()
    
    col1, col2 = st.columns(2)
    
    with col1:
        growth_class = "growth-positive" if growth_data['growth_percentage'] >= 0 else "growth-negative"
        growth_sign = "+" if growth_data['growth_percentage'] >= 0 else ""
        st.markdown(f"""
        <div class="insight-box">
            <h4>📈 Price Growth Trend</h4>
            <p>Historical median: <span class="price-highlight">${growth_data['historical_median']:,.0f}</span></p>
            <p>Current median: <span class="price-highlight">${growth_data['current_median']:,.0f}</span></p>
            <p>Growth: <span class="{growth_class}">{growth_sign}{growth_data['growth_percentage']:.1f}%</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Top performing suburbs
        suburb_performance = data_processor.get_suburb_performance(3)
        st.markdown(f"""
        <div class="insight-box">
            <h4>🏆 Top 3 Most Expensive Suburbs</h4>
            <ol>
                <li><strong>{suburb_performance.index[0]}</strong>: <span class="price-highlight">${suburb_performance.iloc[0]['Average Price']:,.0f}</span></li>
                <li><strong>{suburb_performance.index[1]}</strong>: <span class="price-highlight">${suburb_performance.iloc[1]['Average Price']:,.0f}</span></li>
                <li><strong>{suburb_performance.index[2]}</strong>: <span class="price-highlight">${suburb_performance.iloc[2]['Average Price']:,.0f}</span></li>
            </ol>
        </div>
        """, unsafe_allow_html=True)


def show_price_analysis(data_processor: DataProcessor):
    """Display price analysis page"""
    st.header("📈 Price Analysis")
    
    # Price trends over time
    st.subheader("📊 Price Trends Over Time")
    monthly_data = data_processor.get_monthly_trends()
    trend_chart = ChartGenerator.create_price_trend_chart(monthly_data)
    st.plotly_chart(trend_chart, use_container_width=True)
    
    # Price distribution
    st.subheader("📊 Price Distribution")
    col1, col2 = st.columns(2)
    
    with col1:
        dist_chart = ChartGenerator.create_price_distribution_chart(data_processor.historical_data)
        st.plotly_chart(dist_chart, use_container_width=True)
    
    with col2:
        # Price statistics
        price_stats = data_processor.historical_data['Purchase price'].describe()
        st.write("**Price Statistics**")
        st.write(f"- **Mean**: ${price_stats['mean']:,.0f}")
        st.write(f"- **Median**: ${price_stats['50%']:,.0f}")
        st.write(f"- **Min**: ${price_stats['min']:,.0f}")
        st.write(f"- **Max**: ${price_stats['max']:,.0f}")
        st.write(f"- **Std Dev**: ${price_stats['std']:,.0f}")
        
        # Price ranges
        st.write("**Price Ranges**")
        distribution = data_processor.get_price_distribution()
        for item in distribution:
            st.write(f"- **{item['range']}**: {item['count']:,} ({item['percentage']:.1f}%)")


def show_suburb_analysis(data_processor: DataProcessor):
    """Display suburb analysis page"""
    st.header("🏘️ Suburb Analysis")
    
    # Suburb performance
    st.subheader("🏆 Suburb Performance Rankings")
    suburb_stats = data_processor.get_suburb_performance(10)
    
    # Top 10 most expensive suburbs
    st.write("**Top 10 Most Expensive Suburbs**")
    suburb_chart = ChartGenerator.create_suburb_performance_chart(suburb_stats)
    st.plotly_chart(suburb_chart, use_container_width=True)
    
    # Display table
    st.dataframe(suburb_stats, use_container_width=True)
    
    # Suburb comparison
    st.subheader("📊 Suburb Comparison")
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales volume by suburb
        suburb_volume = data_processor.historical_data.groupby('Property locality').size().sort_values(ascending=False).head(10)
        volume_chart = ChartGenerator.create_sales_volume_chart(suburb_volume)
        st.plotly_chart(volume_chart, use_container_width=True)
    
    with col2:
        # Price vs volume scatter
        suburb_summary = data_processor.historical_data.groupby('Property locality').agg({
            'Purchase price': ['mean', 'count']
        }).round(0)
        suburb_summary.columns = ['Average Price', 'Sales Count']
        
        scatter_chart = ChartGenerator.create_price_vs_volume_scatter(suburb_summary)
        st.plotly_chart(scatter_chart, use_container_width=True)


def show_price_comparisons(data_processor: DataProcessor):
    """Display price comparison analysis"""
    st.header("💰 Price Comparisons")
    
    # Overall comparison
    st.subheader("📊 Overall Price Comparison")
    growth_data = data_processor.get_price_growth()
    
    col1, col2 = st.columns(2)
    
    with col1:
        comparison_chart = ChartGenerator.create_price_comparison_chart(
            growth_data['historical_median'], 
            growth_data['current_median']
        )
        st.plotly_chart(comparison_chart, use_container_width=True)
        
        # Calculate difference
        st.metric(
            label="Price Difference",
            value=f"{growth_data['growth_percentage']:+.1f}%",
            delta=f"{growth_data['growth_percentage']:+.1f}%"
        )
    
    with col2:
        # Price distribution comparison
        dist_comparison_chart = ChartGenerator.create_distribution_comparison_chart(
            data_processor.historical_data, 
            data_processor.current_data
        )
        st.plotly_chart(dist_comparison_chart, use_container_width=True)
    
    # Suburb-level comparison
    st.subheader("🏘️ Suburb-Level Comparison")
    comparison_df = data_processor.get_suburb_comparison()
    
    if not comparison_df.empty:
        suburb_comparison_chart = ChartGenerator.create_suburb_comparison_chart(comparison_df)
        st.plotly_chart(suburb_comparison_chart, use_container_width=True)
        st.dataframe(comparison_df, use_container_width=True)
    else:
        st.info("No matching suburbs found between historical and current data")


def show_property_details(data_processor: DataProcessor):
    """Display detailed property information with insights"""
    st.header("🏠 Property Details & Insights")
    
    # Filter controls
    col1, col2, col3 = st.columns(3)
    
    with col1:
        # Suburb filter
        available_suburbs = sorted(data_processor.current_data['suburb'].unique())
        selected_suburb = st.selectbox(
            "Filter by suburb:",
            options=['All Suburbs'] + available_suburbs,
            index=0
        )
    
    with col2:
        # Property type filter
        if 'property_type' in data_processor.current_data.columns:
            property_types = sorted(data_processor.current_data['property_type'].unique())
            selected_type = st.selectbox(
                "Filter by property type:",
                options=['All Types'] + property_types,
                index=0
            )
        else:
            selected_type = 'All Types'
    
    with col3:
        # Price range filter
        max_price = data_processor.current_data['price'].max()
        min_price = data_processor.current_data['price'].min()
        price_range = st.slider(
            "Price range:",
            min_value=int(min_price),
            max_value=int(max_price),
            value=(int(min_price), int(max_price)),
            format="$%d"
        )
    
    # Apply filters
    filtered_data = data_processor.current_data.copy()
    
    if selected_suburb != 'All Suburbs':
        filtered_data = filtered_data[filtered_data['suburb'] == selected_suburb]
    
    if selected_type != 'All Types' and 'property_type' in filtered_data.columns:
        filtered_data = filtered_data[filtered_data['property_type'] == selected_type]
    
    filtered_data = filtered_data[
        (filtered_data['price'] >= price_range[0]) & 
        (filtered_data['price'] <= price_range[1])
    ]
    
    st.write(f"**Showing {len(filtered_data)} properties**")
    
    if filtered_data.empty:
        st.warning("No properties match your filter criteria.")
        return
    
    # Property cards
    for idx, property_row in filtered_data.iterrows():
        # Format the property display text
        address = property_row.get('address', 'Address not available')
        price_display = property_row.get('price_display', f"${property_row['price']:,.0f}")
        
        with st.expander(f"🏠 {address} - {price_display}"):
            
            # Property details section
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown('<div class="metric-card">', unsafe_allow_html=True)
                st.subheader("🏠 Property Details")
                
                # Basic info
                st.write(f"**Address:** {property_row.get('address', 'Not available')}")
                st.write(f"**Suburb:** {property_row.get('suburb', 'Not available')}")
                price_text = property_row.get('price_display', f"${property_row['price']:,.0f}")
                st.write(f"**Price:** {price_text}")
                
                if 'property_type' in property_row:
                    st.write(f"**Type:** {property_row['property_type']}")
                
                if 'bedrooms' in property_row:
                    st.write(f"**Bedrooms:** {property_row['bedrooms']}")
                
                if 'bathrooms' in property_row:
                    st.write(f"**Bathrooms:** {property_row['bathrooms']}")
                
                if 'parking' in property_row:
                    st.write(f"**Parking:** {property_row['parking']}")
                
                if 'Area' in property_row or 'square_meters' in property_row:
                    area = property_row.get('Area', property_row.get('square_meters', 0))
                    if area > 0:
                        st.write(f"**Area:** {area:.0f} m²")
                        price_per_sqm = property_row['price'] / area
                        st.write(f"**Price per m²:** ${price_per_sqm:,.0f}")
                
                if 'listing_date' in property_row:
                    st.write(f"**Listed:** {property_row['listing_date']}")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            with col2:
                # Market insights
                st.markdown('<div class="insight-box">', unsafe_allow_html=True)
                st.subheader("📊 Market Insights")
                
                insights = data_processor.get_property_insights(property_row)
                
                if insights['suburb_sales_count'] > 0:
                    st.write(f"**Suburb Avg Price:** ${insights['suburb_avg_price']:,.0f}")
                    st.write(f"**Suburb Median:** ${insights['suburb_median_price']:,.0f}")
                    
                    # Price comparison
                    if insights['price_vs_avg'] > 10:
                        price_indicator = "🔴 Above Average"
                        price_class = "growth-negative"
                    elif insights['price_vs_avg'] < -10:
                        price_indicator = "🟢 Below Average"
                        price_class = "growth-positive"
                    else:
                        price_indicator = "🟡 Average"
                        price_class = ""
                    
                    st.markdown(f"**Price vs Average:** <span class='{price_class}'>{insights['price_vs_avg']:+.1f}%</span> {price_indicator}", unsafe_allow_html=True)
                    
                    # Percentile
                    if insights['price_percentile'] > 0:
                        st.write(f"**Price Percentile:** {insights['price_percentile']:.0f}th percentile")
                    
                    # Area comparison
                    if insights['area_comparison'] != 'Unknown':
                        st.write(f"**Size:** {insights['area_comparison']}")
                    
                    # Price trend
                    if insights['price_trend'] != 'Unknown':
                        if 'Rising' in insights['price_trend']:
                            trend_class = "growth-positive"
                            trend_icon = "📈"
                        elif 'Declining' in insights['price_trend']:
                            trend_class = "growth-negative" 
                            trend_icon = "📉"
                        else:
                            trend_class = ""
                            trend_icon = "📊"
                        
                        st.markdown(f"**Market Trend:** <span class='{trend_class}'>{insights['price_trend']}</span> {trend_icon}", unsafe_allow_html=True)
                    
                    st.write(f"**Historical Sales:** {insights['suburb_sales_count']} in last 5 years")
                else:
                    st.write("No historical data available for this suburb")
                
                st.markdown('</div>', unsafe_allow_html=True)
            
            # Similar properties section
            st.subheader("🔍 Similar Properties Sold Recently")
            similar_props = data_processor.get_similar_properties(property_row, limit=3)
            
            if not similar_props.empty:
                # Clean up the similar properties display
                display_similar = similar_props.copy()
                display_similar['Contract date'] = pd.to_datetime(display_similar['Contract date']).dt.strftime('%Y-%m-%d')
                display_similar['Purchase price'] = display_similar['Purchase price'].apply(lambda x: f"${x:,.0f}")
                display_similar['Area'] = display_similar['Area'].apply(lambda x: f"{x:.0f} m²" if pd.notna(x) else "N/A")
                display_similar = display_similar.drop('similarity_score', axis=1)
                display_similar.columns = ['Sale Date', 'Sale Price', 'Area', 'Postcode']
                
                st.dataframe(display_similar, use_container_width=True, hide_index=True)
            else:
                st.info("No similar properties found in historical data")


def show_data_explorer(data_processor: DataProcessor):
    """Display interactive data explorer"""
    st.header("📋 Data Explorer")
    
    # Data selection
    data_type = st.selectbox("Select data to explore:", ["Historical Sales", "Current Listings"])
    
    if data_type == "Historical Sales":
        st.subheader("Historical Sales Data")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date range filter
            min_date = data_processor.historical_data['Contract date'].min()
            max_date = data_processor.historical_data['Contract date'].max()
            
            date_range = st.date_input(
                "Select date range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        with col2:
            # Price range filter
            min_price = data_processor.historical_data['Purchase price'].min()
            max_price = data_processor.historical_data['Purchase price'].max()
            
            price_range = st.slider(
                "Price range ($):",
                min_value=float(min_price),
                max_value=float(max_price),
                value=(float(min_price), float(max_price))
            )
        
        with col3:
            # Suburb filter
            suburbs = sorted(data_processor.historical_data['Property locality'].unique())
            selected_suburbs = st.multiselect(
                "Select suburbs:",
                options=suburbs,
                default=suburbs[:3]
            )
        
        # Apply filters
        filtered_data = data_processor.historical_data.copy()
        
        if len(date_range) == 2:
            filtered_data = filtered_data[
                (filtered_data['Contract date'] >= pd.Timestamp(date_range[0])) &
                (filtered_data['Contract date'] <= pd.Timestamp(date_range[1]))
            ]
        
        filtered_data = filtered_data[
            (filtered_data['Purchase price'] >= price_range[0]) &
            (filtered_data['Purchase price'] <= price_range[1])
        ]
        
        if selected_suburbs:
            filtered_data = filtered_data[filtered_data['Property locality'].isin(selected_suburbs)]
        
        # Display filtered data
        st.write(f"**Showing {len(filtered_data):,} records**")
        st.dataframe(filtered_data.head(100), use_container_width=True)
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name=f"filtered_historical_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )
    
    elif data_type == "Current Listings":
        st.subheader("Current Listings Data")
        
        # Display current data
        st.write(f"**Showing {len(data_processor.current_data):,} records**")
        st.dataframe(data_processor.current_data, use_container_width=True)
        
        # Download button
        csv = data_processor.current_data.to_csv(index=False)
        st.download_button(
            label="Download current data as CSV",
            data=csv,
            file_name=f"current_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )


def main():
    """Main application function"""
    # Header
    st.markdown('<h1 class="main-header">🏠 Sydney Eastern Suburbs Property Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    
    # Theme toggle for testing
    st.sidebar.subheader("🎨 Theme")
    theme_mode = st.sidebar.selectbox(
        "Choose theme:",
        ["Light", "Dark"],
        help="Toggle between light and dark themes"
    )
    
    # Apply theme (this is just for display - actual theme is controlled by Streamlit settings)
    if theme_mode == "Dark":
        st.sidebar.info("💡 Switch to dark mode in Streamlit settings (☰ menu)")
    else:
        st.sidebar.info("💡 Switch to light mode in Streamlit settings (☰ menu)")
    
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📊 Dashboard", "📈 Price Analysis", "🏘️ Suburb Analysis", "💰 Price Comparisons", "🏠 Property Details", "📋 Data Explorer"]
    )
    
    # Load data
    with st.spinner("Loading property data..."):
        data_dict = load_data()
        data_loader = DataLoader()
        data_loader._current_data = data_dict['current_data']
        data_loader._historical_data = data_dict['historical_data']
        data_processor = DataProcessor(data_dict['historical_data'], data_dict['current_data'])
    
    # Show data source info in sidebar
    if data_loader._current_data is not None and data_loader._historical_data is not None:
        st.sidebar.markdown(f"""
        <div class="data-source-success">
            <strong>📊 Real Data</strong><br>
            {len(data_dict['current_data'])} current + {len(data_dict['historical_data']):,} historical
        </div>
        """, unsafe_allow_html=True)
    else:
        st.sidebar.markdown(f"""
        <div class="data-source-warning">
            <strong>📊 Sample Data</strong><br>
            Demo mode
        </div>
        """, unsafe_allow_html=True)
    
    # Page routing
    if page == "📊 Dashboard":
        show_dashboard(data_processor, data_loader)
    elif page == "📈 Price Analysis":
        show_price_analysis(data_processor)
    elif page == "🏘️ Suburb Analysis":
        show_suburb_analysis(data_processor)
    elif page == "💰 Price Comparisons":
        show_price_comparisons(data_processor)
    elif page == "🏠 Property Details":
        show_property_details(data_processor)
    elif page == "📋 Data Explorer":
        show_data_explorer(data_processor)


if __name__ == "__main__":
    main()
