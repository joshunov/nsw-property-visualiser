#!/usr/bin/env python3
"""
Streamlit Web Application for Property Analysis
Presents all property analysis data in an interactive web interface
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

from analysis.eastern_suburbs_analyzer import EasternSuburbsAnalyzer

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
def load_analyzer():
    """Load the Eastern Suburbs analyzer with caching"""
    analyzer = EasternSuburbsAnalyzer()
    analyzer.load_eastern_suburbs_data()
    return analyzer

@st.cache_data
def load_analysis_results():
    """Load and cache analysis results"""
    analyzer = load_analyzer()
    
    results = {
        'historical_data': analyzer.historical_df,
        'current_data': analyzer.current_df,
        'analyzer': analyzer
    }
    
    # Load CSV files if they exist
    output_dir = analyzer.output_dir
    
    csv_files = {
        'postcode_analysis': 'postcode_analysis.csv',
        'suburb_analysis': 'suburb_analysis.csv',
        'price_per_sqm_analysis': 'price_per_sqm_analysis.csv',
        'price_per_sqm_comparison': 'price_per_sqm_comparison.csv',
        'price_comparison': 'price_comparison.csv'
    }
    
    for key, filename in csv_files.items():
        filepath = os.path.join(output_dir, filename)
        if os.path.exists(filepath):
            try:
                results[key] = pd.read_csv(filepath)
            except Exception as e:
                st.warning(f"Could not load {filename}: {e}")
                results[key] = None
        else:
            results[key] = None
    
    return results

def main():
    """Main Streamlit application"""
    
    # Header
    st.markdown('<h1 class="main-header">🏠 Sydney Eastern Suburbs Property Analysis</h1>', unsafe_allow_html=True)
    
    # Sidebar
    st.sidebar.title("Navigation")
    page = st.sidebar.selectbox(
        "Choose a page:",
        ["📊 Dashboard", "📈 Price Analysis", "🏘️ Suburb Analysis", "💰 Price Comparisons", "📋 Data Explorer", "📊 Visualizations"]
    )
    
    # Load data
    with st.spinner("Loading property data..."):
        results = load_analysis_results()
    
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
    elif page == "📊 Visualizations":
        show_visualizations(results)

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
            st.write(f"- **Date Range**: {historical_data['Contract date'].min()} to {historical_data['Contract date'].max()}")
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
    
    # Recent insights
    st.subheader("💡 Recent Market Insights")
    
    if not historical_data.empty:
        # Filter for recent data (last 2 years)
        historical_data['Contract date'] = pd.to_datetime(historical_data['Contract date'], errors='coerce')
        two_years_ago = datetime.now() - pd.DateOffset(years=2)
        recent_data = historical_data[historical_data['Contract date'] >= two_years_ago]
        
        if len(recent_data) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                recent_avg = recent_data['Purchase price'].mean()
                overall_avg = historical_data['Purchase price'].mean()
                growth = ((recent_avg - overall_avg) / overall_avg) * 100
                
                st.markdown(f"""
                <div class="insight-box">
                    <h4>📈 Price Growth Trend</h4>
                    <p>Recent average price: <strong>${recent_avg:,.0f}</strong></p>
                    <p>Overall average price: <strong>${overall_avg:,.0f}</strong></p>
                    <p>Growth: <strong>{growth:+.1f}%</strong></p>
                </div>
                """, unsafe_allow_html=True)
            
            with col2:
                top_suburbs = recent_data.groupby('Property locality')['Purchase price'].mean().sort_values(ascending=False).head(3)
                st.markdown(f"""
                <div class="insight-box">
                    <h4>🏆 Top 3 Most Expensive Suburbs (Recent)</h4>
                    <ol>
                        <li><strong>{top_suburbs.index[0]}</strong>: ${top_suburbs.iloc[0]:,.0f}</li>
                        <li><strong>{top_suburbs.index[1]}</strong>: ${top_suburbs.iloc[1]:,.0f}</li>
                        <li><strong>{top_suburbs.index[2]}</strong>: ${top_suburbs.iloc[2]:,.0f}</li>
                    </ol>
                </div>
                """, unsafe_allow_html=True)

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
            nbins=50,
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
            (0, 500000, "Under $500k"),
            (500000, 1000000, "$500k - $1M"),
            (1000000, 2000000, "$1M - $2M"),
            (2000000, 5000000, "$2M - $5M"),
            (5000000, float('inf'), "Over $5M")
        ]
        
        for min_price, max_price, label in ranges:
            if max_price == float('inf'):
                count = len(historical_data[historical_data['Purchase price'] >= min_price])
            else:
                count = len(historical_data[(historical_data['Purchase price'] >= min_price) & (historical_data['Purchase price'] < max_price)])
            percentage = (count / len(historical_data)) * 100
            st.write(f"- **{label}**: {count:,} ({percentage:.1f}%)")

def show_suburb_analysis(results):
    """Show suburb-specific analysis"""
    st.header("🏘️ Suburb Analysis")
    
    historical_data = results['historical_data']
    suburb_analysis = results.get('suburb_analysis')
    
    if historical_data.empty:
        st.warning("No historical data available for suburb analysis")
        return
    
    # Suburb performance
    st.subheader("🏆 Suburb Performance Rankings")
    
    if suburb_analysis is not None:
        # Top 10 most expensive suburbs
        st.write("**Top 10 Most Expensive Suburbs**")
        top_10 = suburb_analysis.head(10)
        
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
    
    # Get top suburbs by sales volume
    suburb_volume = historical_data.groupby('Property locality').size().sort_values(ascending=False).head(10)
    
    col1, col2 = st.columns(2)
    
    with col1:
        fig = px.bar(
            x=suburb_volume.values,
            y=suburb_volume.index,
            orientation='h',
            title="Top 10 Suburbs by Sales Volume",
            labels={'x': 'Number of Sales', 'y': 'Suburb'}
        )
        st.plotly_chart(fig, use_container_width=True)
    
    with col2:
        # Suburb price ranges
        suburb_prices = historical_data.groupby('Property locality')['Purchase price'].agg(['mean', 'median', 'min', 'max'])
        suburb_prices = suburb_prices.sort_values('mean', ascending=False).head(10)
        
        fig = px.scatter(
            suburb_prices,
            x='mean',
            y='median',
            size='max',
            hover_data=['min', 'max'],
            title="Suburb Price Analysis (Top 10)",
            labels={'mean': 'Average Price ($)', 'median': 'Median Price ($)'}
        )
        st.plotly_chart(fig, use_container_width=True)

def show_price_comparisons(results):
    """Show price comparison analysis"""
    st.header("💰 Price Comparisons")
    
    current_data = results['current_data']
    historical_data = results['historical_data']
    price_comparison = results.get('price_comparison')
    sqm_comparison = results.get('price_per_sqm_comparison')
    
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
            nbinsx=30
        ))
        
        fig.add_trace(go.Histogram(
            x=current_data['price'],
            name='Current Listings',
            opacity=0.7,
            nbinsx=30
        ))
        
        fig.update_layout(
            title="Price Distribution Comparison",
            xaxis_title="Price ($)",
            yaxis_title="Count",
            barmode='overlay'
        )
        st.plotly_chart(fig, use_container_width=True)
    
    # Postcode comparison
    if price_comparison is not None:
        st.subheader("🏘️ Postcode-Level Comparison")
        
        fig = px.bar(
            price_comparison,
            x='postcode',
            y='difference_percentage',
            color='difference_percentage',
            color_continuous_scale='RdYlGn',
            title="Price Difference by Postcode",
            labels={'difference_percentage': 'Difference (%)', 'postcode': 'Postcode'}
        )
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
        
        # Display comparison table
        st.dataframe(price_comparison, use_container_width=True)
    
    # Square meter comparison
    if sqm_comparison is not None:
        st.subheader("📏 Price per Square Meter Comparison")
        
        fig = px.bar(
            sqm_comparison,
            x='postcode',
            y='difference_percentage',
            color='difference_percentage',
            color_continuous_scale='RdYlGn',
            title="Price per Square Meter Difference by Postcode",
            labels={'difference_percentage': 'Difference (%)', 'postcode': 'Postcode'}
        )
        fig.add_hline(y=0, line_dash="dash", line_color="black")
        st.plotly_chart(fig, use_container_width=True)
        
        st.dataframe(sqm_comparison, use_container_width=True)

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
                default=postcodes[:5]
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
        st.dataframe(filtered_data, use_container_width=True)
        
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
        
        # Filters
        col1, col2 = st.columns(2)
        
        with col1:
            # Price range filter
            min_price = current_data['price'].min()
            max_price = current_data['price'].max()
            
            price_range = st.slider(
                "Price range ($):",
                min_value=float(min_price),
                max_value=float(max_price),
                value=(float(min_price), float(max_price))
            )
        
        with col2:
            # Postcode filter
            postcodes = sorted(current_data['postcode'].unique())
            selected_postcodes = st.multiselect(
                "Select postcodes:",
                options=postcodes,
                default=postcodes
            )
        
        # Apply filters
        filtered_data = current_data.copy()
        
        filtered_data = filtered_data[
            (filtered_data['price'] >= price_range[0]) &
            (filtered_data['price'] <= price_range[1])
        ]
        
        if selected_postcodes:
            filtered_data = filtered_data[filtered_data['postcode'].isin(selected_postcodes)]
        
        # Display filtered data
        st.write(f"**Showing {len(filtered_data):,} records**")
        st.dataframe(filtered_data, use_container_width=True)
        
        # Download button
        csv = filtered_data.to_csv(index=False)
        st.download_button(
            label="Download filtered data as CSV",
            data=csv,
            file_name=f"filtered_current_data_{datetime.now().strftime('%Y%m%d')}.csv",
            mime="text/csv"
        )

def show_visualizations(results):
    """Show advanced visualizations"""
    st.header("📊 Advanced Visualizations")
    
    historical_data = results['historical_data']
    
    if historical_data.empty:
        st.warning("No historical data available for visualizations")
        return
    
    # Prepare data
    historical_data['Contract date'] = pd.to_datetime(historical_data['Contract date'], errors='coerce')
    historical_data = historical_data.dropna(subset=['Contract date', 'Purchase price'])
    historical_data = historical_data[historical_data['Purchase price'] > 0]
    
    # Price heatmap by month and year
    st.subheader("🔥 Price Heatmap by Month and Year")
    
    historical_data['Year'] = historical_data['Contract date'].dt.year
    historical_data['Month'] = historical_data['Contract date'].dt.month
    
    price_heatmap = historical_data.groupby(['Year', 'Month'])['Purchase price'].mean().unstack()
    
    fig = px.imshow(
        price_heatmap,
        title="Average Price Heatmap by Month and Year",
        labels=dict(x="Month", y="Year", color="Average Price ($)"),
        aspect="auto"
    )
    st.plotly_chart(fig, use_container_width=True)
    
    # Price vs Area scatter plot
    if 'Area' in historical_data.columns:
        st.subheader("📏 Price vs Area Analysis")
        
        area_data = historical_data.dropna(subset=['Area'])
        area_data = area_data[area_data['Area'] > 0]
        
        if len(area_data) > 0:
            fig = px.scatter(
                area_data,
                x='Area',
                y='Purchase price',
                color='Property post code',
                hover_data=['Property locality', 'Contract date'],
                title="Price vs Area by Postcode",
                labels={'Area': 'Area (sq m)', 'Purchase price': 'Price ($)'}
            )
            st.plotly_chart(fig, use_container_width=True)
    
    # Price trends by postcode
    st.subheader("📈 Price Trends by Postcode")
    
    # Get top 5 postcodes by sales volume
    top_postcodes = historical_data.groupby('Property post code').size().sort_values(ascending=False).head(5)
    
    fig = go.Figure()
    
    for postcode in top_postcodes.index:
        postcode_data = historical_data[historical_data['Property post code'] == postcode]
        monthly_avg = postcode_data.groupby(postcode_data['Contract date'].dt.to_period('M'))['Purchase price'].mean()
        
        fig.add_trace(go.Scatter(
            x=monthly_avg.index.astype(str),
            y=monthly_avg.values,
            mode='lines+markers',
            name=f'Postcode {postcode}'
        ))
    
    fig.update_layout(
        title="Monthly Average Price Trends by Postcode (Top 5)",
        xaxis_title="Month",
        yaxis_title="Average Price ($)",
        height=500
    )
    st.plotly_chart(fig, use_container_width=True)

if __name__ == "__main__":
    main()
