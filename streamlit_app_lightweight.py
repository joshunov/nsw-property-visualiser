#!/usr/bin/env python3
"""
Lightweight Streamlit Web Application for Property Analysis
Optimized for Streamlit Cloud deployment
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
import sys
from datetime import datetime
import numpy as np

# Add src to path for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'src'))

# Page configuration
st.set_page_config(
    page_title="Sydney Eastern Suburbs Property Analysis",
    page_icon="🏠",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
    }
    .insight-box {
        background-color: #e8f4fd;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #ff7f0e;
    }
</style>
""", unsafe_allow_html=True)

@st.cache_data
def load_sample_data():
    """Load sample data for demonstration"""
    try:
        # Try to load current data
        current_file = os.path.join('src', 'data', 'current_property_data.csv')
        if os.path.exists(current_file):
            current_data = pd.read_csv(current_file)
        else:
            # Create sample current data
            current_data = pd.DataFrame({
                'price': [1690154, 1615250, 1850000, 2200000],
                'postcode': ['2026', '2031', '2027', '2029'],
                'suburb': ['Bondi', 'Coogee', 'Double Bay', 'Vaucluse'],
                'Area': [150, 200, 180, 250]
            })
        
        # Create sample historical data (smaller dataset for demo)
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
        
        return {
            'historical_data': sample_historical,
            'current_data': current_data
        }
    except Exception as e:
        st.error(f"Error loading data: {e}")
        return {
            'historical_data': pd.DataFrame(),
            'current_data': pd.DataFrame()
        }

def show_dashboard(results):
    """Show the main dashboard"""
    st.header("📊 Property Market Dashboard")
    
    historical_data = results['historical_data']
    current_data = results['current_data']
    
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
        if not historical_data.empty and 'Purchase price' in historical_data.columns:
            avg_price = historical_data['Purchase price'].mean()
            st.metric(
                label="Average Historical Price",
                value=f"${avg_price:,.0f}",
                help="Average price of historical sales"
            )
    
    with col4:
        if not current_data.empty and 'price' in current_data.columns:
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
        st.write("**Historical Sales Data**")
        if not historical_data.empty:
            st.write(f"- **Records**: {len(historical_data):,}")
            st.write(f"- **Date Range**: {historical_data['Contract date'].min().strftime('%Y-%m-%d')} to {historical_data['Contract date'].max().strftime('%Y-%m-%d')}")
            st.write(f"- **Postcodes**: {historical_data['Property post code'].nunique()}")
            st.write(f"- **Suburbs**: {historical_data['Property locality'].nunique()}")
        else:
            st.write("No historical data available")
    
    with col2:
        st.write("**Current Listings Data**")
        if not current_data.empty:
            st.write(f"- **Records**: {len(current_data):,}")
            st.write(f"- **Postcodes**: {current_data['postcode'].nunique()}")
            st.write(f"- **Suburbs**: {current_data['suburb'].nunique()}")
            if 'Area' in current_data.columns:
                st.write(f"- **With Area Data**: {current_data['Area'].notna().sum()}")
        else:
            st.write("No current data available")

def show_price_analysis(results):
    """Show detailed price analysis"""
    st.header("📈 Price Analysis")
    
    historical_data = results['historical_data']
    
    if historical_data.empty:
        st.warning("No historical data available for price analysis")
        return
    
    # Price trends over time
    st.subheader("📊 Price Trends Over Time")
    
    # Prepare data
    historical_data['Contract date'] = pd.to_datetime(historical_data['Contract date'], errors='coerce')
    historical_data = historical_data.dropna(subset=['Contract date', 'Purchase price'])
    historical_data = historical_data[historical_data['Purchase price'] > 0]
    
    # Monthly price trends
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

def show_suburb_analysis(results):
    """Show suburb-specific analysis"""
    st.header("🏘️ Suburb Analysis")
    
    historical_data = results['historical_data']
    
    if historical_data.empty:
        st.warning("No historical data available for suburb analysis")
        return
    
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

def show_price_comparisons(results):
    """Show price comparison analysis"""
    st.header("💰 Price Comparisons")
    
    current_data = results['current_data']
    historical_data = results['historical_data']
    
    if current_data.empty or historical_data.empty:
        st.warning("Both current and historical data are required for price comparisons")
        return
    
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

def show_data_explorer(results):
    """Show interactive data explorer"""
    st.header("📋 Data Explorer")
    
    historical_data = results['historical_data']
    current_data = results['current_data']
    
    # Data selection
    data_type = st.selectbox("Select data to explore:", ["Historical Sales", "Current Listings"])
    
    if data_type == "Historical Sales" and not historical_data.empty:
        st.subheader("Historical Sales Data")
        
        # Filters
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Date range filter
            if 'Contract date' in historical_data.columns:
                historical_data['Contract date'] = pd.to_datetime(historical_data['Contract date'], errors='coerce')
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
            # Postcode filter
            postcodes = sorted(historical_data['Property post code'].unique())
            selected_postcodes = st.multiselect(
                "Select postcodes:",
                options=postcodes,
                default=postcodes[:3]
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
        
        if selected_postcodes:
            filtered_data = filtered_data[filtered_data['Property post code'].isin(selected_postcodes)]
        
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
    
    elif data_type == "Current Listings" and not current_data.empty:
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
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📊 Dashboard", "📈 Price Analysis", "🏘️ Suburb Analysis", "💰 Price Comparisons", "📋 Data Explorer"]
    )
    
    # Load data
    with st.spinner("Loading property data..."):
        results = load_sample_data()
    
    # Page routing
    if page == "📊 Dashboard":
        show_dashboard(results)
    elif page == "📈 Price Analysis":
        show_price_analysis(results)
    elif page == "🏘️ Suburb Analysis":
        show_suburb_analysis(results)
    elif page == "💰 Price Comparisons":
        show_price_comparisons(results)
    elif page == "📋 Data Explorer":
        show_data_explorer(results)

if __name__ == "__main__":
    main()
