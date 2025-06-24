#!/usr/bin/env python3
"""
Test script for reconciliation settings functionality.
This script tests the settings module and its integration with the main application.
"""

import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys

# Add the current directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Mock streamlit for testing
class MockStreamlit:
    def __init__(self):
        self.session_state = {}
    
    def markdown(self, text):
        pass
    
    def number_input(self, label, **kwargs):
        return kwargs.get('value', 0)
    
    def selectbox(self, label, options, **kwargs):
        return options[kwargs.get('index', 0)]
    
    def slider(self, label, **kwargs):
        return kwargs.get('value', 0)
    
    def checkbox(self, label, **kwargs):
        return kwargs.get('value', False)
    
    def button(self, label, **kwargs):
        return False
    
    def success(self, text):
        print(f"SUCCESS: {text}")
    
    def error(self, text):
        print(f"ERROR: {text}")
    
    def info(self, text):
        print(f"INFO: {text}")
    
    def columns(self, n):
        return [MockStreamlit() for _ in range(n)]
    
    def tabs(self, names):
        return [MockStreamlit() for _ in names]
    
    def expander(self, label):
        return MockStreamlit()
    
    def dataframe(self, data, **kwargs):
        pass
    
    def download_button(self, **kwargs):
        pass
    
    def file_uploader(self, **kwargs):
        return None

# Mock streamlit module
sys.modules['streamlit'] = MockStreamlit()

from utils.settings import ReconciliationSettings, apply_settings_to_reconciliation
from utils.helpers import calculate_total_tax_difference, get_tax_diff_status, get_date_status, get_tax_diff_status_with_status, get_date_status_with_status

def get_current_settings():
    """Mock function to get current settings without Streamlit dependency."""
    settings_manager = ReconciliationSettings()
    return settings_manager.settings

def create_test_data():
    """Create test data for reconciliation testing."""
    np.random.seed(42)  # For reproducible results
    
    # Create sample reconciliation data
    data = []
    for i in range(20):
        # Generate random tax differences
        igst_diff = np.random.uniform(-50, 50)
        cgst_diff = np.random.uniform(-30, 30)
        sgst_diff = np.random.uniform(-20, 20)
        
        # Generate random date differences
        date_diff = np.random.randint(-5, 6)
        
        # Assign different statuses
        if i < 5:
            status = 'Partial Match'
        elif i < 10:
            status = 'Exact Match'
        elif i < 15:
            status = 'Books Only'
        else:
            status = 'GSTR-2A Only'
        
        data.append({
            'IGST Diff': igst_diff,
            'CGST Diff': cgst_diff,
            'SGST Diff': sgst_diff,
            'Date Diff': date_diff,
            'Status': status,
            'Narrative': f'Test narrative for row {i+1}'
        })
    
    return pd.DataFrame(data)

def test_settings_creation():
    """Test settings creation and validation."""
    print("Testing settings creation...")
    
    # Create settings instance
    settings = ReconciliationSettings()
    
    # Test default settings
    assert settings.settings['tax_amount_tolerance'] == 10.0
    assert settings.settings['date_tolerance_days'] == 1
    assert settings.settings['name_preference'] == "Legal Name"
    
    print("✅ Settings creation test passed")

def test_settings_validation():
    """Test settings validation."""
    print("Testing settings validation...")
    
    settings = ReconciliationSettings()
    
    # Test valid settings
    valid_settings = {
        'tax_amount_tolerance': 15.0,
        'date_tolerance_days': 2,
        'name_preference': 'Trade Name',
        'currency_format': 'INR',
        'decimal_precision': 2,
        'case_sensitive_names': False,
        'similarity_threshold': 85.0,
        'group_tax_tolerance': 75.0,
        'enable_advanced_matching': True,
        'auto_apply_settings': True
    }
    
    is_valid, error = settings.validate_settings(valid_settings)
    assert is_valid, f"Valid settings failed validation: {error}"
    
    # Test invalid settings
    invalid_settings = {
        'tax_amount_tolerance': -5.0,  # Negative value
        'date_tolerance_days': 1,
        'name_preference': 'Legal Name'
    }
    
    is_valid, error = settings.validate_settings(invalid_settings)
    assert not is_valid, "Invalid settings should have failed validation"
    assert "non-negative" in error.lower()
    
    print("✅ Settings validation test passed")

