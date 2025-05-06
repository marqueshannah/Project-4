import json
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from collections import Counter
import os


class CosmeticsAnalyzer:
    def __init__(self, file_path='makeup_data.json'):
        """Initialize the analyzer with the path to the cosmetics JSON file."""
        self.file_path = file_path
        self.data = None
        self.df = None
        
    def load_data(self):
        """Load and parse the JSON data file."""
        try:
            with open(self.file_path, 'r', encoding='utf-8') as f:
                self.data = json.load(f)
            print(f"Successfully loaded {len(self.data)} products")
            
            # Convert to pandas DataFrame for easier analysis
            self.df = pd.json_normalize(self.data)
            
            # Convert price to numeric
            self.df['price'] = pd.to_numeric(self.df['price'], errors='coerce')
            
            return True
        except Exception as e:
            print(f"Error loading data: {e}")
            return False
    
    def save_processed_data(self, output_path='processed_cosmetics.csv'):
        """Save the processed DataFrame to a CSV file."""
        if self.df is not None:
            self.df.to_csv(output_path, index=False)
            print(f"Processed data saved to {output_path}")
            return True
        return False
    
    def get_basic_stats(self):
        """Generate basic statistics about the dataset."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        stats = {
            'total_products': len(self.df),
            'unique_brands': self.df['brand'].nunique(),
            'unique_product_types': self.df['product_type'].nunique(),
            'unique_categories': self.df['category'].nunique(),
            'price_stats': {
                'min': self.df['price'].min(),
                'max': self.df['price'].max(),
                'mean': self.df['price'].mean(),
                'median': self.df['price'].median()
            }
        }
        
        # Save stats to JSON
        with open('analysis_stats.json', 'w') as f:
            json.dump(stats, f, indent=4)
        
        return stats
    
    def analyze_brands(self):
        """Analyze brand distribution in the dataset."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        # Count products by brand
        brand_counts = self.df['brand'].value_counts().reset_index()
        brand_counts.columns = ['brand', 'count']
        
        # Save top brands to CSV
        top_brands = brand_counts.head(20)
        top_brands.to_csv('top_brands.csv', index=False)
        
        # Create a visualization
        plt.figure(figsize=(12, 8))
        sns.barplot(data=top_brands.head(10), x='count', y='brand')
        plt.title('Top 10 Brands by Product Count')
        plt.tight_layout()
        plt.savefig('brand_distribution.png')
        
        return top_brands
    
    def analyze_product_types(self):
        """Analyze product type distribution."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        # Count products by type
        type_counts = self.df['product_type'].value_counts().reset_index()
        type_counts.columns = ['product_type', 'count']
        
        # Save to CSV
        type_counts.to_csv('product_types.csv', index=False)
        
        # Create a visualization
        plt.figure(figsize=(12, 8))
        sns.barplot(data=type_counts.head(10), x='count', y='product_type')
        plt.title('Product Types Distribution')
        plt.tight_layout()
        plt.savefig('product_types.png')
        
        return type_counts
    
    def analyze_price_distribution(self):
        """Analyze the price distribution of products."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        # Create price range bins
        price_bins = [0, 5, 10, 15, 20, 30, float('inf')]
        price_labels = ['Under $5', '$5-$10', '$10-$15', '$15-$20', '$20-$30', '$30+']
        
        self.df['price_range'] = pd.cut(self.df['price'], bins=price_bins, labels=price_labels)
        price_dist = self.df['price_range'].value_counts().reset_index()
        price_dist.columns = ['price_range', 'count']
        
        # Save to CSV
        price_dist.to_csv('price_distribution.csv', index=False)
        
        # Create a visualization
        plt.figure(figsize=(10, 6))
        sns.barplot(data=price_dist, x='price_range', y='count')
        plt.title('Price Range Distribution')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('price_distribution.png')
        
        return price_dist
    
    def analyze_tags(self):
        """Analyze product tags in the dataset."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        # Collect all tags
        all_tags = []
        for tags in self.df['tag_list']:
            if isinstance(tags, list):
                all_tags.extend(tags)
        
        # Count frequency
        tag_counts = Counter(all_tags)
        tag_df = pd.DataFrame(tag_counts.items(), columns=['tag', 'count'])
        tag_df = tag_df.sort_values('count', ascending=False)
        
        # Save to CSV
        tag_df.to_csv('tag_distribution.csv', index=False)
        
        # Create a visualization
        plt.figure(figsize=(12, 8))
        sns.barplot(data=tag_df.head(10), x='count', y='tag')
        plt.title('Top 10 Product Tags')
        plt.tight_layout()
        plt.savefig('tag_distribution.png')
        
        return tag_df
    
    def analyze_colors(self):
        """Analyze product color distribution."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        # Process products with color data
        products_with_colors = self.df[self.df['product_colors'].apply(lambda x: isinstance(x, list) and len(x) > 0)]
        
        # Extract color names
        all_colors = []
        for colors in products_with_colors['product_colors']:
            if isinstance(colors, list):
                for color in colors:
                    if isinstance(color, dict) and 'colour_name' in color and color['colour_name'] is not None:
                        try:
                            all_colors.append(color['colour_name'].lower())
                        except AttributeError:
                            # Skip if colour_name is not a string or is None
                            continue
        
        # Count frequency
        color_counts = Counter(all_colors)
        color_df = pd.DataFrame(color_counts.items(), columns=['color', 'count'])
        color_df = color_df.sort_values('count', ascending=False)
        
        # Save to CSV
        color_df.to_csv('color_distribution.csv', index=False)
        
        # Create a visualization
        plt.figure(figsize=(12, 8))
        sns.barplot(data=color_df.head(15), x='count', y='color')
        plt.title('Top 15 Product Colors')
        plt.tight_layout()
        plt.savefig('color_distribution.png')
        
        return color_df
    
    def find_products_by_brand(self, brand_name):
        """Find all products from a specific brand."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        brand_products = self.df[self.df['brand'].str.lower() == brand_name.lower()]
        return brand_products
    
    def find_products_by_price_range(self, min_price, max_price):
        """Find products within a specific price range."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        price_range_products = self.df[(self.df['price'] >= min_price) & (self.df['price'] <= max_price)]
        return price_range_products
    
    def create_brand_price_report(self):
        """Create a report of average prices by brand."""
        if self.df is None:
            print("No data loaded. Call load_data() first.")
            return None
        
        # Calculate average price by brand
        brand_prices = self.df.groupby('brand')['price'].agg(['mean', 'min', 'max', 'count']).reset_index()
        brand_prices = brand_prices.sort_values('count', ascending=False)
        
        # Save to CSV
        brand_prices.to_csv('brand_price_report.csv', index=False)
        
        # Create a visualization for top 10 brands
        plt.figure(figsize=(12, 8))
        top_10_brands = brand_prices.head(10)
        sns.barplot(data=top_10_brands, x='brand', y='mean')
        plt.title('Average Price by Top 10 Brands')
        plt.xticks(rotation=45)
        plt.tight_layout()
        plt.savefig('brand_prices.png')
        
        return brand_prices
    
    def run_full_analysis(self):
        """Run all analysis methods and generate a comprehensive report."""
        if not self.load_data():
            return False
        
        print("\n----- Running Full Analysis -----")
        
        # Create output directory for reports
        os.makedirs('reports', exist_ok=True)
        
        # Get basic stats
        stats = self.get_basic_stats()
        print("\n----- Dataset Summary -----")
        print(f"Total Products: {stats['total_products']}")
        print(f"Number of Brands: {stats['unique_brands']}")
        print(f"Number of Product Types: {stats['unique_product_types']}")
        print(f"Number of Categories: {stats['unique_categories']}")
        print(f"Price Range: ${stats['price_stats']['min']} - ${stats['price_stats']['max']}")
        print(f"Average Price: ${stats['price_stats']['mean']:.2f}")
        
        # Run all analyses
        self.analyze_brands()
        self.analyze_product_types()
        self.analyze_price_distribution()
        self.analyze_tags()
        self.analyze_colors()
        self.create_brand_price_report()
        
        # Save processed data
        self.save_processed_data()
        
        print("\n----- Analysis Complete -----")
        print("All reports and visualizations have been saved.")
        return True


# Example usage
if __name__ == "__main__":
    analyzer = CosmeticsAnalyzer('makeup_data.json')
    analyzer.run_full_analysis()