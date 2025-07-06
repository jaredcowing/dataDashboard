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


        

def main():
    st.write("Welcome to your dashboard! Choose a dashboard view from the left.")
    st.write("You can interact with most visualizations by hovering over them. You will see icons in the top right.")
    st.write("Want to try panning a line chart? Want to zoom in on a section of a line chart? Try selecting the appropriate icon and dragging your cursor over the chart.")
    video=open("zoom and pan.mp4","rb")
    videob=video.read()
    st.video(videob)
    st.write("You can also hide lines with a single click or focus on them with a double click.")
    video2=open("hide and select.mp4","rb")
    videob2=video2.read()
    st.video(videob2)


if __name__ == '__main__':
    main()
    