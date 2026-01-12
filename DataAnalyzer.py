# Import required libraries for data analysis and visualization
import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns 
import io

# Configure the Streamlit page
st.set_page_config(page_title='Data Science Analyzer', page_icon='🏛️', layout='wide')

# Page header
st.title('🏺 Analyze Your Data 🏺')
st.write('Upload your dataset to explore and visualize it interactively!')

# File upload section
uploaded_file = st.file_uploader('Upload a CSV or Excel File ⬇', type=['csv','xlsx','xlsm','xlsb'])

if uploaded_file is not None:
    try:
        # Read uploaded file with proper type handling
        if uploaded_file.name.endswith('.csv'):
            data = pd.read_csv(uploaded_file)
            # Convert boolean columns to string for better display
            bool_cols = data.select_dtypes(include=['bool']).columns
            data[bool_cols] = data[bool_cols].astype('str')
        else:
            data = pd.read_excel(uploaded_file)
            # Apply same boolean conversion for Excel files
            bool_cols = data.select_dtypes(include=['bool']).columns
            data[bool_cols] = data[bool_cols].astype('str')

        st.success("✅ File uploaded successfully!")

    except Exception as e:
        st.error(f'Error reading file: {str(e)}')
        st.stop()

    # Data preview section
    st.write('### Data Preview')
    st.dataframe(data.head())

    # Data health metrics
    st.write('### 🔎 Data Overview')
    col_m1, col_m2, col_m3, col_m4 = st.columns(4)
    col_m1.metric("Rows", data.shape[0])
    col_m2.metric("Columns", data.shape[1])
    col_m3.metric("Missing Values", data.isnull().sum().sum())
    col_m4.metric("Duplicates", data.duplicated().sum())

    # Detailed dataset information
    st.write('### 🗂️ Dataset Information')
    buffer = io.StringIO()
    data.info(buf=buffer)
    st.text(buffer.getvalue())

    # Statistical summary for non-numeric columns
    st.write('### 📊 Categorical Data Summary')
    non_numeric_cols = data.select_dtypes(include=['bool','object']).columns
    if not non_numeric_cols.empty:
        st.dataframe(data[non_numeric_cols].describe())
    else:
        st.info('No categorical columns found in this dataset.')

    # Visualization setup
    st.write('### 🖋️ Create Visualizations')
    columns = data.columns.tolist()
    
    # Column selection for plots
    col_sel1, col_sel2 = st.columns(2)
    with col_sel1:
        x_axis = st.selectbox('Select X-Axis Column', options=columns)
    with col_sel2:
        y_axis = st.selectbox('Select Y-Axis Column', options=columns)

    # Visualization type buttons
    col1, col2, col3, col4, col5 = st.columns(5)
    with col1: line_btn = st.button('Line Graph')
    with col2: scatter_btn = st.button('Scatter Graph')
    with col3: bar_btn = st.button('Bar Graph')
    with col4: heat_btn = st.button('Heatmap')
    with col5: pie_btn = st.button('Pie Chart')

    # Generate line graph
    if line_btn:
        try:
            st.write('### Line Graph')
            # Convert columns to numeric, handling errors
            x_data = pd.to_numeric(data[x_axis], errors='coerce')
            y_data = pd.to_numeric(data[y_axis], errors='coerce')
            
            # Remove rows with missing values
            clean_data = pd.DataFrame({x_axis: x_data, y_axis: y_data}).dropna()
            
            if len(clean_data) > 0:
                fig, ax = plt.subplots()
                ax.plot(clean_data[x_axis], clean_data[y_axis])
                ax.set_title(f'{x_axis} vs {y_axis}')
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                st.pyplot(fig)
            else:
                st.error("No valid numeric data for line plot.")
        except Exception as e:
            st.error(f"Could not generate line plot: {str(e)}")

    # Generate scatter plot
    if scatter_btn:
        try:
            st.write('### Scatter Plot')
            x_data = pd.to_numeric(data[x_axis], errors='coerce')
            y_data = pd.to_numeric(data[y_axis], errors='coerce')
            
            clean_data = pd.DataFrame({x_axis: x_data, y_axis: y_data}).dropna()
            
            if len(clean_data) > 0:
                fig, ax = plt.subplots()
                ax.scatter(clean_data[x_axis], clean_data[y_axis])
                ax.set_title(f'{x_axis} vs {y_axis}')
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                st.pyplot(fig)
            else:
                st.error("No valid numeric data for scatter plot.")
        except Exception as e:
            st.error(f"Could not generate scatter plot: {str(e)}")

    # Generate bar chart
    if bar_btn:
        try:
            st.write('### Bar Chart')
            y_data = pd.to_numeric(data[y_axis], errors='coerce')
            
            if not y_data.isnull().all():
                fig, ax = plt.subplots(figsize=(10, 6))
                
                # Limit display for columns with many unique values
                if data[x_axis].nunique() > 20:
                    st.warning(f"Showing first 20 of {data[x_axis].nunique()} categories")
                    unique_vals = data[x_axis].value_counts().head(20).index
                    filtered_data = data[data[x_axis].isin(unique_vals)]
                    ax.bar(filtered_data[x_axis].astype(str), 
                          pd.to_numeric(filtered_data[y_axis], errors='coerce'))
                    plt.xticks(rotation=45, ha='right')
                else:
                    ax.bar(data[x_axis].astype(str), y_data)
                
                ax.set_title(f'{x_axis} vs {y_axis}')
                ax.set_xlabel(x_axis)
                ax.set_ylabel(y_axis)
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.error(f"Column '{y_axis}' must contain numeric data.")
        except Exception as e:
            st.error(f"Could not generate bar chart: {str(e)}")

    # Generate pie chart
    if pie_btn:
        try:
            st.write('### Pie Chart')
            # Verify Y-axis is numeric
            if pd.api.types.is_numeric_dtype(data[y_axis]):
                # Limit to top 10 categories for readability
                if data[x_axis].nunique() > 10:
                    st.warning(f"Showing top 10 of {data[x_axis].nunique()} categories")
                    top_categories = data[x_axis].value_counts().head(10).index
                    filtered_data = data[data[x_axis].isin(top_categories)]
                    values = filtered_data.groupby(x_axis)[y_axis].sum()
                    labels = values.index
                else:
                    values = data.groupby(x_axis)[y_axis].sum()
                    labels = values.index
                
                fig, ax = plt.subplots()
                ax.pie(values, labels=labels, autopct='%1.1f%%', startangle=90)
                ax.axis('equal')
                ax.set_title(f'{y_axis} Distribution by {x_axis}')
                st.pyplot(fig)
            else:
                st.error(f"Y-axis column must be numeric for pie chart.")
        except Exception as e:
            st.error(f"Could not generate pie chart: {str(e)}")

    # Generate correlation heatmap
    if heat_btn:
        try:
            st.write('### Correlation Heatmap')
            # Select only numeric columns
            numeric_df = data.select_dtypes(include=[np.number])
            if not numeric_df.empty:
                # Warn if many columns
                if len(numeric_df.columns) > 15:
                    st.warning(f"Showing correlation for {len(numeric_df.columns)} numeric columns")
                
                fig, ax = plt.subplots(figsize=(12, 8))
                sns.heatmap(numeric_df.corr(), annot=True, cmap='coolwarm', ax=ax, 
                           fmt='.2f', linewidths=0.5, center=0)
                plt.title('Correlation Between Numeric Columns')
                plt.tight_layout()
                st.pyplot(fig)
            else:
                st.warning("No numeric columns available for correlation heatmap.")
        except Exception as e:
            st.error(f"Could not generate heatmap: {str(e)}")

# Display when no file is uploaded
else:
    st.info('Upload a CSV or Excel file to begin analysis.')