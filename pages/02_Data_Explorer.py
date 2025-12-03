import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# ------------------------------------------------------------
# PAGE CONFIG
# ------------------------------------------------------------
st.set_page_config(page_title="Game Sales Explorer", layout="wide")

# ------------------------------------------------------------
# ADVANCED STYLING
# ------------------------------------------------------------
st.markdown("""
<style>
body { background-color: #f5f5f5; color: #333; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; }
h1, h2, h3, h4 { color: #1f77b4; }
.stMetric { background-color: #ffffff !important; border-radius: 12px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
[data-testid="stSidebar"] { background-color: #e3f2fd; padding: 15px; border-radius: 10px; }
.css-1lcbmhc.e1fqkh3o3 { background-color: #ffffff !important; border-radius: 10px; padding: 5px; }
.stDataFrame div[data-testid="stVerticalBlock"] { background-color: #ffffff; border-radius: 10px; padding: 10px; box-shadow: 2px 2px 5px rgba(0,0,0,0.1); }
</style>
""", unsafe_allow_html=True)

# ------------------------------------------------------------
# SIDEBAR — FILE UPLOAD
# ------------------------------------------------------------
st.sidebar.header("📂 Upload Dataset")
file = st.sidebar.file_uploader("Upload Excel File", type=["xlsx", "xls"], key="file_uploader")

if file is None:
    st.title("🎮 Game Sales Dashboard")
    st.info("Upload a dataset to begin.")
    st.stop()

# ------------------------------------------------------------
# LOAD EXCEL USING PANDAS
# ------------------------------------------------------------
try:
    df = pd.read_excel(file)
except Exception as e:
    st.error(f"❌ Failed to load Excel file.\nError: {e}")
    st.stop()

# ------------------------------------------------------------
# CLEAN COLUMN NAMES AND SET REGIONS
# ------------------------------------------------------------
df.columns = df.columns.str.strip()
df.columns = df.columns.str.replace('\s+', ' ', regex=True)
df.columns = df.columns.str.title()

# Detect available region columns
all_possible_regions = ["North America", "Europe", "Japan", "Rest Of World", "Global"]
regions = [col for col in all_possible_regions if col in df.columns]

# ------------------------------------------------------------
# DATA CLEANING
# ------------------------------------------------------------
def clean_dataset(pdf):
    pdf.drop_duplicates(inplace=True)
    for col in ["Game", "Genre", "Publisher"]:
        if col in pdf.columns:
            pdf[col] = (
                pdf[col].astype(str)
                .str.strip()
                .str.replace("  ", " ")
                .str.title()
            )
    if "Year" in pdf.columns:
        pdf = pdf[pdf["Year"].between(1980, 2030)]
    for col in regions:
        pdf[col] = pd.to_numeric(pdf[col], errors='coerce').fillna(0).clip(lower=0)
    if "Global" in pdf.columns:
        pdf = pdf[pdf["Global"] > 0]
    return pdf

df = clean_dataset(df)

# ------------------------------------------------------------
# FILTERS
# ------------------------------------------------------------
st.title("🎮 Video Game Sales Explorer")
col1, col2, col3, col4 = st.columns(4)

with col1:
    genres = sorted(df["Genre"].unique())
    genre_options = ["All"] + genres

    selected_genres = st.multiselect(
        "Genre",
        genre_options,
        default=["All"],   # Default selects ALL
        key="genre_selectbox"
    )

# Handle "All" selection
if "All" in selected_genres:
    selected_genres = genres


with col2:
    publishers = sorted(df["Publisher"].unique())
    publisher_options = ["All"] + publishers

    selected_publishers = st.multiselect(
        "Publisher",
        publisher_options,
        default=["All"],
        key="publisher_multiselect"
    )

# Handle "All" selection
if "All" in selected_publishers:
    selected_publishers = publishers


with col3:
    year_min, year_max = int(df["Year"].min()), int(df["Year"].max())
    year_range = st.slider("Year Range", year_min, year_max, (year_min, year_max), key="year_slider")

with col4:
    default_index = regions.index("Global") if "Global" in regions else 0
    selected_region = st.selectbox("Region Focus", regions, index=default_index, key="region_selectbox")

# Apply filters
filtered = df.copy()
filtered = filtered[filtered["Year"].between(year_range[0], year_range[1])]
if selected_genres:
    filtered = filtered[filtered["Genre"].isin(selected_genres)]
if selected_publishers:
    filtered = filtered[filtered["Publisher"].isin(selected_publishers)]


# ------------------------------------------------------------
# KPIs
# ------------------------------------------------------------
st.markdown("## 📌 Key Performance Indicators")
k1, k2, k3, k4 = st.columns(4)
k1.metric(f"Total Sales in Millions ({selected_region})", f"{filtered[selected_region].sum():,.2f}")
k2.metric(f"Avg Sales/Game in Millions ({selected_region})", f"{filtered[selected_region].mean():.2f}")
k3.metric("Games Released", len(filtered))
k4.metric("Active Publishers", filtered["Publisher"].nunique())
st.markdown("---")

# ------------------------------------------------------------
# VISUAL ANALYSIS
# ------------------------------------------------------------
tab1, tab2 = st.tabs(["📊 Visual Analysis", "📄 Raw Data"])

with tab1:
    # Genre distribution
    st.subheader(f"🎭 Genre Distribution ({selected_region})")
    genre_counts = filtered.groupby("Genre")[selected_region].sum().reset_index()
    fig1 = px.pie(genre_counts, values=selected_region, names="Genre")
    st.plotly_chart(fig1, use_container_width=True)
    st.markdown("---")

    # Top publishers
    st.subheader(f"🏆 Top Publishers by {selected_region} Sales")
    pub_sales = filtered.groupby("Publisher")[selected_region].sum().nlargest(10).reset_index()
    fig2 = px.bar(pub_sales, x=selected_region, y="Publisher", orientation="h")
    st.plotly_chart(fig2, use_container_width=True)
    st.markdown("---")

    # NA vs EU / Histogram for other regions
    if selected_region in ["North America", "Europe"]:
        st.subheader("🌎 North America vs Europe Sales")
        fig3 = px.scatter(filtered, x="North America", y="Europe", color="Genre",
                          size=selected_region, hover_data=["Game"])
    else:
        st.subheader(f"🌎 {selected_region} Sales Distribution by Genre")
        fig3 = px.histogram(filtered, x="Genre", y=selected_region, color="Genre")
    st.plotly_chart(fig3, use_container_width=True)
    st.markdown("---")

    # Market share trend
    st.subheader(f"📈 Market Share (Top 5 Genres) - {selected_region}")
    top_genres = filtered.groupby("Genre")[selected_region].sum().nlargest(5).index
    trend = filtered[filtered["Genre"].isin(top_genres)]
    grouped = trend.groupby(["Year", "Genre"])[selected_region].sum().reset_index()
    fig4 = alt.Chart(grouped).mark_area().encode(
        x="Year:O",
        y=alt.Y(f"{selected_region}:Q", stack="normalize"),
        color="Genre:N"
    )
    st.altair_chart(fig4, use_container_width=True)
    st.markdown("---")

    # Box plot
    st.subheader(f"📦 Sales Distribution by Genre ({selected_region})")
    fig5 = px.box(filtered, x="Genre", y=selected_region, points="all")
    st.plotly_chart(fig5, use_container_width=True)

with tab2:
    st.subheader("📄 Raw Data")
    st.dataframe(filtered, use_container_width=True)
