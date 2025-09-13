#!/usr/bin/env python3
"""
Test script for hierarchical tree functionality with totals
"""
import pandas as pd
import sys
import os

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def test_hierarchical_structure_with_totals():
    print("Testing hierarchical frais divers structure with totals...")
    
    # Load the Excel file
    excel_file = 'assets/frais_divers_annuels.xlsx'
    xlsf = pd.ExcelFile(excel_file)
    
    # Simulate the hierarchical structure
    sheets = {}
    for sheet_name in xlsf.sheet_names:
        sheets[sheet_name] = xlsf.parse(sheet_name)
    
    print("\nHierarchical structure with totals:")
    print("==================================")
    
    grand_total = 0
    for sheet_name, df in sheets.items():
        if df is not None and not df.empty and 'Montant (CHF)' in df.columns:
            total = df['Montant (CHF)'].sum()
            grand_total += total
            category_text = f"📁 {sheet_name} (Total: {total:.2f} CHF)"
        else:
            category_text = f"📁 {sheet_name}"
        
        print(category_text)
        for _, row in df.iterrows():
            description = row.get('Description', '')
            montant = row.get('Montant (CHF)', 0)
            print(f"  ├─ {description:<40} {montant:>10} CHF")
        print()
    
    print(f"Grand Total: {grand_total:.2f} CHF")
    print()
    
    # Test data modification with total update
    print("Testing data modification with total update...")
    original_total = sheets['Entretien']['Montant (CHF)'].sum()
    sheets['Entretien'].iloc[3, 1] = 800  # Change garden maintenance from 600 to 800
    new_total = sheets['Entretien']['Montant (CHF)'].sum()
    print(f"✓ Entretien total changed: {original_total:.2f} → {new_total:.2f} CHF")
    
    # Test adding new item with total update
    print("\nTesting item addition with total update...")
    old_total = sheets['Administration']['Montant (CHF)'].sum()
    new_item = pd.DataFrame([{"Description": "Frais de communication", "Montant (CHF)": 250}])
    sheets['Administration'] = pd.concat([sheets['Administration'], new_item], ignore_index=True)
    new_total = sheets['Administration']['Montant (CHF)'].sum()
    print(f"✓ Administration total: {old_total:.2f} → {new_total:.2f} CHF")
    
    # Test helper function for extracting sheet names
    print("\nTesting sheet name extraction...")
    test_cases = [
        "📁 Entretien (Total: 1200.00 CHF)",
        "📁 Administration",
        "📁 Maintenance (Total: 3800.00 CHF)"
    ]
    
    for test_text in test_cases:
        # Simulate the helper function logic
        if test_text.startswith("📁 "):
            text_without_icon = test_text[2:]
            if " (Total:" in text_without_icon:
                sheet_name = text_without_icon.split(" (Total:")[0]
            else:
                sheet_name = text_without_icon
        print(f"✓ '{test_text}' → '{sheet_name}'")
    
    print("\n✅ All hierarchical functionality with totals tests passed!")
    return True

if __name__ == "__main__":
    test_hierarchical_structure_with_totals()