def test_tax_diff_status():
    """Test tax difference status calculation."""
    print("Testing tax difference status...")
    
    settings = ReconciliationSettings()
    
    # Test with default tolerance (10.0)
    assert settings.apply_tax_diff_status(5.0) == "No Difference"
    assert settings.apply_tax_diff_status(15.0) == "Has Difference"
    assert settings.apply_tax_diff_status(-8.0) == "No Difference"
    assert settings.apply_tax_diff_status(-12.0) == "Has Difference"
    
    # Test with custom tolerance
    settings.settings['tax_amount_tolerance'] = 20.0
    assert settings.apply_tax_diff_status(15.0) == "No Difference"
    assert settings.apply_tax_diff_status(25.0) == "Has Difference"
    
    print("✅ Tax difference status test passed")

def test_date_status():
    """Test date status calculation."""
    print("Testing date status...")
    
    settings = ReconciliationSettings()
    
    # Test with default tolerance (1 day)
    assert settings.apply_date_status(0) == "Within Tolerance"
    assert settings.apply_date_status(1) == "Within Tolerance"
    assert settings.apply_date_status(2) == "Outside Tolerance"
    assert settings.apply_date_status(-1) == "Within Tolerance"
    assert settings.apply_date_status(-2) == "Outside Tolerance"
    
    # Test with custom tolerance
    settings.settings['date_tolerance_days'] = 3
    assert settings.apply_date_status(2) == "Within Tolerance"
    assert settings.apply_date_status(4) == "Outside Tolerance"
    
    print("✅ Date status test passed")

def test_name_preference():
    """Test name preference functionality."""
    print("Testing name preference...")
    
    settings = ReconciliationSettings()
    
    # Test with Legal Name preference (default)
    assert settings.get_name_for_comparison("Trade Name", "Legal Name") == "Legal Name"
    assert settings.get_name_for_comparison("", "Legal Name") == "Legal Name"
    assert settings.get_name_for_comparison("Trade Name", "") == "Trade Name"
    
    # Test with Trade Name preference
    settings.settings['name_preference'] = "Trade Name"
    assert settings.get_name_for_comparison("Trade Name", "Legal Name") == "Trade Name"
    assert settings.get_name_for_comparison("", "Legal Name") == "Legal Name"
    assert settings.get_name_for_comparison("Trade Name", "") == "Trade Name"
    
    print("✅ Name preference test passed")

def test_currency_formatting():
    """Test currency formatting."""
    print("Testing currency formatting...")
    
    settings = ReconciliationSettings()
    
    # Test INR formatting
    assert settings.format_currency(1234.56) == "₹1,234.56"
    assert settings.format_currency(0.00) == "₹0.00"
    
    # Test USD formatting
    settings.settings['currency_format'] = 'USD'
    assert settings.format_currency(1234.56) == "$1,234.56"
    
    # Test precision
    settings.settings['decimal_precision'] = 0
    assert settings.format_currency(1234.56) == "$1,235"
    
    print("✅ Currency formatting test passed")

