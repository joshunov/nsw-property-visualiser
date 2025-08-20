#!/usr/bin/env python3
"""
Simple Streamlit Web Application for Property Analysis
No external dependencies - works reliably on Streamlit Cloud
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import numpy as np
from datetime import datetime, timedelta
import os # Added for file path handling

# Page configuration
st.set_page_config(
    page_title="Sydney Eastern Suburbs Property Analysis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling - Theme-aware colors
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

@st.cache_data
def load_property_data():
    """Load real property data from the extractor"""
    try:
        # Try to load current data from the extractor output
        current_file = os.path.join('src', 'data', 'current_property_data.csv')
        if os.path.exists(current_file):
            current_data = pd.read_csv(current_file)
            st.success(f"✅ Loaded {len(current_data)} current properties from real data")
        else:
            # Fallback to sample data if real data not found
            st.warning("⚠️ Real current data not found, using sample data")
            current_data = generate_sample_current_data()
        
        # Try to load real historical data
        historical_file = os.path.join('data', 'extract-3-very-clean.csv')
        if os.path.exists(historical_file):
            try:
                # Load only Eastern Suburbs data to keep it manageable
                eastern_suburbs = ['Bondi', 'Coogee', 'Double Bay', 'Vaucluse', 'Bronte', 'Rose Bay', 'Bellevue Hill', 'Paddington', 'Woollahra', 'Bondi Junction', 'Waverley', 'Queens Park', 'Bondi Beach', 'North Bondi', 'Tamarama', 'Edgecliff', 'Dover Heights', 'Watsons Bay', 'Clovelly', 'South Coogee', 'Kensington', 'Maroubra', 'Maroubra South', 'Pagewood', 'Eastgardens', 'Chifley', 'Malabar', 'Little Bay', 'Phillip Bay']
                
                # Read the full dataset
                full_historical = pd.read_csv(historical_file, low_memory=False)
                
                # Filter for Eastern Suburbs
                historical_data = full_historical[full_historical['Property locality'].isin(eastern_suburbs)].copy()
                
                # Convert date column
                historical_data['Contract date'] = pd.to_datetime(historical_data['Contract date'], errors='coerce')
                
                # Remove rows with invalid dates
                historical_data = historical_data.dropna(subset=['Contract date'])
                
                # Filter for recent data (last 5 years to keep it manageable)
                five_years_ago = pd.Timestamp.now() - pd.DateOffset(years=5)
                historical_data = historical_data[historical_data['Contract date'] >= five_years_ago]
                
                st.success(f"✅ Loaded {len(historical_data):,} historical properties from real data (last 5 years)")
                
            except Exception as e:
                st.warning(f"⚠️ Error loading historical data: {e}, using sample data")
                historical_data = generate_sample_historical_data()
        else:
            # Fallback to sample data if real data not found
            st.warning("⚠️ Real historical data not found, using sample data")
            historical_data = generate_sample_historical_data()
        
        return {
            'historical_data': historical_data,
            'current_data': current_data
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        # Fallback to sample data
        return {
            'historical_data': generate_sample_historical_data(),
            'current_data': generate_sample_current_data()
        }

@st.cache_data
def generate_sample_current_data():
    """Generate sample current data as fallback"""
    # Eastern Suburbs data
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
    
    # Generate current listings data (20 records)
    current_data = []
    for suburb, info in suburbs_data.items():
        for _ in range(np.random.randint(2, 5)):  # 2-4 listings per suburb
            base_price = info['avg_price'] * 1.1  # Current prices slightly higher
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

@st.cache_data
def generate_sample_historical_data():
    """Generate sample historical data for comparison"""
    # Eastern Suburbs data
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
    
    # Generate historical data (1000 records)
    sample_historical = pd.DataFrame({
        'Contract date': pd.date_range('2020-01-01', periods=1000, freq='D'),
        'Purchase price': np.random.normal(1500000, 500000, 1000),
        'Property post code': np.random.choice(['2026', '2031', '2027', '2029'], 1000),
        'Property locality': np.random.choice(['Bondi', 'Coogee', 'Double Bay', 'Vaucluse'], 1000),
        'Area': np.random.normal(200, 50, 1000)
    })
    
    # Ensure positive values
    sample_historical['Purchase price'] = sample_historical['Purchase price'].abs()
    sample_historical['Area'] = sample_historical['Area'].abs()
    
    return sample_historical

def show_dashboard(historical_data, current_data):
    """Show the main dashboard"""
    st.header("📊 Property Market Dashboard")
    
    # Data source indicator with better styling
    current_file = os.path.join('src', 'data', 'current_property_data.csv')
    historical_file = os.path.join('data', 'extract-3-very-clean.csv')
    
    # Check if we're using real data
    using_real_current = os.path.exists(current_file)
    using_real_historical = os.path.exists(historical_file)
    
    if using_real_current and using_real_historical:
        st.markdown(f"""
        <div class="data-source-success">
            <strong>✅ Real Data Loaded</strong><br>
            {len(current_data)} current properties + {len(historical_data):,} historical properties (last 5 years)
        </div>
        """, unsafe_allow_html=True)
    elif using_real_current:
        st.markdown(f"""
        <div class="data-source-success">
            <strong>✅ Real Current Data</strong><br>
            {len(current_data)} current properties from Eastern Suburbs extractor
        </div>
        """, unsafe_allow_html=True)
        st.markdown(f"""
        <div class="data-source-warning">
            <strong>⚠️ Sample Historical Data</strong><br>
            Using generated sample data for historical comparison
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
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            label="Historical Sales",
            value=f"{len(historical_data):,}",
            help="Total number of historical property sales"
        )
    
    with col2:
        st.metric(
            label="Current Listings",
            value=f"{len(current_data):,}",
            help="Total number of current property listings"
        )
    
    with col3:
        avg_price = historical_data['Purchase price'].mean()
        st.metric(
            label="Average Historical Price",
            value=f"${avg_price:,.0f}",
            help="Average price of historical sales"
        )
    
    with col4:
        avg_current = current_data['price'].mean()
        st.metric(
            label="Average Current Price",
            value=f"${avg_current:,.0f}",
            help="Average price of current listings"
        )
    
    # Data overview
    st.subheader("📋 Data Overview")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.write("**Historical Sales Data**")
        st.write(f"- **Records**: {len(historical_data):,}")
        st.write(f"- **Date Range**: {historical_data['Contract date'].min().strftime('%Y-%m-%d')} to {historical_data['Contract date'].max().strftime('%Y-%m-%d')}")
        st.write(f"- **Postcodes**: {historical_data['Property post code'].nunique()}")
        st.write(f"- **Suburbs**: {historical_data['Property locality'].nunique()}")
        if using_real_historical:
            st.write(f"- **Data Source**: Real NSW property data")
        else:
            st.write(f"- **Data Source**: Sample data")
        st.markdown('</div>', unsafe_allow_html=True)
    
    with col2:
        st.markdown('<div class="metric-card">', unsafe_allow_html=True)
        st.write("**Current Listings Data**")
        st.write(f"- **Records**: {len(current_data):,}")
        st.write(f"- **Postcodes**: {current_data['postcode'].nunique()}")
        st.write(f"- **Suburbs**: {current_data['suburb'].nunique()}")
        if 'Area' in current_data.columns:
            st.write(f"- **With Area Data**: {current_data['Area'].notna().sum()}")
        if using_real_current:
            st.write(f"- **Data Source**: Real Eastern Suburbs extractor")
        else:
            st.write(f"- **Data Source**: Sample data")
        
        # Show top suburbs by property count
        if len(current_data) > 0:
            suburb_counts = current_data['suburb'].value_counts().head(5)
            st.markdown('<div class="suburb-list">', unsafe_allow_html=True)
            st.write("**Top 5 Suburbs by Listings:**")
            for suburb, count in suburb_counts.items():
                st.write(f"- {suburb}: {count} properties")
            st.markdown('</div>', unsafe_allow_html=True)
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Market insights
    st.subheader("💡 Market Insights")
    
    # Calculate price growth
    hist_median = historical_data['Purchase price'].median()
    current_median = current_data['price'].median()
    growth = ((current_median - hist_median) / hist_median) * 100
    
    col1, col2 = st.columns(2)
    
    with col1:
        growth_class = "growth-positive" if growth >= 0 else "growth-negative"
        growth_sign = "+" if growth >= 0 else ""
        st.markdown(f"""
        <div class="insight-box">
            <h4>📈 Price Growth Trend</h4>
            <p>Historical median: <span class="price-highlight">${hist_median:,.0f}</span></p>
            <p>Current median: <span class="price-highlight">${current_median:,.0f}</span></p>
            <p>Growth: <span class="{growth_class}">{growth_sign}{growth:.1f}%</span></p>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        # Top performing suburbs
        suburb_performance = historical_data.groupby('Property locality')['Purchase price'].mean().sort_values(ascending=False).head(3)
        st.markdown(f"""
        <div class="insight-box">
            <h4>🏆 Top 3 Most Expensive Suburbs</h4>
            <ol>
                <li><strong>{suburb_performance.index[0]}</strong>: <span class="price-highlight">${suburb_performance.iloc[0]:,.0f}</span></li>
                <li><strong>{suburb_performance.index[1]}</strong>: <span class="price-highlight">${suburb_performance.iloc[1]:,.0f}</span></li>
                <li><strong>{suburb_performance.index[2]}</strong>: <span class="price-highlight">${suburb_performance.iloc[2]:,.0f}</span></li>
            </ol>
        </div>
        """, unsafe_allow_html=True)

def show_price_analysis(historical_data):
    """Show detailed price analysis"""
    st.header("📈 Price Analysis")
    
    # Price trends over time
    st.subheader("📊 Price Trends Over Time")
    
    # Monthly price trends
    historical_data['Contract date'] = pd.to_datetime(historical_data['Contract date'])
    monthly_prices = historical_data.groupby(historical_data['Contract date'].dt.to_period('M'))['Purchase price'].agg(['mean', 'median', 'count'])
    monthly_prices.index = monthly_prices.index.astype(str)
    
    # Create price trend chart
    fig = make_subplots(
        rows=2, cols=1,
        subplot_titles=('Average Price Over Time', 'Sales Volume Over Time'),
        vertical_spacing=0.1
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_prices.index, y=monthly_prices['mean'], 
                  mode='lines+markers', name='Average Price', line=dict(color='blue')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Scatter(x=monthly_prices.index, y=monthly_prices['median'], 
                  mode='lines+markers', name='Median Price', line=dict(color='red')),
        row=1, col=1
    )
    
    fig.add_trace(
        go.Bar(x=monthly_prices.index, y=monthly_prices['count'], 
               name='Sales Volume', marker_color='green'),
        row=2, col=1
    )
    
    fig.update_layout(height=600, showlegend=True)
    st.plotly_chart(fig, use_container_width=True)
    
    # Price distribution
    st.subheader("📊 Price Distribution")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Price histogram
        fig = px.histogram(
            historical_data, 
            x='Purchase price', 
            nbins=30,
            title="Price Distribution",
            labels={'Purchase price': 'Price ($)', 'count': 'Number of Properties'}
        )
        fig.update_layout(showlegend=False)
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price statistics
        price_stats = historical_data['Purchase price'].describe()
        st.write("**Price Statistics**")
        st.write(f"- **Mean**: ${price_stats['mean']:,.0f}")
        st.write(f"- **Median**: ${price_stats['50%']:,.0f}")
        st.write(f"- **Min**: ${price_stats['min']:,.0f}")
        st.write(f"- **Max**: ${price_stats['max']:,.0f}")
        st.write(f"- **Std Dev**: ${price_stats['std']:,.0f}")
        
        # Price ranges
        st.write("**Price Ranges**")
        ranges = [
            (0, 1000000, "Under $1M"),
            (1000000, 2000000, "$1M - $2M"),
            (2000000, 3000000, "$2M - $3M"),
            (3000000, 5000000, "$3M - $5M"),
            (5000000, float('inf'), "Over $5M")
        ]
        
        for min_price, max_price, label in ranges:
            if max_price == float('inf'):
                count = len(historical_data[historical_data['Purchase price'] >= min_price])
            else:
                count = len(historical_data[(historical_data['Purchase price'] >= min_price) & (historical_data['Purchase price'] < max_price)])
            percentage = (count / len(historical_data)) * 100
            st.write(f"- **{label}**: {count:,} ({percentage:.1f}%)")

def show_suburb_analysis(historical_data):
    """Show suburb-specific analysis"""
    st.header("🏘️ Suburb Analysis")
    
    # Suburb performance
    st.subheader("🏆 Suburb Performance Rankings")
    
    # Get suburb statistics
    suburb_stats = historical_data.groupby('Property locality')['Purchase price'].agg(['count', 'mean', 'median']).round(0)
    suburb_stats.columns = ['Sales Count', 'Average Price', 'Median Price']
    suburb_stats = suburb_stats.sort_values('Average Price', ascending=False)
    
    # Top 10 most expensive suburbs
    st.write("**Top 10 Most Expensive Suburbs**")
    top_10 = suburb_stats.head(10)
    
    fig = px.bar(
        top_10, 
        x='Average Price', 
        y=top_10.index,
        orientation='h',
        title="Top 10 Most Expensive Suburbs",
        labels={'Average Price': 'Average Price ($)', 'index': 'Suburb'}
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Display table
    st.dataframe(top_10, use_container_width=True)
    
    # Suburb comparison
    st.subheader("📊 Suburb Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sales volume by suburb
        suburb_volume = historical_data.groupby('Property locality').size().sort_values(ascending=False).head(10)
        
        fig = px.bar(
            x=suburb_volume.values,
            y=suburb_volume.index,
            orientation='h',
            title="Top 10 Suburbs by Sales Volume",
            labels={'x': 'Number of Sales', 'y': 'Suburb'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Price vs volume scatter
        suburb_summary = historical_data.groupby('Property locality').agg({
            'Purchase price': ['mean', 'count']
        }).round(0)
        suburb_summary.columns = ['Average Price', 'Sales Count']
        
        fig = px.scatter(
            suburb_summary,
            x='Average Price',
            y='Sales Count',
            hover_data=suburb_summary.index,
            title="Suburb Price vs Sales Volume",
            labels={'Average Price': 'Average Price ($)', 'Sales Count': 'Number of Sales'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_price_comparisons(historical_data, current_data):
    """Show price comparison analysis"""
    st.header("💰 Price Comparisons")
    
    # Overall comparison
    st.subheader("📊 Overall Price Comparison")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Historical vs Current prices
        hist_median = historical_data['Purchase price'].median()
        current_median = current_data['price'].median()
        
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=['Historical Sales', 'Current Listings'],
            y=[hist_median, current_median],
            text=[f"${hist_median:,.0f}", f"${current_median:,.0f}"],
            textposition='auto',
            marker_color=['blue', 'orange']
        ))
        fig.update_layout(
            title="Median Price Comparison",
            yaxis_title="Price ($)",
            showlegend=False
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Calculate difference
        difference = ((current_median - hist_median) / hist_median) * 100
        st.metric(
            label="Price Difference",
            value=f"{difference:+.1f}%",
            delta=f"{difference:+.1f}%"
        )
    
    with col2:
        # Price distribution comparison
        fig = go.Figure()
        
        fig.add_trace(go.Histogram(
            x=historical_data['Purchase price'],
            name='Historical Sales',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig.add_trace(go.Histogram(
            x=current_data['price'],
            name='Current Listings',
            opacity=0.7,
            nbinsx=20
        ))
        
        fig.update_layout(
            title="Price Distribution Comparison",
            xaxis_title="Price ($)",
            yaxis_title="Count",
            barmode='overlay'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Suburb-level comparison
    st.subheader("🏘️ Suburb-Level Comparison")
    
    # Get matching suburbs
    hist_suburbs = set(historical_data['Property locality'].unique())
    current_suburbs = set(current_data['suburb'].unique())
    matching_suburbs = hist_suburbs & current_suburbs
    
    if matching_suburbs:
        comparison_data = []
        for suburb in matching_suburbs:
            hist_median = historical_data[historical_data['Property locality'] == suburb]['Purchase price'].median()
            current_median = current_data[current_data['suburb'] == suburb]['price'].median()
            difference = ((current_median - hist_median) / hist_median) * 100
            
            comparison_data.append({
                'Suburb': suburb,
                'Historical Median': hist_median,
                'Current Median': current_median,
                'Difference (%)': difference
            })
        
        comparison_df = pd.DataFrame(comparison_data)
        comparison_df = comparison_df.sort_values('Difference (%)', ascending=False)
        
        fig = px.bar(
            comparison_df,
            x='Suburb',
            y='Difference (%)',
            color='Difference (%)',
            color_continuous_scale='RdYlGn',
            title="Price Difference by Suburb",
            labels={'Difference (%)': 'Price Difference (%)'}
        )
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(comparison_df, use_container_width=True)
    else:
        st.info("No matching suburbs found between historical and current data")

def show_data_explorer(historical_data, current_data):
    """Show interactive data explorer"""
    st.header("📋 Data Explorer")
    
    # Data selection
    data_type = st.selectbox("Select data to explore:", ["Historical Sales", "Current Listings"])
    
    if data_type == "Historical Sales":
        st.subheader("Historical Sales Data")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date range filter
            min_date = historical_data['Contract date'].min()
            max_date = historical_data['Contract date'].max()
            
            date_range = st.date_input(
                "Select date range:",
                value=(min_date, max_date),
                min_value=min_date,
                max_value=max_date
            )
        
        with col2:
            # Price range filter
            min_price = historical_data['Purchase price'].min()
            max_price = historical_data['Purchase price'].max()
            
            price_range = st.slider(
                "Price range ($):",
                min_value=float(min_price),
                max_value=float(max_price),
                value=(float(min_price), float(max_price))
            )
        
        with col3:
            # Suburb filter
            suburbs = sorted(historical_data['Property locality'].unique())
            selected_suburbs = st.multiselect(
                "Select suburbs:",
                options=suburbs,
                default=suburbs[:3]
            )
        
        # Apply filters
        filtered_data = historical_data.copy()
        
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
        st.dataframe(filtered_data.head(100), use_container_width=True)  # Limit to first 100 rows
        
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
        st.write(f"**Showing {len(current_data):,} records**")
        st.dataframe(current_data, use_container_width=True)
        
        # Download button
        csv = current_data.to_csv(index=False)
        st.download_button(
            label="Download current data as CSV",
            data=csv,
            file_name=f"current_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def main():
    """Main Streamlit application"""
    
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
        ["📊 Dashboard", "📈 Price Analysis", "🏘️ Suburb Analysis", "💰 Price Comparisons", "📋 Data Explorer"]
    )
    
    # Load data
    with st.spinner("Loading property data..."):
        data_dict = load_property_data()
        historical_data = data_dict['historical_data']
        current_data = data_dict['current_data']
    
    # Show data source info
    current_file = os.path.join('src', 'data', 'current_property_data.csv')
    historical_file = os.path.join('data', 'extract-3-very-clean.csv')
    
    if os.path.exists(current_file) and os.path.exists(historical_file):
        st.sidebar.markdown(f"""
        <div class="data-source-success">
            <strong>📊 Real Data</strong><br>
            {len(current_data)} current + {len(historical_data):,} historical
        </div>
        """, unsafe_allow_html=True)
    elif os.path.exists(current_file):
        st.sidebar.markdown(f"""
        <div class="data-source-success">
            <strong>📊 Real Current</strong><br>
            {len(current_data)} properties
        </div>
        """, unsafe_allow_html=True)
        st.sidebar.markdown(f"""
        <div class="data-source-warning">
            <strong>📊 Sample Historical</strong><br>
            Demo mode
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
        show_dashboard(historical_data, current_data)
    elif page == "📈 Price Analysis":
        show_price_analysis(historical_data)
    elif page == "🏘️ Suburb Analysis":
        show_suburb_analysis(historical_data)
    elif page == "💰 Price Comparisons":
        show_price_comparisons(historical_data, current_data)
    elif page == "📋 Data Explorer":
        show_data_explorer(historical_data, current_data)

if __name__ == "__main__":
    main()
