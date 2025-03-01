import os
import pandas as pd
import plotly.express as px
from sklearn.cluster import KMeans
from datetime import datetime

# Define data folder path
DATA_FOLDER = "data/cleaned_data"
OUTPUT_FOLDER = "data/processed_data"

# Ensure the output folder exists
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

def load_data(file_name):
    """ Load the cleaned RFM dataset """
    file_path = os.path.join(DATA_FOLDER, file_name)
    df = pd.read_csv(file_path)
    print(f"✅ Loaded {file_name} with {df.shape[0]} rows and {df.shape[1]} columns")
    return df

def save_data(df, file_name):
    """ Save the processed dataset """
    output_path = os.path.join(OUTPUT_FOLDER, file_name)
    df.to_csv(output_path, index=False)
    print(f"💾 Saved processed data: {output_path}")

def calculate_rfm(df):
    """ Compute RFM (Recency, Frequency, Monetary) metrics """
    df['SalesDate'] = pd.to_datetime(df['SalesDate'])

    # Define the reference date (most recent transaction in dataset)
    reference_date = df['SalesDate'].max()

    # Compute RFM metrics
    rfm = df.groupby('CustomerID').agg({
        'SalesDate': [  # Recency & Frequency
            lambda x: (reference_date - x.max()).days,  # Recency
            'count'  # Frequency (number of transactions)
        ],
        'TotalPrice': 'sum'  # Monetary
    })

    # Fix: Properly rename the multi-index columns
    rfm.columns = ['Recency', 'Frequency', 'Monetary']

    print("\n📊 Checking available columns in RFM DataFrame before clustering:", rfm.columns)
    print("\n✅ RFM metrics calculated successfully!\n")
    return rfm

def cluster_customers(rfm, n_clusters=4):
    """ Apply K-Means Clustering to segment customers """
    # Normalize data (scale between 0-1)
    rfm_scaled = (rfm - rfm.min()) / (rfm.max() - rfm.min())

    # Apply K-Means clustering
    kmeans = KMeans(n_clusters=n_clusters, random_state=42, n_init=10)
    rfm['Cluster'] = kmeans.fit_predict(rfm_scaled)

    print("\n✅ Customers segmented into clusters successfully!\n")
    return rfm

def visualize_clusters(rfm):
    """ Create an interactive 3D scatter plot for customer segmentation """
    print("\n📊 Checking available columns in RFM DataFrame before visualization:", rfm.columns)

    fig = px.scatter_3d(rfm, x='Recency', y='Frequency', z='Monetary',
                        color='Cluster', title="Customer Segmentation (RFM Analysis)",
                        hover_data=['Recency', 'Frequency', 'Monetary'])

    fig.show()
    fig.write_html(os.path.join(OUTPUT_FOLDER, "rfm_clusters.html"))
    print("📊 Interactive visualization saved as 'rfm_clusters.html'")

def main():
    print("\n🚀 Starting Customer Segmentation (RFM Analysis)...\n")

    # Step 1: Load Data
    df = load_data("cleaned_rfm_analysis.csv")

    # Step 2: Calculate RFM Metrics
    rfm = calculate_rfm(df)

    # Step 3: Apply Clustering
    rfm_segmented = cluster_customers(rfm)

    # Step 4: Visualize Clusters
    visualize_clusters(rfm_segmented)

    # Step 5: Save Processed Data
    save_data(rfm_segmented, "rfm_segmented_customers.csv")

    print("\n✅ Customer segmentation completed successfully!\n")

if __name__ == "__main__":
    main()
