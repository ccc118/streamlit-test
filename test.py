import streamlit as st
import pandas as pd


option = st.selectbox('Live today', ('Manchester United vs Brighton', 'Chelsea vs Brentford'))

st.write('You selected:', option)
