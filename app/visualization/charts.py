"""
Chart generation functionality for property analysis
"""

import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
from typing import Dict, List, Optional
import logging

logger = logging.getLogger(__name__)


class ChartGenerator:
    """Generates various charts for property analysis"""
    
    @staticmethod
    def create_price_trend_chart(monthly_data: pd.DataFrame) -> go.Figure:
        """Create price trend chart with volume"""
        fig = make_subplots(
            rows=2, cols=1,
            subplot_titles=('Average Price Over Time', 'Sales Volume Over Time'),
            vertical_spacing=0.1
        )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_data.index, 
                y=monthly_data['Average Price'],
                mode='lines+markers', 
                name='Average Price', 
                line=dict(color='blue')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Scatter(
                x=monthly_data.index, 
                y=monthly_data['Median Price'],
                mode='lines+markers', 
                name='Median Price', 
                line=dict(color='red')
            ),
            row=1, col=1
        )
        
        fig.add_trace(
            go.Bar(
                x=monthly_data.index, 
                y=monthly_data['Sales Volume'],
                name='Sales Volume', 
                marker_color='green'
            ),
            row=2, col=1
        )
        
        fig.update_layout(height=600, showlegend=True)
        return fig
    
    @staticmethod
    def create_price_distribution_chart(historical_data: pd.DataFrame) -> go.Figure:
        """Create price distribution histogram"""
        fig = px.histogram(
            historical_data, 
            x='Purchase price', 
            nbins=30,
            title="Price Distribution",
            labels={'Purchase price': 'Price ($)', 'count': 'Number of Properties'}
        )
        fig.update_layout(showlegend=False)
        return fig
    
    @staticmethod
    def create_suburb_performance_chart(suburb_stats: pd.DataFrame) -> go.Figure:
        """Create suburb performance bar chart"""
        fig = px.bar(
            suburb_stats, 
            x='Average Price', 
            y=suburb_stats.index,
            orientation='h',
            title="Top Suburbs by Average Price",
            labels={'Average Price': 'Average Price ($)', 'index': 'Suburb'}
        )
        return fig
    
    @staticmethod
    def create_price_comparison_chart(hist_median: float, current_median: float) -> go.Figure:
        """Create price comparison bar chart"""
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
        return fig
    
    @staticmethod
    def create_distribution_comparison_chart(
        historical_data: pd.DataFrame, 
        current_data: pd.DataFrame
    ) -> go.Figure:
        """Create price distribution comparison chart"""
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
        return fig
    
    @staticmethod
    def create_suburb_comparison_chart(comparison_df: pd.DataFrame) -> go.Figure:
        """Create suburb comparison chart"""
        if comparison_df.empty:
            return go.Figure()
            
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
        return fig
    
    @staticmethod
    def create_sales_volume_chart(suburb_volume: pd.Series) -> go.Figure:
        """Create sales volume by suburb chart"""
        fig = px.bar(
            x=suburb_volume.values,
            y=suburb_volume.index,
            orientation='h',
            title="Top Suburbs by Sales Volume",
            labels={'x': 'Number of Sales', 'y': 'Suburb'}
        )
        return fig
    
    @staticmethod
    def create_price_vs_volume_scatter(suburb_summary: pd.DataFrame) -> go.Figure:
        """Create price vs volume scatter plot"""
        fig = px.scatter(
            suburb_summary,
            x='Average Price',
            y='Sales Count',
            hover_data=suburb_summary.index,
            title="Suburb Price vs Sales Volume",
            labels={'Average Price': 'Average Price ($)', 'Sales Count': 'Number of Sales'}
        )
        return fig
