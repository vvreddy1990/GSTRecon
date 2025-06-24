#!/usr/bin/env python3
"""
Test script for Indian currency formatting function
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from utils.helpers import format_indian_currency

def test_indian_currency_formatting():
    """Test the Indian currency formatting function"""
    
    test_cases = [
        (0, "₹0"),
        (100, "₹100.00"),
        (1000, "₹1,000.00"),
        (10000, "₹10,000.00"),
        (100000, "₹1 lakh"),
        (150000, "₹1.50 lakh"),
        (1000000, "₹10 lakh"),
        (10000000, "₹1 crore"),
        (15000000, "₹1.50 crore"),
        (100000000, "₹10 crore"),
        (-1000, "-₹1,000.00"),
        (-100000, "-₹1 lakh"),
        (-10000000, "-₹1 crore"),
        (None, "₹0"),
        (float('nan'), "₹0"),
    ]
    
    print("Testing Indian Currency Formatting:")
    print("=" * 50)
    
    for amount, expected in test_cases:
        try:
            result = format_indian_currency(amount)
            status = "✅ PASS" if result == expected else "❌ FAIL"
            print(f"{status} | {amount} -> {result} (expected: {expected})")
        except Exception as e:
            print(f"❌ ERROR | {amount} -> Exception: {e}")
    
    print("\n" + "=" * 50)
    print("Test completed!")

if __name__ == "__main__":
    test_indian_currency_formatting() 