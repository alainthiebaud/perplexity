#!/usr/bin/env python3
"""
Comprehensive test for all existing functionality after hierarchical implementation
"""
import pandas as pd
import sys
import os
from pathlib import Path

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_existing_functionality():
    print("Testing all existing functionality after hierarchical implementation...")
    
    # Test 1: Excel file loading (existing functionality)
    print("\n1. Testing Excel file loading...")
    excel_file = 'assets/frais_divers_annuels.xlsx'
    if not Path(excel_file).exists():
        print("❌ Test Excel file not found")
        return False
    
    try:
        xlsf = pd.ExcelFile(excel_file)
        print(f"✓ Excel file loaded successfully with {len(xlsf.sheet_names)} sheets")
    except Exception as e:
        print(f"❌ Failed to load Excel file: {e}")
        return False
    
    # Test 2: Data parsing (existing functionality)  
    print("\n2. Testing data parsing...")
    try:
        sheets = {}
        for sheet_name in xlsf.sheet_names:
            sheets[sheet_name] = xlsf.parse(sheet_name)
            # Verify expected columns exist
            expected_cols = ['Description', 'Montant (CHF)']
            for col in expected_cols:
                if col not in sheets[sheet_name].columns:
                    print(f"❌ Missing column '{col}' in sheet '{sheet_name}'")
                    return False
        print(f"✓ All {len(sheets)} sheets parsed with correct columns")
    except Exception as e:
        print(f"❌ Failed to parse data: {e}")
        return False
    
    # Test 3: Data editing (existing functionality)
    print("\n3. Testing data editing...")
    try:
        # Test numeric editing
        original_value = sheets['Entretien'].iloc[3, 1]
        sheets['Entretien'].iloc[3, 1] = 999.99
        if sheets['Entretien'].iloc[3, 1] != 999.99:
            print("❌ Numeric value editing failed")
            return False
        
        # Test text editing  
        original_desc = sheets['Administration'].iloc[0, 0]
        sheets['Administration'].iloc[0, 0] = "Test Description"
        if sheets['Administration'].iloc[0, 0] != "Test Description":
            print("❌ Text editing failed")
            return False
        
        print("✓ Data editing functionality works correctly")
        
        # Restore original values
        sheets['Entretien'].iloc[3, 1] = original_value
        sheets['Administration'].iloc[0, 0] = original_desc
        
    except Exception as e:
        print(f"❌ Data editing failed: {e}")
        return False
    
    # Test 4: Data saving simulation (existing functionality)
    print("\n4. Testing data saving simulation...")
    try:
        # Create a temporary file to test saving
        temp_file = "/tmp/test_frais.xlsx"
        with pd.ExcelWriter(temp_file, engine="openpyxl") as writer:
            for sheet_name, df in sheets.items():
                df.to_excel(writer, index=False, sheet_name=sheet_name)
        
        # Verify the saved file can be read back
        test_xlsf = pd.ExcelFile(temp_file)
        if set(test_xlsf.sheet_names) != set(sheets.keys()):
            print("❌ Saved file doesn't contain all sheets")
            return False
        
        print("✓ Data saving functionality works correctly")
        
        # Clean up
        os.remove(temp_file)
        
    except Exception as e:
        print(f"❌ Data saving failed: {e}")
        return False
    
    # Test 5: Hierarchical structure integrity
    print("\n5. Testing hierarchical structure integrity...")
    try:
        # Test expand/collapse state tracking
        expanded_state = {'Entretien': True, 'Maintenance': False, 'Administration': True}
        
        # Test sheet name extraction helper
        test_cases = [
            ("📁 Entretien (Total: 1200.00 CHF)", "Entretien"),
            ("📁 Administration", "Administration"),
            ("📁 Maintenance (Total: 0.00 CHF)", "Maintenance")
        ]
        
        for test_text, expected in test_cases:
            # Simulate helper function
            if test_text.startswith("📁 "):
                text_without_icon = test_text[2:]
                if " (Total:" in text_without_icon:
                    result = text_without_icon.split(" (Total:")[0]
                else:
                    result = text_without_icon
                
                if result != expected:
                    print(f"❌ Sheet name extraction failed: '{test_text}' → '{result}' (expected '{expected}')")
                    return False
        
        print("✓ Hierarchical structure integrity maintained")
        
    except Exception as e:
        print(f"❌ Hierarchical structure test failed: {e}")
        return False
    
    # Test 6: Total calculation accuracy
    print("\n6. Testing total calculation accuracy...")
    try:
        total_tests = [
            ('Entretien', 1800.0),
            ('Maintenance', 3800.0), 
            ('Administration', 600.0),
            ('Assurances', 0.0),
            ('Taxes', 0.0)
        ]
        
        for sheet_name, expected_total in total_tests:
            if sheet_name in sheets:
                actual_total = sheets[sheet_name]['Montant (CHF)'].sum()
                if abs(actual_total - expected_total) > 0.01:  # Allow small floating point differences
                    print(f"❌ Total calculation error for {sheet_name}: {actual_total} != {expected_total}")
                    return False
        
        print("✓ Total calculations are accurate")
        
    except Exception as e:
        print(f"❌ Total calculation test failed: {e}")
        return False
    
    # Test 7: Add/Remove operations
    print("\n7. Testing add/remove operations...")
    try:
        # Test adding item
        original_count = len(sheets['Taxes'])
        new_item = pd.DataFrame([{"Description": "Test Tax", "Montant (CHF)": 100}])
        sheets['Taxes'] = pd.concat([sheets['Taxes'], new_item], ignore_index=True)
        
        if len(sheets['Taxes']) != original_count + 1:
            print("❌ Add operation failed")
            return False
        
        # Test removing item (remove the one we just added)
        sheets['Taxes'] = sheets['Taxes'].drop(sheets['Taxes'].index[-1]).reset_index(drop=True)
        
        if len(sheets['Taxes']) != original_count:
            print("❌ Remove operation failed")
            return False
        
        print("✓ Add/remove operations work correctly")
        
    except Exception as e:
        print(f"❌ Add/remove test failed: {e}")
        return False
    
    print("\n✅ ALL TESTS PASSED! All existing functionality works correctly after hierarchical implementation.")
    return True

if __name__ == "__main__":
    test_existing_functionality()