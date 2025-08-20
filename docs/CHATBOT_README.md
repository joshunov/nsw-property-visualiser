# 🏠 Eastern Suburbs Property AI Chatbot

An intelligent AI chatbot that provides natural language access to Eastern Suburbs property data, allowing users to ask questions about property prices, trends, comparisons, and market insights.

## 🚀 Features

### 🤖 Natural Language Processing
- **Intelligent Query Understanding**: Understands natural language questions about property data
- **Keyword Extraction**: Automatically identifies property terms, suburbs, prices, and specifications
- **Pattern Recognition**: Recognizes common query patterns for comparisons, trends, and analysis

### 📊 Data Analysis Capabilities
- **Price Analysis**: Average, median, and price range calculations
- **Suburb Comparisons**: Compare property prices between different Eastern Suburbs
- **Market Trends**: Analyze price growth and market changes over time
- **Property Search**: Filter by price, bedrooms, bathrooms, and location

### 💬 Multiple Interfaces
- **Command Line Interface**: Simple text-based interaction
- **Web Interface**: Modern, responsive web application with real-time chat
- **API Endpoints**: RESTful API for integration with other applications

## 🛠️ Installation

### Prerequisites
```bash
pip install -r requirements.txt
```

### Required Dependencies
- `pandas` - Data manipulation and analysis
- `numpy` - Numerical computing
- `flask` - Web framework for the web interface
- `requests` - HTTP library for data fetching
- `beautifulsoup4` - Web scraping capabilities

## 🎯 Usage

### Command Line Interface

Run the chatbot from the command line:
```bash
python run_chatbot.py
```

**Available Commands:**
- `suggestions` - Show example questions
- `web` - Start the web interface
- `quit` - Exit the chatbot

### Web Interface

Start the web interface:
```bash
python run_chatbot.py
# Then type 'web' when prompted
```

Or run directly:
```bash
python src/chatbot/web_interface.py
```

Then open your browser to: `http://localhost:5000`

### Testing

Run the test suite to verify functionality:
```bash
python test_chatbot.py
```

## 💡 Example Queries

### Price Analysis
```
"What's the average price in Bondi?"
"Show me properties in Paddington under $2M"
"What's the price range for 2-bedroom apartments?"
```

### Suburb Comparisons
```
"Compare Bondi vs Coogee prices"
"What's the difference between Vaucluse and Double Bay?"
"Which suburb is more expensive: Bondi or Paddington?"
```

### Market Trends
```
"What's the price trend in Eastern Suburbs?"
"Show me recent sales in Double Bay"
"How have prices changed in the last 2 years?"
```

### Property Search
```
"Find 3-bedroom properties in Vaucluse"
"Show me 2-bathroom houses under $3M"
"What are the most expensive suburbs?"
```

## 🏗️ Architecture

### Core Components

#### 1. PropertyChatbot Class
- **Location**: `src/chatbot/property_chatbot.py`
- **Purpose**: Main chatbot logic and natural language processing
- **Key Methods**:
  - `process_query()` - Main query processing pipeline
  - `extract_keywords()` - Extract relevant terms from queries
  - `generate_price_analysis()` - Create price analysis reports
  - `generate_suburb_comparison()` - Compare suburbs
  - `generate_trend_analysis()` - Analyze market trends

#### 2. Web Interface
- **Location**: `src/chatbot/web_interface.py`
- **Purpose**: Flask-based web application
- **Features**:
  - Real-time chat interface
  - RESTful API endpoints
  - Modern responsive design
  - Suggestion chips for easy interaction

#### 3. HTML Template
- **Location**: `src/chatbot/templates/chatbot.html`
- **Purpose**: Frontend interface
- **Features**:
  - Modern chat UI with typing indicators
  - Suggestion chips for common questions
  - Responsive design for mobile and desktop
  - Real-time message updates

### Data Sources

#### Historical Data
- **Source**: NSW Property Sales Data (past 5 years)
- **Filter**: Eastern Suburbs postcodes (2021-2035)
- **Fields**: Price, date, suburb, postcode, property details

#### Current Listings
- **Source**: Web scraped current property listings
- **Filter**: Eastern Suburbs properties
- **Fields**: Price, address, bedrooms, bathrooms, listing date

## 🔧 Configuration

### Eastern Suburbs Postcodes
The chatbot is configured to focus on Eastern Suburbs of Sydney:
- **2021**: Paddington, Woollahra
- **2022**: Bondi Junction
- **2023**: Bellevue Hill
- **2024**: Bronte, Waverley
- **2025**: Queens Park
- **2026**: Bondi, Bondi Beach, North Bondi, Tamarama
- **2027**: Edgecliff, Double Bay
- **2028**: Rose Bay
- **2029**: Vaucluse, Dover Heights
- **2030**: Watsons Bay
- **2031**: Clovelly, Coogee
- **2032**: South Coogee
- **2033**: Kensington
- **2034**: Maroubra, Maroubra South, Pagewood
- **2035**: Eastgardens, Chifley, Malabar, Little Bay, Phillip Bay

