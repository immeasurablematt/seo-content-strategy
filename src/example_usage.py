#!/usr/bin/env python3
"""
Example usage of the SEO Content Brief Generator
"""

from src.simple_seo_brief import run_with_parameters, main

# Example 1: Run with specific parameters
def generate_gaming_laptop_brief():
    """Generate a brief for gaming laptops"""
    run_with_parameters(
        primary_keyword="best gaming laptops 2024",
        target_audience="gaming enthusiasts and tech buyers",
        content_goal="product review and comparison",
        your_domain="mystore.com"
    )

# Example 2: Run with auto-detection
def generate_auto_brief():
    """Generate a brief with auto-detected audience and goal"""
    run_with_parameters(
        primary_keyword="content marketing strategy",
        your_domain="myblog.com"
        # target_audience and content_goal will be auto-detected
    )

# Example 3: Use the main function directly
def generate_direct_brief():
    """Use the main function directly"""
    main(
        primary_keyword="email marketing best practices",
        target_audience="small business owners",
        content_goal="educational guide",
        your_domain="mycompany.com"
    )

if __name__ == "__main__":
    print("Choose an example to run:")
    print("1. Gaming laptop brief with specific parameters")
    print("2. Auto-detected brief")
    print("3. Direct main function usage")
    
    choice = input("Enter choice (1-3): ")
    
    if choice == "1":
        generate_gaming_laptop_brief()
    elif choice == "2":
        generate_auto_brief()
    elif choice == "3":
        generate_direct_brief()
    else:
        print("Invalid choice")


