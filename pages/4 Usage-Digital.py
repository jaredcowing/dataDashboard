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

st.set_page_config(layout='wide',page_title="Usage-Digital")
st.sidebar.header("Usage-Digital")
import defs

def main(): 

    dfAAs={}
    dfAAs=defs.digitalPrep(dfAAs)
    dfAAs=defs.topDigitalPrep(dfAAs)
    defs.digitalDisplay(dfAAs)
    defs.topDigitalDisplay(dfAAs)

if __name__ == '__main__':
    defs.authBegin()
    if st.session_state.get('authentication_status')==True:
        main()
    