import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import numpy as np

class CosmeticsVisualizer:
    """Create visualizations for the cosmetics dataset."""
    
    def __init__(self, data_folder='data', output_folder='visualizations'):
        self.data_folder = data_folder
        self.output_folder = output_folder
        os.makedirs(output_folder, exist_ok=True)
        
        # Set visualization style
        sns.set_style("whitegrid")
        self.brand_palette = sns.color_palette("viridis", 10)
        self.price_palette = sns.color_palette("YlOrRd", 6)
        self.type_palette = sns.color_palette("muted", 10)
        
    def load_data(self):
        """Load all CSV files from the data folder."""
        self.products = pd.read_csv(f"{self.data_folder}/products_main.csv")
        
        # Try to load optional files
        for file_name, attr_name in [
            ('product_descriptions.csv', 'descriptions'),
            ('product_tags.csv', 'tags'),
            ('product_colors.csv', 'colors')
        ]:
            try:
                setattr(self, attr_name, pd.read_csv(f"{self.data_folder}/{file_name}"))
            except:
                setattr(self, attr_name, None)
        
        # Convert price to numeric
        if 'price' in self.products.columns:
            self.products['price'] = pd.to_numeric(self.products['price'], errors='coerce')
        
        print("Data loaded successfully.")
    
    def save_plot(self, filename, title, close=True):
        """Common function to save plots with proper formatting."""
        plt.title(title, fontsize=16, pad=20)
        plt.tight_layout()
        plt.savefig(f"{self.output_folder}/{filename}", dpi=300, bbox_inches='tight')
        if close:
            plt.close()
        print(f"Saved {filename} to {self.output_folder}/")
    
    def create_bar_chart(self, data, x, y, filename, title, palette=None, rotation=0, add_labels=True):
        """Create a standard bar chart with consistent formatting."""
        plt.figure(figsize=(12, 7))
        ax = sns.barplot(data=data, x=x, y=y, palette=palette or self.brand_palette)
        
        if add_labels:
            for i, v in enumerate(data[x].values):
                ax.text(v + 0.5, i, str(v), va='center')
        
        plt.xlabel(x.replace('_', ' ').title(), fontsize=12)
        plt.ylabel(y.replace('_', ' ').title(), fontsize=12)
        plt.xticks(rotation=rotation)
        self.save_plot(filename, title)
    
    def create_brand_distribution(self):
        """Create a bar chart of top brands by product count."""
        if 'brand' not in self.products.columns:
            return
            
        brand_counts = self.products['brand'].value_counts().reset_index()
        brand_counts.columns = ['brand', 'count']
        
        self.create_bar_chart(
            brand_counts.head(10), 
            'count', 'brand', 
            'brand_distribution.png', 
            'Top 10 Brands by Product Count'
        )
    
    def create_price_distribution(self):
        """Create price distribution visualizations."""
        if 'price' not in self.products.columns:
            return
            
        # Histogram and boxplot
        fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(12, 10))
        
        sns.histplot(data=self.products, x='price', bins=30, kde=True, 
                    color=self.price_palette[3], ax=ax1)
        ax1.set_title('Price Distribution Histogram', fontsize=14)
        ax1.set_xlabel('Price ($)', fontsize=12)
        
        # Filter outliers for boxplot
        price_cutoff = self.products['price'].quantile(0.75) + 1.5 * (
            self.products['price'].quantile(0.75) - self.products['price'].quantile(0.25))
        filtered_prices = self.products[self.products['price'] <= price_cutoff]
        
        sns.boxplot(data=filtered_prices, x='price', color=self.price_palette[2], ax=ax2)
        ax2.set_title('Price Distribution (without extreme outliers)', fontsize=14)
        ax2.set_xlabel('Price ($)', fontsize=12)
        
        self.save_plot('price_distribution.png', '', close=False)
        plt.close()
        
        # Price range bar chart
        price_bins = [0, 5, 10, 15, 20, 30, float('inf')]
        price_labels = ['Under $5', '$5-$10', '$10-$15', '$15-$20', '$20-$30', 'Over $30']
        
        self.products['price_range'] = pd.cut(
            self.products['price'], bins=price_bins, labels=price_labels)
        
        price_counts = self.products['price_range'].value_counts().reset_index()
        price_counts.columns = ['price_range', 'count']
        price_counts['sort_order'] = price_counts['price_range'].map(
            {label: i for i, label in enumerate(price_labels)})
        price_counts = price_counts.sort_values('sort_order')
        
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(data=price_counts, x='price_range', y='count', palette=self.price_palette)
        
        for i, v in enumerate(price_counts['count']):
            ax.text(i, v + 5, str(v), ha='center')
        
        plt.xlabel('Price Range', fontsize=12)
        plt.ylabel('Number of Products', fontsize=12)
        plt.xticks(rotation=45)
        self.save_plot('price_range_distribution.png', 'Price Range Distribution')
    
    def create_product_type_distribution(self):
        """Create product type visualizations."""
        if 'product_type' not in self.products.columns:
            return
            
        type_counts = self.products['product_type'].value_counts().reset_index()
        type_counts.columns = ['product_type', 'count']
        
        # Bar chart
        self.create_bar_chart(
            type_counts.head(10), 
            'count', 'product_type', 
            'product_type_bar.png', 
            'Top 10 Product Types',
            palette=self.type_palette
        )
        
        # Pie chart
        top_types = type_counts.head(8)
        other_count = type_counts.iloc[8:]['count'].sum() if len(type_counts) > 8 else 0
        
        if other_count > 0:
            other_row = pd.DataFrame([{'product_type': 'Other', 'count': other_count}])
            plot_data = pd.concat([top_types, other_row], ignore_index=True)
        else:
            plot_data = top_types
        
        plt.figure(figsize=(10, 10))
        plt.pie(
            plot_data['count'], 
            labels=plot_data['product_type'],
            autopct='%1.1f%%',
            startangle=90,
            colors=self.type_palette,
            wedgeprops=dict(edgecolor='w', linewidth=1)
        )
        plt.axis('equal')
        self.save_plot('product_type_distribution.png', 'Product Types Distribution')
    
    def create_tag_cloud(self):
        """Create tag visualization."""
        if self.tags is None:
            return
            
        try:
            from wordcloud import WordCloud
            
            tag_counts = self.tags['tag'].value_counts()
            
            wordcloud = WordCloud(
                width=1000, height=600,
                background_color='white',
                colormap='viridis',
                max_words=100,
                contour_width=1,
                contour_color='steelblue'
            ).generate_from_frequencies(tag_counts)
            
            plt.figure(figsize=(12, 8))
            plt.imshow(wordcloud, interpolation='bilinear')
            plt.axis("off")
            self.save_plot('tag_cloud.png', 'Product Tags Word Cloud')
            
        except ImportError:
            # Fallback to bar chart if wordcloud not available
            tag_counts = self.tags['tag'].value_counts().reset_index()
            tag_counts.columns = ['tag', 'count']
            
            self.create_bar_chart(
                tag_counts.head(15), 
                'count', 'tag', 
                'top_tags.png', 
                'Top 15 Product Tags',
                palette=sns.color_palette("viridis", 15)
            )
    
    def _is_light_color(self, hex_color):
        """Check if a color is light based on its brightness."""
        hex_color = hex_color.lstrip('#')
        if len(hex_color) < 6:
            return True
        r, g, b = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        return (0.299 * r + 0.587 * g + 0.114 * b) / 255 > 0.5
    
    def create_color_palette(self):
        """Create color palette visualization."""
        if self.colors is None:
            return
            
        top_colors = self.colors['colour_name'].value_counts().head(20).reset_index()
        top_colors.columns = ['colour_name', 'count']
        
        # Extract hex values
        color_mapping = {}
        for color_name in top_colors['colour_name']:
            match = self.colors[self.colors['colour_name'] == color_name].iloc[0]
            hex_value = match.get('hex_value', '#CCCCCC')
            color_mapping[color_name] = hex_value
        
        plt.figure(figsize=(14, 10))
        
        for i, (color_name, count) in enumerate(zip(top_colors['colour_name'], top_colors['count'])):
            hex_value = color_mapping.get(color_name, '#CCCCCC')
            hex_color = hex_value if hex_value.startswith('#') else f"#{hex_value}" if hex_value else "#CCCCCC"
            
            plt.bar(i, count, color=hex_color, edgecolor='black', linewidth=0.5, width=0.8)
            
            text_color = 'black' if self._is_light_color(hex_color) else 'white'
            plt.text(i, count/2, color_name, ha='center', va='center', rotation=90, 
                    fontsize=10, color=text_color)
        
        plt.xlabel('Color', fontsize=12)
        plt.ylabel('Number of Products', fontsize=12)
        plt.xticks([])
        self.save_plot('color_distribution.png', 'Top 20 Product Colors')
    
    def create_brand_price_comparison(self):
        """Compare prices across top brands."""
        if 'brand' not in self.products.columns or 'price' not in self.products.columns:
            return
            
        top_brands = self.products['brand'].value_counts().head(10).index.tolist()
        top_brand_products = self.products[self.products['brand'].isin(top_brands)]
        
        # Box plot
        plt.figure(figsize=(14, 8))
        ax = sns.boxplot(data=top_brand_products, x='brand', y='price', palette=self.brand_palette)
        
        # Set a reasonable y-limit
        q3 = top_brand_products['price'].quantile(0.75)
        ax.set_ylim(0, q3 * 3)
        
        plt.xlabel('Brand', fontsize=12)
        plt.ylabel('Price ($)', fontsize=12)
        plt.xticks(rotation=45)
        self.save_plot('brand_price_comparison.png', 'Price Distribution by Top Brands')
        
        # Average price bar chart
        avg_prices = top_brand_products.groupby('brand')['price'].mean().reset_index()
        avg_prices = avg_prices.sort_values('price', ascending=False)
        
        plt.figure(figsize=(12, 6))
        ax = sns.barplot(data=avg_prices, x='brand', y='price', palette=self.brand_palette)
        
        for i, v in enumerate(avg_prices['price']):
            ax.text(i, v + 0.5, f"${v:.2f}", ha='center')
        
        plt.xlabel('Brand', fontsize=12)
        plt.ylabel('Average Price ($)', fontsize=12)
        plt.xticks(rotation=45)
        self.save_plot('brand_avg_price.png', 'Average Price by Brand')
    
    def create_category_type_heatmap(self):
        """Create a heatmap of product types by category."""
        if 'category' not in self.products.columns or 'product_type' not in self.products.columns:
            return
            
        # Create crosstab and filter sparse rows/columns
        category_type = pd.crosstab(self.products['category'], self.products['product_type'])
        
        threshold = 3
        filtered = category_type.loc[
            category_type.sum(axis=1) >= threshold,
            category_type.sum(axis=0) >= threshold
        ]
        
        if filtered.empty:
            return
        
        plt.figure(figsize=(14, 10))
        sns.heatmap(filtered, annot=True, cmap="YlGnBu", fmt="d", linewidths=0.5)
        
        plt.xlabel('Product Type', fontsize=12)
        plt.ylabel('Category', fontsize=12)
        plt.xticks(rotation=45, ha='right')
        self.save_plot('category_type_heatmap.png', 'Product Types by Category')
    
    def create_combined_visualizations(self):
        """Create additional cross-analysis visualizations."""
        # 1. Color trends by product type
        if self.colors is not None and 'product_type' in self.products.columns:
            # Create merged dataset
            merged = pd.merge(
                self.colors,
                self.products[['id', 'product_type']],
                left_on='product_id', right_on='id', how='inner'
            )
            
            # Get top product types
            top_types = merged['product_type'].value_counts().head(5).index.tolist()
            top_type_data = merged[merged['product_type'].isin(top_types)]
            
            # Create subplot for each product type
            plt.figure(figsize=(15, 12))
            
            for i, prod_type in enumerate(top_types):
                plt.subplot(len(top_types), 1, i+1)
                
                type_data = top_type_data[top_type_data['product_type'] == prod_type]
                top_colors = type_data['colour_name'].value_counts().head(10)
                
                # Map colors to hex values
                color_map = {}
                for color in top_colors.index:
                    hex_val = type_data[type_data['colour_name'] == color]['hex_value'].iloc[0]
                    hex_val = hex_val if hex_val.startswith('#') else f"#{hex_val}"
                    color_map[color] = hex_val
                
                bars = plt.barh(range(len(top_colors)), top_colors.values,
                            color=[color_map.get(c, '#CCC') for c in top_colors.index],
                            edgecolor='black', linewidth=0.5)
                
                for j, (name, count) in enumerate(zip(top_colors.index, top_colors.values)):
                    plt.text(count + 1, j, f"{name} ({count})", va='center', fontsize=10)
                
                plt.title(f'Top Colors for {prod_type.title()}', fontsize=14)
                plt.xlabel('Count', fontsize=10)
                plt.yticks([])
                plt.xlim(0, max(top_colors.values) * 1.2)
            
            plt.tight_layout()
            plt.savefig(f"{self.output_folder}/color_trends_by_type.png", dpi=300)
            plt.close()
            
        # 2. Brand category focus
        if 'brand' in self.products.columns and 'category' in self.products.columns:
            top_brands = self.products['brand'].value_counts().head(5).index.tolist()
            
            fig, axes = plt.subplots(len(top_brands), 1, figsize=(12, 4*len(top_brands)))
            if len(top_brands) == 1:
                axes = [axes]
                
            for i, brand in enumerate(top_brands):
                brand_data = self.products[self.products['brand'] == brand]
                category_counts = brand_data['category'].value_counts().head(8)
                
                sns.barplot(x=category_counts.values, y=category_counts.index,
                           palette=[self.brand_palette[i]]*len(category_counts), ax=axes[i])
                
                for j, v in enumerate(category_counts.values):
                    axes[i].text(v + 0.5, j, str(v), va='center')
                
                axes[i].set_title(f'Top Categories for {brand.title()}', fontsize=14)
                axes[i].set_xlabel('Number of Products', fontsize=10)
                axes[i].set_ylabel('Category', fontsize=10)
            
            plt.tight_layout()
            plt.savefig(f"{self.output_folder}/brand_category_focus.png", dpi=300)
            plt.close()
            
        # 3. Price vs. Rating scatter plot
        if ('price' in self.products.columns and 'rating' in self.products.columns and 
            not self.products['rating'].isna().all()):
            
            plot_data = self.products.dropna(subset=['rating', 'price'])
            
            if len(plot_data) >= 10:
                plt.figure(figsize=(12, 8))
                
                sns.scatterplot(data=plot_data, x='price', y='rating', 
                               hue='brand' if len(plot_data['brand'].unique()) <= 10 else None,
                               alpha=0.7, s=80)
                
                sns.regplot(data=plot_data, x='price', y='rating', scatter=False,
                          color='red', line_kws={'linewidth': 2})
                
                plt.ylim(0, 5.5)
                
                corr = plot_data['price'].corr(plot_data['rating'])
                plt.annotate(f'Correlation: {corr:.2f}', xy=(0.05, 0.95), xycoords='axes fraction',
                            fontsize=12, bbox=dict(boxstyle="round,pad=0.3", facecolor='white'))
                
                plt.xlabel('Price ($)', fontsize=12)
                plt.ylabel('Rating', fontsize=12)
                self.save_plot('price_vs_rating.png', 'Price vs. Rating Relationship')
    
    def run_all_visualizations(self):
        """Generate all available visualizations."""
        print("Starting visualization generation...")
        self.load_data()
        
        # Create basic visualizations
        self.create_brand_distribution()
        self.create_price_distribution()
        self.create_product_type_distribution()
        self.create_tag_cloud()
        self.create_color_palette()
        self.create_brand_price_comparison()
        self.create_category_type_heatmap()
        
        # Create combined visualizations
        self.create_combined_visualizations()
        
        print(f"All visualizations have been saved to {self.output_folder}/")


if __name__ == "__main__":
    visualizer = CosmeticsVisualizer(data_folder='data', output_folder='visualizations')
    visualizer.run_all_visualizations()