import streamlit as st
import pandas as pd
import plotly.express as px
from streamlit_folium import st_folium
import folium
from folium import FeatureGroup
from streamlit.components.v1 import html
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np

# Load data
def load_data():
    file_path = "data.xlsx"  # Relative path to your Excel file
    df = pd.read_excel(file_path)  # Adjust for your file format
    return df

# Preprocess data
def preprocess_data(df):
    # Ensure correct data types
    df['Latitude'] = df['Latitude'].astype(float)
    df['Longitude'] = df['Longitude'].astype(float)
    df['Income 2023'] = pd.to_numeric(df['Income 2023'], errors='coerce')
    df['Income 2024'] = pd.to_numeric(df['Income 2024'], errors='coerce')
    df['Income 2022'] = pd.to_numeric(df['Income 2022'], errors='coerce')
    df['The year founded'] = pd.to_numeric(df['The year founded'], errors='coerce')

    df['Facebook followers'] = pd.to_numeric(df['Facebook followers'], errors='coerce').fillna(0).astype(int)
    df['Instagram followers'] = pd.to_numeric(df['Instagram followers'], errors='coerce').fillna(0).astype(int)

    return df

# Create map with layers
FIXED_HUB_COLORS = {
    "Al Haouz": "#FF0000",  # Red
    "Azilal": "#00FF00",  # Green
    "Idaoutanan": "#0000FF",  # Blue
    "Demnate": "#FFFF00",  # Yellow
    "Imintanout": "#FF00FF",  # Magenta
}

def create_map(data):
    data = data.dropna(subset=['Latitude', 'Longitude'])
    if data.empty:
        return folium.Map(location=[31.5, -7.5], zoom_start=6, control_scale=True)
    map_center = [data['Latitude'].mean(), data['Longitude'].mean()]
    m = folium.Map(location=map_center, zoom_start=7, control_scale=True)

    for hub, color in FIXED_HUB_COLORS.items():
        hub_layer = folium.FeatureGroup(name=f"Hub: {hub}")
        hub_data = data[data['Hub'] == hub]

        for _, row in hub_data.iterrows():
            popup = folium.Popup(f"""
                <b>Cooperative:</b> {row['Cooperative Name']}<br>
                <b>Hub:</b> {row['Hub']}<br>
                <b>Sector:</b> {row['Activity']}<br>
                <b>Members:</b> {row['N of Members']}
            """, max_width=300)

            folium.CircleMarker(
                location=[row['Latitude'], row['Longitude']],
                radius=5,
                color=color,
                fill=True,
                fill_color=color,
                fill_opacity=0.8,
                popup=popup
            ).add_to(hub_layer)

        hub_layer.add_to(m)

    folium.LayerControl(position="topleft", collapsed=True).add_to(m)
    return m

# Main Streamlit app
def main():
    st.markdown(
        """
        <style>
        .main-title {
            font-size: 32px;
            font-weight: bold;
            color: #2E8B57; /* Green */
            margin-bottom: 20px;
        }
        .section-title {
            font-size: 24px;
            font-weight: bold;
            color: #4682B4; /* Blue */
            margin-bottom: 10px;
        }
        .description {
            font-size: 16px;
            color: #696969; /* Gray */
            line-height: 1.6;
        }
        .map-container, .map-section {
            padding: 0 !important;
            margin: 0 !important;
        }
        .map-section {
            margin-bottom: -20px; /* Adjust this to reduce space below the map */
        }
        </style>
        """,
        unsafe_allow_html=True
    )
    
    st.markdown('<div class="main-title">Sustainable Livelihoods Program Dashboard</div>', unsafe_allow_html=True)

    # Load and preprocess data
    data = load_data()
    data = preprocess_data(data)

    # Sidebar Filters
    st.sidebar.title("Filter by Hub")
    all_hubs = sorted(data['Hub'].dropna().unique())
    select_all = st.sidebar.checkbox("Select All Hubs", value=True)

    # Initialize selected hubs based on the checkbox
    if select_all:
        hubs = all_hubs  # Select all hubs by default
        cooperative_data = data
    else:
        hubs = st.sidebar.multiselect("Select Hubs", options=all_hubs, default=all_hubs)
        cooperative_data = data[data['Hub'].isin(hubs)]  # Apply filtering based on selected hubs

   # Filter the dataset based on the selected hubs
    filtered_data = data[data['Hub'].isin(hubs)]
    # Sidebar Filters
   
   

