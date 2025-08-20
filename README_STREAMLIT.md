# 🏠 Sydney Eastern Suburbs Property Analysis - Streamlit Web App

A comprehensive web application for analyzing Sydney Eastern Suburbs property market data, built with Streamlit and deployed on [Streamlit Cloud](https://share.streamlit.io/).

## 🌟 Features

### 📊 Interactive Dashboard
- **Key Metrics**: Historical sales, current listings, average prices
- **Data Overview**: Comprehensive data summary and statistics
- **Market Insights**: Recent trends and growth analysis
- **Real-time Updates**: Live data visualization

### 📈 Price Analysis
- **Price Trends**: Monthly and yearly price movements
- **Price Distribution**: Histograms and statistical analysis
- **Price Ranges**: Breakdown by price categories
- **Interactive Charts**: Plotly-powered visualizations

### 🏘️ Suburb Analysis
- **Suburb Rankings**: Top performing suburbs by price
- **Sales Volume**: Most active suburbs
- **Price Comparisons**: Suburb-to-suburb analysis
- **Geographic Insights**: Postcode-level analysis

### 💰 Price Comparisons
- **Current vs Historical**: Real-time comparison analysis
- **Price Differences**: Percentage changes and trends
- **Postcode Analysis**: Location-specific comparisons
- **Square Meter Analysis**: Price per square meter insights

### 📋 Data Explorer
- **Interactive Filtering**: Date, price, and postcode filters
- **Data Download**: Export filtered data as CSV
- **Real-time Search**: Dynamic data exploration
- **Custom Queries**: Flexible data filtering

### 📊 Advanced Visualizations
- **Price Heatmaps**: Monthly/yearly price patterns
- **Scatter Plots**: Price vs area analysis
- **Trend Analysis**: Postcode-specific trends
- **Interactive Charts**: Hover details and zooming

## 🚀 Quick Start

### Local Development

1. **Install Dependencies**:
   ```bash
   pip install -r requirements_streamlit.txt
   ```

2. **Run the App**:
   ```bash
   streamlit run streamlit_app.py
   ```

3. **Open Browser**: Navigate to `http://localhost:8501`

### Cloud Deployment

1. **Push to GitHub**: Ensure your code is in a GitHub repository
2. **Visit Streamlit Cloud**: Go to [share.streamlit.io](https://share.streamlit.io/)
3. **Connect Repository**: Link your GitHub repository
4. **Deploy**: Click "Deploy" and wait for the build to complete

## 📁 File Structure

```
Property_project/
├── streamlit_app.py              # Main Streamlit application
├── requirements_streamlit.txt    # Python dependencies
├── src/
│   └── analysis/
│       └── eastern_suburbs_analyzer.py  # Analysis engine
├── data/
│   ├── extract-3-very-clean.csv  # Historical property data
│   └── current_property_data.csv # Current listings
└── docs/
    ├── STREAMLIT_DEPLOYMENT.md   # Deployment guide
    └── PRICE_COMPARISON_FEATURE.md # Feature documentation
```

## 📊 Data Requirements

### Historical Data (`extract-3-very-clean.csv`)
Required columns:
- `Contract date`: Sale date
- `Purchase price`: Sale price
- `Property post code`: Postcode
- `Property locality`: Suburb name
- `Area`: Square meters (optional)

### Current Data (`current_property_data.csv`)
Required columns:
- `price`: Listing price
- `postcode`: Postcode
- `suburb`: Suburb name
- `Area`: Square meters (optional)

## 🎨 Customization

### Styling
The app uses custom CSS for enhanced styling. Modify the CSS in `streamlit_app.py`:

```python
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
</style>
""", unsafe_allow_html=True)
```

### Adding New Pages
1. Add to sidebar selection
2. Create page function
3. Add routing logic

Example:
```python
# Add to sidebar
page = st.sidebar.selectbox(
    "Choose a page:",
    ["📊 Dashboard", "📈 Price Analysis", "🆕 New Page"]
)

# Add routing
elif page == "🆕 New Page":
    show_new_page(results)

# Create function
def show_new_page(results):
    st.header("🆕 New Page")
    # Your content here
```

## 🔧 Configuration

### Environment Variables
Set these in Streamlit Cloud if needed:
- `STREAMLIT_SERVER_PORT`: Custom port (default: 8501)
- `STREAMLIT_SERVER_ADDRESS`: Custom address (default: localhost)

### Performance Settings
- **Data Caching**: Uses `@st.cache_data` for optimal performance
- **Lazy Loading**: Data loaded only when needed
- **Memory Optimization**: Efficient data handling for large datasets

## 📈 Analytics Features

### Market Intelligence
- **Price Trends**: Historical price movements
- **Growth Analysis**: Year-over-year comparisons
- **Market Cycles**: Seasonal and cyclical patterns
- **Geographic Patterns**: Location-based insights

### Investment Insights
- **Undervalued Areas**: Properties below market value
- **Overvalued Areas**: Properties above market value
- **Opportunity Identification**: Emerging market trends
- **Risk Assessment**: Market volatility analysis

### Comparative Analysis
- **Current vs Historical**: Real-time market positioning
- **Suburb Comparisons**: Location-based analysis
- **Price per Square Meter**: Value density analysis
- **Temporal Analysis**: Time-based market insights

## 🛠️ Technical Stack

- **Frontend**: Streamlit
- **Visualization**: Plotly
- **Data Processing**: Pandas, NumPy
- **Analysis Engine**: Custom Python modules
- **Deployment**: Streamlit Cloud

## 🔍 Troubleshooting

### Common Issues

1. **Import Errors**:
   - Verify all packages in `requirements_streamlit.txt`
   - Check file paths and imports

2. **Data Loading Issues**:
   - Ensure data files exist and are accessible
   - Verify CSV format and column names
   - Check file permissions

3. **Performance Issues**:
   - Use data caching for expensive operations
   - Consider data sampling for large datasets
   - Optimize data loading patterns

4. **Memory Issues**:
   - Large datasets may cause memory problems
   - Use data sampling or filtering
   - Implement lazy loading

### Debugging

1. **Local Testing**:
   ```bash
   streamlit run streamlit_app.py --logger.level debug
   ```

2. **Check Logs**: View Streamlit Cloud logs for errors

3. **Data Validation**: Verify data format and content

## 📊 Performance Optimization

### Data Caching
```python
@st.cache_data
def load_analysis_results():
    # Expensive data loading operations
    return results
```

### Efficient Queries
- Use pandas operations for data filtering
- Implement lazy loading for large datasets
- Cache expensive computations

### Memory Management
- Sample data for interactive features
- Use efficient data types
- Implement data streaming for large files

## 🔒 Security Considerations

1. **Data Privacy**: Ensure no sensitive data exposure
2. **Input Validation**: Validate all user inputs
3. **Access Control**: Consider authentication for sensitive data
4. **Rate Limiting**: Be aware of Streamlit Cloud limits

## 📈 Monitoring and Analytics

### App Analytics
- Monitor usage in Streamlit Cloud dashboard
- Track user interactions and page views
- Analyze performance metrics

### Error Tracking
- Check logs regularly for errors
- Monitor app response times
- Track user feedback and issues

## 🚀 Deployment Checklist

- [ ] All code committed to GitHub
- [ ] `requirements_streamlit.txt` includes all dependencies
- [ ] Data files are in the repository
- [ ] File paths are correct
- [ ] App tested locally
- [ ] Repository connected to Streamlit Cloud
- [ ] App deployed successfully
- [ ] All features working correctly

## 📞 Support

For issues and questions:

1. **Streamlit Documentation**: [docs.streamlit.io](https://docs.streamlit.io/)
2. **Streamlit Community**: [discuss.streamlit.io](https://discuss.streamlit.io/)
3. **GitHub Issues**: Create issues in your repository
4. **Code Comments**: Check inline documentation

## 🎯 Future Enhancements

- **Real-time Data**: Live data feeds and updates
- **Advanced Analytics**: Machine learning predictions
- **User Authentication**: Secure access control
- **Mobile Optimization**: Responsive design improvements
- **API Integration**: External data sources
- **Export Features**: PDF reports and data exports

## 📄 License

This project is for educational and research purposes. Please ensure compliance with data usage terms and local regulations.

---

**Built with ❤️ using Streamlit and Python**

For more information, visit the [deployment guide](docs/STREAMLIT_DEPLOYMENT.md) or [price comparison documentation](docs/PRICE_COMPARISON_FEATURE.md).
