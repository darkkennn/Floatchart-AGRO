import streamlit as st
from streamlit_folium import st_folium
import folium

st.set_page_config(
    layout="wide",
    page_title="ARGO Float Map",
    initial_sidebar_state="expanded"
)

if 'show_chatbot' not in st.session_state:
    st.session_state.show_chatbot = True

if 'messages' not in st.session_state:
    st.session_state.messages = []

st.markdown("""
    <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .reportview-container .main {
        padding: 0;
    }
    .chatbot-header {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding-top: 10px;
        padding-bottom: 10px;
    }
    .chatbot-container {
        display: flex;
        flex-direction: column;
        height: 80vh;
        background-color: #dcdcdc; /* Light gray background */
        padding: 10px;
        border-radius: 10px;
        border-left: 1px solid #ddd; /* Thin white margin */
    }
    .stChatInput {
        margin-top: auto;
    }
    .chat-history-container {
        flex-grow: 1;
        overflow-y: auto;
    }
    .stButton>button {
        background: none;
        border: none;
        font-size: 1.5rem;
        cursor: pointer;
        padding: 0;
    }
    </style>
    """, unsafe_allow_html=True)

moored_buoy_locations = {
    "AD06": {"coords": [18.5, 67], "color": "darkblue", "icon": "anchor"},
    "AD07": {"coords": [15, 68], "color": "darkblue", "icon": "anchor"},
    "AD08": {"coords": [12, 68], "color": "darkblue", "icon": "anchor"},
    "AD10": {"coords": [10.3, 72.58], "color": "darkblue", "icon": "anchor"},
    "CALVAL": {"coords": [10.5, 72.1], "color": "red", "icon": "anchor"},
    "CB02": {"coords": [10.89, 72.2], "color": "red", "icon": "anchor"},
    "CAU19": {"coords": [9, 72], "color": "red", "icon": "anchor"},
    "CB01": {"coords": [9, 90], "color": "red", "icon": "anchor"},
    "BD10": {"coords": [16, 87], "color": "green", "icon": "anchor"},
    "BD11": {"coords": [13.5, 84], "color": "green", "icon": "anchor"},
    "BD13": {"coords": [14, 86.5], "color": "green", "icon": "anchor"},
    "BD12": {"coords": [10.7, 93.7], "color": "green", "icon": "anchor"},
    "BD14": {"coords": [6.5, 88.3], "color": "green", "icon": "anchor"},
}

AWS_locations = {
    "AWS1": {"coords": [9.96194, 76.28306], "color": "blue", "icon": "cloud"},
    "AWS2": {"coords": [11.04028, 74.97611], "color": "blue", "icon": "cloud"},
    "AWS3": {"coords": [22.54056, 88.3025], "color": "blue", "icon": "cloud"},
}

Drifting_buoy_locations = {
    "I300534064138620": {"coords": [1.2659416, 94.2979406], "color": "orange", "icon": "life-ring"},
    "I300534064139130": {"coords": [-59.6781261, 34.2363898], "color": "orange", "icon": "life-ring"},
    "IN0017": {"coords": [4.885, 72.9357], "color": "orange", "icon": "life-ring"},
    "AR020220830": {"coords": [6.3439, 80.0438], "color": "orange", "icon": "life-ring"},
    "IN0038": {"coords": [15.4683, -93.3828], "color": "orange", "icon": "life-ring"},
    "IN0035": {"coords": [16.9798, 69.4158], "color": "orange", "icon": "life-ring"},
    "IN0030": {"coords": [15.9896, 72.5854], "color": "orange", "icon": "life-ring"},
    "I300534064138600": {"coords": [-12.0335904, 987.2484693], "color": "orange", "icon": "life-ring"},
}

with st.sidebar:
    st.header("Insitu Data")

    if 'show_moored_buoys' not in st.session_state:
        st.session_state.show_moored_buoys = False

    if 'show_tide_gauges' not in st.session_state:
        st.session_state.show_AWS = False

    if 'show_drifting_buoys' not in st.session_state:
        st.session_state.show_drifting_buoys = False

    st.session_state.show_moored_buoys = st.checkbox("Moored Buoy", value=st.session_state.show_moored_buoys)
    st.session_state.show_AWS = st.checkbox("AWS", value=st.session_state.show_AWS)
    st.session_state.show_drifting_buoys = st.checkbox("Drifting Buoy", value=st.session_state.show_drifting_buoys)
    
    st.markdown("---")
    
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
    m = folium.Map(
        location=[5, 80],
        zoom_start=5,
        min_zoom=3,
        max_bounds=True
    )

    folium.TileLayer(
        tiles='https://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}',
        attr='Tiles &copy; Esri &mdash; Source: Esri, i-cubed, USDA, USGS, AEX, GeoEye, Getmapping, Aerogrid, IGN, IGP, UPR-EGP, and the GIS User Community',
        name='Esri World Imagery',
        max_zoom=18,
        control=False
    ).add_to(m)

    if st.session_state.show_moored_buoys:
        for buoy_id, data in moored_buoy_locations.items():
            tooltip_html = f'<div style="font-family: Arial; font-size: 14px; padding: 5px;"><b>{buoy_id}</b></div>'
            folium.Marker(
                location=data["coords"],
                tooltip=folium.Tooltip(tooltip_html),
                icon=folium.Icon(color=data["color"], icon=data["icon"], prefix='fa')
            ).add_to(m)

    if st.session_state.show_AWS:
        for aws_id, data in AWS_locations.items():
            tooltip_html = f'<div style="font-family: Arial; font-size: 14px; padding: 5px;"><b>{aws_id}</b></div>'
            folium.Marker(
                location=data["coords"],
                tooltip=folium.Tooltip(tooltip_html),
                icon=folium.Icon(color=data["color"], icon=data["icon"], prefix='fa')
            ).add_to(m)

    if st.session_state.show_drifting_buoys:
        for buoy_id, data in Drifting_buoy_locations.items():
            tooltip_html = f'<div style="font-family: Arial; font-size: 14px; padding: 5px;"><b>{buoy_id}</b></div>'
            folium.Marker(
                location=data["coords"],
                tooltip=folium.Tooltip(tooltip_html),
                icon=folium.Icon(color=data["color"], icon=data["icon"], prefix='fa')
            ).add_to(m)

    st_data = st_folium(m, width="100%", height=700)

    if st_data.get("last_clicked"):
        lat = st_data["last_clicked"]["lat"]
        lon = st_data["last_clicked"]["lng"]

if st.session_state.show_chatbot and col2 is not None:
    with col2:
        with st.container():
            header_col, button_col = st.columns([10, 1])
            with header_col:
                st.header("Chatbot")
            with button_col:
                if st.button("X", key="hide_chatbot_button"):
                    st.session_state.show_chatbot = False
                    st.rerun()

            chat_history_container = st.container(height=600)
            with chat_history_container:
                for message in st.session_state.messages:
                    with st.chat_message(message["role"]):
                        st.markdown(message["content"])

            if prompt := st.chat_input("Enter your query for the ARGO data model..."):
                st.session_state.messages.append({"role": "user", "content": prompt})
                st.rerun()
