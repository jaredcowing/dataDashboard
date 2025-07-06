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

st.set_page_config(layout='wide',page_title="Budget")
st.sidebar.header("Budget")

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

import defs

def main():
    st.write('Some budget stats could go here. Maybe also a link to Workday?')


if __name__ == '__main__':
    #with st.empty():
    #    pwd = st.text_input('Password:', value='', type='password')
    #    if pwd=='dashboard':
    #        st.write('')
    #if pwd=='dashboard':
    defs.authBegin()
    if st.session_state.get('authentication_status')==True:
        main()
    