# Key Insights
    st.markdown('<div class="section-title">Key Insights</div>', unsafe_allow_html=True)
    col1, col2 = st.columns(2)
    with col1:
        st.metric("Total Cooperatives - All Cohorts", len(data))
        total_members = data['N of Members'].sum()
        st.metric("Total Members - All Cohorts", f"{total_members:,}")
    with col2:
        total_facebook_followers = data['Facebook followers'].sum()
        total_instagram_followers = data['Instagram followers'].sum()
        st.metric("Social Media Reach - Cohorts 1,2,3", f"{total_facebook_followers + total_instagram_followers:,}")

    st.markdown("<br><br>", unsafe_allow_html=True)
    
# Map Visualization Section
    with st.container():
        st.markdown('<div class="section-title map-section">Geographical Reach</div>', unsafe_allow_html=True)
        
        if filtered_data.empty:
            st.write("No data available for the selected hubs.")
        else:
            col1, col2 = st.columns([4, 1])
            with col1:
               
                    st.markdown('<div class="map-container">', unsafe_allow_html=True)
                    st_folium(create_map(filtered_data), width="100%", height=500)
                    st.markdown('</div>', unsafe_allow_html=True)
            with col2:
               
                    st.markdown("### Legend")
                    for hub, color in FIXED_HUB_COLORS.items():
                        st.markdown(
                            f"""
                            <div style="display: flex; align-items: center; margin-bottom: 8px;">
                                <div style="width: 20px; height: 20px; background-color: {color}; margin-right: 8px;"></div>
                                <span>{hub}</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
  
                    

# Sector Distribution Section
    st.markdown('<div class="section-title chart-container">Sector Distribution</div>', unsafe_allow_html=True)
    st.markdown("""
    This chart illustrates the distribution of cooperatives across different sectors, focusing on cohorts 1 to 3.

    - **Sector Specialization**: Cooperatives that focus on specific products like argan oil or honey.  
    - **Diverse Agricultural Products**: Cooperatives combining multiple products, catering to broader markets.
    """)

    if not filtered_data.empty:
        with st.container():
            pie_chart_data = filtered_data.groupby(['Activity']).size().reset_index(name='Count')
            pie_fig = px.pie(
                pie_chart_data,
                values='Count',
                names='Activity',
                title="Sector Distribution by Selected Hubs",
                color_discrete_sequence=px.colors.qualitative.Safe
            )
            st.plotly_chart(pie_fig, use_container_width=True)

    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown('<div class="section-title">Founding Years of Partner Cooperatives</div>', unsafe_allow_html=True)
    
    if not filtered_data.empty:
        with st.container():
            # Set style
            sns.set_style("whitegrid", {"axes.grid": False})

            # Plot the distribution of founding years
            fig, ax = plt.subplots()
            filtered_data["The year founded"].hist(
                bins=20, ax=ax, color="skyblue", edgecolor="black"
            )
            
            # Get sorted founding year counts
            founding_year_counts = filtered_data["The year founded"].value_counts().sort_index()

            # Ensure x-axis displays integers and is formatted properly
            ax.set_xticks(founding_year_counts.index.astype(int))  # Convert to integers
            ax.set_xticklabels(
                founding_year_counts.index.astype(int), rotation=45, ha="right", fontsize=10
            )

            # Set titles and labels
           
            ax.set_xlabel("Founding Year", fontsize=12)
            ax.set_ylabel("Number of Cooperatives", fontsize=12)

            # Display the plot
            st.pyplot(fig)


    
    st.markdown("<br><br>", unsafe_allow_html=True)
    st.markdown("<br><br>", unsafe_allow_html=True)
   
    # Case Studies Section - increase
    st.markdown('<div class="section-title">Case studies - Revenue Increase</div>', unsafe_allow_html=True)
   
    

    # Filter data for the specified cooperatives
    selected_coops = ["Atkiss", "top bio",  "Tighanimin", "Amagor's amaguour women",'Tagmat aziar ','Tizgui ','Tazwit Ntighanimin','Boukhedou Akermoud','Ritaj Ntighanimin ']
    case_study_data = data[data["Cooperative Name"].isin(selected_coops)]

        # Calculate income increases
    case_study_data["Increase 2023 (%)"] = (
        (case_study_data["Income 2023"] - case_study_data["Income 2022"])
        / case_study_data["Income 2022"]
        * 100
    ).fillna(0)
    case_study_data["Increase 2024 (%)"] = (
        (case_study_data["Income 2024"] - case_study_data["Income 2023"])
        / case_study_data["Income 2023"]
        * 100
    ).fillna(0)

    # Plot income evolution
    # Plot income evolution
    with st.container():
        fig, ax = plt.subplots(figsize=(10, 8))

        # Define manual annotation offsets for specific cooperatives and years
        manual_offsets = {
            ("Boukhedou Akermoud", "2023"): (20, -10),  # Custom offset for Boukhedou Akermoud in 2023
            ("Boukhedou Akermoud" , "2024"): (-20, 20),
            ("Amagor's amaguour women" , "2024"): (5,-15)
            # Add more as needed
        }

        for _, row in case_study_data.iterrows():
            coop_name = row["Cooperative Name"]
            income_2022 = row["Income 2022"]
            income_2023 = row["Income 2023"]
            income_2024 = row["Income 2024"]

            # Income values over years
            years = ["2022", "2023", "2024"]
            incomes = [income_2022, income_2023, income_2024]

            # Filter out missing data
            valid_years = [year for year, inc in zip(years, incomes) if pd.notna(inc)]
            valid_incomes = [inc for inc in incomes if pd.notna(inc)]

            # Plot the line
            ax.plot(valid_years, valid_incomes, marker="o", label=coop_name)

            # Add annotations for percentage increase
            for year, income, percentage_key in [
                ("2023", income_2023, "Increase 2023 (%)"),
                ("2024", income_2024, "Increase 2024 (%)"),
            ]:
                if pd.notna(row[percentage_key]) and row[percentage_key] > 0:
                    # Check for manual offset, otherwise use default
                    xytext_offset = manual_offsets.get((coop_name, year), (-20, 10))

                    ax.annotate(
                        f"{row[percentage_key]:.1f}%",
                        xy=(year, income),
                        xytext=xytext_offset,  # Use manual or default offset
                        textcoords="offset points",
                        fontsize=9,
                        color="green",
                        bbox=dict(boxstyle="round,pad=0.3", edgecolor="green", facecolor="white"),
                        arrowprops=dict(arrowstyle="->", color="green", lw=0.5),
                    )

        # Finalizing the plot
        ax.set_title("Turnover Evolution of Selected Cooperatives (2022-2024)", fontsize=14, pad=20)
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Turnover", fontsize=12)
        ax.legend(title="Cooperative Name", loc="upper left", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)

        # Adjust layout for better spacing
        fig.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(fig)





    

    # Case Studies Section - Decrease
    st.markdown('<div class="section-title">Case studies - Revenue Decrease</div>', unsafe_allow_html=True)

    # Filter data for the specified cooperatives
    selected_coops_decrease = ["Tamo", "Ritaj Ouzoud", "Imin Tadart", "Al Oulfa", "Tifawine Angale"]
    case_study_data_decrease = data[data["Cooperative Name"].isin(selected_coops_decrease)]

    # Calculate income decreases
    case_study_data_decrease["Decrease 2023 (%)"] = (
        (case_study_data_decrease["Income 2023"] - case_study_data_decrease["Income 2022"])
        / case_study_data_decrease["Income 2022"]
        * 100
    ).fillna(0)
    case_study_data_decrease["Decrease 2024 (%)"] = (
        (case_study_data_decrease["Income 2024"] - case_study_data_decrease["Income 2023"])
        / case_study_data_decrease["Income 2023"]
        * 100
    ).fillna(0)

   


    # Plot income evolution for Revenue Decrease
    # Plot income evolution for Revenue Decrease
# Plot income evolution for Revenue Decrease
    manual_offsets = {
        ("Tamo", 2024): (0, 15),  # Offset for Tamo in 2023
        ("Imin Tadart", 2024): (10, -20),  # Offset for Imin Tadart in 2024
        ("Ritaj Ouzoud", 2024): (-30, -20),  # Offset for Ritaj Ouzoud in 2023
        ("Al Oulfa", 2024): (-55, 5) 
        # Add more entries as needed
    }
    with st.container():
        fig, ax = plt.subplots(figsize=(10, 8))

        for _, row in case_study_data_decrease.iterrows():
            coop_name = row["Cooperative Name"]
            income_2022 = row.get("Income 2022", None)
            income_2023 = row.get("Income 2023", None)
            income_2024 = row.get("Income 2024", None)

            # Define years and incomes
            years = [2022, 2023, 2024]
            incomes = [income_2022, income_2023, income_2024]

            # Filter out missing data
            valid_data = [(year, inc) for year, inc in zip(years, incomes) if pd.notna(inc)]
            if valid_data:
                valid_years, valid_incomes = zip(*valid_data)

                # Plot the line
                ax.plot(valid_years, valid_incomes, marker="o", label=coop_name)

                # Add annotations for percentage changes
                for i in range(1, len(valid_years)):
                    year_prev = valid_years[i - 1]
                    year_curr = valid_years[i]
                    income_prev = valid_incomes[i - 1]
                    income_curr = valid_incomes[i]

                    # Calculate percentage change
                    if income_prev > 0:
                        percent_change = ((income_curr - income_prev) / income_prev) * 100

                        # Check for manual offset, otherwise use default
                        xytext_offset = manual_offsets.get((coop_name, year_curr), (5, 10))  # Default offset (5, 10)

                        # Annotate percentage change
                        ax.annotate(
                            f"{percent_change:.1f}%",
                            xy=(year_curr, income_curr),
                            xytext=xytext_offset,  # Use manual or default offset
                            textcoords="offset points",
                            fontsize=9,
                            color="red" if percent_change < 0 else "green",  # Red for decrease, green for increase
                            bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white"),
                            arrowprops=dict(arrowstyle="->", color="gray", lw=0.5)
                        )
                        
        

                        # Annotate percentage change
                        ax.annotate(
                            f"{percent_change:.1f}%",
                            xy=(year_curr, income_curr),
                            xytext=xytext_offset,  # Use dynamic offset
                            textcoords="offset points",
                            fontsize=9,
                            color="red" if percent_change < 0 else "green",  # Red for decrease, green for increase
                            bbox=dict(boxstyle="round,pad=0.3", edgecolor="gray", facecolor="white"),
                            arrowprops=dict(arrowstyle="->", color="gray", lw=0.5)
                        )

        # Finalizing the plot
        ax.set_title("Turnover Evolution of Cooperatives with Revenue Decrease (2022-2024)", fontsize=14, pad=20)
        ax.set_xlabel("Year", fontsize=12)
        ax.set_ylabel("Turnover", fontsize=12)
        ax.legend(title="Cooperative Name", loc="upper left", fontsize=10)
        ax.grid(True, linestyle="--", alpha=0.5)

        # Force numeric x-axis for proper ordering
        ax.set_xticks([2022, 2023, 2024])  # Explicitly define x-axis ticks
        ax.set_xticklabels([2022, 2023, 2024], fontsize=10)

        # Adjust layout for better spacing
        fig.tight_layout()

        # Display the plot in Streamlit
        st.pyplot(fig)




# Cooperative Table
    st.markdown("<br><br>", unsafe_allow_html=True) 
    st.markdown("<br><br>", unsafe_allow_html=True)
    
    st.markdown('<div class="section-title">Cooperatives List</div>', unsafe_allow_html=True)
    if cooperative_data.empty:
        st.write("No cooperatives match the selected hubs.")
    else:
        # Add a search filter
        search_query = st.text_input("Search for a cooperative by name", "")

        # Filter the dataframe based on the search query
        filtered_cooperative_data = cooperative_data[
            cooperative_data['Cooperative Name'].str.contains(search_query, case=False, na=False)
        ]

        if filtered_cooperative_data.empty:
            st.write("No cooperatives match the search query or selected hubs.")
        else:
            st.dataframe(
                filtered_cooperative_data[
                    ['Cooperative Name', 'Cohort', 'Hub', 'N of Members', 'Activity','Income 2023','Income 2024','Facebook','Instagram']
                ].rename(columns={
                    'Cooperative Name': 'Cooperative Name',
                    'Cohort': 'Cohort',
                    'Hub': 'Hub',
                    'N of Members': 'Members',
                    'Activity': 'Activity',
                    'Income 2023':'Income 2023',
                    'Income 2024':'Income 2024',
                    'Facebook': 'Facebook',
                    'Instagram': 'Instagram'
                })
            )






# Run the app
if __name__ == "__main__":
    main()
