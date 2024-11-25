import streamlit as st
import google.generativeai as genai

st.title("eIM + Offence Classifier + Summarizer")

api_key = st.secrets["gsc_connections"]["api_key"]
genai.configure(api_key=api_key)


