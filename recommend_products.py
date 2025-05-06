#!/usr/bin/env python3
"""
Cosmetic Products Recommendation System
Provides product recommendations based on user-selected features.
"""

import pandas as pd
import os
import argparse
from difflib import get_close_matches


class CosmeticRecommender:
    def __init__(self, data_folder='data', output_folder='recommendations'):
        self.data_folder = data_folder
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        
        # Initialize data attributes
        self.products = None
        self.tags = None
        self.colors = None
        self.options = {}  # Will store all available filter options
    
    def load_data(self):
        """Load all necessary data files for recommendation system."""
        try:
            # Load main product data
            self.products = pd.read_csv(f"{self.data_folder}/products_main.csv")
            print(f"Loaded {len(self.products)} products")
            
            # Try to load optional data
            for file_name, attr_name in [
                ('product_tags.csv', 'tags'),
                ('product_colors.csv', 'colors')
            ]:
                try:
                    setattr(self, attr_name, pd.read_csv(f"{self.data_folder}/{file_name}"))
                    print(f"Loaded {file_name}")
                except:
                    print(f"{file_name} not available")
            
            # Extract available options
            self._extract_options()
            return True
            
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def _extract_options(self):
        """Extract all available filter options at once."""
        if self.products is None:
            return
            
        # Store all options in the options dictionary
        for column in ['brand', 'product_type', 'category']:
            if column in self.products.columns:
                self.options[column] = sorted(self.products[column].dropna().unique())
        
        # Create price ranges
        if 'price' in self.products.columns:
            self.products['price'] = pd.to_numeric(self.products['price'], errors='coerce')
            self.options['price_range'] = ['Under $5', '$5-$10', '$10-$15', '$15-$20', '$20-$30', 'Over $30']
        
        # Extract tags and colors (only common ones)
        threshold = 3  # Minimum occurrences to be considered common
        
        if self.tags is not None:
            tag_counts = self.tags['tag'].value_counts()
            self.options['tags'] = sorted(tag_counts[tag_counts >= threshold].index.tolist())
            
        if self.colors is not None:
            color_counts = self.colors['colour_name'].value_counts()
            self.options['colors'] = sorted(color_counts[color_counts >= threshold].index.tolist())
            
        # Print summary of available options
        for key, values in self.options.items():
            print(f"Found {len(values)} {key.replace('_', ' ')}s")
    
    def show_options(self):
        """Display available options for filtering."""
        print("\n===== AVAILABLE OPTIONS FOR FILTERING =====")
        
        for category, options in self.options.items():
            display_name = category.replace('_', ' ').title()
            
            # Only show top 10 for long lists
            if len(options) > 10:
                print(f"\n{display_name}s ({len(options)} total, showing top 10):")
                for option in options[:10]:
                    print(f"- {option}")
                print("...")
            else:
                print(f"\n{display_name}s ({len(options)} total):")
                for option in options:
                    print(f"- {option}")
    
    def recommend(self, **criteria):
        """Find products matching the given criteria."""
        if self.products is None:
            print("Data not loaded. Call load_data() first.")
            return None
            
        # Start with all products
        results = self.products.copy()
        filters_applied = []
        
        # Apply simple filters (exact matches)
        for field in ['brand', 'product_type', 'category']:
            if field in criteria and criteria[field] and field in self.options:
                value = criteria[field]
                if value in self.options[field]:
                    results = results[results[field] == value]
                    filters_applied.append(f"{field.title()}: {value}")
        
        # Apply price range filter
        if 'price_range' in criteria and criteria['price_range'] in self.options.get('price_range', []):
            price_range = criteria['price_range']
            
            # Map price range strings to numeric ranges
            ranges = {
                'Under $5': (0, 5),
                '$5-$10': (5, 10),
                '$10-$15': (10, 15),
                '$15-$20': (15, 20),
                '$20-$30': (20, 30),
                'Over $30': (30, float('inf'))
            }
            
            if price_range in ranges:
                min_price, max_price = ranges[price_range]
                if max_price == float('inf'):
                    results = results[results['price'] >= min_price]
                else:
                    results = results[(results['price'] >= min_price) & (results['price'] < max_price)]
                    
                filters_applied.append(f"Price Range: {price_range}")
        
        # Apply tag filter (products must have ALL specified tags)
        if 'tags' in criteria and criteria['tags'] and self.tags is not None:
            tags = criteria['tags'] if isinstance(criteria['tags'], list) else [criteria['tags']]
            valid_tags = [tag for tag in tags if tag in self.options.get('tags', [])]
            
            if valid_tags:
                matching_products = set()
                first_tag = True
                
                for tag in valid_tags:
                    products_with_tag = set(self.tags[self.tags['tag'] == tag]['id'])
                    if first_tag:
                        matching_products = products_with_tag
                        first_tag = False
                    else:
                        matching_products &= products_with_tag  # Intersection
                
                results = results[results['id'].isin(matching_products)]
                filters_applied.append(f"Tags: {', '.join(valid_tags)}")
        
        # Apply color filter (products must have ANY of the specified colors)
        if 'colors' in criteria and criteria['colors'] and self.colors is not None:
            colors = criteria['colors'] if isinstance(criteria['colors'], list) else [criteria['colors']]
            valid_colors = [color for color in colors if color in self.options.get('colors', [])]
            
            if valid_colors:
                matching_products = set()
                
                for color in valid_colors:
                    products_with_color = set(self.colors[self.colors['colour_name'] == color]['product_id'])
                    matching_products |= products_with_color  # Union
                
                results = results[results['id'].isin(matching_products)]
                filters_applied.append(f"Colors: {', '.join(valid_colors)}")
        
        # Apply rating filter
        if 'min_rating' in criteria and criteria['min_rating'] is not None:
            min_rating = criteria['min_rating']
            results = results[(results['rating'] >= min_rating) & results['rating'].notna()]
            filters_applied.append(f"Minimum Rating: {min_rating}")
        
        # Sort results (by rating if available, otherwise by name)
        if 'rating' in results.columns and results['rating'].notna().any():
            results = results.sort_values('rating', ascending=False)
        else:
            results = results.sort_values('name')
        
        # Apply limit
        limit = criteria.get('limit', 10)
        if limit > 0:
            results = results.head(limit)
        
        # Print filter information
        if filters_applied:
            print(f"\nFilters applied: {' | '.join(filters_applied)}")
            
        print(f"\nFound {len(results)} matching products")
        return results
    
    def print_recommendations(self, recommendations):
        """Print formatted recommendations."""
        if recommendations is None or len(recommendations) == 0:
            print("\nNo products match your criteria. Try adjusting your filters.")
            return
            
        print("\n===== RECOMMENDED PRODUCTS =====\n")
        
        for i, (_, product) in enumerate(recommendations.iterrows(), 1):
            print(f"{i}. {product['name']}")
            print(f"   Brand: {product['brand']}")
            print(f"   Type: {product['product_type']}")
            
            # Print optional fields if available
            for field, label in [
                ('category', 'Category'),
                ('price', 'Price'),
                ('rating', 'Rating')
            ]:
                if field in product and not pd.isna(product[field]):
                    value = product[field]
                    if field == 'price':
                        currency = product.get('price_sign', '$')
                        print(f"   {label}: {currency}{value}")
                    elif field == 'rating':
                        print(f"   {label}: {value:.1f}/5.0")
                    else:
                        print(f"   {label}: {value}")
            
            # Print tags if available
            if self.tags is not None:
                product_tags = self.tags[self.tags['id'] == product['id']]['tag'].tolist()
                if product_tags:
                    print(f"   Tags: {', '.join(product_tags)}")
                    
            # Print colors (limited to 5)
            if self.colors is not None:
                product_colors = self.colors[self.colors['product_id'] == product['id']]['colour_name'].tolist()
                if product_colors:
                    display_colors = product_colors[:5]
                    print(f"   Colors: {', '.join(display_colors)}")
                    if len(product_colors) > 5:
                        print(f"           ... and {len(product_colors) - 5} more")
            
            print()  # Empty line between products
    
    def save_recommendations(self, recommendations, filename=None):
        """Save recommendations to a CSV file."""
        if recommendations is None or len(recommendations) == 0:
            return None
            
        if filename is None:
            timestamp = pd.Timestamp.now().strftime("%Y%m%d_%H%M%S")
            filename = f"recommendations_{timestamp}"
            
        output_path = f"{self.output_folder}/{filename}.csv"
        
        try:
            # Get available columns
            columns_to_save = ['id', 'brand', 'name', 'product_type', 'category', 
                              'price', 'price_sign', 'currency', 'rating']
            existing_columns = [col for col in columns_to_save if col in recommendations.columns]
            
            recommendations[existing_columns].to_csv(output_path, index=False)
            print(f"\nRecommendations saved to {output_path}")
            return output_path
        except Exception as e:
            print(f"Error saving recommendations: {e}")
            return None
    
    def get_user_input(self, prompt, options=None):
        """Get user input with validation against available options."""
        value = input(prompt).strip()
        
        if not value or options is None:
            return None if not value else value
            
        if value not in options:
            # Try to find close matches
            matches = get_close_matches(value.lower(), [opt.lower() for opt in options], n=1, cutoff=0.6)
            if matches:
                match_idx = [opt.lower() for opt in options].index(matches[0])
                match = options[match_idx]
                
                use_match = input(f"'{value}' not found. Did you mean '{match}'? (y/n): ").lower()
                if use_match.startswith('y'):
                    return match
            
            print(f"'{value}' not found in available options. Skipping this filter.")
            return None
            
        return value
    
    def run_interactive(self):
        """Run the recommender in interactive mode."""
        if not self.load_data():
            print("Failed to load data. Exiting.")
            return
            
        print("\n===== COSMETIC PRODUCT RECOMMENDATION SYSTEM =====")
        print("This system helps you find cosmetic products based on your preferences.")
        
        # Show options if requested
        if input("\nWould you like to see available options? (y/n): ").lower().startswith('y'):
            self.show_options()
            
        print("\nEnter your preferences (press Enter to skip):")
        
        # Collect user preferences
        criteria = {}
        
        # Get simple field inputs
        for field, prompt in [
            ('brand', "Brand: "),
            ('product_type', "Product type: "),
            ('category', "Category: ")
        ]:
            if field in self.options:
                criteria[field] = self.get_user_input(prompt, self.options[field])
        
        # Get price range
        if 'price_range' in self.options:
            print("Available price ranges:")
            for i, pr in enumerate(self.options['price_range'], 1):
                print(f"{i}. {pr}")
                
            price_input = input("Select a price range (number or name): ")
            
            try:
                # Check if input is a number
                choice_idx = int(price_input) - 1
                if 0 <= choice_idx < len(self.options['price_range']):
                    criteria['price_range'] = self.options['price_range'][choice_idx]
            except ValueError:
                # Input is a range name
                if price_input in self.options['price_range']:
                    criteria['price_range'] = price_input
                elif price_input:
                    print(f"Price range '{price_input}' not found. Skipping price filter.")
        
        # Get multi-value inputs
        for field, prompt in [
            ('tags', "Tags (comma-separated): "),
            ('colors', "Colors (comma-separated): ")
        ]:
            if field in self.options:
                value = input(prompt)
                if value:
                    items = [item.strip() for item in value.split(',')]
                    valid_items = [item for item in items if item in self.options[field]]
                    if valid_items:
                        criteria[field] = valid_items
                    elif items:
                        print(f"No valid {field} found. Skipping {field} filter.")
        
        # Get rating and limit
        try:
            min_rating = input("Minimum rating (1-5): ")
            criteria['min_rating'] = float(min_rating) if min_rating else None
            if criteria['min_rating'] is not None and not (1 <= criteria['min_rating'] <= 5):
                print("Rating must be between 1 and 5. Skipping rating filter.")
                criteria['min_rating'] = None
        except ValueError:
            criteria['min_rating'] = None
            
        try:
            limit_input = input("Number of recommendations (default: 10): ")
            criteria['limit'] = int(limit_input) if limit_input else 10
        except ValueError:
            criteria['limit'] = 10
        
        # Get recommendations
        recommendations = self.recommend(**criteria)
        
        # Print and save recommendations
        self.print_recommendations(recommendations)
        
        if recommendations is not None and len(recommendations) > 0:
            if input("\nWould you like to save these recommendations? (y/n): ").lower().startswith('y'):
                self.save_recommendations(recommendations)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Cosmetic Product Recommendation System")
    parser.add_argument("--data", default="data", help="Path to data folder")
    parser.add_argument("--output", default="recommendations", help="Path to output folder")
    
    args = parser.parse_args()
    
    recommender = CosmeticRecommender(data_folder=args.data, output_folder=args.output)
    recommender.run_interactive()