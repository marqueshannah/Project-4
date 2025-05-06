# Cosmetic Brand Products Analysis

This project analyzes cosmetic product data to extract insights about brands, product types, pricing, and more. The dataset contains detailed information about makeup products including their prices, colors, tags, and categories.

## Project Files

Here are all the files needed for this project:

1. **makeup_data.json** - The main dataset file (input)
2. **main.py** - The orchestration script that runs the entire workflow
3. **cosmetics_analysis.py** - Main analysis script
4. **json_to_csv_converter.py** - Script to convert JSON to CSV files
5. **visualize_cosmetics.py** - Script to create visualizations
6. **recommend_products.py** - Product recommendation system based on user preferences

### Output Files and Folders
When the scripts are run, they will create:

1. **data/** - Folder containing processed CSV files:
   - products_main.csv
   - product_descriptions.csv
   - product_tags.csv
   - product_urls.csv
   - product_colors.csv

2. **reports/** - Folder containing analysis reports:
   - analysis_stats.json
   - top_brands.csv
   - product_types.csv
   - price_distribution.csv
   - tag_distribution.csv
   - color_distribution.csv
   - brand_price_report.csv
   - processed_cosmetics.csv

3. **visualizations/** - Folder containing charts and graphs:
   - brand_distribution.png
   - price_distribution.png
   - price_range_distribution.png
   - product_type_distribution.png
   - product_type_bar.png
   - tag_cloud.png (or top_tags.png)
   - color_distribution.png
   - brand_price_comparison.png
   - brand_avg_price.png
   - category_type_heatmap.png
   - color_trends_by_type.png
   - brand_category_focus.png
   - price_vs_rating.png (if rating data is available)

4. **recommendations/** - Folder containing product recommendation results:
   - recommendations_[timestamp].csv

## Installation

To run this project, you'll need Python 3.6+ and the following packages:

```bash
pip install pandas matplotlib seaborn numpy wordcloud
```

Note: The `wordcloud` package is optional. If not installed, the script will fall back to a bar chart representation of tags.

## Dataset

This project uses the Cosmetic Brand Products Dataset available from the following sources:

- **Kaggle**: [Cosmetic Brand Products Dataset](https://www.kaggle.com/datasets/shivd24coder/cosmetic-brand-products-dataset)
- **Original API**: [Makeup API](http://makeup-api.herokuapp.com/)

The dataset contains 931 cosmetic products with information about brands, prices, colors, and more. The data is sourced from the Makeup API and includes products from various brands like Colourpop, Maybelline, NYX, and others.

To use this project:
1. Download the dataset from one of the links above
2. Rename it to `makeup_data.json` and place it in the project directory
3. Run the scripts as described below

## Usage

### All-in-One Execution

The easiest way to run the complete analysis is with the main script:

```bash
python main.py
```

This will execute all steps: JSON to CSV conversion, analysis, and visualization generation.

### Command Line Options

The main script accepts several options:

```bash
python main.py --input your_file.json    # Specify a different input file
python main.py --skip-conversion         # Skip JSON to CSV conversion
python main.py --skip-analysis           # Skip analysis step
python main.py --skip-visualization      # Skip visualization step
```

### Running Individual Scripts

You can run each component of the project separately:

#### 1. Convert JSON to CSV

```bash
python json_to_csv_converter.py makeup_data.json data
```

#### 2. Run the Analysis

```bash
python cosmetics_analysis.py
```

#### 3. Create Visualizations

```bash
python visualize_cosmetics.py
```

#### 4. Get Product Recommendations

```bash
python recommend_products.py
```

### Using the Recommendation System

The recommendation system helps you find products based on your preferences. To use it:

1. Make sure you've already run the data conversion step (using `main.py` or `json_to_csv_converter.py`)
2. Run the recommendation script:
   ```bash
   python recommend_products.py
   ```
3. The interactive prompt will guide you through selecting preferences:
   - When asked "Would you like to see available options?", enter "y" to see what you can filter by
   - Enter your preferences for brand, product type, category, etc.
   - Leave any field blank (just press Enter) to skip that filter
   - For tags and colors, enter multiple values separated by commas (e.g., "vegan, cruelty free")
   - Specify a minimum rating on a scale of 1-5
   - Choose how many recommendations you want to see
4. The script will display matching products with details like price, rating, tags, and colors
5. You can save the recommendations to a CSV file for later reference

#### Command-line options for the recommendation script:

```bash
python recommend_products.py --data custom_data_folder
python recommend_products.py --output custom_recommendations_folder
```

## Key Features

- Brand analysis: Identifies top brands by product count and price points
- Price analysis: Examines price distribution and compares pricing across brands
- Product type analysis: Shows the distribution of product types and categories
- Color analysis: Visualizes the most common colors in the product lineup
- Tag analysis: Displays common tags and attributes of products
- Cross-analysis: Examines relationships between different attributes (e.g., color trends by product type)
- Recommendations: Provides personalized product suggestions based on user preferences

## Example Insights

The analysis can help answer questions such as:

- Which brands have the most products in the dataset?
- What is the average price of products by brand?
- What are the most common product types?
- Which price ranges are most common across cosmetic products?
- What colors are most frequently offered in cosmetic products?
- How do product types distribute across different categories?
- Which product types offer the most color variety?
- Is there a correlation between price and rating?
- What products match my specific preferences?

## Data Structure

The input JSON file has the following structure:

```json
[
    {
        "id": 1048,
        "brand": "colourpop",
        "name": "Lippie Pencil",
        "price": "5.0",
        "price_sign": "$",
        "currency": "CAD",
        "image_link": "...",
        "product_link": "...",
        "website_link": "...",
        "description": "...",
        "rating": null,
        "category": "pencil",
        "product_type": "lip_liner",
        "tag_list": [
            "cruelty free",
            "Vegan"
        ],
        "created_at": "2018-07-08T23:45:08.056Z",
        "updated_at": "2018-07-09T00:53:23.301Z",
        "product_api_url": "...",
        "api_featured_image": "...",
        "product_colors": [
            {
                "hex_value": "#B28378",
                "colour_name": "BFF Pencil"
            },
            ...
        ]
    },
    ...
]
```

## Workflow Steps

Here's the typical workflow for using this project:

1. **Data Preparation**: Place your JSON file in the project directory
2. **Data Processing**: Convert JSON to CSV format
3. **Analysis**: Generate statistics and insights about the dataset
4. **Visualization**: Create charts and graphs to visualize the findings
5. **Recommendations**: Get personalized product suggestions based on preferences

## Troubleshooting

- **Missing files**: If you get "file not found" errors, ensure that all script files are in the same directory and that you've run the data conversion step first
- **Empty results in recommendations**: Try relaxing your filter criteria - you might be applying too many constraints
- **Error in color analysis**: The script handles null values in color data, but if you encounter issues, try using the `--skip-analysis` option in main.py
- **Visualization errors**: If you don't have the wordcloud package installed, the script will automatically use bar charts instead
- **Data format issues**: Ensure your JSON data follows the structure shown above

## Extending the Project

You can extend this project by:

1. Adding sentiment analysis on product descriptions
2. Creating a machine learning model to predict product ratings
3. Implementing time series analysis for product trends (using created_at dates)
4. Developing an interactive web dashboard for the data
5. Conducting competitive analysis between similar brands
6. Enhancing the recommendation system with collaborative filtering (based on user preferences)

## References

- [Makeup API](http://makeup-api.herokuapp.com/) - The original source of the cosmetics data
- [Kaggle Dataset](https://www.kaggle.com/datasets/shivd24coder/cosmetic-brand-products-dataset) - The Cosmetic Brand Products Dataset hosted on Kaggle
- [Gigasheet Sample](https://www.gigasheet.com/sample-data/cosmetic-brand-products-dataset) - Another source for exploring the same dataset