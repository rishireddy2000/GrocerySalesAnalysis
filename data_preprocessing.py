import os
import pandas as pd

# Define data folder paths
DATA_FOLDER = "data"
OUTPUT_FOLDER = os.path.join(DATA_FOLDER, "cleaned_data")

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def load_csv(file_name):
    """ Load CSV file, trying both semicolon and comma delimiters """
    file_path = os.path.join(DATA_FOLDER, file_name)
    
    try:
        df = pd.read_csv(file_path, sep=';', na_values=['NULL', 'NA', 'N/A', 'NaN', ''])
        if df.shape[1] == 1:  # If only one column, try comma delimiter
            df = pd.read_csv(file_path, sep=',', na_values=['NULL', 'NA', 'N/A', 'NaN', ''])
    except Exception as e:
        print(f"❌ Error loading {file_name}: {e}")
        return None

    print(f"✅ Loaded {file_name} with {df.shape[0]} rows and {df.shape[1]} columns")
    return df

def save_csv(df, file_name):
    """ Save DataFrame as CSV in the cleaned data folder """
    output_path = os.path.join(OUTPUT_FOLDER, file_name)
    df.to_csv(output_path, index=False)
    print(f"💾 Saved cleaned data: {output_path}")

# 🛠 Fix: **Recalculate TotalPrice after merging with Products**
def recalculate_total_price(sales, products):
    """ Merge sales with product prices and recalculate TotalPrice """
    sales = sales.merge(products[['ProductID', 'Price']], on='ProductID', how='left')

    # Fill missing prices with 0
    sales['Price'] = sales['Price'].fillna(0)

    # Recalculate TotalPrice
    mask = (sales['TotalPrice'].isna()) | (sales['TotalPrice'] == 0)
    sales.loc[mask, 'TotalPrice'] = (sales.loc[mask, 'Price'] * sales.loc[mask, 'Quantity']) - sales.loc[mask, 'Discount']

    return sales

# 🛠 Module-Specific Tables

### **1️⃣ Customer Segmentation (RFM Analysis)**
def create_rfm_table():
    sales = load_csv("sales.csv")
    customers = load_csv("customers.csv")
    cities = load_csv("cities.csv")
    countries = load_csv("countries.csv")
    products = load_csv("products.csv")

    if sales is None or customers is None or cities is None or countries is None or products is None:
        return None

    sales = recalculate_total_price(sales, products)

    sales = sales.merge(customers[['CustomerID', 'CityID']], on='CustomerID', how='left')
    sales = sales.merge(cities[['CityID', 'CountryID']], on='CityID', how='left')
    sales = sales.merge(countries[['CountryID', 'CountryName']], on='CountryID', how='left')

    save_csv(sales[['CustomerID', 'TotalPrice', 'SalesDate', 'CityID', 'CountryID', 'CountryName']], "cleaned_rfm_analysis.csv")

### **2️⃣ Product Recommendations (Market Basket Analysis)**
def create_product_recommendation_table():
    sales = load_csv("sales.csv")
    products = load_csv("products.csv")
    categories = load_csv("categories.csv")

    if sales is None or products is None or categories is None:
        return None

    sales = recalculate_total_price(sales, products)

    sales = sales.merge(products[['ProductID', 'CategoryID']], on='ProductID', how='left')
    sales = sales.merge(categories[['CategoryID', 'CategoryName']], on='CategoryID', how='left')

    save_csv(sales[['SalesID', 'CustomerID', 'ProductID', 'CategoryID', 'CategoryName', 'TotalPrice']], "cleaned_product_recommendations.csv")

### **3️⃣ Sales Forecasting**
def create_sales_forecasting_table():
    sales = load_csv("sales.csv")
    products = load_csv("products.csv")

    if sales is None or products is None:
        return None

    sales = recalculate_total_price(sales, products)

    save_csv(sales[['SalesID', 'SalesDate', 'TotalPrice', 'Quantity']], "cleaned_sales_forecasting.csv")

### **4️⃣ Employee Performance Analysis**
def create_employee_performance_table():
    sales = load_csv("sales.csv")
    employees = load_csv("employees.csv")
    products = load_csv("products.csv")

    if sales is None or employees is None or products is None:
        return None

    sales = recalculate_total_price(sales, products)

    sales = sales.merge(employees[['EmployeeID', 'FirstName', 'LastName', 'HireDate']], left_on='SalesPersonID', right_on='EmployeeID', how='left')

    save_csv(sales[['SalesID', 'SalesPersonID', 'FirstName', 'LastName', 'HireDate', 'TotalPrice']], "cleaned_employee_performance.csv")

### **5️⃣ Geographical Sales Insights**
def create_geographical_sales_table():
    sales = load_csv("sales.csv")
    customers = load_csv("customers.csv")
    cities = load_csv("cities.csv")
    countries = load_csv("countries.csv")
    products = load_csv("products.csv")

    if sales is None or customers is None or cities is None or countries is None or products is None:
        return None

    sales = recalculate_total_price(sales, products)

    sales = sales.merge(customers[['CustomerID', 'CityID']], on='CustomerID', how='left')
    sales = sales.merge(cities[['CityID', 'CountryID', 'CityName']], on='CityID', how='left')
    sales = sales.merge(countries[['CountryID', 'CountryName']], on='CountryID', how='left')

    save_csv(sales[['SalesID', 'SalesDate', 'TotalPrice', 'CustomerID', 'CityID', 'CityName', 'CountryID', 'CountryName']], "cleaned_geographical_sales.csv")

### **🚀 Run All Cleaning & Table Creation Functions**
def main():
    print("\n🚀 Starting Data Preprocessing...\n")

    create_rfm_table()  # Customer segmentation data
    create_product_recommendation_table()  # Market basket analysis data
    create_sales_forecasting_table()  # Sales forecasting data
    create_employee_performance_table()  # Employee performance data
    create_geographical_sales_table()  # Geographical sales analysis data

    print("\n✅ All module-specific datasets cleaned and saved successfully!\n")

if __name__ == "__main__":
    main()
