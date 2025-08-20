# Square Meter Extraction Implementation

## Overview

The property scraper has been enhanced to extract square meter data from property listings on both realestate.com.au and domain.com.au. This feature allows for more comprehensive property analysis including price per square meter calculations.

## Features Implemented

### 1. Square Meter Extraction Methods

#### `_extract_square_meters(card, details_text)`
- Extracts square meter data from property cards using multiple CSS selectors
- Searches for area information in property features, size, and land size elements
- Falls back to parsing the entire card text if specific elements are not found

#### `_parse_square_meters(text)`
- Parses square meter values from text using regex patterns
- Supports multiple unit formats:
  - Square meters: `sqm`, `sq m`, `m²`, `square meters`
  - Square feet: `sq ft`, `sqft`, `ft²`, `square feet`
  - Acres: `acres`, `ac`
  - Hectares: `hectares`, `ha`
  - Square yards: `sq yd`, `sqyd`, `yd²`, `square yards`
- Automatically converts all units to square meters

### 2. Unit Conversion Support

The extractor can handle and convert various area units:

| Unit | Conversion Factor | Example |
|------|------------------|---------|
| Square meters | 1:1 | `500 sqm` → 500 sqm |
| Square feet | 0.092903 | `750 sq ft` → 69 sqm |
| Acres | 4046.86 | `0.5 acres` → 2023 sqm |
| Hectares | 10000 | `2 hectares` → 20000 sqm |
| Square yards | 0.836127 | `1000 sq yd` → 836 sqm |

### 3. Integration with Existing Pipeline

- **Realestate.com.au extraction**: Enhanced `_extract_property_from_card()` method
- **Domain.com.au extraction**: Enhanced `_extract_property_from_domain_card()` method
- **Data processing**: Square meters are mapped to the `Area` field for compatibility with historical data
- **Sample data**: Includes realistic square meter values for testing

### 4. Data Structure Updates

The extracted data now includes:
- `square_meters`: Raw square meter value from extraction
- `Area`: Mapped field for compatibility with historical data format

## Usage

### Basic Usage

```python
from src.extractors.current_property_extractor import CurrentPropertyExtractor

# Create extractor
extractor = CurrentPropertyExtractor()

# Run extraction with square meter data
output_file = extractor.run_full_extraction(
    suburbs=['Bondi', 'Coogee'], 
    max_pages=3, 
    use_sample_data=True
)
```

### Testing Square Meter Parsing

```python
# Test different unit formats
extractor = CurrentPropertyExtractor()
test_cases = [
    '500 sqm',
    '750 sq ft', 
    '0.5 acres',
    '2 hectares',
    '1000 sq yd'
]

for text in test_cases:
    sqm = extractor._parse_square_meters(text)
    print(f'{text} -> {sqm} sqm')
```

## Output Format

The extracted data includes square meter information in the CSV output:

```csv
address,suburb,state,postcode,price,price_display,bedrooms,bathrooms,parking,square_meters,property_type,listing_date,source,data_type,Area,...
"100 Sample St, Bondi NSW 2026",Bondi,NSW,2026,1584920,"$1,584,920",2,1,1,157,House,2025-08-20,sample_data,for_sale,157,...
```

## Benefits

1. **Enhanced Analysis**: Enables price per square meter calculations
2. **Better Comparisons**: Allows for more accurate property value comparisons
3. **Market Insights**: Provides insights into land value vs. building value
4. **Historical Compatibility**: Works with existing analysis tools that expect `Area` field

## Technical Details

### CSS Selectors Used

The extractor searches for square meter data using these selectors:
- `span[data-testid="property-features-text"]`
- `span[data-testid="property-size"]`
- `div[data-testid="property-size"]`
- `span.size`, `div.size`
- `span[data-testid="land-size"]`
- `div[data-testid="land-size"]`
- `span.land-size`, `div.land-size`

### Regex Patterns

The parser uses these regex patterns to extract area values:
- Square meters: `(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:sq\s*m|sqm|m²|square\s*meters?)`
- Square feet: `(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:sq\s*ft|sqft|ft²|square\s*feet?)`
- Acres: `(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:acres?|ac)`
- Hectares: `(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:hectares?|ha)`
- Square yards: `(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:sq\s*yd|sqyd|yd²|square\s*yards?)`

## Future Enhancements

1. **More Data Sources**: Extend to other property websites
2. **Improved Parsing**: Add support for more unit formats
3. **Validation**: Add range validation for realistic square meter values
4. **Caching**: Cache parsed square meter data for performance
5. **Machine Learning**: Use ML to improve extraction accuracy

## Testing

The implementation includes comprehensive testing:
- Unit conversion accuracy
- Sample data generation
- Full extraction pipeline
- Integration with existing analysis tools

All tests pass and the feature is ready for production use.
