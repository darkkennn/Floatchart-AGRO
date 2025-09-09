import folium
from folium.plugins import MarkerCluster # Add this import

def create_argo_map(show_moored_buoys, show_AWS, show_drifting_buoys, argo_locations):
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

    map = folium.Map(
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
    ).add_to(map)

    if show_moored_buoys:
        for buoy_id, data in moored_buoy_locations.items():
            tooltip_html = f'<div style="font-family: Arial; font-size: 14px; padding: 5px;"><b>{buoy_id}</b></div>'
            folium.Marker(
                location=data["coords"],
                tooltip=folium.Tooltip(tooltip_html),
                icon=folium.Icon(color=data["color"], icon=data["icon"], prefix='fa')
            ).add_to(map)

    if show_AWS:
        for aws_id, data in AWS_locations.items():
            tooltip_html = f'<div style="font-family: Arial; font-size: 14px; padding: 5px;"><b>{aws_id}</b></div>'
            folium.Marker(
                location=data["coords"],
                tooltip=folium.Tooltip(tooltip_html),
                icon=folium.Icon(color=data["color"], icon=data["icon"], prefix='fa')
            ).add_to(map)

    if show_drifting_buoys:
        for buoy_id, data in Drifting_buoy_locations.items():
            tooltip_html = f'<div style="font-family: Arial; font-size: 14px; padding: 5px;"><b>{buoy_id}</b></div>'
            folium.Marker(
                location=data["coords"],
                tooltip=folium.Tooltip(tooltip_html),
                icon=folium.Icon(color=data["color"], icon=data["icon"], prefix='fa')
            ).add_to(map)
    
    if argo_locations:
        marker_cluster = MarkerCluster().add_to(map)
        for profile_id, lat, lon in argo_locations:
            folium.Marker(
                location=[lat, lon],
                tooltip=f"ARGO Profile ID: {profile_id}",
                icon=folium.Icon(color='purple', icon='circle', prefix='fa')
            ).add_to(marker_cluster)
    return map