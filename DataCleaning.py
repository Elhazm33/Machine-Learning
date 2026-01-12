# Import required libraries
import streamlit as st
import pandas as pd
import numpy as np
import io

# Configure the Streamlit page
st.set_page_config(page_title='Data Cleaning App', page_icon='🧼', layout='wide')

# Page title and description
st.title('🧼 Data Cleaning App 🧼 ')
st.write("Upload your dataset and clean it using the tools below.")

# File uploader section
uploaded_file = st.file_uploader('Upload your file ⬇', type=['csv','xlsx','xlsm','xlsb'])

if uploaded_file:
    # Initialize session state to persist data through interactions
    if 'original_df' not in st.session_state:
        try:
            # Read CSV files with bool column handling
            if uploaded_file.name.endswith('.csv'):
                data = pd.read_csv(uploaded_file)
                bool_cols = data.select_dtypes(include=['bool']).columns
                data[bool_cols] = data[bool_cols].astype('str')
                st.session_state.df = data
                st.session_state.original_df = data.copy()
            # Read Excel files with bool column handling
            else:
                data = pd.read_excel(uploaded_file)
                bool_cols = data.select_dtypes(include=['bool']).columns
                data[bool_cols] = data[bool_cols].astype('str')
                st.session_state.df = data
                st.session_state.original_df = data.copy()
            
            st.success(f"✅ File loaded successfully!")
            
        except Exception as e:
            st.error(f'Error loading file: {str(e)}')
            st.stop()
    
    # Create working copies of the data
    df = st.session_state.df.copy()
    original_df = st.session_state.original_df.copy()

    # Display data health metrics
    st.write("### 📊 Data Health Summary")
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    
    total_missing = df.isnull().sum().sum()
    total_dupes = df.duplicated().sum()

    col_m1.metric("Total Rows", df.shape[0])
    col_m2.metric("Total Columns", df.shape[1])
    col_m3.metric("Missing Values", total_missing)
    col_m4.metric("Duplicate Records", total_dupes)

    # Show detailed missing values by column
    if total_missing > 0:
        with st.expander("📋 View Missing Values by Column"):
            missing_df = pd.DataFrame({
                'Column': df.columns,
                'Missing Values': df.isnull().sum().values,
                'Percentage': (df.isnull().sum() / len(df) * 100).round(2)
            })
            missing_df = missing_df[missing_df['Missing Values'] > 0]
            st.dataframe(missing_df.sort_values('Missing Values', ascending=False))

    st.write("---")
    
    # Data cleaning tools section
    st.write("### 🛠️ Data Cleaning Tools")
    col_btn1, col_btn2, col_btn3 = st.columns(3)

    # Tool 1: Remove all rows with missing values
    with col_btn1:
        st.subheader("Remove Missing Values")
        if st.button("Remove All Missing Rows"):
            st.session_state.df = df.dropna()
            st.success("Removed all rows with missing values!")
            st.rerun()

    # Tool 2: Fill missing values with statistical measures
    with col_btn2:
        st.subheader("Fill Missing Values")
        target_col = st.selectbox("Select Column", options=df.columns)
        strategy = st.radio("Fill Method", ["Mean", "Median", "Mode"])
        
        if st.button("Apply Fill Method"):
            # Validate column type for mean/median
            if strategy in ["Mean", "Median"] and not pd.api.types.is_numeric_dtype(df[target_col]):
                st.error(f"Cannot use {strategy} on text column '{target_col}'")
            else:
                # Calculate fill value based on selected method
                if strategy == "Mean":
                    fill_val = df[target_col].mean()
                elif strategy == "Median":
                    fill_val = df[target_col].median()
                else:
                    fill_val = df[target_col].mode()[0] if not df[target_col].mode().empty else np.nan
                
                # Apply the fill if valid
                if pd.isna(fill_val):
                    st.warning(f"Cannot calculate {strategy} for this column")
                else:
                    st.session_state.df[target_col] = df[target_col].fillna(fill_val)
                    st.success(f"Filled missing values with {strategy}")
                    st.rerun()

    # Tool 3: Remove duplicate rows
    with col_btn3:
        st.subheader("Remove Duplicates")
        if st.button("Remove All Duplicates"):
            st.session_state.df = df.drop_duplicates()
            st.success("Removed all duplicate rows!")
            st.rerun()

    # Additional cleaning options
    st.write("---")
    st.write("### 🔧 Additional Tools")
    
    col_opt1, col_opt2 = st.columns(2)
    
    # Option to drop specific columns
    with col_opt1:
        col_to_drop = st.selectbox("Select column to remove:", ['Select column...'] + df.columns.tolist())
        if col_to_drop != 'Select column...' and st.button("Remove Selected Column"):
            st.session_state.df = df.drop(columns=[col_to_drop])
            st.success(f"Removed '{col_to_drop}' column")
            st.rerun()
    
    # Option to standardize column names
    with col_opt2:
        if st.button("Standardize Column Names"):
            st.session_state.df.columns = [col.strip().lower().replace(' ', '_') for col in df.columns]
            st.success("Column names standardized!")
            st.rerun()

    # Preview cleaned data
    st.write("---")
    st.write("### 📄 Cleaned Data Preview")
    st.dataframe(st.session_state.df, use_container_width=True)

    # Download section
    st.write("### 📥 Download Cleaned File")
    
    # Use original filename as default
    default_name = uploaded_file.name.split('.')[0] + '_cleaned'
    file_name_input = st.text_input("Filename for download:", default_name)
    
    # Create download buttons in columns
    down_col1, down_col2, down_col3 = st.columns(3)
    
    # CSV download button
    with down_col1:
        csv_bytes = st.session_state.df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            label="Download CSV",
            data=csv_bytes,
            file_name=f"{file_name_input}.csv",
            mime="text/csv",
            use_container_width=True
        )

    # Excel download button
    with down_col2:
        try:
            output = io.BytesIO()
            with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                st.session_state.df.to_excel(writer, index=False, sheet_name='Cleaned_Data')
            
            st.download_button(
                label="Download Excel",
                data=output.getvalue(),
                file_name=f"{file_name_input}.xlsx",
                mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                use_container_width=True
            )
        except Exception as e:
            st.warning("Install xlsxwriter: pip install xlsxwriter")

    # Reset button
    with down_col3:
        if st.button("Reset to Original", use_container_width=True):
            st.session_state.df = original_df.copy()
            st.success("Data reset to original!")
            st.rerun()

# Show when no file is uploaded
else:
    st.info("👋 Upload a CSV or Excel file to begin cleaning.")
    
    # Sample data for testing
    if st.button("Try Sample Data"):
        sample_data = pd.DataFrame({
            'Name': ['John', 'Jane', np.nan, 'Bob', 'Alice', 'John'],
            'Age': [25, 30, np.nan, 35, 28, 25],
            'City': ['NYC', 'LA', 'Chicago', np.nan, 'NYC', 'NYC'],
            'Salary': [50000, 60000, 55000, 70000, np.nan, 50000],
            'Department': ['IT', 'HR', 'IT', 'Finance', 'HR', 'IT'],
            'Active': [True, False, True, np.nan, False, True]
        })
        
        # Convert bool columns to string for consistency
        bool_cols = sample_data.select_dtypes(include=['bool']).columns
        sample_data[bool_cols] = sample_data[bool_cols].astype('str')
        
        # Provide sample file download
        csv = sample_data.to_csv(index=False)
        st.download_button(
            label="Download Sample CSV",
            data=csv,
            file_name="sample_data.csv",
            mime="text/csv"
        )
        st.info("Download and upload the sample file to test the app.")
