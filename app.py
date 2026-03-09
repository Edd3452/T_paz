import streamlit as st
import pandas as pd
import os
import geopandas as gpd

try:
    import folium
    from streamlit_folium import st_folium
except ImportError:
    st.error("Missing libraries: folium, streamlit_folium.")
    st.stop()

st.set_page_config(layout="wide", page_title="Territorios de Paz")

st.markdown("""
    <div style="background-color: #581845; padding: 20px; border-radius: 5px; margin-bottom: 20px;">
        <h1 style="color: white; text-align: center; margin: 0; font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; font-weight: bold;">
            Territorios de Paz
        </h1>
    </div>
""", unsafe_allow_html=True)

# Custom CSS
st.markdown('''
    <style>
    .stApp { background-color: white; color: black; }
    </style>
''', unsafe_allow_html=True)

google_sheet_url = "https://docs.google.com/spreadsheets/d/1RdV79i1ifRCt_r3j8zEDqt71ItqNRO39MpB1fKA8uZY/export?format=csv&gid=0"
try:
    df = pd.read_csv(google_sheet_url)
    st.write("### Datos Demográficos y Socioeconómicos")
    st.dataframe(df.style.set_properties(**{'background-color': '#FAFBF5', 'color': 'black'}))
except Exception as e:
    st.error(f"Error loading data from Google Sheets: {e}")
    st.stop()

st.write("### Mapa de Territorios de Paz")

# Initialize Folium map
m = folium.Map(location=[19.4326, -99.1332], zoom_start=10, tiles="CartoDB positron", control_scale=True)

# Add 09mun base layer
mun_shp_path = os.path.join(".", "09mun.shp")
if os.path.exists(mun_shp_path):
    try:
        mun_gdf = gpd.read_file(mun_shp_path)
        if mun_gdf.crs is None and not mun_gdf.empty:
            x_min = mun_gdf.total_bounds[0]
            if x_min < -180 or x_min > 180:
                mun_gdf.set_crs(epsg=32614, inplace=True)
            else:
                mun_gdf.set_crs(epsg=4326, inplace=True)
        if mun_gdf.crs and mun_gdf.crs.to_string() != "EPSG:4326":
            mun_gdf = mun_gdf.to_crs(epsg=4326)
            
        folium.GeoJson(
            mun_gdf,
            name="Límites Municipales",
            style_function=lambda x: {
                'color': '#333333',
                'weight': 1.5,
                'fillOpacity': 0,
                'dashArray': '5, 5'
            },
            tooltip="Límite Municipal"
        ).add_to(m)
    except Exception as e:
        print(f"Error loading 09mun.shp: {e}")

# Mapping of dataset names to actual .shp filenames
shapefile_mapping = {
    "Barrio norte": "Barrio norte.shp",
    "Lomas de Becerra": "Lomas becerra.shp",
    "San Pedro Xalpa": "San Pedro Xalpa.shp",
    "Pedregal de Santo Domingo": None,  # Not found
    "San Mateo Tlaltenango": "San Mateo Tlaltenango.shp",
    "Colonia Obrera": "Colonia Obrera.shp",
    "Colonia Morelos": "Colonia Morelos.shp",
    "Barrio Tepito": "Barrio tepito.shp",
    "Campamento 2 de Octubre": "Campamento 2 de ocubre.shp",
    "San Felipe de Jesús": "San felipe de jesus.shp",
    "Chalma de Guadalupe": "Chalma de guadalupe .shp",
    "Infonavit Iztacalco": "Infonavit iztacalco.shp",
    "Desarrollo Urbano Quetzalcóatl": "Desarrollo Urbano Quetzalcóatl.shp",
    "Tierra Unida": "Tierra Unida.shp",
    "Tacuba": "Tacuba.shp",
    "San Antonio Tecómitl": "San Antonio Tecomit.shp",
    "San Miguel Topilejo": "San Muiguel Topilejo.shp",
    "San Gregorio Atlapulco": "San Gregorio Atlapulco .shp",
    "San Andres Mixquic": "San Andrés Mixqui.shp",
    "CTM Ixtahucan": "CTM Culhuacan.shp", # Best guess for CTM
}

T_PAZ_DIR = "."

@st.cache_data
def load_and_process_shapefile(filepath):
    try:
        gdf = gpd.read_file(filepath)
        if gdf.crs is None and not gdf.empty:
            x_min = gdf.total_bounds[0]
            if x_min < -180 or x_min > 180:
                gdf.set_crs(epsg=32614, inplace=True)
            else:
                gdf.set_crs(epsg=4326, inplace=True)
        if gdf.crs and gdf.crs.to_string() != "EPSG:4326":
            gdf = gdf.to_crs(epsg=4326)
        return gdf
    except Exception as e:
        return None

colors = [
    '#e6194b', '#3cb44b', '#ffe119', '#4363d8', '#f58231', 
    '#911eb4', '#46f0f0', '#f032e6', '#bcf60c', '#fabebe', 
    '#008080', '#e6beff', '#9a6324', '#fffac8', '#800000', 
    '#aaffc3', '#808000', '#ffd8b1', '#000075', '#808080'
]

# Create a master dictionary linking df row to the shapefile
for idx, row in df.iterrows():
    name = str(row["Territorio de paz"]).strip()
    shp_file = shapefile_mapping.get(name)
    
    if shp_file and os.path.exists(os.path.join(T_PAZ_DIR, shp_file)):
        gdf = load_and_process_shapefile(os.path.join(T_PAZ_DIR, shp_file))
        if gdf is not None and not gdf.empty:
            layer_color = colors[idx % len(colors)]
            
            # Additional tooltip info from the spreadsheet
            tooltip_html = f"<b>{name}</b><br>"
            for col in ["Acaldía", "Habitantes", "Edad", "Actividad Económica"]:
                if pd.notna(row.get(col)):
                    tooltip_html += f"<b>{col}:</b> {row[col]}<br>"
            
            folium.GeoJson(
                gdf,
                name=name,
                style_function=lambda x, color=layer_color: {
                    'color': color,
                    'weight': 2,
                    'fillOpacity': 0.5,
                    'fillColor': color
                },
                tooltip=tooltip_html
            ).add_to(m)
    else:
        # Fallback to lat/lon point if available and shapefile missing
        lat = row.get("latitud(y)")
        lon = row.get("longitud(x)")
        if pd.notna(lat) and pd.notna(lon):
            tooltip_html = f"<b>{name}</b> (Solo Punto)<br>"
            for col in ["Acaldía", "Habitantes"]:
                if pd.notna(row.get(col)):
                    tooltip_html += f"<b>{col}:</b> {row[col]}<br>"
            
            folium.CircleMarker(
                location=[lat, lon],
                radius=6,
                color=colors[idx % len(colors)],
                fill=True,
                fill_opacity=0.7,
                tooltip=tooltip_html
            ).add_to(m)

folium.LayerControl().add_to(m)

st_folium(m, width="100%", height=600, returned_objects=[])

st.markdown(
    """
    <style>
    .footer {
        position: fixed;
        left: 0;
        bottom: 0;
        width: 100%;
        background-color: white;
        color: #333;
        text-align: center;
        padding: 5px;
        font-size: 14px;
        border-top: 1px solid #eaeaea;
        z-index: 9999;
    }
    </style>
    <div class="footer">
        Territorios de Paz - Datos procesados desde Google Sheets
    </div>
    """,
    unsafe_allow_html=True
)
