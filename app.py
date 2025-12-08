import streamlit as st
import pandas as pd

# Data path
# NOTE: Ensure 'data/Netflix_and_PrimeVideo.csv' exists or update the path
DATA_PATH = 'data/Netflix_and_PrimeVideo.csv'

# --- PLATFORM SUBSCRIPTION PRICES ---
subscription_prices = {
    "Netflix": {"min": 4.99, "max": 19.99},
    "Amazon": {"min": 8.99, "max": 19.99}  # Updated range
}

# --- LOAD DATA ---
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(DATA_PATH)
        
        # Normalize platform
        if 'Platform' in df.columns:
            df = df.rename(columns={'Platform': 'platform'})
        if 'platform' in df.columns:
            df['platform'] = df['platform'].astype(str).str.strip()
            # Normalize names to match subscription_prices
            df['platform'] = df['platform'].replace({'Prime Video': 'Amazon', 'Netflix': 'Netflix'})
        
        # Normalize genre
        if 'Genre' in df.columns:
            df = df.rename(columns={'Genre': 'genre'})
        if 'genre' in df.columns:
            df['genre'] = df['genre'].astype(str).str.strip()
        
        # Normalize title
        if 'Title' in df.columns:
            df = df.rename(columns={'Title': 'title'})
        
        # Normalize release year
        if 'Year' in df.columns:
            df = df.rename(columns={'Year': 'release_year'})
        
        # Normalize rating and IMDB
        if 'Rating' in df.columns:
            df['Rating'] = df['Rating'].astype(str).str.strip()
        if 'IMDB' in df.columns:
            df['IMDB'] = pd.to_numeric(df['IMDB'], errors='coerce')
        
        # Normalize Price if exists
        if 'Price' in df.columns:
            df['Price'] = pd.to_numeric(df['Price'], errors='coerce')
        
        return df
    except FileNotFoundError:
        st.error(f"File '{DATA_PATH}' not found. Please ensure the data file is in the correct location.")
        return pd.DataFrame()

st.set_page_config(page_title="StreamFlix Advisor", page_icon="🎬", layout="wide")

# Load data
df = load_data()


# =============================================================================
# --- START OF UI & STYLING CODE --- (Added to your existing script)
# =============================================================================

# --- 1. Custom CSS Injector ---
def local_css(file_name):
    """Function to load the custom CSS file."""
    try:
        with open(file_name) as f:
            st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)
    except FileNotFoundError:
        st.warning(f"Custom CSS file '{file_name}' not found. Please ensure it exists for the custom design.")

# Inject the custom CSS
local_css(".streamlit/style.css")

# --- 2. Sidebar Customization (To match the image's structure) ---
with st.sidebar:
    # Use h2 to match the size/weight of the title in the image
    st.markdown("## StreamAdvisor") 
    st.markdown("Find Your Match")
    st.markdown("---") 
    # The actual navigation links will be generated automatically by Streamlit due to the 'pages/' folder

# --- 3. Main Header ---
st.markdown("## 🍿 StreamFlix Advisor")
st.markdown("Find your perfect streaming platform match based on your viewing preferences.")
st.markdown("---")


if df.empty:
    st.error("Cannot proceed without data.")
