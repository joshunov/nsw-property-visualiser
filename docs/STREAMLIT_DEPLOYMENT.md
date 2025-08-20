# Streamlit Web Application Deployment Guide

## Overview

This guide explains how to deploy the Sydney Eastern Suburbs Property Analysis web application to [Streamlit Cloud](https://share.streamlit.io/).

## Features

The Streamlit web application provides:

- **📊 Interactive Dashboard**: Key metrics and market insights
- **📈 Price Analysis**: Detailed price trends and distributions
- **🏘️ Suburb Analysis**: Suburb performance rankings and comparisons
- **💰 Price Comparisons**: Current vs historical price analysis
- **📋 Data Explorer**: Interactive data filtering and exploration
- **📊 Advanced Visualizations**: Heatmaps, scatter plots, and trend analysis

## Prerequisites

1. **GitHub Account**: Your code must be in a GitHub repository
2. **Streamlit Account**: Sign up at [share.streamlit.io](https://share.streamlit.io/)
3. **Data Files**: Ensure your data files are in the repository

## File Structure

Your repository should have this structure:

```
Property_project/
├── streamlit_app.py              # Main Streamlit application
├── requirements_streamlit.txt    # Python dependencies
├── src/
│   └── analysis/
│       └── eastern_suburbs_analyzer.py
├── data/
│   ├── extract-3-very-clean.csv  # Historical data
│   └── current_property_data.csv # Current listings
└── docs/
    └── STREAMLIT_DEPLOYMENT.md
```

## Deployment Steps

### 1. Prepare Your Repository

1. **Ensure all files are committed to GitHub**:
   ```bash
   git add .
   git commit -m "Add Streamlit web application"
   git push origin main
   ```

2. **Verify file structure**:
   - `streamlit_app.py` is in the root directory
   - `requirements_streamlit.txt` is in the root directory
   - Data files are accessible from the application

### 2. Deploy to Streamlit Cloud

1. **Go to [share.streamlit.io](https://share.streamlit.io/)**
2. **Sign in with your GitHub account**
3. **Click "New app"**
4. **Configure your app**:
   - **Repository**: Select your GitHub repository
   - **Branch**: Select `main` (or your default branch)
   - **Main file path**: Enter `streamlit_app.py`
   - **App URL**: Choose a custom URL (optional)
5. **Click "Deploy!"**

### 3. Configuration

The app will automatically:
- Install dependencies from `requirements_streamlit.txt`
- Run the Streamlit application
- Make it available at your custom URL

## Data Requirements

### Required Data Files

1. **Historical Data**: `data/extract-3-very-clean.csv`
   - Must contain columns: `Contract date`, `Purchase price`, `Property post code`, `Property locality`
   - Optional: `Area` column for square meter analysis

2. **Current Data**: `data/current_property_data.csv`
   - Must contain columns: `price`, `postcode`, `suburb`
   - Optional: `Area` column for square meter analysis

### Data Format

#### Historical Data Format:
```csv
Contract date,Purchase price,Property post code,Property locality,Area
2023-01-15,1500000,2026,Bondi,150
2023-02-20,2000000,2031,Coogee,200
```

#### Current Data Format:
```csv
price,postcode,suburb,Area
1690154,2026,Bondi,150
1615250,2031,Coogee,200
```

## Application Features

### 📊 Dashboard
- Key metrics display
- Data overview
- Recent market insights
- Price growth trends

### 📈 Price Analysis
- Price trends over time
- Price distribution analysis
- Monthly price statistics
- Price range breakdowns

### 🏘️ Suburb Analysis
- Suburb performance rankings
- Sales volume analysis
- Price comparison by suburb
- Interactive suburb charts

### 💰 Price Comparisons
- Current vs historical price comparison
- Price difference analysis
- Postcode-level comparisons
- Square meter price analysis

### 📋 Data Explorer
- Interactive data filtering
- Date range selection
- Price range filtering
- Postcode selection
- Data download functionality

### 📊 Advanced Visualizations
- Price heatmaps
- Price vs area scatter plots
- Postcode trend analysis
- Interactive charts

## Troubleshooting

### Common Issues

1. **Import Errors**:
   - Ensure all required packages are in `requirements_streamlit.txt`
   - Check that file paths are correct

2. **Data Loading Issues**:
   - Verify data files exist in the repository
   - Check file permissions
   - Ensure CSV format is correct

3. **Memory Issues**:
   - Large datasets may cause memory problems
   - Consider data sampling for large files
   - Use data caching with `@st.cache_data`

4. **Performance Issues**:
   - Use data caching for expensive operations
   - Limit data size for interactive features
   - Optimize data loading

### Debugging

1. **Check Streamlit logs**:
   - Go to your app URL
   - Click the hamburger menu (☰)
   - Select "View app source"
   - Check for error messages

2. **Local testing**:
   ```bash
   pip install -r requirements_streamlit.txt
   streamlit run streamlit_app.py
   ```

## Customization

### Styling
The app uses custom CSS for styling. You can modify the CSS in the `streamlit_app.py` file:

```python
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 2rem;
    }
    /* Add more custom styles here */
</style>
""", unsafe_allow_html=True)
```

### Adding New Pages
To add new pages:

1. Add the page to the sidebar selection:
   ```python
   page = st.sidebar.selectbox(
       "Choose a page:",
       ["📊 Dashboard", "📈 Price Analysis", "🏘️ Suburb Analysis", "💰 Price Comparisons", "📋 Data Explorer", "📊 Visualizations", "🆕 New Page"]
   )
   ```

2. Add the page routing:
   ```python
   elif page == "🆕 New Page":
       show_new_page(results)
   ```

3. Create the page function:
   ```python
   def show_new_page(results):
       st.header("🆕 New Page")
       # Your page content here
   ```

## Security Considerations

1. **Data Privacy**: Ensure no sensitive data is exposed
2. **Access Control**: Consider adding authentication if needed
3. **Rate Limiting**: Be aware of Streamlit Cloud usage limits
4. **Data Validation**: Validate all user inputs

## Performance Optimization

1. **Data Caching**: Use `@st.cache_data` for expensive operations
2. **Lazy Loading**: Load data only when needed
3. **Data Sampling**: Use samples for large datasets
4. **Efficient Queries**: Optimize database queries if applicable

## Monitoring

1. **App Analytics**: Monitor app usage in Streamlit Cloud dashboard
2. **Error Tracking**: Check logs regularly for errors
3. **Performance Monitoring**: Monitor app response times
4. **User Feedback**: Collect user feedback for improvements

## Updates and Maintenance

1. **Regular Updates**: Keep dependencies updated
2. **Data Refresh**: Update data files regularly
3. **Feature Updates**: Add new features based on user needs
4. **Bug Fixes**: Address issues promptly

## Support

For issues with:
- **Streamlit Cloud**: Check [Streamlit documentation](https://docs.streamlit.io/)
- **Application Code**: Check the code comments and documentation
- **Data Issues**: Verify data format and file paths

## Example Deployment URL

Once deployed, your app will be available at:
```
https://your-app-name-your-username.streamlit.app
```

Replace `your-app-name` and `your-username` with your actual values.
