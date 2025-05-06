#!/usr/bin/env python3
"""
Main script for Cosmetic Brand Products Analysis Project.
This script orchestrates the entire workflow from data conversion to visualization.
"""

import os
import json
import argparse
import sys
from pathlib import Path

# Add the current directory to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import project modules
try:
    from json_to_csv_converter import convert_json_to_csv
    from cosmetic_analysis import CosmeticsAnalyzer
    from visualize_cosmetics import CosmeticsVisualizer
except ImportError as e:
    print(f"Error importing project modules: {e}")
    print("Make sure all project files are in the same directory or in the Python path.")
    sys.exit(1)

def setup_directories():
    """Create necessary directories for the project."""
    os.makedirs('data', exist_ok=True)
    os.makedirs('reports', exist_ok=True)
    os.makedirs('visualizations', exist_ok=True)
    print("Created project directories: data, reports, visualizations")

def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(description='Cosmetic Brand Products Analysis')
    parser.add_argument('--input', '-i', type=str, default='makeup_data.json',
                        help='Input JSON file path (default: makeup_data.json)')
    parser.add_argument('--data-dir', '-d', type=str, default='data',
                        help='Directory to store processed data (default: data)')
    parser.add_argument('--reports-dir', '-r', type=str, default='reports',
                        help='Directory to store analysis reports (default: reports)')
    parser.add_argument('--vis-dir', '-v', type=str, default='visualizations',
                        help='Directory to store visualizations (default: visualizations)')
    parser.add_argument('--skip-conversion', '-s', action='store_true',
                        help='Skip JSON to CSV conversion step')
    parser.add_argument('--skip-analysis', '-a', action='store_true',
                        help='Skip analysis step')
    parser.add_argument('--skip-visualization', '-z', action='store_true',
                        help='Skip visualization step')
    return parser.parse_args()

def check_file_exists(filepath):
    """Check if a file exists and return True/False."""
    file = Path(filepath)
    return file.is_file()

def main():
    """Main function to run the entire workflow."""
    # Parse arguments
    args = parse_arguments()
    
    # Setup directories
    setup_directories()
    
    # Validate input file
    if not check_file_exists(args.input):
        print(f"Error: Input file '{args.input}' not found.")
        sys.exit(1)
    
    print(f"\n{'='*60}\nCOSMETIC BRAND PRODUCTS ANALYSIS\n{'='*60}")
    
    # Step 1: Convert JSON to CSV
    if not args.skip_conversion:
        print(f"\n{'-'*60}\nStep 1: Converting JSON to CSV\n{'-'*60}")
        convert_json_to_csv(args.input, args.data_dir)
    else:
        print(f"\n{'-'*60}\nStep 1: Skipping JSON to CSV conversion\n{'-'*60}")
    
    # Step 2: Run analysis
    if not args.skip_analysis:
        print(f"\n{'-'*60}\nStep 2: Running Analysis\n{'-'*60}")
        analyzer = CosmeticsAnalyzer(args.input)
        analyzer.run_full_analysis()
    else:
        print(f"\n{'-'*60}\nStep 2: Skipping analysis\n{'-'*60}")
    
    # Step 3: Generate visualizations
    if not args.skip_visualization:
        print(f"\n{'-'*60}\nStep 3: Generating Visualizations\n{'-'*60}")
        visualizer = CosmeticsVisualizer(args.data_dir, args.vis_dir)
        visualizer.run_all_visualizations()
    else:
        print(f"\n{'-'*60}\nStep 3: Skipping visualization generation\n{'-'*60}")
    
    print(f"\n{'='*60}\nAnalysis Complete!\n{'='*60}")
    print(f"\nResults can be found in:")
    print(f"  - Processed data: {args.data_dir}/")
    print(f"  - Analysis reports: {args.reports_dir}/")
    print(f"  - Visualizations: {args.vis_dir}/")

if __name__ == "__main__":
    main()