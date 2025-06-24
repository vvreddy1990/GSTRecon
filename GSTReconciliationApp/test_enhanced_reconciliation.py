#!/usr/bin/env python3
"""
Test script to verify enhanced reconciliation functionality
"""

import pandas as pd
import numpy as np
from datetime import datetime
from utils.reconciliation import GSTReconciliation

def create_test_data():
    """Create test data for reconciliation"""
    # Create sample data
    data = []
    
    # Books records
    data.append({
        'Source Name': 'Books',
        'Supplier GSTIN': 'GSTIN001',
        'Supplier Legal Name': 'Test Company 1',
        'Supplier Trade Name': 'Test Co 1',
        'Invoice Date': '2024-01-15',
        'Books Date': '2024-01-15',
        'Invoice Number': 'INV001',
        'Total Taxable Value': 1000,
        'Total Tax Value': 180,
        'Total IGST Amount': 180,
        'Total CGST Amount': 0,
        'Total SGST Amount': 0,
        'Total Invoice Value': 1180
    })
    
    data.append({
        'Source Name': 'Books',
        'Supplier GSTIN': 'GSTIN001',
        'Supplier Legal Name': 'Test Company 1',
        'Supplier Trade Name': 'Test Co 1',
        'Invoice Date': '2024-01-15',
        'Books Date': '2024-01-15',
        'Invoice Number': 'INV001',
        'Total Taxable Value': 500,
        'Total Tax Value': 90,
        'Total IGST Amount': 90,
        'Total CGST Amount': 0,
        'Total SGST Amount': 0,
        'Total Invoice Value': 590
    })
    
    # GSTR-2A records
    data.append({
        'Source Name': 'GSTR-2A',
        'Supplier GSTIN': 'GSTIN001',
        'Supplier Legal Name': 'Test Company 1',
        'Supplier Trade Name': 'Test Co 1',
        'Invoice Date': '2024-01-15',
        'Books Date': '2024-01-15',
        'Invoice Number': 'INV001',
        'Total Taxable Value': 1500,
        'Total Tax Value': 270,
        'Total IGST Amount': 270,
        'Total CGST Amount': 0,
        'Total SGST Amount': 0,
        'Total Invoice Value': 1770
    })
    
    # Books only record
    data.append({
        'Source Name': 'Books',
        'Supplier GSTIN': 'GSTIN002',
        'Supplier Legal Name': 'Test Company 2',
        'Supplier Trade Name': 'Test Co 2',
        'Invoice Date': '2024-01-20',
        'Books Date': '2024-01-20',
        'Invoice Number': 'INV002',
        'Total Taxable Value': 2000,
        'Total Tax Value': 360,
        'Total IGST Amount': 360,
        'Total CGST Amount': 0,
        'Total SGST Amount': 0,
        'Total Invoice Value': 2360
    })
    
    # GSTR-2A only record
    data.append({
        'Source Name': 'GSTR-2A',
        'Supplier GSTIN': 'GSTIN003',
        'Supplier Legal Name': 'Test Company 3',
        'Supplier Trade Name': 'Test Co 3',
        'Invoice Date': '2024-01-25',
        'Books Date': '2024-01-25',
        'Invoice Number': 'INV003',
        'Total Taxable Value': 1500,
        'Total Tax Value': 270,
        'Total IGST Amount': 270,
        'Total CGST Amount': 0,
        'Total SGST Amount': 0,
        'Total Invoice Value': 1770
    })
    
    return pd.DataFrame(data)

