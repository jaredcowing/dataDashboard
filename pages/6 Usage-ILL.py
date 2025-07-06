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
pup install python-dateutil
'''

#https://developers.google.com/sheets/api/quickstart/python
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
import numpy as np

st.set_page_config(layout='wide',page_title="Usage-ILL")
st.sidebar.header("Usage-ILL")
import defs

def main():
    
    #Gather and prepare the data
    try:
        dfIlls={}
        dfIlls=defs.illPrep(dfIlls)

    except HttpError as err:
        print(err)
    
    apaths=[]
    dfAAs={}
    colp1,colp2=st.columns(2)
    with colp1:
        defs.illBEtypesDisplay(dfIlls)
        defs.illBETSDisplay(dfIlls)
        defs.illBTTDisplay(dfIlls)
        
    with colp2:
        defs.illBPtypesDisplay(dfIlls)
        defs.illBPTSDisplay(dfIlls)
    colRDT1,colRDT2=st.columns([1.5,1])
    with colRDT1:
        defs.illBDailyRDTDisplay(dfIlls)
    with colRDT2:
        st.html('<div style="display:inline-block; height=40px">')
        defs.illBDailyRDTTotalsDisplay(dfIlls)
    
    defs.illBDailySDisplay(dfIlls)
    defs.illBDailySIDDisplay(dfIlls)
    
    colb1,colb2=st.columns(2)
    with colb1:
        defs.illLEtypesDisplay(dfIlls)
        defs.illLSIDDisplay(dfIlls)
        
    with colb2:
        defs.illLPtypesDisplay(dfIlls)
    colRDT3,colRDT4=st.columns([1.5,1])
    with colRDT3:
        defs.illLDailyRDTDisplay(dfIlls)
    with colRDT4:
        defs.illLDailyRDTTotalsDisplay(dfIlls)
    defs.illDDDailyDisplay(dfIlls)
        
if __name__ == '__main__':
    defs.authBegin()
    if st.session_state.get('authentication_status')==True:
        main()
    