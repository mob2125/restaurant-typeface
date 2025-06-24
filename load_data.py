print("--- SCRIPT EXECUTION STARTED ---")

import pandas as pd
from sqlalchemy import create_engine
import time
import os

# --- 1. DATABASE CONFIGURATION ---
# Make sure these credentials are correct.
DB_USER = "priyanshu"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "zomato_db"

DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"

# --- 2. FILE PATH CONFIGURATION ---
CSV_FILE_PATH = "zomato.csv"
XLSX_FILE_PATH = "Country-Code.xlsx" # The name of your country code file

def clean_column_names(df):
    """Cleans and standardizes the column names of a DataFrame."""
    new_cols = [col.lower().replace(' ', '_').replace('-', '_').replace('?', '') for col in df.columns]
    df.columns = new_cols
    return df

def load_data():
    """
    Connects to the database and loads both the countries and restaurants data.
    This will replace any existing tables with the same names.
    """
    print("--- Starting data loading process... ---")

    # --- Verify all required files exist ---
    if not os.path.exists(CSV_FILE_PATH) or not os.path.exists(XLSX_FILE_PATH):
        print(f"ERROR: Make sure both '{CSV_FILE_PATH}' and '{XLSX_FILE_PATH}' are in the same folder as the script.")
        return

    try:
        # --- Establish Database Connection ---
        print(f"--- Connecting to the database '{DB_NAME}'... ---")
        engine = create_engine(DATABASE_URL)
        print("--- Database connection successful! ---")

        # --- PART 1: LOAD COUNTRIES TABLE ---
        print(f"\n--- Processing '{XLSX_FILE_PATH}'... ---")
        country_df = pd.read_excel(XLSX_FILE_PATH)
        
        # Clean column names (e.g., 'Country Code' -> 'country_code')
        country_df = clean_column_names(country_df)
        country_df.rename(columns={'country': 'country_name'}, inplace=True) # Rename 'country' to 'country_name' for clarity
        
        countries_table_name = "countries"
        print(f"--- Loading data into '{countries_table_name}' table... ---")
        country_df.to_sql(
            countries_table_name,
            con=engine,
            if_exists='replace',
            index=False
        )
        print(f"--- Successfully created and populated '{countries_table_name}'. ---")


        # --- PART 2: LOAD RESTAURANTS TABLE ---
        print(f"\n--- Processing '{CSV_FILE_PATH}'... ---")
        restaurant_df = pd.read_csv(CSV_FILE_PATH, encoding='ISO-8859-1')
        
        # Clean column names
        restaurant_df = clean_column_names(restaurant_df)

        restaurants_table_name = "restaurants"
        print(f"--- Loading data into '{restaurants_table_name}' table... ---")
        restaurant_df.to_sql(
            restaurants_table_name,
            con=engine,
            if_exists='replace',
            index=False,
            chunksize=1000
        )
        print(f"--- Successfully created and populated '{restaurants_table_name}'. ---")


        print("\n" + "✅" * 3)
        print("ALL DATA LOADED SUCCESSFULLY!")
        print(f"Your database '{DB_NAME}' now contains the '{countries_table_name}' and '{restaurants_table_name}' tables.")
        print("✅" * 3)

    except Exception as e:
        print(f"\nAN ERROR OCCURRED: {e}")
        print("\n--- TROUBLESHOOTING ---")
        print("1. Did you install openpyxl? (`pip install openpyxl`)")
        print("2. Is your PostgreSQL server running?")
        print("3. Are the database credentials in the script correct?")

# This 'if' statement must have ZERO indentation
if __name__ == "__main__":
    load_data()