"""Helper functions to manage the Streamlit application."""

import streamlit as st
import pandas as pd

import itables
from itables import JavascriptFunction

import streamlit.components.v1 as components


from analysis import analysis_manager as am

@st.cache_data
def load_data() -> dict:
    """Retrieve our data and loads it into the pd.DataFrame object.

    Returns
    -------
    dict
        returns a dict containing the pd.DataFrame objects of our datasets.
    """
    # DATA_URL needs to be the URL of the last version of the data.
    # I cannot be the identifier provided by the master DOI.
    DATA_URL = "https://zenodo.org/record/7856806"
    dfs = {}
    datasets = pd.read_parquet(
        f"{DATA_URL}/files/datasets.parquet"
    )
    files = pd.read_parquet(
        f"{DATA_URL}/files/files.parquet"
    )

    dfs["datasets"] = datasets
    dfs["files"] = files
    return dfs

@st.cache_data
def find_dataset_by_id(datasets: pd.DataFrame, dataset_id: str) -> pd.DataFrame:
    """Find a dataset in the pd.DataFrame using a dataset ID.

    Parameters
    ----------
    datasets: pd.DataFrame
        Contains all the information from our extracted MD data.
    dataset_id: str
        The dataset ID used for searching.

    Returns
    -------
    pd.DataFrame
        Returns the pd.DataFrame object filtered by dataset ID.
    """
    to_keep = [
        "dataset_url",
        "dataset_origin",
        "dataset_id",
        "title",
        "date_creation",
        "author",
        "description",
        "file_number",
    ]

    # Filter data for datasets containing the specified dataset_id
    results = datasets[datasets["dataset_id"].str.contains(dataset_id, case=False, regex=False)]

    # Select only the specified columns
    results = results[to_keep]

    # Rename columns for readability
    results.columns = [
        "URL",
        "Dataset",
        "ID",
        "Title",
        "Creation date",
        "Authors",
        "Description",
        "# Files",
    ]

    if not results.empty:
        return results.iloc[0]
    else:
        return None

@st.cache_data
def find_files_by_dataset_id(files: pd.DataFrame, dataset_id: str) -> pd.DataFrame:
    """Find a dataset in the pd.DataFrame using a dataset ID.

    Parameters
    ----------
    data: pd.DataFrame
        Contains all the information from our extracted MD data.
    dataset_id: str
        The dataset ID used for searching.

    Returns
    -------
    pd.DataFrame
        Returns the pd.DataFrame object filtered by dataset ID.
    """
    to_keep = [
        "file_type",
        "file_size",
        "file_name",
        "file_url",
    ]

    # Filter data for datasets containing the specified dataset_id
    results = files[files["dataset_id"].str.contains(dataset_id, case=False, regex=False)]

    # Select only the specified columns
    results = results[to_keep]

    # Rename columns for readability
    results.columns = [
        "File type",
        "File size",
        "File name",
        "URL",
    ]
    if not results.empty:
        return results
    else:
        return None

def display_search_bar():
    """Configure the display of the search bar.

    Returns
    -------
    int
        search id.
    """
    placeholder = (
        "Enter dataset ID."
    )
    search_id = st.sidebar.text_input("Datasets quick search", placeholder=placeholder)

    st.session_state["querydatasetid"] = search_id

def update_contents(data: pd.DataFrame) -> None:
    """Change the content display according to the cursor position.

    Parameters
    ----------
    data: pd.DataFrame
        dataframe.
    """
    datasetid = st.session_state["querydatasetid"]

    datasets = data["datasets"]
    files = data["files"]

    result_data = find_dataset_by_id(datasets, datasetid)
    
    if result_data is None or result_data.empty:
        st.sidebar.write("No result found.")
        return

    contents = f"""
    **Dataset:**
    [{result_data["Dataset"]} {result_data["ID"]}]({result_data["URL"]})  
    **Creation date:** {result_data["Creation date"]}  
    **Author(s):** {result_data["Authors"]}  
    **Title:** {result_data["Title"]}  
    **Description:**\n *{result_data["Description"]}*\n
    """

    result_files = find_files_by_dataset_id(files, datasetid)
    if result_data.empty:
        st.sidebar.write("No files found.")
    
    def format_size(size_str):
        """ Converts a size in bytes into KB, MB, GB, etc. formats. """
        size = int(size_str)
        for unit in ['bytes', 'KB', 'MB', 'GB', 'TB', 'PB', 'EB', 'ZB', 'YB']:
            if size < 1024.0:
                return f"{size:.1f} {unit}"
            size /= 1024.0
        return f"{size:.1f} YB"  #  Returns in Yottabytes if the value is extremely large

    def format_file_info(row):
        return f"""
    📄  {row['File name']}    
    🗄️  {format_size(row['File size'])}\n
        """

    files_contents = "".join(result_files.apply(format_file_info, axis=1))

    datasetinfo_expander = st.sidebar.expander("Dataset informations:")
    datasetinfo_expander.markdown(contents)

    filesinfo_expander = st.sidebar.expander("Files:", expanded=True)
    filesinfo_expander.markdown(files_contents)


    # st.session_state["content"] = contents + files_contents
    st.session_state["content"] = [datasetinfo_expander, filesinfo_expander]
    st.session_state["files"] = result_files

    

def display_details(data: pd.DataFrame) -> None:
    """Show the details of the selected rows in the sidebar.

    Parameters
    ----------
    data: pd.DataFrame
        dataframe.
    """
    if (
        "querydatasetid" not in st.session_state
        or "content" not in st.session_state
    ):
        st.session_state["querydatasetid"] = 0
        st.session_state["content"] = ""

    datasets = data["datasets"]
    size_selected = len(datasets)
    if not size_selected:
        return
    
    if size_selected > 1:
        display_search_bar()
    
    update_contents(data)

    if not st.session_state["content"]:
        return
    
    with st.sidebar:
        [comp for comp in st.session_state["content"]]
    am.init_analysis_tools()
    
            


def load_css() -> None:
    """Load a css style."""
    st.markdown(
        """
        <style>
            /* Centre the add filter checkbox and the download button */
            .stCheckbox {
                position: absolute;
                top: 40px;
            }

            .stDownloadButton {
                position: absolute;
                top: 33px;
            }

            /* Responsive display */
            @media (max-width:640px) {
                .stCheckbox {
                    position: static;
                }

                .stDownloadButton {
                    position: static;
                }
            }

            /* Maximize thedusplay of the data explorer search */
            .block-container:first-of-type {
                padding-top: 20px;
                padding-left: 20px;
                padding-right: 20px;
            }
        </style>
    """,
        unsafe_allow_html=True,
    )
    itables.options.css = """
            /* Change the display of the table */
            .itables {
                font-family: 'sans-serif';
                font-size: 0.8rem;
                background: white;
                padding: 10px;
            }

            /* Specific column titles */
            .itables table th {
                word-wrap: break-word;
                font-size: 11px;
            }

            /* Cells specific */
            .itables table td {
                word-wrap: break-word;
                min-width: 50px;
                max-width: 50px;
                overflow: hidden;
                text-overflow: ellipsis;
                font-size: 12px;
            }

            /* Set the width of the id column */
            .itables table td:nth-child(4) {
                min-width: 80px;
                max-width: 80px;
            }

            /* Set the width of the title and description columns */
            .itables table td:nth-child(5), .itables table td:nth-child(8) {
                max-width: 300px;
            }

            /* Hide the URL column */
            .itables table th:nth-child(2), .itables table td:nth-child(2){
                display:none;
            }

            /* Apply colour to links */
            a:link, a:visited {
                color: rgb(51, 125, 255);
            }
    """