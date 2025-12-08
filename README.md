🎬 StreamFlix Advisor: Subscription Recommendation Dashboard
The StreamFlix Advisor is a data-driven application built using Streamlit that helps users decide which streaming platform (Netflix or Amazon Prime Video) is the best value based on their preferred content genres, quality score (IMDb), content rating, and budget.

✨ Features
Personalized Recommendation: Receive a specific platform recommendation based on user-defined criteria (Genre, Rating, IMDb score, and Budget).

Dynamic Filtering: The recommendation engine filters content based on subscription price ranges to ensure budget suitability.

Data Overview (EDA): The Overview page provides visualizations for platform content distribution (Netflix vs. Amazon) and the top 5 most frequent content genres.

Custom Dark Theme: Features a modern, custom dark-mode UI with a prominent blue/purple accent, designed for clarity and aesthetic appeal.

📁 Project Structure
This project uses Streamlit's multi-page feature for clean organization:

streamlit-app-template/
├── app.py                  # Main page (Home) and Recommendation Engine
├── pages/
│   ├── 01_Compare.py       # (Placeholder) For future comparison logic
│   ├── 02_Overview.py      # Data analysis, Top Genres, Platform Ratio charts
│   └── 03_About.py         # (Placeholder) Information about the project/data
├── .streamlit/
│   ├── config.toml         # Streamlit configuration for dark theme and colors
│   └── style.css           # Custom CSS for the unique dark theme and sidebar design
├── data/
│   └── Netflix_and_PrimeVideo.csv # The dataset used for analysis
└── requirements.txt        # Python dependencies
⚙️ Setup and Installation
Follow these steps to get a copy of the project running on your local machine.

Prerequisites
You need Python 3.8+ installed on your system.

1. Clone the Repository
Bash

git clone [YOUR_REPO_URL]
cd streamlit-app-template
2. Prepare the Data
Ensure your primary data file is correctly named and placed:

File Name: Netflix_and_PrimeVideo.csv

Location: data/ directory

The required columns in this CSV file are: Title, Year, Rating, IMDb, Genre, and Platform.

3. Install Dependencies
Install all necessary Python libraries using the requirements.txt file:

Bash

pip install -r requirements.txt
(Note: The primary libraries are streamlit, pandas, and altair.)

4. Run the Application
Launch the Streamlit application from your terminal:

Bash

streamlit run app.py
The application will automatically open in your default web browser (usually at http://localhost:8501).

🖥️ Usage
Home Page (app.py):

Navigate to the sidebar.

Select your preferences (Genre, IMDb Score, Budget).

Click "Get Recommendation" to see which platform offers the most titles matching your criteria within your budget.

Overview Page (02_Overview.py):

View descriptive analytics on the dataset, including bar charts for top genres and a donut chart for platform content ratio.

🤝 Contribution
Feel free to submit issues or pull requests if you have suggestions for new features, bug fixes, or improvements to the data analysis or UI.

📄 License
This project is licensed under the MIT License - see the LICENSE.md file (if applicable) for details.