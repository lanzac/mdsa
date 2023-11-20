"""Helper functions to manage the Streamlit application."""

import streamlit as st
import pandas as pd

import itables
from itables import JavascriptFunction


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
def find_dataset_by_id(data: pd.DataFrame, dataset_id: str) -> pd.DataFrame:
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
    results = data[data["dataset_id"].str.contains(dataset_id, case=False, regex=False)]

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
    if not datasetid:
        return
    
    result_data = find_dataset_by_id(data, datasetid)

    print(result_data)

    if result_data.empty:
        st.sidebar.write("No result found.")
        return


    contents = f"""
        **Dataset:**
        [{result_data["Dataset"]} {result_data["ID"]}]({result_data["URL"]})<br />
        **Creation date:** {result_data["Creation date"]}<br />
        **Author(s):** {result_data["Authors"]}<br />
        **Title:** *{result_data["Title"]}*<br />
        **Description:**<br /> {result_data["Description"]}
    """
    st.session_state["content"] = contents

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

    size_selected = len(data)
    if size_selected:
        if size_selected > 1:
            display_search_bar()
        update_contents(data)
        st.sidebar.markdown(st.session_state["content"], unsafe_allow_html=True)


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