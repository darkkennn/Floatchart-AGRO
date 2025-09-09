import xarray as xr
import pandas as pd
import os
import streamlit as st
import zipfile
import shutil
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/drive.readonly"]

def get_drive_service():
    creds = None
    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file("client_secret_899458151364-hekjtoi1oc8p0rfpv792hgvom9p0qm24.apps.googleusercontent.com.json", SCOPES)
            creds = flow.run_local_server(port=0)
        with open("token.json", "w") as token:
            token.write(creds.to_json())
    return build("drive", "v3", credentials=creds)

def list_files_in_folder(service, folder_id):
    results = service.files().list(
        q=f"'{folder_id}' in parents and trashed=false",
        fields="nextPageToken, files(id, name, mimeType)",
    ).execute()
    items = results.get("files", [])
    return items

def download_file(service, file_id, file_path):
    request = service.files().get_media(fileId=file_id)
    with open(file_path, "wb") as f:
        f.write(request.execute())
    return file_path

def process_nc_data(parent_folder_id: str) -> pd.DataFrame:
    st.info("Starting data ingestion...")
    service = get_drive_service()
    temp_dir = "temp_data"

    if os.path.exists(temp_dir):
        shutil.rmtree(temp_dir)
    os.makedirs(temp_dir)
        
    all_data = []

    try:
        root_folders = list_files_in_folder(service, parent_folder_id)
        
        for folder in root_folders:
            st.info(f"Processing source: {folder['name']}")
            if folder["mimeType"] == "application/vnd.google-apps.folder":
                float_id_folders = list_files_in_folder(service, folder["id"])
                
                for float_folder in float_id_folders:
                    if float_folder["mimeType"] == "application/vnd.google-apps.folder":
                        items_in_float_folder = list_files_in_folder(service, float_folder["id"])
                        for profiles_folder in items_in_float_folder:
                            if profiles_folder["name"] == "profiles" and profiles_folder["mimeType"] == "application/vnd.google-apps.folder":
                                nc_files = list_files_in_folder(service, profiles_folder["id"])
                                for nc_file_item in nc_files:
                                    if nc_file_item["name"].endswith(".nc"):
                                        st.write(f"  - Processing: {nc_file_item['name']}")
                                        file_path = os.path.join(temp_dir, nc_file_item["name"])
                                        
                                        try:
                                            download_file(service, nc_file_item["id"], file_path)
                                            with xr.open_dataset(file_path, decode_times=False) as ds:
                                                float_lon = ds['LONGITUDE'].values
                                                float_lat = ds['LATITUDE'].values
                                                float_time = ds['JULD'].values

                                                argo_df = pd.DataFrame({
                                                    'longitude': float_lon,
                                                    'latitude': float_lat,
                                                    'time': pd.to_datetime(float_time, unit='D', origin='1950-01-01')
                                                })
                                            
                                                argo_df = argo_df[(argo_df['latitude'] >= -90) & (argo_df['latitude'] <= 90)]
                                                if not argo_df.empty:
                                                    all_data.append(argo_df)
                                        
                                        except Exception as e:
                                            st.warning(f"- Could not process file {nc_file_item['name']}: {e}")
                                        finally:
                                            if os.path.exists(file_path):
                                                os.remove(file_path)

    except Exception as e:
        st.error(f"An unexpected error occurred: {e}")
        st.exception(e)
    finally:
        if os.path.exists(temp_dir):
            shutil.rmtree(temp_dir)
            
    if not all_data:
        st.error("Ingestion finished, but no valid ARGO data was extracted. Please check file permissions and contents.")
        return pd.DataFrame()
    
    st.success(f"✅ Success! Ingested data for {len(all_data)} ARGO floats.")
    return pd.concat(all_data, ignore_index=True)