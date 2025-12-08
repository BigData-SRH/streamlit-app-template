import streamlit as st
import pandas as pd
import altair as alt

# --- CONFIGURATION & DATA PATH ---
DATA_PATH = 'data/Netflix_and_PrimeVideo.csv'

# Set page configuration (Inherits theme from config.toml)
st.set_page_config(page_title="Overview", page_icon="📈", layout="wide")

# --- DATA LOADING FUNCTION (Reusing the corrected logic) ---
@st.cache_data
def load_data():
    """Loads and preprocesses the dataset based on provided column names."""
    try:
        df = pd.read_csv(DATA_PATH)
        
        # --- Column Normalization ---
        # Map your actual capitalized columns to the lowercase standardized names
        df = df.rename(columns={
            'Title': 'title',
            'Year': 'release_year',
            'Genre': 'genre',
            'Platform': 'platform',
            'IMDb': 'imdb_score', 
            'Rating': 'rating'      
        }, errors='ignore')
        
        # --- Data Cleaning ---
        if 'platform' in df.columns:
            df['platform'] = df['platform'].astype(str).str.strip()
            df['platform'] = df['platform'].replace({'Prime Video': 'Amazon', 'Netflix': 'Netflix'})
        
        if 'genre' in df.columns:
            df['genre'] = df['genre'].astype(str).str.strip()
        
        if 'imdb_score' in df.columns:
            df['imdb_score'] = pd.to_numeric(df['imdb_score'], errors='coerce')
        
        return df
    except FileNotFoundError:
        return pd.DataFrame()

# --- Load Data ---
df = load_data()

# --- Custom CSS Injector ---
def local_css(file_name):
    """Function to load the custom CSS file."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        pass 

# Inject the custom CSS for styling consistency
local_css(".streamlit/style.css")


# --- START OF PAGE CONTENT ---
st.markdown("# 📊 Content Overview and EDA")
st.markdown("A descriptive analysis of the streaming content dataset.")

required_cols = ['title', 'platform', 'genre', 'imdb_score']
if df.empty:
    st.warning("Cannot display analysis because the data could not be loaded.")
elif not all(col in df.columns for col in required_cols):
     st.error(
        f"Critical error: Missing one or more required columns ({', '.join(required_cols)}) "
        "even after normalization. Please check that 'Title', 'Platform', 'Genre', and 'IMDb' columns are present in your CSV."
    )
else:
    # Use the same two-column structure for the analysis sections
    col1, col2 = st.columns(2)
    
    # --- 1. Top 5 Genres Analysis (Bar Chart) ---
    with col1:
        st.subheader("🎬 Top 5 Content Genres")
        
        # Calculate top 5 genres
        genre_counts = df['genre'].value_counts().nlargest(5).reset_index()
        genre_counts.columns = ['Genre', 'Count']
        
        # Create Altair Bar Chart
        chart = alt.Chart(genre_counts).mark_bar().encode(
            x=alt.X('Count', title='Total Titles'),
            y=alt.Y('Genre', sort='-x', title=None),
            color=alt.value("#5C6BC0"), 
            tooltip=['Genre', 'Count']
        ).properties(
            title='Count of Top 5 Genres'
        ).interactive()
        
        st.altair_chart(chart, use_container_width=True)


    # --- 2. Netflix vs. Amazon Content Ratio (Donut Chart) ---
    with col2:
        st.subheader("🍿 Platform Content Distribution")
        
        platform_counts = df['platform'].value_counts().reset_index()
        platform_counts.columns = ['Platform', 'Count']
        
        # --- FIX: Explicitly define the color scheme ---
        color_scale = alt.Scale(domain=['Netflix', 'Amazon'],
                                range=['#E50914', '#FF9900']) # Netflix Red and Amazon Orange
        
        # Create Altair Donut Chart
        base = alt.Chart(platform_counts).encode(
            theta=alt.Theta("Count", stack=True)
        ).properties(
            title='Netflix vs. Amazon Content Ratio'
        )

        pie = base.mark_arc(outerRadius=120, innerRadius=80).encode(
            color=alt.Color("Platform", scale=color_scale),
            order=alt.Order("Count", sort="descending"),
            tooltip=["Platform", "Count"]
        )
        
        # Adding text labels outside the arc
        text = base.mark_text(radius=150).encode(
            text=alt.Text("Count", format=".0f"),
            order=alt.Order("Count", sort="descending"),
            color=alt.value("white")
        )
        
        # Combine the pie chart and text layers
        chart_final = pie # The text layer wasn't strictly necessary for a quick fix, 
                         # but we keep the robust pie chart with explicit colors.

        st.altair_chart(chart_final, use_container_width=True)

    st.markdown("---")


    # --- 3. Top 5 Best Movies (Table/List) ---
    st.subheader("🌟 Top 5 Highest Rated Titles (by IMDB Score)")
    
    top_titles = df.dropna(subset=['imdb_score', 'title', 'platform']).sort_values(
        by='imdb_score', ascending=False
    ).drop_duplicates(subset='title').head(5)

    display_data = top_titles[['title', 'platform', 'imdb_score', 'release_year']].copy()
    display_data.columns = ['Title', 'Platform', 'IMDB Score', 'Year']
    
    st.dataframe(display_data, use_container_width=True)
    
    # Stylized list
    for index, row in display_data.iterrows():
        st.markdown(
            f"""
            <div style='background-color: #373A47; padding: 10px; margin-bottom: 5px; border-radius: 5px;'>
                <span style='color: #5C6BC0; font-weight: bold;'>{round(row['IMDB Score'], 1)} IMDB</span> 
                &nbsp; | &nbsp; 
                <span style='color: white; font-weight: bold;'>{row['Title']}</span> 
                ({int(row['Year'])}) - {row['Platform']}
            </div>
            """, 
            unsafe_allow_html=True
        )