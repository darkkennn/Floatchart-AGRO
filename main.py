import streamlit as st
import pandas as pd
from streamlit_folium import st_folium
from map_generator import create_argo_map
from database_manager import get_all_argo_data, insert_data, is_data_present, ensure_table_exists
from data_handler import process_nc_data
import os

st.set_page_config(
    layout="wide",
    page_title="ARGO Float Map",
    initial_sidebar_state="expanded"
)

ensure_table_exists()

st.markdown("""
    <style>
        #MainMenu, footer, .stAppDeployButton {
            visibility: hidden;
        }
        .block-container {
            padding: 2rem 1rem 1rem 1rem !important;
        }
    </style>
    """, unsafe_allow_html=True)

if 'argo_data' not in st.session_state:
    st.session_state.argo_data = get_all_argo_data()
if 'show_chatbot' not in st.session_state:
    st.session_state.show_chatbot = True
if 'messages' not in st.session_state:
    st.session_state.messages = []
if 'show_moored_buoys' not in st.session_state:
    st.session_state.show_moored_buoys = False
if 'show_AWS' not in st.session_state:
    st.session_state.show_AWS = False
if 'show_drifting_buoys' not in st.session_state:
    st.session_state.show_drifting_buoys = False

with st.sidebar:
    st.header("Insitu Data")
    show_moored_buoys = st.checkbox("Moored Buoy")
    show_AWS = st.checkbox("AWS")
    show_drifting_buoys = st.checkbox("Drifting Buoy")
    
    st.markdown("---")
    
    st.header("ARGO Floats Filter")

    if not st.session_state.argo_data.empty:
        all_years = st.session_state.argo_data['timestamp'].dt.year.unique()
        years_list = sorted(all_years, reverse=True)
        
        selected_year = st.selectbox(
            "First, select a year:",
            options=["Select a year..."] + years_list
        )
    else:
        st.info("No ARGO data in database to filter.")
        selected_year = "Select a year..."

    region_selections = {}
    if selected_year and selected_year != "Select a year...":
        st.write("Next, select region(s):")
        region_selections['arabian_sea'] = st.checkbox("Arabian Sea")
        region_selections['bay_of_bengal'] = st.checkbox("Bay of Bengal")
        region_selections['laccadive_sea'] = st.checkbox("Laccadive Sea")
        region_selections['indian_ocean'] = st.checkbox("Indian Ocean")
        region_selections['pacific_ocean'] = st.checkbox("Pacific Ocean")
        region_selections['atlantic_ocean'] = st.checkbox("Atlantic Ocean")
        region_selections['southern_ocean'] = st.checkbox("Southern Ocean")
        region_selections['arctic_ocean'] = st.checkbox("Arctic Ocean")

    st.markdown("---")

    if not is_data_present():
        st.warning("No ARGO data found in the database.")
        google_drive_folder_id = "1wJzy0MNZpQpCoX-IxyD1dW_mCR4zUUBW"
        if st.button("Ingest ARGO data from Google Drive"):
            with st.spinner("Processing and ingesting data..."):
                argo_data_df = process_nc_data(google_drive_folder_id)
                if not argo_data_df.empty:
                    insert_data(argo_data_df)
                    st.success("Data ingestion complete!")
                    del st.session_state.argo_data
                    st.rerun()
                else:
                    st.error("Failed to ingest data. Check logs for details.")

    if st.session_state.show_chatbot:
        if st.button("Hide Chatbot"):
            st.session_state.show_chatbot = False
            st.rerun()
    else:
        if st.button("Show Chatbot"):
            st.session_state.show_chatbot = True
            st.rerun()

if st.session_state.show_chatbot:
    col1, col2 = st.columns([4, 1], gap="small")
else:
    col1 = st.container()
    col2 = None

with col1:
    df_to_display = pd.DataFrame()
    
    if (selected_year and selected_year not in ["All", "Select a year..."] and any(region_selections.values())):
        df_filtered = st.session_state.argo_data.copy()
        df_filtered = df_filtered[df_filtered['timestamp'].dt.year == selected_year]
        
        bboxes = {
            'arabian_sea': [50, 5, 78, 25],
            'bay_of_bengal': [80, 5, 100, 23],
            'laccadive_sea': [70, 5, 80, 15],
            'indian_ocean': [20, -60, 120, 30],
            'atlantic_ocean': [-70, -60, 20, 60],
            'southern_ocean': [-180, -90, 180, -60],
            'arctic_ocean': [-180, 60, 180, 90]
        }
        
        combined_mask = pd.Series(False, index=df_filtered.index)
        for region, selected in region_selections.items():
            if selected:
                if region == 'pacific_ocean':
                    mask = (df_filtered['longitude'] >= 120) | (df_filtered['longitude'] <= -70)
                    combined_mask |= mask
                elif region in bboxes:
                    box = bboxes[region]
                    mask = ((df_filtered['longitude'].between(box[0], box[2])) & (df_filtered['latitude'].between(box[1], box[3])))
                    combined_mask |= mask
        
        df_to_display = df_filtered[combined_mask]

    filtered_argo_locations = []
    if not df_to_display.empty:
        filtered_argo_locations = list(df_to_display[['id', 'latitude', 'longitude']].itertuples(index=False, name=None))
    
    st.info(f"Displaying {len(filtered_argo_locations)} of {len(st.session_state.argo_data)} total ARGO floats.")

    m = create_argo_map(
        show_moored_buoys=show_moored_buoys,
        show_AWS=show_AWS,
        show_drifting_buoys=show_drifting_buoys,
        argo_locations=filtered_argo_locations
    )
    
    st_folium(m, width="100%", height=720)

if st.session_state.show_chatbot and col2 is not None:
    with col2:
        with st.container():
            header_col, button_col = st.columns([10, 1])
            with header_col:
                st.header("Chatbot")
            with button_col:
                if st.button("X", key="hide_chatbot_button_main"):
                    st.session_state.show_chatbot = False
                    st.rerun()

            chat_history_container = st.container(height=650)
            with chat_history_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            if prompt := st.chat_input("Enter your query..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()