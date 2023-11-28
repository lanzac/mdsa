"""Streamlit web app for analyzing molecular dynamics (MD) data."""

import streamlit as st
from wordcloud import WordCloud, STOPWORDS

import website_management as wm


st.set_page_config(page_title="MDverse simulation analysis", page_icon="🔬", layout="wide")

st.write("# Welcome to MDverse simulation analysis 🔬")





def user_interaction() -> None:
    """Control the streamlit application.

    Allows interaction between the user and our informational data from MD
    data.
    """
    wm.load_css()

    data = wm.load_data()
    wm.display_details(data)




if __name__ == "__main__":
    user_interaction()