def test_enhanced_reconciliation():
    """Test the enhanced reconciliation functionality"""
    print("Creating test data...")
    df = create_test_data()
    
    print(f"Test data created with {len(df)} records")
    print(f"Books records: {len(df[df['Source Name'] == 'Books'])}")
    print(f"GSTR-2A records: {len(df[df['Source Name'] == 'GSTR-2A'])}")
    
    print("\nInitializing reconciliation...")
    recon = GSTReconciliation(df)
    
    print("\nGetting initial results...")
    results = recon.get_results()
    
    print(f"Initial matched count: {results['matched_count']}")
    print(f"Initial partial count: {results['partial_count']}")
    print(f"Initial books only count: {results['books_only_count']}")
    print(f"Initial GSTR-2A only count: {results['gstr2a_only_count']}")
    
    # Test enhanced group matching
    print("\n" + "="*50)
    print("TESTING ENHANCED GROUP MATCHING")
    print("="*50)
    
    # Run intelligent enhanced matching
    analysis = recon.run_intelligent_enhanced_matching()
    
    # Get updated results
    updated_results = recon.get_results()
    
    print(f"\nEnhanced Matching Analysis:")
    print(f"  Books Only records: {analysis['books_only_count']}")
    print(f"  GSTR-2A Only records: {analysis['gstr2a_only_count']}")
    print(f"  Partial matches with tax differences: {analysis['partials_with_diff_count']}")
    print(f"  Potential GSTIN+Invoice groups: {analysis['potential_gstin_inv_groups']}")
    
    print(f"\nRecommendations:")
    for i, rec in enumerate(analysis['recommendations'], 1):
        print(f"  {i}. {rec['pattern']} ({rec['priority']} priority)")
        print(f"     {rec['description']}")
        print(f"     Estimated matches: {rec['estimated_matches']}")
    
    # Verify that counts have been updated
    print(f"\nUpdated Counts after Enhanced Matching:")
    print(f"  Exact Matches: {updated_results['matched_count']}")
    print(f"  Partial Matches: {updated_results['partial_count']}")
    print(f"  Group Matches: {updated_results['group_count']}")
    print(f"  Data Entry Swap Matches: {updated_results['data_entry_swap_count']}")
    print(f"  Tax-Based Group Matches: {updated_results['tax_based_group_count']}")
    print(f"  Books Only: {updated_results['books_only_count']}")
    print(f"  GSTR-2A Only: {updated_results['gstr2a_only_count']}")
    
    # Check if group matches were created
    group_matches = updated_results['final_report'][updated_results['final_report']['Status'] == 'Group Match']
    if not group_matches.empty:
        print(f"\nGroup Matches found: {len(group_matches)} records")
        unique_groups = group_matches['Group ID'].nunique()
        print(f"Unique Groups: {unique_groups}")
        
        # Show some group match details
        print("\nSample Group Match Details:")
        sample_groups = group_matches.head(3)
        for _, row in sample_groups.iterrows():
            print(f"  Group ID: {row['Group ID']}, GSTIN: {row['Supplier GSTIN']}, Invoice: {row['Invoice Number']}")
    else:
        print("\nNo Group Matches found")
    
    # Verify that the enhanced matching worked correctly
    assert len(updated_results['final_report']) == len(results['final_report']), "Total record count should remain the same"
    
    # Check if any new group matches were created
    original_group_count = len(results['final_report'][results['final_report']['Status'] == 'Group Match'])
    updated_group_count = len(updated_results['final_report'][updated_results['final_report']['Status'] == 'Group Match'])
    
    print(f"\nGroup Match Count Change: {original_group_count} -> {updated_group_count}")
    
    # The enhanced matching should either create new group matches or improve existing ones
    if updated_group_count > original_group_count:
        print("✅ Enhanced matching successfully created new group matches")
    else:
        print("ℹ️  No new group matches created (this is normal if no suitable groups were found)")
    
    print("\n✅ Enhanced reconciliation test completed successfully!")