else:
    # --- 4. Two Column Layout (3:2 ratio to match the image) ---
    col1_main, col2_main = st.columns([3, 2])
    
    # Initialize session state for recommendation trigger
    if 'run_recommendation' not in st.session_state:
        st.session_state['run_recommendation'] = False

    # =================================================================
    # LEFT COLUMN (col1_main): USER PREFERENCES & RECOMMENDATION LOGIC
    # =================================================================
    with col1_main:
        st.subheader("👤 Personalized Subscription Recommendation")
        st.markdown("---")
        
        # --- Content Type/Genre Selection ---
        st.markdown("#### Content Type")
        # Since Streamlit doesn't have native multi-select buttons, we'll use an invisible multiselect 
        # for filtering but rely on the custom CSS for visual style.
        content_type_options = ['Movies', 'TV Shows', 'Documentaries', 'Saved-up List'] 
        selected_content_types = st.multiselect(
            "Select Content Types (Hidden)",
            content_type_options,
            default=['Movies'],
            label_visibility="collapsed",
            key="content_type_select"
        )
        
        st.markdown("#### Favorite genres (select multiple)")
        genre_options = sorted(df['genre'].dropna().unique().tolist()) if 'genre' in df.columns else []
        selected_genres = st.multiselect(
            "Select Genre (Hidden)",
            genre_options,
            default=genre_options[:3] if len(genre_options) >= 3 else None,
            label_visibility="collapsed",
            key="genre_select"
        )
        
        # --- RATING & IMDB ---
        rating_options = df['Rating'].dropna().unique().tolist() if 'Rating' in df.columns else []
        selected_rating = st.selectbox(
            "Select Rating", 
            ['Family-friendly content'] + rating_options, # Adding a custom label
            index=0,
            key="rating_select"
        ) if rating_options else None
        
        selected_imdb = st.slider(
            "Minimum IMDB Score", 
            0.0, 10.0, 7.5, 0.1, 
            key="imdb_slider"
        ) if 'IMDB' in df.columns else None
        
        # --- PRICE SELECTION (Radio buttons styled as buttons) ---
        st.markdown("---")
        st.markdown("#### Select: budget preference")
        price_options = ["Under 10€", "10-15€", "15+€"]
        selected_price = st.radio(
            "Select Price Range", 
            price_options, 
            horizontal=True, 
            index=0,
            key="price_radio",
            label_visibility="collapsed"
        )
        
        # --- Action Buttons ---
        col_btn1, col_btn2 = st.columns([2, 1])
        with col_btn1:
            if st.button("Get Recommendation", use_container_width=True, type="primary"):
                st.session_state['run_recommendation'] = True
        with col_btn2:
            if st.button("Reset", use_container_width=True):
                st.session_state['run_recommendation'] = False
                # Re-run the script to reset all widgets
                st.rerun() 
        
        # --- Filtering Logic ---
        filtered_df = df.copy()
        
        # 1. Genre filter
        if selected_genres and 'genre' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['genre'].isin(selected_genres)]
        
        # 2. Rating filter
        if selected_rating and selected_rating != 'Family-friendly content' and 'Rating' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['Rating'] == selected_rating]
        
        # 3. IMDB filter
        if selected_imdb is not None and 'IMDB' in filtered_df.columns:
            filtered_df = filtered_df[filtered_df['IMDB'] >= selected_imdb]
        
        # 4. Price filter
        eligible_platforms = []
        for platform, price in subscription_prices.items():
            min_price = price["min"]
            max_price = price["max"]
            if selected_price == "Under 10€" and min_price <= 10:
                eligible_platforms.append(platform)
            elif selected_price == "10-15€" and (min_price < 15 and max_price >= 10):
                eligible_platforms.append(platform)
            elif selected_price == "15+€" and max_price > 15:
                eligible_platforms.append(platform)
        
        filtered_df = filtered_df[filtered_df['platform'].isin(eligible_platforms)]

    
    # =================================================================
    # RIGHT COLUMN (col2_main): RECOMMENDED PLATFORM CARD & METRICS
    # =================================================================
    with col2_main:
        
        # Mimic the 'Selected Preferences' header
        st.markdown("#### Selected Preferences")
        
        # Placeholder for data info (like the reference image)
        st.markdown(f"""
            <div style='background-color: #373A47; padding: 15px; border-radius: 8px;'>
                <p style='color: white; font-weight: bold; margin: 0;'>Data Source:</p>
                <p style='color: #A0C4FF; font-size: 0.9rem; margin: 0;'>Netflix_and_PrimeVideo.csv</p>
                <p style='color: #D3D3D3; font-size: 0.8rem; margin-top: 5px;'>Titles analyzed: {len(df)}</p>
            </div>
            """, unsafe_allow_html=True)
        
        st.markdown("---")

        if st.session_state.get('run_recommendation', False):
            if not filtered_df.empty:
                platform_counts = filtered_df['platform'].value_counts()
                recommended_platform = platform_counts.idxmax()
                num_titles = platform_counts.max()
                
                # --- Custom Recommendation Card (To mimic the red box) ---
                st.markdown(
                    f"""
                    <div style='background-color: #373A47; padding: 20px; border-radius: 10px; border-left: 5px solid #E57373; box-shadow: 0 4px 8px 0 rgba(0,0,0,0.2);'>
                        <p style='color: #E57373; font-weight: bold; margin-bottom: 0;'>🔥 Our Top Pick For You</p>
                        <h3 style='color: white; margin-top: 5px;'>{recommended_platform}</h3>
                        <p style='color: #D3D3D3; margin-top: 10px; font-size: 0.9rem;'>
                        💰 **Best Price:** Starting at **${subscription_prices.get(recommended_platform, {}).get("min", "N/A")}**/month
                        </p>
                        <p style='color: #D3D3D3; margin-top: 5px; font-size: 0.9rem;'>
                        🎬 **Matching Titles:** **{num_titles}** titles match your criteria.
                        </p>
                    </div>
                    """, 
                    unsafe_allow_html=True
                )
                
                # --- Match Scores Bar (Mimics the bottom section of the image) ---
                st.markdown("---")
                st.subheader("Your Match Scores")
                
                total_matches = platform_counts.sum()
                for platform, count in platform_counts.items():
                    score = (count / total_matches) * 100 if total_matches > 0 else 0
                    st.markdown(f"**{platform}** ({count} titles)")
                    st.progress(score / 100) # Streamlit progress bar needs value between 0.0 and 1.0

            else:
                st.warning("No platforms available for your selected criteria and budget.")
                
        else:
            st.info("Click **'Get Recommendation'** to analyze your choices and see the best match!")