from pathlib import Path
import streamlit as st
from analysis.structural import rmsd

def get_ext(path_str: str):
    return Path(path_str).suffix

def init_analysis_tools():
    analysis_type_option = st.selectbox(
        "Analysis types:",
        ("Structural", "Composition")
    )

    st.session_state["analysis_type"] = analysis_type_option

    check_files()

    call_tool()

def check_files():

    
    st.session_state["available_analyses_by_type"] = {
        "Structural" : ["test"],
        "Composition" : []
    }


    extension_file_df = st.session_state["files"]["File name"].apply(get_ext)
    extension_counts = extension_file_df.value_counts()

    one_gro = extension_counts.get('.gro', 0) == 1
    one_trr = extension_counts.get('.trr', 0) == 1

    if (one_gro and one_trr):
        st.session_state["available_analyses_by_type"]["Structural"].append("RMSD")

    analysis_type_option = st.session_state["analysis_type"]

    st.session_state["analysis_option"] = st.selectbox(
        "Available analyses:",
        st.session_state["available_analyses_by_type"][analysis_type_option]
    )

    # analysis_count = len(st.session_state["available_analyses_by_type"][analysis_type_option])

def call_tool():
    match st.session_state["analysis_option"]:
        case "RMSD":
            rmsd.run_rmsd()
        
