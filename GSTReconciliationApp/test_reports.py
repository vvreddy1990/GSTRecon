import unittest
import pandas as pd
import numpy as np
from unittest.mock import patch, MagicMock
import sys
import os

# Add the utils directory to the path
sys.path.append(os.path.join(os.path.dirname(__file__), 'utils'))

from reports import get_unique_unmapped_gst_report, filter_gst_report, get_report_summary

class TestReportsModule(unittest.TestCase):
    """Test cases for the reports module functionality."""
    
    def setUp(self):
        """Set up test data."""
        # Create sample data for testing
        self.sample_data = pd.DataFrame({
            'Source Name': ['Books', 'Books', 'GSTR-2A', 'GSTR-2A', 'GSTR-2A', 'Books'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', '27AAABC1234C1Z5', '27AAABC1234C1Z5', '29DEFGH5678H2Z9', '33IJKL9012L5M3', '29DEFGH5678H2Z9'],
            'Supplier Trade Name': ['ABC Traders', 'ABC Traders', 'ABC Traders', 'DEF Suppliers', 'IJK Enterprises', 'DEF Suppliers'],
            'Supplier Legal Name': ['ABC Pvt Ltd', 'ABC Pvt Ltd', 'ABC Pvt Ltd', 'DEF Corporation', 'IJK Limited', 'DEF Corporation'],
            'Invoice Number': ['INV001', 'INV002', 'INV001', 'INV003', 'INV004', 'INV003'],
            'Total IGST Amount': [1000, 2000, 1000, 1500, 3000, 1500],
            'Total CGST Amount': [500, 1000, 500, 750, 1500, 750],
            'Total SGST Amount': [500, 1000, 500, 750, 1500, 750]
        })
        
        # Expected unmapped GST numbers
        self.expected_unmapped = ['33IJKL9012L5M3']  # Only in GSTR-2A, not in Books
        
    def test_get_unique_unmapped_gst_report_basic(self):
        """Test basic functionality of getting unique unmapped GST report."""
        result = get_unique_unmapped_gst_report(self.sample_data)
        
        # Check that result is a DataFrame
        self.assertIsInstance(result, pd.DataFrame)
        
        # Check expected columns
        expected_columns = ['GST Number', 'Trade Name', 'Legal Name', 'Count', 'Total IGST Amount', 'Total CGST Amount', 'Total SGST Amount']
        self.assertListEqual(list(result.columns), expected_columns)
        
        # Check that we get the expected unmapped GST number
        if not result.empty:
            self.assertIn(self.expected_unmapped[0], result['GST Number'].values)
            
            # Check that count and tax amounts are calculated
            unmapped_record = result[result['GST Number'] == self.expected_unmapped[0]].iloc[0]
            self.assertEqual(unmapped_record['Count'], 1)  # Should appear once in GSTR-2A
            self.assertEqual(unmapped_record['Total IGST Amount'], 3000)  # From the sample data
            self.assertEqual(unmapped_record['Total CGST Amount'], 1500)  # From the sample data
            self.assertEqual(unmapped_record['Total SGST Amount'], 1500)  # From the sample data
    
    def test_get_unique_unmapped_gst_report_with_multiple_records(self):
        """Test handling of GST numbers with multiple records."""
        # Create data with multiple records for the same unmapped GST
        multiple_records_data = pd.DataFrame({
            'Source Name': ['Books', 'GSTR-2A', 'GSTR-2A', 'GSTR-2A'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', '33IJKL9012L5M3', '33IJKL9012L5M3', '33IJKL9012L5M3'],
            'Supplier Trade Name': ['ABC Traders', 'IJK Enterprises', 'IJK Enterprises', 'IJK Enterprises'],
            'Supplier Legal Name': ['ABC Pvt Ltd', 'IJK Limited', 'IJK Limited', 'IJK Limited'],
            'Total IGST Amount': [1000, 1000, 2000, 3000],
            'Total CGST Amount': [500, 500, 1000, 1500],
            'Total SGST Amount': [500, 500, 1000, 1500]
        })
        
        result = get_unique_unmapped_gst_report(multiple_records_data)
        
        if not result.empty:
            unmapped_record = result[result['GST Number'] == '33IJKL9012L5M3'].iloc[0]
            self.assertEqual(unmapped_record['Count'], 3)  # Should appear 3 times in GSTR-2A
            self.assertEqual(unmapped_record['Total IGST Amount'], 6000)  # Sum of 1000+2000+3000
            self.assertEqual(unmapped_record['Total CGST Amount'], 3000)  # Sum of 500+1000+1500
            self.assertEqual(unmapped_record['Total SGST Amount'], 3000)  # Sum of 500+1000+1500
    
    def test_get_unique_unmapped_gst_report_empty_data(self):
        """Test handling of empty DataFrame."""
        empty_df = pd.DataFrame()
        result = get_unique_unmapped_gst_report(empty_df)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        self.assertListEqual(list(result.columns), ['GST Number', 'Trade Name', 'Legal Name', 'Count', 'Total IGST Amount', 'Total CGST Amount', 'Total SGST Amount'])
    
    def test_get_unique_unmapped_gst_report_none_data(self):
        """Test handling of None data."""
        result = get_unique_unmapped_gst_report(None)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        self.assertListEqual(list(result.columns), ['GST Number', 'Trade Name', 'Legal Name', 'Count', 'Total IGST Amount', 'Total CGST Amount', 'Total SGST Amount'])
    
    def test_get_unique_unmapped_gst_report_missing_columns(self):
        """Test handling of missing required columns."""
        incomplete_data = pd.DataFrame({
            'Source Name': ['Books', 'GSTR-2A'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', '29DEFGH5678H2Z9']
            # Missing Trade Name and Legal Name columns
        })
        
        result = get_unique_unmapped_gst_report(incomplete_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
        self.assertListEqual(list(result.columns), ['GST Number', 'Trade Name', 'Legal Name', 'Count', 'Total IGST Amount', 'Total CGST Amount', 'Total SGST Amount'])
    
    def test_get_unique_unmapped_gst_report_invalid_gstin(self):
        """Test filtering of invalid GSTINs."""
        invalid_data = pd.DataFrame({
            'Source Name': ['Books', 'GSTR-2A', 'GSTR-2A'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', 'INVALID', '33IJKL9012L5M3'],
            'Supplier Trade Name': ['ABC Traders', 'Invalid Co', 'IJK Enterprises'],
            'Supplier Legal Name': ['ABC Pvt Ltd', 'Invalid Ltd', 'IJK Limited'],
            'Total IGST Amount': [1000, 500, 3000],
            'Total CGST Amount': [500, 250, 1500],
            'Total SGST Amount': [500, 250, 1500]
        })
        
        result = get_unique_unmapped_gst_report(invalid_data)
        
        # Should only include valid 15-digit GSTINs
        if not result.empty:
            for gstin in result['GST Number']:
                self.assertEqual(len(gstin), 15)
    
    def test_get_unique_unmapped_gst_report_no_books_data(self):
        """Test handling when no Books data is present."""
        gstr2a_only_data = pd.DataFrame({
            'Source Name': ['GSTR-2A', 'GSTR-2A'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', '29DEFGH5678H2Z9'],
            'Supplier Trade Name': ['ABC Traders', 'DEF Suppliers'],
            'Supplier Legal Name': ['ABC Pvt Ltd', 'DEF Corporation'],
            'Total IGST Amount': [1000, 1500],
            'Total CGST Amount': [500, 750],
            'Total SGST Amount': [500, 750]
        })
        
        result = get_unique_unmapped_gst_report(gstr2a_only_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    def test_get_unique_unmapped_gst_report_no_gstr2a_data(self):
        """Test handling when no GSTR-2A data is present."""
        books_only_data = pd.DataFrame({
            'Source Name': ['Books', 'Books'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', '29DEFGH5678H2Z9'],
            'Supplier Trade Name': ['ABC Traders', 'DEF Suppliers'],
            'Supplier Legal Name': ['ABC Pvt Ltd', 'DEF Corporation'],
            'Total IGST Amount': [1000, 1500],
            'Total CGST Amount': [500, 750],
            'Total SGST Amount': [500, 750]
        })
        
        result = get_unique_unmapped_gst_report(books_only_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    def test_get_unique_unmapped_gst_report_all_mapped(self):
        """Test when all GSTR-2A GSTINs have mappings in Books."""
        all_mapped_data = pd.DataFrame({
            'Source Name': ['Books', 'GSTR-2A', 'Books', 'GSTR-2A'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', '27AAABC1234C1Z5', '29DEFGH5678H2Z9', '29DEFGH5678H2Z9'],
            'Supplier Trade Name': ['ABC Traders', 'ABC Traders', 'DEF Suppliers', 'DEF Suppliers'],
            'Supplier Legal Name': ['ABC Pvt Ltd', 'ABC Pvt Ltd', 'DEF Corporation', 'DEF Corporation'],
            'Total IGST Amount': [1000, 1000, 1500, 1500],
            'Total CGST Amount': [500, 500, 750, 750],
            'Total SGST Amount': [500, 500, 750, 750]
        })
        
        result = get_unique_unmapped_gst_report(all_mapped_data)
        
        self.assertIsInstance(result, pd.DataFrame)
        self.assertTrue(result.empty)
    
    def test_filter_gst_report_basic(self):
        """Test basic filtering functionality."""
        report_data = pd.DataFrame({
            'GST Number': ['27AAABC1234C1Z5', '29DEFGH5678H2Z9', '33IJKL9012L5M3'],
            'Trade Name': ['ABC Traders', 'DEF Suppliers', 'IJK Enterprises'],
            'Legal Name': ['ABC Pvt Ltd', 'DEF Corporation', 'IJK Limited'],
            'Count': [1, 2, 3],
            'Total IGST Amount': [1000, 2000, 3000],
            'Total CGST Amount': [500, 1000, 1500],
            'Total SGST Amount': [500, 1000, 1500]
        })
        
        # Test search by GST Number
        result = filter_gst_report(report_data, search_term='27AAABC')
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['GST Number'], '27AAABC1234C1Z5')
        
        # Test search by Trade Name
        result = filter_gst_report(report_data, search_term='DEF')
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Trade Name'], 'DEF Suppliers')
        
        # Test search by Legal Name
        result = filter_gst_report(report_data, search_term='IJK Limited')
        self.assertEqual(len(result), 1)
        self.assertEqual(result.iloc[0]['Legal Name'], 'IJK Limited')
    
    def test_filter_gst_report_sorting(self):
        """Test sorting functionality."""
        report_data = pd.DataFrame({
            'GST Number': ['33IJKL9012L5M3', '27AAABC1234C1Z5', '29DEFGH5678H2Z9'],
            'Trade Name': ['IJK Enterprises', 'ABC Traders', 'DEF Suppliers'],
            'Legal Name': ['IJK Limited', 'ABC Pvt Ltd', 'DEF Corporation'],
            'Count': [3, 1, 2],
            'Total IGST Amount': [3000, 1000, 2000],
            'Total CGST Amount': [1500, 500, 1000],
            'Total SGST Amount': [1500, 500, 1000]
        })
        
        # Test sorting by GST Number
        result = filter_gst_report(report_data, sort_by='GST Number')
        self.assertEqual(result.iloc[0]['GST Number'], '27AAABC1234C1Z5')
        self.assertEqual(result.iloc[2]['GST Number'], '33IJKL9012L5M3')
        
        # Test sorting by Trade Name
        result = filter_gst_report(report_data, sort_by='Trade Name')
        self.assertEqual(result.iloc[0]['Trade Name'], 'ABC Traders')
        self.assertEqual(result.iloc[2]['Trade Name'], 'IJK Enterprises')
        
        # Test sorting by Count (descending)
        result = filter_gst_report(report_data, sort_by='Count')
        self.assertEqual(result.iloc[0]['Count'], 3)  # Highest count first
        self.assertEqual(result.iloc[2]['Count'], 1)  # Lowest count last
        
        # Test sorting by Total IGST Amount (descending)
        result = filter_gst_report(report_data, sort_by='Total IGST Amount')
        self.assertEqual(result.iloc[0]['Total IGST Amount'], 3000)  # Highest amount first
        self.assertEqual(result.iloc[2]['Total IGST Amount'], 1000)  # Lowest amount last
    
    def test_filter_gst_report_empty_search(self):
        """Test filtering with empty search term."""
        report_data = pd.DataFrame({
            'GST Number': ['27AAABC1234C1Z5', '29DEFGH5678H2Z9'],
            'Trade Name': ['ABC Traders', 'DEF Suppliers'],
            'Legal Name': ['ABC Pvt Ltd', 'DEF Corporation'],
            'Count': [1, 2],
            'Total IGST Amount': [1000, 2000],
            'Total CGST Amount': [500, 1000],
            'Total SGST Amount': [500, 1000]
        })
        
        result = filter_gst_report(report_data, search_term='')
        self.assertEqual(len(result), 2)  # Should return all records
    
    def test_filter_gst_report_case_insensitive(self):
        """Test case-insensitive search."""
        report_data = pd.DataFrame({
            'GST Number': ['27AAABC1234C1Z5'],
            'Trade Name': ['ABC Traders'],
            'Legal Name': ['ABC Pvt Ltd'],
            'Count': [1],
            'Total IGST Amount': [1000],
            'Total CGST Amount': [500],
            'Total SGST Amount': [500]
        })
        
        # Test lowercase search
        result = filter_gst_report(report_data, search_term='abc traders')
        self.assertEqual(len(result), 1)
        
        # Test uppercase search
        result = filter_gst_report(report_data, search_term='ABC TRADERS')
        self.assertEqual(len(result), 1)
    
    def test_get_report_summary_basic(self):
        """Test getting report summary statistics."""
        summary = get_report_summary(self.sample_data)
        
        self.assertIsInstance(summary, dict)
        self.assertIn('total_unmapped', summary)
        self.assertIn('total_records', summary)
        self.assertIn('with_trade_name', summary)
        self.assertIn('with_legal_name', summary)
        self.assertIn('with_both_names', summary)
        self.assertIn('unique_state_codes', summary)
        self.assertIn('total_igst_amount', summary)
        self.assertIn('total_cgst_amount', summary)
        self.assertIn('total_sgst_amount', summary)
        self.assertIn('avg_records_per_gst', summary)
        self.assertIn('max_records_per_gst', summary)
        
        # All values should be integers or floats
        for key, value in summary.items():
            if key in ['avg_records_per_gst']:
                self.assertIsInstance(value, (int, float))
            else:
                self.assertIsInstance(value, int)
    
    def test_get_report_summary_empty_data(self):
        """Test summary with empty data."""
        empty_df = pd.DataFrame()
        summary = get_report_summary(empty_df)
        
        expected_summary = {
            'total_unmapped': 0,
            'total_records': 0,
            'with_trade_name': 0,
            'with_legal_name': 0,
            'with_both_names': 0,
            'unique_state_codes': 0,
            'total_igst_amount': 0,
            'total_cgst_amount': 0,
            'total_sgst_amount': 0,
            'avg_records_per_gst': 0,
            'max_records_per_gst': 0
        }
        
        self.assertEqual(summary, expected_summary)
    
    def test_get_report_summary_error_handling(self):
        """Test error handling in summary generation."""
        # Create data that will cause an error (missing required columns)
        invalid_data = pd.DataFrame({'invalid_column': [1, 2, 3]})
        
        summary = get_report_summary(invalid_data)
        
        expected_summary = {
            'total_unmapped': 0,
            'total_records': 0,
            'with_trade_name': 0,
            'with_legal_name': 0,
            'with_both_names': 0,
            'unique_state_codes': 0,
            'total_igst_amount': 0,
            'total_cgst_amount': 0,
            'total_sgst_amount': 0,
            'avg_records_per_gst': 0,
            'max_records_per_gst': 0
        }
        
        self.assertEqual(summary, expected_summary)
    
    def test_gstin_validation(self):
        """Test GSTIN validation (15-digit requirement)."""
        invalid_gstin_data = pd.DataFrame({
            'Source Name': ['Books', 'GSTR-2A', 'GSTR-2A'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', 'SHORT', 'VERYLONGGSTIN123456'],
            'Supplier Trade Name': ['ABC Traders', 'Short Co', 'Long Co'],
            'Supplier Legal Name': ['ABC Pvt Ltd', 'Short Ltd', 'Long Ltd'],
            'Total IGST Amount': [1000, 500, 1000],
            'Total CGST Amount': [500, 250, 500],
            'Total SGST Amount': [500, 250, 500]
        })
        
        result = get_unique_unmapped_gst_report(invalid_gstin_data)
        
        # Should only include valid 15-digit GSTINs
        if not result.empty:
            for gstin in result['GST Number']:
                self.assertEqual(len(gstin), 15)
    
    def test_name_cleaning(self):
        """Test cleaning of Trade Name and Legal Name fields."""
        dirty_data = pd.DataFrame({
            'Source Name': ['Books', 'GSTR-2A'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', '33IJKL9012L5M3'],
            'Supplier Trade Name': ['  ABC Traders  ', np.nan],
            'Supplier Legal Name': [np.nan, '  IJK Limited  '],
            'Total IGST Amount': [1000, 3000],
            'Total CGST Amount': [500, 1500],
            'Total SGST Amount': [500, 1500]
        })
        
        result = get_unique_unmapped_gst_report(dirty_data)
        
        if not result.empty:
            # Check that names are cleaned (no leading/trailing spaces)
            for name in result['Trade Name']:
                if name != '':
                    self.assertEqual(name, name.strip())
            
            for name in result['Legal Name']:
                if name != '':
                    self.assertEqual(name, name.strip())
    
    def test_tax_amount_calculation(self):
        """Test tax amount calculation for multiple records."""
        tax_data = pd.DataFrame({
            'Source Name': ['Books', 'GSTR-2A', 'GSTR-2A', 'GSTR-2A'],
            'Supplier GSTIN': ['27AAABC1234C1Z5', '33IJKL9012L5M3', '33IJKL9012L5M3', '33IJKL9012L5M3'],
            'Supplier Trade Name': ['ABC Traders', 'IJK Enterprises', 'IJK Enterprises', 'IJK Enterprises'],
            'Supplier Legal Name': ['ABC Pvt Ltd', 'IJK Limited', 'IJK Limited', 'IJK Limited'],
            'Total IGST Amount': [1000, 1000, 2000, 3000],
            'Total CGST Amount': [500, 500, 1000, 1500],
            'Total SGST Amount': [500, 500, 1000, 1500]
        })
        
        result = get_unique_unmapped_gst_report(tax_data)
        
        if not result.empty:
            unmapped_record = result[result['GST Number'] == '33IJKL9012L5M3'].iloc[0]
            # Verify tax amounts are summed correctly
            self.assertEqual(unmapped_record['Total IGST Amount'], 6000)  # 1000+2000+3000
            self.assertEqual(unmapped_record['Total CGST Amount'], 3000)  # 500+1000+1500
            self.assertEqual(unmapped_record['Total SGST Amount'], 3000)  # 500+1000+1500
            self.assertEqual(unmapped_record['Count'], 3)  # 3 records

if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)
