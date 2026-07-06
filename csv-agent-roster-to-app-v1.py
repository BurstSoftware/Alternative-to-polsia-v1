import streamlit as st
import pandas as pd

# 1. Configure the page settings
st.set_page_config(page_title="AI Agents Roster", layout="wide")

st.title("Top 100 Autonomous AI Agents")
st.write("This dashboard reads the agent roster directly from the GitHub repository.")

# 2. Define the URL
# IMPORTANT: Convert the standard GitHub URL to the "raw.githubusercontent.com" version
CSV_URL = "https://raw.githubusercontent.com/BurstSoftware/Alternative-to-polsia-v1/main/Top-100-ai-agents-roster.csv"

# 3. Create a cached data loading function
# The @st.cache_data decorator prevents Streamlit from re-downloading the CSV every time you interact with the app
@st.cache_data
def load_data(url):
    try:
        # Read the CSV directly from the URL into a pandas DataFrame
        df = pd.read_csv(url)
        return df
    except Exception as e:
        st.error(f"Error loading the CSV file: {e}")
        return pd.DataFrame()

# 4. Load and display the data
df = load_data(CSV_URL)

if not df.empty:
    st.write(f"**Total rows loaded:** {len(df)}")
    
    # Display the data as an interactive table
    # use_container_width=True ensures the table stretches to fit the screen
    st.dataframe(df, use_container_width=True)
else:
    st.warning("No data found or the file is empty.")