def test_settings_application():
    """Test applying settings to reconciliation data."""
    print("Testing settings application...")
    
    # Create test data
    test_df = create_test_data()
    
    # Test with default settings
    settings = get_current_settings()
    result_df = apply_settings_to_reconciliation(test_df, settings)
    
    # Verify columns were added
    assert 'Total Tax Diff' in result_df.columns
    assert 'Tax Diff Status' in result_df.columns
    assert 'Date Status' in result_df.columns
    
    # Verify calculations
    for idx, row in result_df.iterrows():
        # Check total tax difference calculation (signed sum, not abs sum)
        expected_total = row['IGST Diff'] + row['CGST Diff'] + row['SGST Diff']
        assert abs(row['Total Tax Diff'] - expected_total) < 0.01
        
        # Check tax diff status
        if row['Status'] in ['Books Only', 'GSTR-2A Only']:
            assert row['Tax Diff Status'] == "N/A", f"Expected N/A for {row['Status']}, got {row['Tax Diff Status']}"
        else:
            expected_tax_status = get_tax_diff_status(row['Total Tax Diff'], settings['tax_amount_tolerance'])
            assert row['Tax Diff Status'] == expected_tax_status
        
        # Check date status
        if row['Status'] in ['Books Only', 'GSTR-2A Only']:
            assert row['Date Status'] == "N/A", f"Expected N/A for {row['Status']}, got {row['Date Status']}"
        else:
            expected_date_status = get_date_status(row['Date Diff'], settings['date_tolerance_days'])
            assert row['Date Status'] == expected_date_status
    
    print("✅ Settings application test passed")

def test_settings_persistence():
    """Test settings save and load functionality."""
    print("Testing settings persistence...")
    
    settings = ReconciliationSettings()
    test_file = "test_settings.json"
    
    # Temporarily change settings file for testing
    original_file = settings.settings_file
    settings.settings_file = test_file
    
    try:
        # Test saving settings
        test_settings = {
            'tax_amount_tolerance': 25.0,
            'date_tolerance_days': 3,
            'name_preference': 'Trade Name',
            'currency_format': 'USD',
            'decimal_precision': 3,
            'case_sensitive_names': True,
            'similarity_threshold': 90.0,
            'group_tax_tolerance': 100.0,
            'enable_advanced_matching': False,
            'auto_apply_settings': False
        }
        
        success = settings.save_settings(test_settings)
        assert success, "Settings save failed"
        
        # Test loading settings
        loaded_settings = settings.load_settings()
        for key, value in test_settings.items():
            assert loaded_settings[key] == value, f"Setting {key} not loaded correctly"
        
        print("✅ Settings persistence test passed")
        
    finally:
        # Clean up
        settings.settings_file = original_file
        if os.path.exists(test_file):
            os.remove(test_file)

def test_helper_functions():
    """Test helper functions."""
    print("Testing helper functions...")
    
    # Test calculate_total_tax_difference
    total_diff = calculate_total_tax_difference(100, 50, 25, 95, 45, 20)
    expected = abs(100-95) + abs(50-45) + abs(25-20)
    assert abs(total_diff - expected) < 0.01
    
    # Test get_tax_diff_status
    assert get_tax_diff_status(5.0, 10.0) == "No Difference"
    assert get_tax_diff_status(15.0, 10.0) == "Has Difference"
    
    # Test get_tax_diff_status_with_status
    assert get_tax_diff_status_with_status(5.0, "Partial Match", 10.0) == "No Difference"
    assert get_tax_diff_status_with_status(15.0, "Exact Match", 10.0) == "Has Difference"
    assert get_tax_diff_status_with_status(5.0, "Books Only", 10.0) == "N/A"
    assert get_tax_diff_status_with_status(15.0, "GSTR-2A Only", 10.0) == "N/A"
    
    # Test get_date_status
    assert get_date_status(0, 1) == "Within Tolerance"
    assert get_date_status(2, 1) == "Outside Tolerance"
    
    # Test get_date_status_with_status
    assert get_date_status_with_status(0, "Partial Match", 1) == "Within Tolerance"
    assert get_date_status_with_status(2, "Exact Match", 1) == "Outside Tolerance"
    assert get_date_status_with_status(0, "Books Only", 1) == "N/A"
    assert get_date_status_with_status(2, "GSTR-2A Only", 1) == "N/A"
    
    print("✅ Helper functions test passed")

def run_all_tests():
    """Run all tests."""
    print("🧪 Running reconciliation settings tests...\n")
    
    try:
        test_settings_creation()
        test_settings_validation()
        test_tax_diff_status()
        test_date_status()
        test_name_preference()
        test_currency_formatting()
        test_settings_application()
        test_settings_persistence()
        test_helper_functions()
        
        print("\n🎉 All tests passed successfully!")
        return True
        
    except Exception as e:
        print(f"\n❌ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)
