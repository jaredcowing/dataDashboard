'''
Non-conda installs required:
pip install streamlit
pip install streamlit-elements
pip install google-auth
pip install google-auth-oauthlib
pip install google-api-python-client
pip install seaborn
pip install plotly
pip install elementpath
pip install regex
pip install python-dateutil
'''
import streamlit as st
import pandas as pd
from streamlit_elements import elements, mui, html
from google.auth.transport.requests import Request as GRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import os
import urllib
import requests
from requests import Session, Request
from urllib.parse import urlencode, quote_plus, quote
from streamlit_elements import nivo
from datetime import datetime, timedelta
from dateutil import relativedelta
import seaborn as sn
import matplotlib.pyplot as plt
import xml.etree.ElementTree as ET
import re
import plotly.express as px
import plotly.graph_objects as go
import math

st.set_page_config(layout='wide',page_title="Usage-Print & Spaces")
st.sidebar.header("Usage-Print & Spaces")
import defs

#https://developers.google.com/sheets/api/quickstart/python
def main():
    #Gather and prepare the data
    try:
        dfGGs={}
        dfGGs=defs.gateCountPrep(dfGGs)
    except HttpError as error:
        st.write(error)

    dfAAs={}
    
    #st.write(type(dfAAs))
    dfAAs=defs.circTotalsPrep(dfAAs)
    dfAAs=defs.requestsLsfPrep(dfAAs)
    dfAAs=defs.circUGPrep(dfAAs)
    dfAAs=defs.circLocPrep(dfAAs)
    st.markdown(
    """
	<style>
	.stSelectbox {
	    font-size:10pt;
    	padding: 0px;
        margin-bottom:-30px;
        position: relative;
        z-index:1;
	}
	</style>
    """, unsafe_allow_html=True
    )
    
    defs.gateCountDisplay(dfGGs)
    defs.circTotalsDisplay(dfAAs)
    col1,col2=st.columns([1.5,1])
    with col1:
        defs.circUGDisplay(dfAAs)
    with col2:
        #st.html('<div style="display:inline-block; height=10px">')
        defs.circUGTotalsDisplay(dfAAs)
    colL1,colL2=st.columns([1.5,1])
    with colL1:
        defs.circLocDisplay(dfAAs)
    with colL2:
        #st.html('<div style="display:inline-block; height=10px">')
        defs.circLocTotalsDisplay(dfAAs)
    defs.requestsLsfDisplay(dfAAs)
    defs.requestsLsfCountsDisplay(dfAAs)


if __name__ == '__main__':
    defs.authBegin()
    if st.session_state.get('authentication_status')==True:
        main()
    