def test_strict_matching_rules():
    """Test that strict GSTIN and name similarity rules prevent wrong matches."""
    print("Testing strict matching rules...")
    
    # Create test data with different scenarios
    test_data = []
    
    # Scenario 1: GSTIN doesn't match, names don't match - should NOT match
    test_data.extend([
        {
            'Source Name': 'Books',
            'Supplier GSTIN': '27AABCA1234A1Z5',
            'Supplier Legal Name': 'ABC Company Limited',
            'Supplier Trade Name': 'ABC Corp',
            'Invoice Date': '2024-01-15',
            'Books Date': '2024-01-15',
            'Invoice Number': 'INV001',
            'Total Taxable Value': 10000,
            'Total Tax Value': 1800,
            'Total IGST Amount': 1800,
            'Total CGST Amount': 0,
            'Total SGST Amount': 0,
            'Total Invoice Value': 11800
        },
        {
            'Source Name': 'GSTR-2A',
            'Supplier GSTIN': '29XYZDE5678B2W9',  # Different GSTIN
            'Supplier Legal Name': 'XYZ Enterprises Pvt Ltd',  # Different name
            'Supplier Trade Name': 'XYZ Ltd',  # Different trade name
            'Invoice Date': '2024-01-15',
            'Books Date': '2024-01-15',
            'Invoice Number': 'INV002',
            'Total Taxable Value': 10000,
            'Total Tax Value': 1800,
            'Total IGST Amount': 1800,
            'Total CGST Amount': 0,
            'Total SGST Amount': 0,
            'Total Invoice Value': 11800
        }
    ])
    
    # Scenario 2: GSTIN doesn't match, but legal name matches - should match
    test_data.extend([
        {
            'Source Name': 'Books',
            'Supplier GSTIN': '27AABCA1234A1Z5',
            'Supplier Legal Name': 'ABC Company Limited',
            'Supplier Trade Name': 'ABC Corp',
            'Invoice Date': '2024-01-15',
            'Books Date': '2024-01-15',
            'Invoice Number': 'INV003',
            'Total Taxable Value': 10000,
            'Total Tax Value': 1800,
            'Total IGST Amount': 1800,
            'Total CGST Amount': 0,
            'Total SGST Amount': 0,
            'Total Invoice Value': 11800
        },
        {
            'Source Name': 'GSTR-2A',
            'Supplier GSTIN': '29XYZDE5678B2W9',  # Different GSTIN
            'Supplier Legal Name': 'ABC Company Limited',  # Same legal name
            'Supplier Trade Name': 'ABC Corp',  # Same trade name
            'Invoice Date': '2024-01-15',
            'Books Date': '2024-01-15',
            'Invoice Number': 'INV004',
            'Total Taxable Value': 10000,
            'Total Tax Value': 1800,
            'Total IGST Amount': 1800,
            'Total CGST Amount': 0,
            'Total SGST Amount': 0,
            'Total Invoice Value': 11800
        }
    ])
    
    # Scenario 3: GSTIN doesn't match, trade name similar but below threshold - should NOT match
    test_data.extend([
        {
            'Source Name': 'Books',
            'Supplier GSTIN': '27AABCA1234A1Z5',
            'Supplier Legal Name': 'ABC Company Limited',
            'Supplier Trade Name': 'ABC Corporation',
            'Invoice Date': '2024-01-15',
            'Books Date': '2024-01-15',
            'Invoice Number': 'INV005',
            'Total Taxable Value': 10000,
            'Total Tax Value': 1800,
            'Total IGST Amount': 1800,
            'Total CGST Amount': 0,
            'Total SGST Amount': 0,
            'Total Invoice Value': 11800
        },
        {
            'Source Name': 'GSTR-2A',
            'Supplier GSTIN': '29XYZDE5678B2W9',  # Different GSTIN
            'Supplier Legal Name': 'Different Company Ltd',  # Different legal name
            'Supplier Trade Name': 'ABC Corp',  # Similar but different trade name
            'Invoice Date': '2024-01-15',
            'Books Date': '2024-01-15',
            'Invoice Number': 'INV006',
            'Total Taxable Value': 10000,
            'Total Tax Value': 1800,
            'Total IGST Amount': 1800,
            'Total CGST Amount': 0,
            'Total SGST Amount': 0,
            'Total Invoice Value': 11800
        }
    ])
    
    # Scenario 4: GSTIN matches - should match regardless of names
    test_data.extend([
        {
            'Source Name': 'Books',
            'Supplier GSTIN': '27AABCA1234A1Z5',
            'Supplier Legal Name': 'ABC Company Limited',
            'Supplier Trade Name': 'ABC Corp',
            'Invoice Date': '2024-01-15',
            'Books Date': '2024-01-15',
            'Invoice Number': 'INV007',
            'Total Taxable Value': 10000,
            'Total Tax Value': 1800,
            'Total IGST Amount': 1800,
            'Total CGST Amount': 0,
            'Total SGST Amount': 0,
            'Total Invoice Value': 11800
        },
        {
            'Source Name': 'GSTR-2A',
            'Supplier GSTIN': '27AABCA1234A1Z5',  # Same GSTIN
            'Supplier Legal Name': 'Different Legal Name',  # Different legal name
            'Supplier Trade Name': 'Different Trade Name',  # Different trade name
            'Invoice Date': '2024-01-15',
            'Books Date': '2024-01-15',
            'Invoice Number': 'INV008',
            'Total Taxable Value': 10000,
            'Total Tax Value': 1800,
            'Total IGST Amount': 1800,
            'Total CGST Amount': 0,
            'Total SGST Amount': 0,
            'Total Invoice Value': 11800
        }
    ])
    
    # Create DataFrame
    df = pd.DataFrame(test_data)
    
    # Initialize reconciliation
    reconciliation = GSTReconciliation(df)
    
    # Get results
    results = reconciliation.get_results()
    
    # Analyze results
    print("\n=== Strict Matching Rules Test Results ===")
    
    # Check Scenario 1: Should NOT match (GSTIN different, names different)
    scenario1_books = results['final_report'][
        (results['final_report']['Source Name'] == 'Books') & 
        (results['final_report']['Invoice Number'] == 'INV001')
    ]
    scenario1_gstr2a = results['final_report'][
        (results['final_report']['Source Name'] == 'GSTR-2A') & 
        (results['final_report']['Invoice Number'] == 'INV002')
    ]
    
    print(f"Scenario 1 (GSTIN different, names different):")
    print(f"  Books status: {scenario1_books['Status'].iloc[0] if len(scenario1_books) > 0 else 'Not found'}")
    print(f"  GSTR-2A status: {scenario1_gstr2a['Status'].iloc[0] if len(scenario1_gstr2a) > 0 else 'Not found'}")
    print(f"  Expected: Both should be 'Books Only' or 'GSTR-2A Only'")
    
    # Check Scenario 2: Should match (GSTIN different, but legal name matches)
    scenario2_books = results['final_report'][
        (results['final_report']['Source Name'] == 'Books') & 
        (results['final_report']['Invoice Number'] == 'INV003')
    ]
    scenario2_gstr2a = results['final_report'][
        (results['final_report']['Source Name'] == 'GSTR-2A') & 
        (results['final_report']['Invoice Number'] == 'INV004')
    ]
    
    print(f"\nScenario 2 (GSTIN different, legal name matches):")
    print(f"  Books status: {scenario2_books['Status'].iloc[0] if len(scenario2_books) > 0 else 'Not found'}")
    print(f"  GSTR-2A status: {scenario2_gstr2a['Status'].iloc[0] if len(scenario2_gstr2a) > 0 else 'Not found'}")
    print(f"  Expected: Both should be 'Partial Match' or 'Tax-Based Group Match'")
    
    # Check Scenario 3: Should NOT match (GSTIN different, trade name similar but below threshold)
    scenario3_books = results['final_report'][
        (results['final_report']['Source Name'] == 'Books') & 
        (results['final_report']['Invoice Number'] == 'INV005')
    ]
    scenario3_gstr2a = results['final_report'][
        (results['final_report']['Source Name'] == 'GSTR-2A') & 
        (results['final_report']['Invoice Number'] == 'INV006')
    ]
    
    print(f"\nScenario 3 (GSTIN different, trade name similar but below threshold):")
    print(f"  Books status: {scenario3_books['Status'].iloc[0] if len(scenario3_books) > 0 else 'Not found'}")
    print(f"  GSTR-2A status: {scenario3_gstr2a['Status'].iloc[0] if len(scenario3_gstr2a) > 0 else 'Not found'}")
    print(f"  Expected: Both should be 'Books Only' or 'GSTR-2A Only'")
    
    # Check Scenario 4: Should match (GSTIN matches)
    scenario4_books = results['final_report'][
        (results['final_report']['Source Name'] == 'Books') & 
        (results['final_report']['Invoice Number'] == 'INV007')
    ]
    scenario4_gstr2a = results['final_report'][
        (results['final_report']['Source Name'] == 'GSTR-2A') & 
        (results['final_report']['Invoice Number'] == 'INV008')
    ]
    
    print(f"\nScenario 4 (GSTIN matches):")
    print(f"  Books status: {scenario4_books['Status'].iloc[0] if len(scenario4_books) > 0 else 'Not found'}")
    print(f"  GSTR-2A status: {scenario4_gstr2a['Status'].iloc[0] if len(scenario4_gstr2a) > 0 else 'Not found'}")
    print(f"  Expected: Both should be 'Exact Match' or 'Partial Match'")
    
    # Print summary statistics
    print(f"\n=== Summary Statistics ===")
    status_counts = results['final_report']['Status'].value_counts()
    print("Status distribution:")
    for status, count in status_counts.items():
        print(f"  {status}: {count}")
    
    # Verify strict rules are working
    print(f"\n=== Verification of Strict Rules ===")
    
    # Check that no matches have low GSTIN similarity AND low name similarity
    matched_records = results['final_report'][
        results['final_report']['Status'].isin(['Partial Match', 'Tax-Based Group Match'])
    ]
    
    if len(matched_records) > 0:
        print(f"Checking {len(matched_records)} matched records for strict rule compliance...")
        
        violations = 0
        for _, record in matched_records.iterrows():
            gstin_score = record.get('GSTIN Score', 0)
            legal_name_score = record.get('Legal Name Score', 0)
            trade_name_score = record.get('Trade Name Score', 0)
            
            # Check if GSTIN similarity is low but name similarities are also low
            if gstin_score < 80 and legal_name_score < 70 and trade_name_score < 70:
                violations += 1
                print(f"  VIOLATION: Match ID {record['Match ID']} - GSTIN: {gstin_score}%, Legal: {legal_name_score}%, Trade: {trade_name_score}%")
        
        if violations == 0:
            print("  ✓ All matches comply with strict rules!")
        else:
            print(f"  ✗ Found {violations} violations of strict rules")
    else:
        print("No matched records found to verify")
    
    return results

if __name__ == "__main__":
    # Run the strict matching rules test
    test_results = test_strict_matching_rules()
    
    print("\n=== Test Completed ===")
    print("The strict matching rules should prevent wrong matches when:")
    print("1. GSTIN similarity < 80% AND")
    print("2. Legal name similarity < 70% AND")
    print("3. Trade name similarity < 70%")
    print("\nThis ensures that records are only matched when there's sufficient")
    print("similarity in either GSTIN or supplier names.") 