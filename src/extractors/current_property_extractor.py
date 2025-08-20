import logging
import pandas as pd
import requests
from bs4 import BeautifulSoup
import time
import re
from datetime import datetime
import json
import os

# Configure logging
import os

# Ensure logs directory exists
logs_dir = os.path.join(os.path.dirname(__file__), '..', 'logs')
os.makedirs(logs_dir, exist_ok=True)

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s', 
                   handlers=[logging.FileHandler(os.path.join(logs_dir, "current_extraction.log")), logging.StreamHandler()])

class CurrentPropertyExtractor:
    """Handles extraction of current property listings data from various sources."""
    
    def __init__(self):
        # Ensure data directory exists
        data_dir = os.path.join(os.path.dirname(__file__), '..', 'data')
        os.makedirs(data_dir, exist_ok=True)
        
        self.output_file = os.path.join(data_dir, "current_property_data.csv")
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
            'Accept-Language': 'en-US,en;q=0.5',
            'Accept-Encoding': 'gzip, deflate',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
        })
        self.properties = []
        
    def extract_from_realestate_com_au(self, suburbs=None, max_pages=5):
        """Extract current property listings from realestate.com.au"""
        logging.info('Extracting current property data from realestate.com.au')
        
        if suburbs is None:
            # Eastern Suburbs of Sydney
            suburbs = ['Paddington', 'Woollahra', 'Bondi Junction', 'Bellevue Hill', 'Bronte', 
                      'Waverley', 'Queens Park', 'Bondi', 'Bondi Beach', 'North Bondi', 
                      'Tamarama', 'Edgecliff', 'Double Bay', 'Rose Bay', 'Vaucluse', 
                      'Dover Heights', 'Watsons Bay', 'Clovelly', 'Coogee', 'South Coogee', 
                      'Kensington', 'Maroubra', 'Maroubra South', 'Pagewood', 'Eastgardens', 
                      'Chifley', 'Malabar', 'Little Bay', 'Phillip Bay']
        
        for suburb in suburbs:
            logging.info(f'Extracting properties from {suburb}')
            try:
                # Search for properties in the suburb
                suburb_properties = self._scrape_realestate_suburb(suburb, max_pages)
                self.properties.extend(suburb_properties)
                logging.info(f'Found {len(suburb_properties)} properties in {suburb}')
                
                # Be respectful with delays
                time.sleep(5)  # Increased delay to avoid rate limiting
                
            except Exception as e:
                logging.error(f'Error extracting from {suburb}: {e}')
                continue
                
    def _scrape_realestate_suburb(self, suburb, max_pages):
        """Scrape properties from a specific suburb on realestate.com.au"""
        properties = []
        
        for page in range(1, max_pages + 1):
            try:
                # Construct the search URL for Eastern Suburbs
                suburb_clean = suburb.lower().replace(' ', '-')
                # Use a more specific search for Eastern Suburbs
                url = f"https://www.realestate.com.au/buy/property-house-with-{suburb_clean}-nsw/list-{page}"
                
                logging.info(f'Scraping page {page} for {suburb}: {url}')
                
                response = self.session.get(url, timeout=20)
                
                # Check for rate limiting
                if response.status_code == 429:
                    logging.warning(f'Rate limited for {suburb}, waiting 60 seconds...')
                    time.sleep(60)
                    continue
                    
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors for property cards (website structure may change)
                property_cards = []
                selectors = [
                    'article[data-testid="residential-card"]',
                    'article.residential-card',
                    'div[data-testid="listing-card"]',
                    'article[data-testid="listing-card"]',
                    'div.residential-card',
                    'article[data-testid="property-card"]',
                    'div[data-testid="property-card"]',
                    'article.property-card',
                    'div.property-card',
                    'article[data-testid="card"]',
                    'div[data-testid="card"]',
                    'article.card',
                    'div.card',
                    'div[data-testid="search-result"]',
                    'article[data-testid="search-result"]',
                    'div.search-result',
                    'article.search-result'
                ]
                
                for selector in selectors:
                    property_cards = soup.select(selector)
                    if property_cards:
                        logging.info(f'Found {len(property_cards)} properties using selector: {selector}')
                        break
                
                if not property_cards:
                    # Try a more generic approach - look for any article or div with price information
                    all_articles = soup.find_all(['article', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['card', 'listing', 'property', 'result']))
                    for article in all_articles:
                        # Check if this article contains price information
                        price_text = article.get_text()
                        if any(word in price_text.lower() for word in ['$', 'price', 'contact', 'guide']):
                            property_cards.append(article)
                    
                    if property_cards:
                        logging.info(f'Found {len(property_cards)} properties using generic approach')
                    else:
                        logging.info(f'No properties found on page {page} for {suburb}')
                        break
                
                for card in property_cards:
                    try:
                        property_data = self._extract_property_from_card(card, suburb)
                        if property_data:
                            properties.append(property_data)
                    except Exception as e:
                        logging.warning(f'Error extracting property from card: {e}')
                        continue
                
                # Check if we should continue to next page
                if len(property_cards) < 15:  # Usually 20 properties per page, but some pages have fewer
                    break
                
                # Add delay between pages to be respectful
                time.sleep(3)
                    
            except Exception as e:
                logging.error(f'Error scraping page {page} for {suburb}: {e}')
                break
                
        return properties
        
    def _extract_property_from_card(self, card, suburb):
        """Extract property data from a single property card"""
        try:
            # Try multiple selectors for price (website structure may change)
            price_elem = None
            price_selectors = [
                'span[data-testid="listing-details__summary-price"]',
                'span.property-price',
                'p[data-testid="listing-details__summary-price"]',
                'div[data-testid="price"]',
                'span.price',
                'div.price',
                'p.price',
                'span[data-testid="price"]',
                'div[data-testid="listing-price"]',
                'span[data-testid="listing-price"]',
                'p[data-testid="price"]',
                'div[class*="price"]',
                'span[class*="price"]',
                'p[class*="price"]'
            ]
            
            for selector in price_selectors:
                price_elem = card.select_one(selector)
                if price_elem:
                    break
            
            # If no price element found, try to find price in the entire card text
            if not price_elem:
                card_text = card.get_text()
                # Look for price patterns in the text
                price_match = re.search(r'\$[\d,]+(?:\.\d{2})?', card_text)
                if price_match:
                    price_text = price_match.group(0)
                else:
                    price_text = 'Contact Agent'
            else:
                price_text = price_elem.text.strip()
            
            price = self._extract_price(price_text)
            
            # Try multiple selectors for address
            address_elem = None
            address_selectors = [
                'span[data-testid="address"]',
                'span.property-address',
                'h2[data-testid="listing-details__summary-title"]',
                'div[data-testid="address"]',
                'span.address',
                'div.address',
                'h2[data-testid="address"]',
                'h3[data-testid="address"]',
                'div[data-testid="listing-address"]',
                'span[data-testid="listing-address"]',
                'div[class*="address"]',
                'span[class*="address"]',
                'h2[class*="address"]',
                'h3[class*="address"]'
            ]
            
            for selector in address_selectors:
                address_elem = card.select_one(selector)
                if address_elem:
                    break
            
            address = address_elem.text.strip() if address_elem else f'{suburb}, NSW'
            
            # Try multiple selectors for property details
            details_elem = None
            details_selectors = [
                'div[data-testid="property-features"]',
                'div.property-features',
                'div[data-testid="listing-details__summary-features"]',
                'div.features',
                'div[data-testid="features"]',
                'span[data-testid="features"]',
                'div[class*="features"]',
                'span[class*="features"]',
                'div[data-testid="property-details"]',
                'div[class*="details"]'
            ]
            
            for selector in details_selectors:
                details_elem = card.select_one(selector)
                if details_elem:
                    break
            
            details_text = details_elem.text if details_elem else ''
            
            # If no details element found, use the entire card text
            if not details_text:
                details_text = card.get_text()
            
            bedrooms = self._extract_bedrooms(details_text)
            bathrooms = self._extract_bathrooms(details_text)
            parking = self._extract_parking(details_text)
            
            # Extract square meters
            square_meters = self._extract_square_meters(card, details_text)
            
            # Extract property type
            property_type = self._extract_property_type(card)
            
            # Extract listing date
            listing_date = datetime.now().strftime('%Y-%m-%d')
            
            # Get postcode from address or use Eastern Suburbs mapping
            postcode = self._extract_postcode(address)
            if not postcode:
                # Eastern Suburbs postcode mapping
                EASTERN_SUBURBS_POSTCODES = {
                    'Paddington': '2021', 'Woollahra': '2021',
                    'Bondi Junction': '2022', 'Bellevue Hill': '2023',
                    'Bronte': '2024', 'Waverley': '2024', 'Queens Park': '2025',
                    'Bondi': '2026', 'Bondi Beach': '2026', 'North Bondi': '2026', 'Tamarama': '2026',
                    'Edgecliff': '2027', 'Double Bay': '2027', 'Rose Bay': '2028',
                    'Vaucluse': '2029', 'Dover Heights': '2029', 'Watsons Bay': '2030',
                    'Clovelly': '2031', 'Coogee': '2031', 'South Coogee': '2032',
                    'Kensington': '2033', 'Maroubra': '2034', 'Maroubra South': '2034', 'Pagewood': '2034',
                    'Eastgardens': '2035', 'Chifley': '2035', 'Malabar': '2035', 'Little Bay': '2035', 'Phillip Bay': '2035'
                }
                postcode = EASTERN_SUBURBS_POSTCODES.get(suburb, '2021')
            
            return {
                'address': address,
                'suburb': suburb,
                'state': 'NSW',
                'postcode': postcode,
                'price': price,
                'price_display': price_text,
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'parking': parking,
                'square_meters': square_meters,
                'property_type': property_type,
                'listing_date': listing_date,
                'source': 'realestate.com.au',
                'data_type': 'for_sale',
                'Area': square_meters
            }
            
        except Exception as e:
            logging.warning(f'Error extracting property data: {e}')
            return None
            
    def _extract_price(self, price_text):
        """Extract numeric price from price text"""
        if not price_text:
            return 0
            
        # Remove common price prefixes and extract numbers
        price_text = price_text.upper().replace('PRICE GUIDE', '').replace('CONTACT AGENT', '')
        
        # Extract numbers
        numbers = re.findall(r'[\d,]+', price_text)
        if numbers:
            # Take the first number and convert to integer
            price_str = numbers[0].replace(',', '')
            try:
                return int(price_str)
            except ValueError:
                return 0
        return 0
        
    def _extract_bedrooms(self, text):
        """Extract number of bedrooms from text"""
        if not text:
            return 0
        match = re.search(r'(\d+)\s*bed', text.lower())
        return int(match.group(1)) if match else 0
        
    def _extract_bathrooms(self, text):
        """Extract number of bathrooms from text"""
        if not text:
            return 0
        match = re.search(r'(\d+)\s*bath', text.lower())
        return int(match.group(1)) if match else 0
        
    def _extract_parking(self, text):
        """Extract number of parking spaces from text"""
        if not text:
            return 0
        match = re.search(r'(\d+)\s*park', text.lower())
        return int(match.group(1)) if match else 0
        
    def _extract_property_type(self, card):
        """Extract property type from card"""
        # Look for property type indicators
        card_text = card.get_text().lower()
        if 'house' in card_text:
            return 'House'
        elif 'unit' in card_text or 'apartment' in card_text:
            return 'Unit/Apartment'
        elif 'townhouse' in card_text:
            return 'Townhouse'
        else:
            return 'Unknown'
            
    def _extract_postcode(self, address):
        """Extract postcode from address"""
        if not address:
            return ''
        match = re.search(r'(\d{4})', address)
        return match.group(1) if match else ''
        
    def extract_from_domain_com_au(self, suburbs=None, max_pages=5):
        """Extract current property listings from domain.com.au"""
        logging.info('Extracting current property data from domain.com.au')
        
        if suburbs is None:
            # Eastern Suburbs of Sydney
            suburbs = ['Paddington', 'Woollahra', 'Bondi Junction', 'Bellevue Hill', 'Bronte', 
                      'Waverley', 'Queens Park', 'Bondi', 'Bondi Beach', 'North Bondi', 
                      'Tamarama', 'Edgecliff', 'Double Bay', 'Rose Bay', 'Vaucluse', 
                      'Dover Heights', 'Watsons Bay', 'Clovelly', 'Coogee', 'South Coogee', 
                      'Kensington', 'Maroubra', 'Maroubra South', 'Pagewood', 'Eastgardens', 
                      'Chifley', 'Malabar', 'Little Bay', 'Phillip Bay']
        
        for suburb in suburbs:
            logging.info(f'Extracting properties from {suburb} on Domain')
            try:
                suburb_properties = self._scrape_domain_suburb(suburb, max_pages)
                self.properties.extend(suburb_properties)
                logging.info(f'Found {len(suburb_properties)} properties in {suburb} on Domain')
                
                time.sleep(5)  # Increased delay to avoid rate limiting
                
            except Exception as e:
                logging.error(f'Error extracting from Domain {suburb}: {e}')
                continue
                
    def _scrape_domain_suburb(self, suburb, max_pages):
        """Scrape properties from a specific suburb on domain.com.au"""
        properties = []
        
        for page in range(1, max_pages + 1):
            try:
                # Construct the search URL for Domain Eastern Suburbs
                suburb_clean = suburb.lower().replace(' ', '-')
                url = f"https://www.domain.com.au/sale/{suburb_clean}-nsw/house/?page={page}"
                
                logging.info(f'Scraping Domain page {page} for {suburb}: {url}')
                
                response = self.session.get(url, timeout=15)
                
                # Check for rate limiting
                if response.status_code == 429:
                    logging.warning(f'Rate limited for {suburb} on Domain, waiting 30 seconds...')
                    time.sleep(30)
                    continue
                    
                response.raise_for_status()
                
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Try multiple selectors for Domain property cards
                property_cards = []
                domain_selectors = [
                    'div[data-testid="listing-details__summary"]',
                    'article[data-testid="listing-card"]',
                    'div[data-testid="listing-card"]',
                    'article.listing-card',
                    'div.listing-card'
                ]
                
                for selector in domain_selectors:
                    property_cards = soup.select(selector)
                    if property_cards:
                        logging.info(f'Found {len(property_cards)} properties on Domain using selector: {selector}')
                        break
                
                if not property_cards:
                    logging.info(f'No properties found on Domain page {page} for {suburb}')
                    break
                
                for card in property_cards:
                    try:
                        property_data = self._extract_property_from_domain_card(card, suburb)
                        if property_data:
                            properties.append(property_data)
                    except Exception as e:
                        logging.warning(f'Error extracting property from Domain card: {e}')
                        continue
                
                if len(property_cards) < 20:
                    break
                    
            except Exception as e:
                logging.error(f'Error scraping Domain page {page} for {suburb}: {e}')
                break
                
        return properties
        
    def _extract_property_from_domain_card(self, card, suburb):
        """Extract property data from a single Domain property card"""
        try:
            # Try multiple selectors for price on Domain
            price_elem = None
            domain_price_selectors = [
                'p[data-testid="listing-details__summary-price"]',
                'span[data-testid="listing-details__summary-price"]',
                'div[data-testid="price"]',
                'span.price',
                'p.price'
            ]
            
            for selector in domain_price_selectors:
                price_elem = card.select_one(selector)
                if price_elem:
                    break
            
            price = self._extract_price(price_elem.text if price_elem else '')
            
            # Try multiple selectors for address on Domain
            address_elem = None
            domain_address_selectors = [
                'span[data-testid="address"]',
                'h2[data-testid="listing-details__summary-title"]',
                'div[data-testid="address"]',
                'span.address',
                'h2.address'
            ]
            
            for selector in domain_address_selectors:
                address_elem = card.select_one(selector)
                if address_elem:
                    break
            
            address = address_elem.text.strip() if address_elem else f'{suburb}, NSW'
            
            # Try multiple selectors for property features on Domain
            features_elem = None
            domain_features_selectors = [
                'div[data-testid="property-features"]',
                'div[data-testid="listing-details__summary-features"]',
                'div.features',
                'div.property-features'
            ]
            
            for selector in domain_features_selectors:
                features_elem = card.select_one(selector)
                if features_elem:
                    break
            
            features_text = features_elem.text if features_elem else ''
            bedrooms = self._extract_bedrooms(features_text)
            bathrooms = self._extract_bathrooms(features_text)
            parking = self._extract_parking(features_text)
            
            # Extract square meters
            square_meters = self._extract_square_meters(card, features_text)
            
            # Get postcode from address or use Eastern Suburbs mapping
            postcode = self._extract_postcode(address)
            if not postcode:
                # Eastern Suburbs postcode mapping
                EASTERN_SUBURBS_POSTCODES = {
                    'Paddington': '2021', 'Woollahra': '2021',
                    'Bondi Junction': '2022', 'Bellevue Hill': '2023',
                    'Bronte': '2024', 'Waverley': '2024', 'Queens Park': '2025',
                    'Bondi': '2026', 'Bondi Beach': '2026', 'North Bondi': '2026', 'Tamarama': '2026',
                    'Edgecliff': '2027', 'Double Bay': '2027', 'Rose Bay': '2028',
                    'Vaucluse': '2029', 'Dover Heights': '2029', 'Watsons Bay': '2030',
                    'Clovelly': '2031', 'Coogee': '2031', 'South Coogee': '2032',
                    'Kensington': '2033', 'Maroubra': '2034', 'Maroubra South': '2034', 'Pagewood': '2034',
                    'Eastgardens': '2035', 'Chifley': '2035', 'Malabar': '2035', 'Little Bay': '2035', 'Phillip Bay': '2035'
                }
                postcode = EASTERN_SUBURBS_POSTCODES.get(suburb, '2021')
            
            return {
                'address': address,
                'suburb': suburb,
                'state': 'NSW',
                'postcode': postcode,
                'price': price,
                'price_display': price_elem.text.strip() if price_elem else 'Contact Agent',
                'bedrooms': bedrooms,
                'bathrooms': bathrooms,
                'parking': parking,
                'square_meters': square_meters,
                'property_type': 'House',  # Domain search is for houses
                'listing_date': datetime.now().strftime('%Y-%m-%d'),
                'source': 'domain.com.au',
                'data_type': 'for_sale'
            }
            
        except Exception as e:
            logging.warning(f'Error extracting Domain property data: {e}')
            return None
        
    def process_current_data(self):
        """Process and clean current property data"""
        logging.info('Processing current property data')
        
        if not self.properties:
            logging.warning('No properties found to process')
            # Create empty DataFrame with correct structure
            df = pd.DataFrame(columns=[
                'address', 'suburb', 'state', 'postcode', 'price', 'price_display',
                'bedrooms', 'bathrooms', 'parking', 'square_meters', 'property_type', 'listing_date',
                'source', 'data_type', 'Contract date', 'Settlement date', 'Purchase price',
                'Property locality', 'Property street name', 'Property post code',
                'Area', 'Zoning', 'Primary purpose'
            ])
        else:
            # Convert to DataFrame
            df = pd.DataFrame(self.properties)
            
            # Clean and standardize data
            df = self._clean_property_data(df)
        
        # Save to CSV
        df.to_csv(self.output_file, index=False)
        logging.info(f'Processed {len(df)} properties and saved to {self.output_file}')
        
        return self.output_file
        
    def _clean_property_data(self, df):
        """Clean and standardize property data"""
        # Remove duplicates based on address and price
        df = df.drop_duplicates(subset=['address', 'price'], keep='first')
        
        # Clean price data
        df['price'] = pd.to_numeric(df['price'], errors='coerce').fillna(0)
        
        # Clean numeric fields
        for field in ['bedrooms', 'bathrooms', 'parking']:
            df[field] = pd.to_numeric(df[field], errors='coerce').fillna(0)
            
        # Standardize property types
        df['property_type'] = df['property_type'].fillna('Unknown')
        
        # Add missing columns to match historical data format
        df['Contract date'] = df['listing_date']
        df['Settlement date'] = ''
        df['Purchase price'] = df['price']
        df['Property locality'] = df['suburb']
        df['Property street name'] = df['address'].apply(lambda x: x.split(',')[0] if ',' in x else x)
        df['Property post code'] = df['postcode']
        # Map square_meters to Area field (historical data format)
        df['Area'] = df.get('square_meters', 0)
        df['Zoning'] = 'Residential'
        df['Primary purpose'] = 'House'
        
        return df
        
    def create_sample_data(self, suburbs=None):
        """Create sample property data for testing when web scraping fails"""
        logging.info('Creating sample property data for testing')
        
        # Eastern Suburbs postcode mapping
        EASTERN_SUBURBS_POSTCODES = {
            'Paddington': '2021', 'Woollahra': '2021',
            'Bondi Junction': '2022',
            'Bellevue Hill': '2023',
            'Bronte': '2024', 'Waverley': '2024',
            'Queens Park': '2025',
            'Bondi': '2026', 'Bondi Beach': '2026', 'North Bondi': '2026', 'Tamarama': '2026',
            'Edgecliff': '2027', 'Double Bay': '2027',
            'Rose Bay': '2028',
            'Vaucluse': '2029', 'Dover Heights': '2029',
            'Watsons Bay': '2030',
            'Clovelly': '2031', 'Coogee': '2031',
            'South Coogee': '2032',
            'Kensington': '2033',
            'Maroubra': '2034', 'Maroubra South': '2034', 'Pagewood': '2034',
            'Eastgardens': '2035', 'Chifley': '2035', 'Malabar': '2035', 'Little Bay': '2035', 'Phillip Bay': '2035'
        }
        
        if suburbs is None:
            # Eastern Suburbs of Sydney
            suburbs = ['Paddington', 'Woollahra', 'Bondi Junction', 'Bellevue Hill', 'Bronte', 
                      'Waverley', 'Queens Park', 'Bondi', 'Bondi Beach', 'North Bondi', 
                      'Tamarama', 'Edgecliff', 'Double Bay', 'Rose Bay', 'Vaucluse', 
                      'Dover Heights', 'Watsons Bay', 'Clovelly', 'Coogee', 'South Coogee', 
                      'Kensington', 'Maroubra', 'Maroubra South', 'Pagewood', 'Eastgardens', 
                      'Chifley', 'Malabar', 'Little Bay', 'Phillip Bay']
        
        sample_properties = []
        
        for suburb in suburbs:
            # Create 5-8 sample properties per suburb (increased from 2)
            num_properties = 5 + (hash(suburb) % 4)  # 5-8 properties per suburb
            
            for i in range(num_properties):
                # Generate realistic Eastern Suburbs prices (1.2M - 6M range)
                base_price = 1200000 + (hash(suburb) % 1200000)  # Vary base price by suburb
                price = base_price + (i * 150000) + (hash(f"{suburb}{i}") % 400000)  # Add variation
                bedrooms = 2 + (i % 4)  # 2, 3, 4, or 5 bedrooms
                bathrooms = 1 + (i % 3)  # 1, 2, or 3 bathrooms
                
                # Get correct postcode for the suburb
                postcode = EASTERN_SUBURBS_POSTCODES.get(suburb, '2021')
                
                # Generate realistic area data (150-500 sqm for Eastern Suburbs houses)
                area = 150 + (hash(f"{suburb}{i}") % 350)
                
                # Vary property types
                property_types = ['House', 'Unit/Apartment', 'Townhouse']
                property_type = property_types[i % len(property_types)]
                
                # Vary parking spaces
                parking = 1 + (i % 3)  # 1, 2, or 3 parking spaces
                
                sample_properties.append({
                    'address': f'{100 + i * 25} Sample St, {suburb} NSW {postcode}',
                    'suburb': suburb,
                    'state': 'NSW',
                    'postcode': postcode,
                    'price': price,
                    'price_display': f'${price:,}',
                    'bedrooms': bedrooms,
                    'bathrooms': bathrooms,
                    'parking': parking,
                    'square_meters': area,
                    'property_type': property_type,
                    'listing_date': datetime.now().strftime('%Y-%m-%d'),
                    'source': 'sample_data',
                    'data_type': 'for_sale',
                    'Area': area
                })
        
        self.properties = sample_properties
        logging.info(f'Created {len(sample_properties)} sample properties for Eastern Suburbs')
        return sample_properties

    def run_full_extraction(self, suburbs=None, max_pages=5, use_sample_data=True):
        """Run the complete current property extraction pipeline"""
        logging.info('Starting current property extraction pipeline')
        
        if use_sample_data:
            # Use sample data instead of web scraping
            self.create_sample_data(suburbs)
        else:
            # Step 1: Extract from various sources
            try:
                self.extract_from_realestate_com_au(suburbs, max_pages)
            except Exception as e:
                logging.error(f'Failed to extract from realestate.com.au: {e}')
                
            try:
                self.extract_from_domain_com_au(suburbs, max_pages)
            except Exception as e:
                logging.error(f'Failed to extract from domain.com.au: {e}')
            
            # If no properties were found, create sample data
            if not self.properties:
                logging.warning('No properties found from web scraping, creating sample data')
                self.create_sample_data(suburbs)
        
        # Step 2: Process and clean data
        output_file = self.process_current_data()
        
        logging.info('Current property extraction pipeline complete')
        logging.info(f'Output saved to: {output_file}')
        
        return output_file

    def _extract_square_meters(self, card, details_text):
        """Extract square meter data from property card"""
        try:
            # Try multiple selectors for square meter data
            sqm_selectors = [
                'span[data-testid="property-features-text"]',
                'span[data-testid="property-size"]',
                'div[data-testid="property-size"]',
                'span.size',
                'div.size',
                'span[data-testid="land-size"]',
                'div[data-testid="land-size"]',
                'span.land-size',
                'div.land-size'
            ]
            
            # First try to find square meter data in the card elements
            for selector in sqm_selectors:
                sqm_elem = card.select_one(selector)
                if sqm_elem:
                    sqm_text = sqm_elem.text.strip()
                    sqm = self._parse_square_meters(sqm_text)
                    if sqm > 0:
                        return sqm
            
            # If not found in elements, try to extract from details text
            if details_text:
                sqm = self._parse_square_meters(details_text)
                if sqm > 0:
                    return sqm
            
            # If still not found, try to extract from the entire card text
            card_text = card.get_text()
            sqm = self._parse_square_meters(card_text)
            return sqm if sqm > 0 else 0
            
        except Exception as e:
            logging.warning(f'Error extracting square meters: {e}')
            return 0
    
    def _parse_square_meters(self, text):
        """Parse square meter value from text"""
        if not text:
            return 0
        
        # Common patterns for square meters
        patterns = [
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:sq\s*m|sqm|m²|square\s*meters?)',
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:sq\s*ft|sqft|ft²|square\s*feet?)',
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:acres?|ac)',
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:hectares?|ha)',
            r'(\d+(?:,\d+)?(?:\.\d+)?)\s*(?:sq\s*yd|sqyd|yd²|square\s*yards?)'
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                value = float(match.group(1).replace(',', ''))
                
                # Convert to square meters based on unit
                if 'sq ft' in match.group(0) or 'sqft' in match.group(0) or 'ft²' in match.group(0):
                    return int(value * 0.092903)  # Convert sq ft to sq m
                elif 'acres' in match.group(0) or 'ac' in match.group(0):
                    return int(value * 4046.86)  # Convert acres to sq m
                elif 'hectares' in match.group(0) or 'ha' in match.group(0):
                    return int(value * 10000)  # Convert hectares to sq m
                elif 'sq yd' in match.group(0) or 'sqyd' in match.group(0) or 'yd²' in match.group(0):
                    return int(value * 0.836127)  # Convert sq yards to sq m
                else:
                    return int(value)  # Already in square meters
        
        return 0

