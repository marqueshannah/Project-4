import json
import pandas as pd
import sys
import os

def convert_json_to_csv(json_file, output_folder='data'):
    """
    Convert the cosmetics JSON file to CSV format and split into separate files
    for easier processing.
    
    Args:
        json_file (str): Path to the JSON file
        output_folder (str): Folder to save the CSV files
    """
    try:
        # Create output directory if it doesn't exist
        os.makedirs(output_folder, exist_ok=True)
        
        # Read the JSON file
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        print(f"Successfully loaded {len(data)} products")
        
        # Convert to DataFrame
        df = pd.json_normalize(data)
        
        # Save the main product data
        main_columns = [
            'id', 'brand', 'name', 'price', 'price_sign', 'currency', 
            'category', 'product_type', 'rating', 'created_at', 'updated_at'
        ]
        
        # Extract columns that exist in the data
        available_main_columns = [col for col in main_columns if col in df.columns]
        
        # Save main product data
        main_df = df[available_main_columns]
        main_df.to_csv(f"{output_folder}/products_main.csv", index=False)
        print(f"Saved main product data to {output_folder}/products_main.csv")
        
        # Save description data
        if 'description' in df.columns:
            descriptions = df[['id', 'name', 'description']]
            descriptions.to_csv(f"{output_folder}/product_descriptions.csv", index=False)
            print(f"Saved product descriptions to {output_folder}/product_descriptions.csv")
        
        # Save tag data
        if 'tag_list' in df.columns:
            # Explode tag list into separate rows
            tags_df = df[['id', 'name', 'tag_list']].explode('tag_list')
            tags_df = tags_df.rename(columns={'tag_list': 'tag'})
            tags_df = tags_df[tags_df['tag'].notna()]  # Remove missing tags
            tags_df.to_csv(f"{output_folder}/product_tags.csv", index=False)
            print(f"Saved product tags to {output_folder}/product_tags.csv")
        
        # Save URL and links data
        url_columns = [
            'id', 'name', 'image_link', 'product_link', 'website_link', 
            'product_api_url', 'api_featured_image'
        ]
        available_url_columns = [col for col in url_columns if col in df.columns]
        
        if available_url_columns:
            urls_df = df[available_url_columns]
            urls_df.to_csv(f"{output_folder}/product_urls.csv", index=False)
            print(f"Saved product URLs to {output_folder}/product_urls.csv")
        
        # Handle product colors (more complex)
        if 'product_colors' in df.columns:
            # Create a list to store all colors
            all_colors = []
            
            # Process each product's colors
            for index, row in df.iterrows():
                product_id = row['id']
                product_name = row['name']
                
                # Check if product_colors is a list and not empty
                if isinstance(row['product_colors'], list):
                    for color in row['product_colors']:
                        if isinstance(color, dict):
                            color_data = {
                                'product_id': product_id,
                                'product_name': product_name,
                                'colour_name': color.get('colour_name', ''),
                                'hex_value': color.get('hex_value', '')
                            }
                            all_colors.append(color_data)
            
            # Convert to DataFrame and save
            if all_colors:
                colors_df = pd.DataFrame(all_colors)
                colors_df.to_csv(f"{output_folder}/product_colors.csv", index=False)
                print(f"Saved product colors to {output_folder}/product_colors.csv")
        
        print(f"Successfully converted JSON to CSV files in the '{output_folder}' directory")
        return True
    
    except Exception as e:
        print(f"Error converting JSON to CSV: {e}")
        return False

if __name__ == "__main__":
    # Get file path from command line argument or use default
    json_file = 'makeup_data.json'
    output_folder = 'data'
    
    if len(sys.argv) > 1:
        json_file = sys.argv[1]
    
    if len(sys.argv) > 2:
        output_folder = sys.argv[2]
    
    convert_json_to_csv(json_file, output_folder)