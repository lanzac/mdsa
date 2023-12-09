import streamlit as st
import MDAnalysis as mda
import requests

def init_rmsd():
    st.button("Run", type="primary", on_click=run_rmsd)

def run_rmsd():

    files = st.session_state["files"]

    pdb_file_content = download_file_content(files, ".pdb")
    trr_file_content = download_file_content(files, ".trr")

    # with open('tmp.pdb', 'wb') as file:
    #         file.write(pdb_file_content)
    # with open('tmp.trr', 'wb') as file:
    #         file.write(trr_file_content)

    u = mda.Universe("tmp.pdb", "tmp.trr")

def download_file_content(df, file_extension):
    file_url = df[df["File name"].str.endswith(file_extension)]["URL"].iloc[0]
    response = requests.get(file_url)

    if response.status_code == 200:
        return response.content
    else:
        print(f"Download failed for {file_url} with status {response.status_code}")
        return None