if __name__ == "__main__":
    extractor = CurrentPropertyExtractor()
    
    # Example usage for Eastern Suburbs - using more suburbs to get more properties
    target_suburbs = [
        'Paddington', 'Woollahra', 'Bondi Junction', 'Bellevue Hill', 'Bronte', 
        'Waverley', 'Queens Park', 'Bondi', 'Bondi Beach', 'North Bondi', 
        'Tamarama', 'Edgecliff', 'Double Bay', 'Rose Bay', 'Vaucluse', 
        'Dover Heights', 'Watsons Bay', 'Clovelly', 'Coogee', 'South Coogee', 
        'Kensington', 'Maroubra', 'Maroubra South', 'Pagewood', 'Eastgardens', 
        'Chifley', 'Malabar', 'Little Bay', 'Phillip Bay'
    ]
    
    print("🏠 Starting Eastern Suburbs Property Extraction")
    print(f"📊 Targeting {len(target_suburbs)} suburbs")
    
    output_file = extractor.run_full_extraction(
        suburbs=target_suburbs, 
        max_pages=3, 
        use_sample_data=True  # Use sample data for reliable results
    )
    
    print(f"✅ Extraction completed!")
    print(f"📁 Results saved to: {output_file}")
    
    # Show summary
    import pandas as pd
    if os.path.exists(output_file):
        df = pd.read_csv(output_file)
        print(f"\n📊 Summary:")
        print(f"   Total properties: {len(df)}")
        print(f"   Suburbs covered: {df['suburb'].nunique()}")
        print(f"   Average price: ${df['price'].mean():,.0f}")
        print(f"   Price range: ${df['price'].min():,.0f} - ${df['price'].max():,.0f}")
