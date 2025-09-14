"""
Excel to CSV Converter for SuperStore Data
Run this script to convert your Excel file to CSV files for better Streamlit Cloud deployment
"""

import pandas as pd
import os

def convert_excel_to_csv(excel_file='SuperStore Data.xlsx'):
    """
    Convert Excel file with multiple sheets to individual CSV files
    """
    try:
        print("🔄 Starting Excel to CSV conversion...")
        
        # Check if Excel file exists
        if not os.path.exists(excel_file):
            print(f"❌ File '{excel_file}' not found!")
            print("💡 Make sure the Excel file is in the same directory as this script")
            return False
        
        # Define sheet names
        sheet_names = ['Orders', 'Location', 'Calendar', 'Customers', 'Products', 'SalesTeam']
        
        print(f"📁 Reading Excel file: {excel_file}")
        
        # Convert each sheet to CSV
        for sheet_name in sheet_names:
            try:
                # Read the sheet
                df = pd.read_excel(excel_file, sheet_name=sheet_name, engine='openpyxl')
                
                # Create CSV filename
                csv_filename = f"{sheet_name.lower().replace(' ', '_')}.csv"
                
                # Save as CSV
                df.to_csv(csv_filename, index=False)
                
                print(f"✅ Converted '{sheet_name}' → '{csv_filename}' ({len(df)} rows)")
                
            except Exception as e:
                print(f"⚠️  Warning: Could not convert sheet '{sheet_name}': {str(e)}")
        
        print("\n🎉 Conversion completed successfully!")
        print("\n📋 Files created:")
        for sheet_name in sheet_names:
            csv_filename = f"{sheet_name.lower().replace(' ', '_')}.csv"
            if os.path.exists(csv_filename):
                file_size = os.path.getsize(csv_filename) / 1024  # KB
                print(f"   • {csv_filename} ({file_size:.1f} KB)")
        
        print("\n💡 Next steps for Streamlit deployment:")
        print("1. Upload these CSV files to your GitHub repository")
        print("2. Use the CSV-friendly Streamlit app code")
        print("3. Deploy on Streamlit Community Cloud")
        
        return True
        
    except Exception as e:
        print(f"❌ Error during conversion: {str(e)}")
        return False

def verify_csv_files():
    """
    Verify that all CSV files were created successfully
    """
    expected_files = ['orders.csv', 'location.csv', 'calendar.csv', 'customers.csv', 'products.csv', 'salesteam.csv']
    
    print("\n🔍 Verifying CSV files...")
    
    all_good = True
    for file in expected_files:
        if os.path.exists(file):
            df = pd.read_csv(file)
            print(f"✅ {file}: {len(df)} rows, {len(df.columns)} columns")
        else:
            print(f"❌ {file}: Not found!")
            all_good = False
    
    if all_good:
        print("\n🎯 All CSV files verified successfully!")
        print("Ready for Streamlit deployment! 🚀")
    else:
        print("\n⚠️  Some files are missing. Please check the conversion process.")
    
    return all_good

if __name__ == "__main__":
    print("=" * 60)
    print("🏪 SUPERSTORE DATA CONVERTER")
    print("=" * 60)
    
    # Convert Excel to CSV
    success = convert_excel_to_csv()
    
    if success:
        # Verify the conversion
        verify_csv_files()
        
        print("\n" + "=" * 60)
        print("🎉 CONVERSION COMPLETE!")
        print("=" * 60)
        
        print("\n📦 Your deployment package should include:")
        print("• app.py (Streamlit application)")
        print("• requirements.txt (Python dependencies)")
        print("• orders.csv (Orders data)")
        print("• location.csv (Location data)")
        print("• customers.csv (Customer data)")
        print("• products.csv (Product data)")
        print("• salesteam.csv (Sales team data)")
        print("• README.md (Optional: Project documentation)")
        
    else:
        print("\n❌ Conversion failed. Please check your Excel file and try again.")
