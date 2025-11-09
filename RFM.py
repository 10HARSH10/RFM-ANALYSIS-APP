import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px

st.set_page_config(page_title="RFM Analysis App", layout="wide")

# --- TITLE ---
st.title("📊 RFM Analysis for Superstore Dataset")

# --- FILE UPLOAD ---
uploaded_file = st.file_uploader("Upload your Superstore dataset (CSV or Excel)", type=["csv", "xlsx"])

if uploaded_file:
    # --- READ DATA ---
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file, parse_dates=['Order_Date'])
    else:
        df = pd.read_excel(uploaded_file, parse_dates=['Order_Date'])
    
    st.subheader("Dataset Preview")
    st.dataframe(df.head())
    
  # --- CHECK REQUIRED COLUMNS ---
    required_cols = ['Customer_ID', 'Order_Date', 'Sales']
    if not all(col in df.columns for col in required_cols):
        st.error(f"Dataset must include these columns: {required_cols}")
    else:
        # --- CALCULATE RFM METRICS ---
        st.subheader("Calculating RFM Metrics...")
        snapshot_date = df['Order_Date'].max() + pd.Timedelta(days=1)

        rfm = df.groupby('Customer_ID').agg({
            'Order_Date': lambda x: (snapshot_date - x.max()).days,
            'Customer_ID': 'count',
            'Sales': 'sum'
        }).rename(columns={
            'Order_Date': 'Recency',
            'Customer_ID': 'Frequency',
            'Sales': 'Monetary'
        })

        # --- SCORING ---
        rfm['R_Score'] = pd.qcut(rfm['Recency'], 5, labels=[5,4,3,2,1])
        rfm['F_Score'] = pd.qcut(rfm['Frequency'].rank(method='first'), 5, labels=[1,2,3,4,5])
        rfm['M_Score'] = pd.qcut(rfm['Monetary'], 5, labels=[1,2,3,4,5])

        rfm['RFM_Score'] = rfm[['R_Score','F_Score','M_Score']].astype(int).sum(axis=1)

        # --- SEGMENTATION ---
        def segment_customer(score):
            if score >= 9:
                return 'Champions'
            elif score >= 7:
                return 'Loyal Customers'
            elif score >= 5 :
                return 'Potential Loyalist'
            elif score >= 3:
                return 'At Risk'
            else:
                return 'Lost'
        
        rfm['Segment'] = rfm['RFM_Score'].apply(segment_customer)

        st.success("✅ RFM Analysis Completed!")

        # --- DISPLAY RESULTS ---
        st.subheader("RFM Table")
        st.dataframe(rfm.reset_index())

        # --- VISUALIZATIONS ---
        st.subheader("Customer Segments Distribution")
        seg_counts = rfm['Segment'].value_counts().reset_index()
        seg_counts.columns = ['Segment', 'Count']

        fig = px.bar(seg_counts, x='Segment', y='Count', color='Segment',
                     title='Customer Segments Distribution')
        st.plotly_chart(fig, use_container_width=True)

        st.subheader("RFM Scatter Plot (Recency vs Monetary)")
        fig2 = px.scatter(rfm, x='Recency', y='Monetary', color='Segment',
                          hover_data=['Frequency'], title='Recency vs Monetary by Segment')
        st.plotly_chart(fig2, use_container_width=True)

        # --- DOWNLOAD RESULTS ---
        csv = rfm.reset_index().to_csv(index=False).encode('utf-8')
        st.download_button("📥 Download RFM Results", csv, "rfm_results.csv", "text/csv")

else:
    st.info("👆 Upload your dataset to start the RFM analysis.")