### Query Patterns
The chatbot recognizes various query patterns:
- **Price ranges**: "$1.5M to $2M", "between 1.5 and 2 million"
- **Bedroom counts**: "3 bedroom", "4 beds"
- **Bathroom counts**: "2 bathroom", "3 baths"
- **Comparisons**: "compare", "vs", "versus"
- **Trends**: "trend", "growth", "change"
- **Time periods**: "recent", "latest", "current"

## 📈 Analysis Features

### Price Analysis
- **Average Price**: Mean property price for filtered data
- **Median Price**: Middle value for price distribution
- **Price Range**: Minimum to maximum prices
- **Property Count**: Number of properties matching criteria

### Suburb Comparisons
- **Side-by-side Analysis**: Compare two suburbs directly
- **Price Differences**: Absolute and percentage differences
- **Property Counts**: Number of properties in each suburb
- **Market Positioning**: Relative affordability analysis

### Trend Analysis
- **Annual Growth**: Year-over-year price changes
- **Recent Trends**: Last 2 years vs previous periods
- **Growth Rates**: Percentage changes over time
- **Market Direction**: Increasing or decreasing trends

## 🎨 User Experience

### Command Line Interface
- **Simple Interaction**: Type questions and get immediate responses
- **Help Commands**: Built-in suggestions and help system
- **Error Handling**: Graceful error messages and recovery

### Web Interface
- **Modern Design**: Clean, professional chat interface
- **Real-time Updates**: Instant responses with typing indicators
- **Suggestion Chips**: Clickable suggestions for common questions
- **Mobile Responsive**: Works on all device sizes
- **Visual Feedback**: Loading states and error handling

## 🔍 Query Processing Pipeline

1. **Preprocessing**: Normalize and clean user input
2. **Keyword Extraction**: Identify property-related terms
3. **Pattern Recognition**: Match query patterns
4. **Filter Building**: Create database filters
5. **Data Querying**: Retrieve relevant property data
6. **Analysis Generation**: Create insights and reports
7. **Response Formatting**: Format output with emojis and structure

## 🚀 Future Enhancements

### Planned Features
- **Machine Learning**: Improve query understanding with ML models
- **Voice Interface**: Speech-to-text and text-to-speech capabilities
- **Advanced Analytics**: More sophisticated market analysis
- **Property Recommendations**: AI-powered property suggestions
- **Market Predictions**: Price forecasting models
- **Integration**: Connect with real estate APIs

### Technical Improvements
- **Caching**: Improve response times with data caching
- **Scalability**: Support for larger datasets and concurrent users
- **API Rate Limiting**: Protect against abuse
- **Advanced Filtering**: More sophisticated property filters
- **Data Visualization**: Charts and graphs in responses

## 🐛 Troubleshooting

### Common Issues

#### Data Loading Errors
- **Problem**: "Historical data file not found"
- **Solution**: Ensure `extract-3-very-clean.csv` exists in the `data/` directory

#### Web Interface Issues
- **Problem**: "Flask not installed"
- **Solution**: Run `pip install flask`

#### Import Errors
- **Problem**: Module import failures
- **Solution**: Ensure you're running from the project root directory

### Performance Optimization
- **Large Datasets**: The chatbot automatically filters to Eastern Suburbs and past 5 years
- **Memory Usage**: Data is loaded once and cached for subsequent queries
- **Response Time**: Queries are processed locally for fast responses

## 📝 API Documentation

### Chat Endpoint
```
POST /api/chat
Content-Type: application/json

{
    "message": "What's the average price in Bondi?"
}

Response:
{
    "response": "📊 Historical Price Analysis:\n🏠 Properties found: 5,469\n💰 Average price: $3,036,224\n...",
    "suggestions": ["What's the average price in Bondi?", "Show me properties in Paddington under $2M", ...]
}
```

### Suggestions Endpoint
```
GET /api/suggestions

Response:
{
    "suggestions": ["What's the average price in Bondi?", "Show me properties in Paddington under $2M", ...]
}
```

## 🤝 Contributing

### Development Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements.txt`
3. Run tests: `python test_chatbot.py`
4. Start development: `python run_chatbot.py`

### Code Structure
- **Core Logic**: `src/chatbot/property_chatbot.py`
- **Web Interface**: `src/chatbot/web_interface.py`
- **Templates**: `src/chatbot/templates/`
- **Tests**: `test_chatbot.py`
- **Runner**: `run_chatbot.py`

### Testing
- **Unit Tests**: Test individual chatbot methods
- **Integration Tests**: Test full query processing pipeline
- **User Acceptance Tests**: Test with real user queries

## 📄 License

This project is part of the NSW Property Visualiser and follows the same licensing terms.

## 🆘 Support

For issues and questions:
1. Check the troubleshooting section
2. Review the test output
3. Check the logs in `src/logs/`
4. Create an issue in the repository

---

**🏠 Eastern Suburbs Property AI Chatbot** - Making property data accessible through natural language!
