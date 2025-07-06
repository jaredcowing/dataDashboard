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

#https://developers.google.com/sheets/api/quickstart/python
import streamlit as st
import pandas as pd
from streamlit_elements import elements, mui, html
from google.auth.transport.requests import Request as GRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader

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
import numpy as np

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly']
api_key='redacted'
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'redacted' #LSPG data sheet
SPREADSHEET_ID2 = 'redacted' #Sawyer gate count 2025
SPREADSHEET_ID3 = 'redacted' #Schow gate count 2025
SPREADSHEET_ID4 = 'redacted' #Self-maintained Google sheet

RANGE_NAME = 'Gate count!A1:C33'
RANGE_2 = 'Loans by user group-books!A1:C79'
RANGE_3 = '!A2:D500'
RANGE_4 = 'ILL Borrowing-Request Sent!A1:I200'
RANGE_5 = 'ILL Borrowing-Delivered to Web!A1:I1000'
RANGE_6 = 'ILL Borrowing-Request Finished!A1:I16000'
RANGE_7 = 'ILL Borrowing-Cancelled by Customer!A1:I1500'
RANGE_8 = 'ILL Borrowing-Cancelled by Staff!A1:I1500'
RANGE_9 = 'ILL DD-Delivered to Web!A1:I1000'
RANGE_10 = 'ILL DD-Request Finished!A1:I2000'
RANGE_11 = 'ILL Lending-Item Shipped!A1:I3000'
RANGE_12 = 'ILL Lending-Request Finished!A1:I16000'

theme={
    'fontSize':'14px',
    "textColor": "#31333F",
    'fontFamily':'sans-serif'
}
asDict={
    'College Archives - Accessions':[['Accessions','College Archives - Accessions'],['Accessions','College Archives']],
    'Chapin Library - Accessions':[['Accessions','Chapin Library - Accessions'],['Accessions','Chapin Library']],
    'College Archives - Archival Objects':[['Archival Objects','College Archives - Archival Objects'],['Archival Objects','College Archives']],
    'Chapin Library - Archival Objects':[['Archival Objects','Chapin Library - Archival Objects'],['Archival Objects','Chapin Library']],
    'College Archives - Digital Objects':[['Digital Objects','College Archives - Digital Objects'],['Digital Objects','College Archives']],
    'Chapin Library - Digital Objects':[['Digital Objects','Chapin Library - Digital Objects'],['Digital Objects','Chapin Library']],
    'College Archives - Top Containers':[['Top Containers','College Archives - Top Containers'],['Top Containers','College Archives']],
    'Chapin Library - Top Containers':[['Top Containers','Chapin Library - Top Containers'],['Top Containers','Chapin Library']]
}
gDict={
    '1st Year Student':['Student','Undergraduate','1st Year Student'],
    'Sophomore':['Student','Undergraduate','Sophomore'],
    'Junior':['Student','Undergraduate','Junior'],
    'Senior':['Student','Undergraduate','Senior'],
    'Faculty/Curator':['Faculty','Faculty/Curator',''],
    'First Yr Graduate Student':['Student','Graduate','First Yr Graduate Student'],
    'ILL Lending':['Community','ILL','ILL Lending'],
    '2nd Yr Graduate Student':['Student','Graduate','2nd Yr Graduate Student'],
    'Administrative & Support Staff':['Staff','Administrative & Support Staff',''],
    'Williamstown Residents':['Community','Williamstown Residents',''],
    'Surrounding Towns':['Community','Surrounding Towns',''],
    'Retirees (Williams)':['Community','Retirees (Williams)',''],
    'Research Associate':['Community','Research Associate',''],
    'Fac/Admin/Staff/Stu Spouse':['Community','Fac/Admin/Staff/Stu Spouse',''],
    'Special Student':['Student','Student Other','Special Student'],
    'TA (Foreign Language)':['Student','Student Other','TA (Foreign Language)'],
    'CDE Student':['Student','Graduate','CDE Student'],
    'Nearby College Faculty':['Community','Nearby College Faculty',''],
    'Clark Art Admin. & Staff':['Community','Clark Art Admin. & Staff',''],
    'Alumni & Spouse':['Community','Alumni & Spouse',''],
    'Contracted Musicians':['Community','Contracted Musicians',''],
    'WTF Conference':['Community','WTF Conference',''],
    'Grandfathered Annual Patrons':['Community','Grandfathered Annual Patrons','']
}
lDict={
    'Sawyer':['Print','Sawyer',''],
    'Sawyer Equipment':['Equipment & Realia','Sawyer Equipment',''],
    'Schow Equipment':['Equipment & Realia','Schow Equipment',''],
    'Schow':['Print','Schow',''],
    'LSF':['Misc','Misc Non-Ill/Reserve/AV','LSF'],
    'Score':['Print','Score',''],
    'Borrowing Resource Sharing Requests':['Misc','Borrowing Resource Sharing Requests',''],
    'Sawyer DVD':['Misc','Audiovisual','Sawyer DVD'],
    'Sawyer Reserve':['Misc','Reserve','Sawyer Reserve'],
    'Sawyer New Book':['Print','Sawyer New Book',''],
    'Compact Disc':['Misc','Audiovisual','Compact Disc'],
    'LSF Schow':['Misc','Misc Non-Ill/Reserve/AV','LSF Schow'],
    'Game':['Equipment & Realia','Game',''],
    'Sawyer Zines':['Print','Sawyer Zines',''],
    'Schow Circ Desk':['Equipment & Realia','Schow Circ Desk',''],
    'Schow Reserve':['Misc','Reserve','Schow Reserve'],
    'LSF Video':['Misc','Audiovisual','LSF Video',''],
    'Sawyer Folio':['Print','Sawyer Folio',''],
    'Schow New Book':['Print','Schow New Book',''],
    'Access Services Office':['Misc','Misc Non-Ill/Reserve/AV','Access Services Office']
}
illBRDTDict={
    'Electronic - Article':[['Electronic','Electronic - Article',''],['Electronic','Article','']],
    'Electronic - Book Chapter':[['Electronic','Electronic - Book Chapter',''],['Electronic','Book Chapter,''']],
    'Physical - Book':[['Physical','Physical - Book',''],['Physical','Book','']],
    'Electronic - Book':[['Electronic','Electronic - Other','Electronic - Book',''],['Electronic','Other','Book','']],
    'Physical - Video':[['Physical','Physical - Other','Physical - Video'],['Physical','Other','Video']],
    'Physical - Thesis':[['Physical','Physical - Other','Physical - Thesis'],['Physical','Other','Thesis']],
    'Electronic - Conference':[['Electronic','Electronic - Other','Electronic - Conference'],['Electronic','Other','Conference']],
    'Physical - Score':[['Physical','Physical - Other','Physical - Score'],['Physical','Other','Score']],
    'Physical - Microform':[['Physical','Physical - Other','Physical - Microform'],['Physical','Other','Microform']],
    'Electronic - Video':[['Electronic','Electronic - Other','Electronic - Video'],['Electronic','Other','Video']],
    'Physical - Conference':[['Physical','Physical - Conference',''],['Physical','Conference','']],
    'Physical - ':[['Physical','Physical - ',''],['Physical','No type provided','']],
    'Electronic - ':[['Electronic','Electronic - ',''],['Electronic','No type provided','']],
}

cols={}
selectBoxes={}
colors=px.colors.qualitative.Bold
colorsPie=px.colors.qualitative.Safe

def mapToLabelParent(df,map,mapCols,leafLevel,rootName,count):
    sbLists={}
    sbLists['ids']=[]
    sbLists['parents']=[]
    sbLists['labels']=[]
    sbLists['values']=[]
    
    for rowi in range(len(df)):
        row=df.iloc[rowi]
        val=row[leafLevel]
        #Assumes that each row contains unique leaf value
        try: 
            if isinstance(map[val][0], list):
                ids=map[val][0]
                labs=map[val][1]
            else:
                ids=map[val]
                labs=map[val]
            #It's easier to ensure id uniqueness by using parent IDs in name, and it's easier to reference a parent's own compound id by building from top down (rather than leaf up).
            for c in range(len(ids)):
                #i=len(ids)-1-c
                if c!=0:
                    par=ids[c-1]
                    if c>1:
                        fulPar=f'{ids[c-2]}-{par}'
                    else:
                        fulPar=f'{rootName}-{par}'
                else:
                    par=rootName
                    fulPar=rootName
                if ids[c]!='' and f'{par}-{ids[c]}' not in sbLists['ids']:
                    sbLists['ids'].append(f'{par}-{ids[c]}')
                    sbLists['parents'].append(fulPar)
                    sbLists['labels'].append(labs[c])
                    #If this node is a leaf
                    if c+1==len(ids) or (len(ids)>c+1 and ids[c+1])=='':
                        sbLists['values'].append(row[count])
                    else:
                        sbLists['values'].append(0)
        except:
            sbLists['ids'].append('Category not assigned')
            sbLists['parents'].append(rootName)
            sbLists['labels'].append('Category not assigned')
            sbLists['values'].append(row[count])
    #st.write(sbLists)
    return sbLists

#More general funcs
def authBegin():
    with open('conf.yaml') as file:
        config=yaml.load(file, Loader=SafeLoader)
    authenticator = stauth.Authenticate(
        config['credentials'],
        config['cookie']['name'],
        config['cookie']['key'],
        config['cookie']['expiry_days']
    )
    try:
        if st.session_state.get('authentication_status') is None:
            st.warning('Please enter your username and password')
        elif st.session_state.get('authentication_status') is False:
            st.error('Username/password is incorrect')
        authenticator.login(callback=authSub(config,authenticator))
    except Exception as e:
        st.error(e)

def authSub(config,authenticator):
    if st.session_state.get('authentication_status') is True:
        with open('conf.yaml', 'w') as file:
            if len(config)>1:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
        #authenticator.logout(location='sidebar')
        with st.sidebar:
            st.sidebar.success(f'Welcome *{st.session_state.get("name")}*')
        authenticator.logout(location='sidebar')
    
def callFavorites():
    #st.write(st.session_state.get('roles'))
    dfLocals={}
    dfAAs={}
    dfGGs={}
    roles=[]
    un=st.session_state.get('username')
    with open('conf.yaml','r') as file:
        config=yaml.load(file, Loader=SafeLoader)
        for r in config['credentials']['usernames'][un]['roles']:
            roles.append(r)
    if len(roles)==0:
        st.write('You can view your favorite visualizations here. Go to one of the listed dashboard pages to favorite something.')
    if 'analytics' in roles:
        dfAAs=analyticsPrep(dfAAs)
        analyticsDisplay(dfAAs)
    if 'analyticsMonthly' in roles:
        dfAAs=analyticsMonthlyPrep(dfAAs)
        analyticsMonthlyDisplay(dfAAs)
    if 'analyticsMonthlyP' in roles:
        if 'analyticsSPiv' not in dfAAs:
            dfAAs=analyticsMonthlyPrep(dfAAs)
        analyticsMonthlyPDisplay(dfAAs)
    if 'api' in roles:
        dfAAs=apiPrep(dfAAs)
        apiDisplay(dfAAs)
    if 'aspaceCataloging' in roles:
        if 'aspaceCataloging' not in dfLocals:
            dfLocals=aspacePrep(dfLocals)
        aspaceCatalogingDisplay(dfLocals)
    if 'aspaceCatalogingTotals' in roles:
        if 'aspaceCataloging' not in dfLocals:
            dfLocals=aspacePrep(dfLocals)
        aspaceCatalogingTotalsDisplay(dfLocals)
    if 'aspaceCounts' in roles:
        if 'aspaceCounts' not in dfLocals:
            dfLocals=aspacePrep(dfLocals)
        aspaceCountsDisplay(dfLocals)
    if 'cataloging' in roles:
        dfAAs=catalogingPrep(dfAAs)
        catalogingDisplay(dfAAs)
    if 'circLoc' in roles:
        dfAAs=circLocPrep(dfAAs)
        circLocDisplay(dfAAs)
    if 'circLocTotals' in roles:
        if 'circLocTotals' not in dfAAs:
            dfAAs=circLocPrep(dfAAs)
        circLocTotalsDisplay(dfAAs)
    if 'circTotals' in roles:
        dfAAs=circTotalsPrep(dfAAs)
        circTotalsDisplay(dfAAs)
    if 'circUG' in roles:
        dfAAs=circUGPrep(dfAAs)
        circUGDisplay(dfAAs)
    if 'circUGTotals' in roles:
        if 'circUGTotals' not in dfAAs:
            dfAAs=circUGPrep(dfAAs)
        circUGTotalsDisplay(dfAAs)
    if 'counter' in roles:
        dfAAs=counterPrep(dfAAs)
        counterDisplay(dfAAs)
    if 'digital' in roles:
        dfAAs=digitalPrep(dfAAs)
        digitalDisplay(dfAAs)
    if 'gateCount' in roles:
        dfGGs=gateCountPrep(dfGGs)
        gateCountDisplay(dfGGs)
    if 'illBEtypes' in roles:
        if 'illBEtypes' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBEtypesDisplay(dfLocals)
    if 'illBDailyRDT' in roles:
        if 'illBDailyRDT' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBDailyRDTDisplay(dfLocals)
    if 'illBDailyRDTTotals' in roles:
        if 'illBDailyRDT' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBDailyRDTTotalsDisplay(dfLocals)
    if 'illBDailyS' in roles:
        if 'illBDailyS' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBDailySDisplay(dfLocals)
    if 'illBDailySID' in roles:
        if 'illBDailySID' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBDailySIDDisplay(dfLocals)
    if 'illBETS' in roles:
        if 'illBETS' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBETSDisplay(dfLocals)
    if 'illBPTS' in roles:
        if 'illBETS' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBPTSDisplay(dfLocals)
    if 'illBPtypes' in roles:
        if 'illBPtypes' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBPtypesDisplay(dfLocals)
    if 'illBTT' in roles:
        if 'illBTT' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illBTTDisplay(dfLocals)
    if 'illDDDaily' in roles:
        if 'illDDDaily' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illDDDailyDisplay(dfLocals)
    if 'illLEtypes' in roles:
        if 'illLEtypes' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illLEtypesDisplay(dfLocals)
    if 'illLSID' in roles:
        if 'illLSID' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illLSIDDisplay(dfLocals)
    if 'illLPtypes' in roles:
        if 'illLPtypes' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illLPtypesDisplay(dfLocals)
    if 'illLDailyRDT' in roles:
        if 'illLDailyRDT' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illLDailyRDTDisplay(dfLocals)
    if 'illLDailyRDTTotals' in roles:
        if 'illLDailyRDT' not in dfLocals:
            dfLocals=illPrep(dfLocals)
        illLDailyRDTTotalsDisplay(dfLocals)
    if 'lrSources' in roles:
        dfAAs=lrSourcesPrep(dfAAs)
        lrSourcesDisplay(dfAAs)
    if 'lr' in roles:
        dfAAs=lrPrep(dfAAs)
        lrDisplay(dfAAs)
    if 'requestsLsf' in roles:
        if 'requestsLsf' not in dfAAs:
            dfAAs=requestsLsfPrep(dfAAs)
        requestsLsfDisplay(dfAAs)
    if 'requestsLsfCounts' in roles:
        if 'requestsLsfCounts' not in dfAAs:
            dfAAs=requestsLsfPrep(dfAAs)
        requestsLsfCountsDisplay(dfAAs)
    if 'topAnalytics' in roles:
        dfAAs=topAnalyticsPrep(dfAAs)
        topAnalyticsDisplay(dfAAs)
    if 'topCounterJ1' in roles:
        if 'topCounterJ1' not in dfAAs:
            dfAAs=topCounterPrep(dfAAs)
        topCounterJ1Display(dfAAs)
    if 'topCounterM1' in roles:
        if 'topCounterM1' not in dfAAs:
            dfAAs=topCounterPrep(dfAAs)
        topCounterM1Display(dfAAs)
    if 'topCounterB1' in roles:
        if 'topCounterB1' not in dfAAs:
            dfAAs=topCounterPrep(dfAAs)
        topCounterB1Display(dfAAs)
    if 'topDigital' in roles:
        dfAAs=topDigitalPrep(dfAAs)
        topDigitalDisplay(dfAAs)

def buttonGen(f,dfs,dRanges,dfSubsCol,dCol,sumCol,unitLabels,dRangeLabels):
    unique_ids = dfs[0][dfSubsCol].unique()
    trace_indices = {id_val: i for i, id_val in enumerate(unique_ids)}
    f.update_traces(hovertemplate=None,opacity=.8)
    updatemenus=[
            dict(
                buttons=list([
                ]),
                direction="down",
                showactive=True,
                xanchor="left",
                yanchor="top",
                x=-.05, y=1.1
            ),
            dict(
                buttons=list([
                ]),
                active=1,
                direction="down",
                showactive=True,
                xanchor="left",
                yanchor="top",
                x=.1,y=1.1
            )
        ]
    for i,d in enumerate(updatemenus):
        if i==0:
            #Dataframe switch
            for i2,df in enumerate(dfs):
                d['buttons'].append(
                    dict(
                        args=[{"x": [df[df[dfSubsCol] == id_val][dCol].tolist() for id_val in unique_ids],
                             "y": [df[df[dfSubsCol] == id_val][sumCol].tolist() for id_val in unique_ids]},
                            [i for i in range(len(unique_ids))]  # Target all traces
                        ],
                        label=unitLabels[i2],
                        method="restyle"
                    )
                )
        if i==1:
            for i2,dr in enumerate(dRanges):
                d['buttons'].append(
                    dict(
                        args=[{"xaxis.range":dr}],
                        label=dRangeLabels[i2],
                        method="relayout"
                    )
                )
    f.update_layout(
        updatemenus=updatemenus
    )
    f.update_layout(
        annotations=[
            dict(text="Time unit",x=-.05,y=1.18,showarrow=False,xref='paper',yref='paper'),
            dict(text="Time length",x=.1,y=1.18,showarrow=False,xref='paper',yref='paper'),
        ]
    )

def colorFromFlatList(list):
    colorMap={}
    for i,v in enumerate(list):
        try:
            colorMap[v]=px.colors.qualitative.Bold[i]
        except:
            colorMap=colorMap
    return colorMap
    
def colorFromHDict(map,sourceFormat,keyFormat,superRoot):
    colorMap={}
    #Top list reflects px.colors.qualitative.Bold

    ray1=['#7F3C8D', '#11A579', '#3969AC', '#F2B701', '#E73F74', '#80BA5A', '#E68310', '#008695', '#CF1C90', '#F97B72', '#A5AA99']
    ray2=['#A26EB4', '#47BB9C', '#6E90C4', '#F6CC42', '#EC6A91', '#A9D17E', '#EDB145', '#3BB3BF', '#DA4EAE', '#FBA59E', '#C0C2B5']
    ray3=['#C69EDB', '#79D0BA', '#A3B8DA', '#F9E183', '#F297AD', '#D3E8A7', '#F2D07B', '#77DFE8', '#E67DD0', '#FDD0CC', '#D8D8D0']
    ray4=['#EADBF7', '#B6E6DC', '#D9E0EF', '#FDF5C4', '#F8C8D7', '#F1F5D2', '#F9E9B6', '#B7F1F8', '#F2B8EE', '#FEE9E7', '#F1F1EF']

    #ray1=['#3366CC', '#DC3912', '#FF9900', '#109618', '#990099', '#0099C6', '#DD4477', '#66AA00', '#B82E2E', '#316395', '#994499', '#22AA99', '#AAAA11', '#6633CC', '#E67300', '#8B0707', '#654321', '#8B4513', '#778899', '#E69138']
    #ray2=['#6E9CF5', '#E9684C', '#FFBB33', '#49B351', '#BB33BB', '#33B5E0', '#E57398', '#91CA33', '#C95C5C', '#6A8EBB', '#BB7BB3', '#57B5A6', '#BBBB47', '#9373E5', '#F09B33', '#AD3F3F', '#917961', '#AD7A5A', '#9DA9B3', '#F0B16E']
    #ray3=['#AABFF8', '#F29787', '#FFDD66', '#82CD88', '#DD66DD', '#66D1EC', '#F0A1BB', '#C1E297', '#DBC8C8', '#A2BAD2', '#D8AACD', '#8CDBD0', '#DDDD8D', '#BCABF0', '#F7C466', '#C47676', '#BCAB98', '#C4AD99', '#C3CAD1', '#F7D0A4']
    #ray4=['#D5E0FA', '#F9C5BC', '#FFEEC9', '#BBEDA0', '#EE99EE', '#99E3F6', '#F7CDD7', '#DCEFB3', '#EBDFDF', '#D0DBE6', '#E9D2E3', '#B8EDEB', '#EEEEB5', '#DED7F8', '#FBC799', '#D9A1A1', '#E2DACE', '#E3D7CC', '#E0E3E8', '#F9E5CE']
    rays=[ray1,ray2,ray3,ray4]
    rootDir=[]
    nonRootDir=[]
    for k,val in map.items():
        if isinstance(map[k][0], list):
            ids=val[0]
        else:
            ids=val
        for c in range(len(ids)):
            if ids[c]!='':
                if c!=0:
                    anc=ids[0]
                    par=ids[c-1]
                    if ids[c] not in [nr['id'] for nr in nonRootDir]:
                        nonRootDir.append({'id':ids[c],'anc':anc,'par':par,'level':c})
                elif ids[c] not in [r['id'] for r in rootDir]:
                    rootDir.append({'id':ids[c],'par':superRoot})
    #Flat mode w/ hier source needs to wait until all roots encountered, so just populate map all at once at this point
    
    if sourceFormat=='hierarchy':
        for i,val in enumerate(rootDir):
            if keyFormat=='simple':
                k=val['id']
            if keyFormat=='parent-self':
                k=f"{val['par']}-{val['id']}"
            if k not in colorMap:
                colorMap[k]=rays[0][i]
        for i,val in enumerate(nonRootDir):
            if keyFormat=='simple':
                k=val['id']
            if keyFormat=='parent-self':
                k=f"{val['par']}-{val['id']}"
            if k not in colorMap:
                colorMap[k]=rays[val['level']][[r['id'] for r in rootDir].index(val['anc'])]
    if sourceFormat=='flat':
        for i,val in enumerate(rootDir):
            try:
                colorMap[val['id']]=rays[0][i]
            except:
                #Ran out of colors
                colorMap=colorMap
        for i,val in enumerate(nonRootDir):
            try:
                colorMap[val['id']]=rays[0][len(rootDir)+i]
            except:
                #Ran out of colors
                colorMap=colorMap
    #st.write(sourceFormat)
    #st.write(keyFormat)
    #st.write(rootDir)
    #st.write(nonRootDir)
    #st.write(colorMap)
    return colorMap
    
def colorsGen(content,keyFormat):
    colorMap={}
    if content=='illFormat':
        illFormat=['Article','Book Chapter','Book','Conference','Video','Thesis','Microform']
        colorMap=colorFromFlatList(illFormat)
    if content=='illRDT':
        colorMap=colorFromHDict(illBRDTDict,'hierarchy',keyFormat,'Types')
    if content=='illStatus':
        illStatus=['Delivered to Web','Cancelled by Customer','Request Sent','Cancelled by ILL Staff','Request Finished']
        colorMap=colorFromFlatList(illStatus)
    if content=='illNetwork':
        illNetwork=['RAPID','OCLC','ISO','OTH']
        colorMap=colorFromFlatList(illNetwork)   
    if content=='Library':
        libraries=['Sawyer','Schow','LSF','Resource Sharing Library']
        colorMap=colorFromFlatList(libraries)
        colorMap['Library Shelving Facility']=colorMap['LSF']
    if content=='UserGroup':
        colorMap=colorFromHDict(gDict,'hierarchy',keyFormat,'User types')
    if content=='ASObjects':
        colorMap=colorFromHDict(asDict,'hierarchy',keyFormat,'Object types')
    if content=='AlmaLocation':
        colorMap=colorFromHDict(lDict,'hierarchy',keyFormat,'Location types')
    return colorMap
    
def lineBarGen(i,fig,fig2):
    cols[f'{i}_0'],cols[f'{i}_1'],cols[f'{i}_2'],cols[f'{i}_3']=st.columns(4)
    with cols[f'{i}_0']:
        selectBoxes[i] = st.selectbox(
            "Chart type:",
            options=['Line', 'Bar'],
            index=0,
            key=f'k_{i}'
        )
    with cols[f'{i}_3']:
        favButton(i,'inline')
    with st.empty():
        if selectBoxes[i]=='Line':
            st.plotly_chart(fig)
        if selectBoxes[i]=='Bar':
            st.plotly_chart(fig2)

def spreadsheetGet(id,creds,range):
    try:
        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=id,range=range).execute()
        values = result.get('values', [])
        return values
    except HttpError as err:
        print(err)

def dfInit(valuesL):
    df=pd.DataFrame(valuesL)
    df.columns=df.iloc[0]
    df=df.iloc[1:]
    return df
    
def dfAAinit(dfAAs,apath,i):
    dataAA=[]
    url2='https://api-na.hosted.exlibrisgroup.com/almaws/v1/analytics/reports'
    queryParams='?'+urlencode({'apikey':api_key,'path':apath,'limit':'200'}).replace('+','%20')
    headers={'Content-Type':'application/xml'}
    #st.write(url2+queryParams)
    response_body=requests.get(url2+queryParams, headers=headers)
    #st.write(response_body.text)
    root=ET.fromstring(re.sub(r'\sxmlns="[^"]+"', '', response_body.text))
    namespaces={'xsd':'http://www.w3.org/2001/XMLSchema','saw-sql':'urn:saw-sql'}
    ET.register_namespace('xsd','http://www.w3.org/2001/XMLSchema')
    ET.register_namespace('saw-sql','urn:saw-sql')
    #print(int(root.attrib['total_record_count']))
    #numRecords=int(root.attrib['total_record_count'])
    df4=pd.DataFrame()
    row=root.findall(".//xsd:complexType[@name='Row']",namespaces)[0]
    #st.write(row)
    newRow=[]
    for cell in row.findall('.//xsd:element',namespaces):
        #st.write(cell.attrib['{urn:saw-sql}columnHeading'])
        newRow.append(cell.attrib['{urn:saw-sql}columnHeading'])
    dataAA.append(newRow)
    for row in root.findall(".//Row",namespaces):
        newRow=[]
        for cell in row.findall(".//*"):
            newRow.append(cell.text)
        dataAA.append(newRow)
    dfAAs['dfAA'+str(i)]=dfInit(dataAA)
    return dfAAs

def drangeImpute(df,dfSubs,dfSubsCol,imputeCol,dCol,dRange,dFormat):
    if dfSubsCol!='whole':
        for l in dfSubs:
            df1=df[df[dfSubsCol]==l]
            df1=df1.set_index(dCol)
            if 'H' in dFormat:
                date_range=pd.date_range(dRange[0],dRange[1],freq='h').strftime(dFormat)
            else:
                date_range=pd.date_range(dRange[0],dRange[1]).strftime(dFormat)
            #st.write(df1.index[df1.index.duplicated(keep='first')])
            
            df1=df1[~df1.index.duplicated(keep='first')]
            #st.write(df1)
            #st.write(date_range)
            df1=df1.reindex(date_range).reset_index().rename(columns={'index':dCol})
            df1[imputeCol]=df1[imputeCol].fillna(0)
            df1[dfSubsCol]=l
            df=pd.concat([df[df[dfSubsCol]!=l],df1])
    else:
        df=df.set_index(dCol)
        if 'H' in dFormat:
            date_range=pd.date_range(dRange[0],dRange[1],freq='h').strftime(dFormat)
        else:
            date_range=pd.date_range(dRange[0],dRange[1]).strftime(dFormat)
        df=df[~df.index.duplicated(keep='first')]
        df=df.reindex(date_range).reset_index().rename(columns={'index':dCol})
        df[imputeCol]=df[imputeCol].fillna(0)
    return df

def dResample(df,dfSubs,dfSubsCol,unit,sumCol,dCol,format):
    for l in dfSubs:
        df1=df[df[dfSubsCol]==l]
        df1[dCol]=pd.to_datetime(df1[dCol])
        #df1=df1.set_index(dCol)
        #df1=df1[~df1.index.duplicated(keep='first')]
        df1=df1.resample(unit,on=dCol)[[sumCol]].sum()
        df1[dfSubsCol]=l
        df1=df1.reset_index().rename(columns={'index':dCol})
        #df1[dCol]=df1[dCol].astype(str)
        #st.write(df1)
        df=pd.concat([df[df[dfSubsCol]!=l],df1])
    dfX=df[dCol].to_frame().map(strToStr,None,format=format,format2=format)
    df[dCol]=dfX[dCol]
    df.sort_values(by=[dCol,dfSubsCol],inplace=True)
    return df

def dtToStr(x,format,format2):
    try:
        x=datetime.strptime(x,format)
        #return datetime.strftime(x,'%Y')
        return datetime.strftime(x,format2)
    except:
        return x

def favButton(key,mode):
    def fbButtonGen():
        un=st.session_state.get('username')
        #Check roles from file rather than st.session, because fav/unfav action will update roles without refreshing session data
        if key in config['credentials']['usernames'][un]['roles']:
            st.button('Remove from favorites',icon=':material/remove:',key=key,on_click=favButtonUnfav,kwargs={'key':key,'config':config})
        else:
            st.button('Add to favorites',icon=':material/star:',key=key,on_click=favButtonFav,kwargs={'key':key,'config':config})
    with open('conf.yaml') as file:
        config=yaml.load(file, Loader=SafeLoader)
    if mode=='inline':
        #st.html('<div style="height:5px;"></div>')
        fbButtonGen()
    elif mode=='standalone':
        fbCol={}
        fbCol[key+'1'],fbCol[key+'2'],fbCol[key+'3']=st.columns(3)
        with fbCol[key+'3']:
            fbButtonGen()
    
    

def favButtonFav(key,config):
    #st.write('fbf call')
    #with open('conf.yaml','r') as file:
    #    config=yaml.load(file, Loader=SafeLoader)
    un=st.session_state.get('username')
    with open('conf.yaml', 'w') as file:
        if key not in config['credentials']['usernames'][un]['roles']:
            config['credentials']['usernames'][un]['roles'].append(key)
            if len(config)>1:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)
    #favButton(key)
    
def favButtonUnfav(key,config):
    #st.write('fbuf call')
    #with open('conf.yaml','r') as file:
    #    config=yaml.load(file, Loader=SafeLoader)
    un=st.session_state.get('username')
    with open('conf.yaml', 'w') as file:
        if key in config['credentials']['usernames'][un]['roles']:
            config['credentials']['usernames'][un]['roles'].pop(config['credentials']['usernames'][un]['roles'].index(key))
            if len(config)>1:
                yaml.dump(config, file, default_flow_style=False, allow_unicode=True)

    #favButton(key)

def googleCreds():
    creds = None
    # The file token.json stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time. If access expires, delete token.json and re-authorization will occur next time you visit dashboard.
    # You'll need an oauth client registered to a Google account: https://console.cloud.google.com/auth/clients
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(GRequest())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return creds

def hierarchyTraverseforTS(df,map,mapCols,targLevel,origLevel,date,count):
    for k,v in map.items():
        k=k.replace('(','\(').replace(')','\)')
        dfNonTarg=df[~df[origLevel].str.contains(k)]
        dfTarg=df[df[origLevel].str.contains(k)]
        if isinstance(v[0], list):
            ids=v[0]
        else:
            ids=v
        for i,m in enumerate(mapCols):
            #st.write(ids)
            #st.write(mapCols)
            if ids[i]!='':
                dfTarg[m]=ids[i]
            else:
                dfTarg[m]=''
        df=pd.concat([dfNonTarg,dfTarg],ignore_index=True)
    
    #If the map doesn't account for a value, make sure it's labeled as such
    #For iloc to work here, i needs to be positional and not a duplicable label. Enumerate and ignore the label.
    for i,(lab,r) in enumerate(df.iterrows()):
        if type(r[targLevel])==float:
            df.iloc[i,df.columns.get_loc(targLevel)]='Category not assigned'
    dfn=df.copy()
    for val in dfn[targLevel].unique():
        valE=val.replace('(','\(').replace(')','\)')
        dfNonTarg=dfn[~dfn[targLevel].str.contains(valE)]
        dfTarg=dfn[dfn[targLevel].str.contains(valE)]
        for val2 in dfTarg[date].unique():
            dfNonTarg=pd.concat([dfNonTarg,pd.DataFrame({'0':['0'],date:val2,targLevel:[val],count:[dfTarg[dfTarg[date]==val2][count].sum()]})],ignore_index=True)
        dfn=dfNonTarg.copy()
    return dfn
   
def hierarchyTraverseforTStoTotals(df,map,mapCols,origLevel,date,count):
    dfn=df.copy()
    for val in dfn[origLevel].unique():
        valE=val.replace('(','\(').replace(')','\)')
        dfNonTarg=dfn[~dfn[origLevel].str.contains(r'^'+valE+'$',regex=True)]
        dfTarg=dfn[dfn[origLevel].str.contains(r'^'+valE+'$',regex=True)]
        newRows={'0':['0'],origLevel:[val],count:[dfTarg[count].sum()]}
        try:
            if isinstance(map[val], list):
                ids=map[val][0]
            else:
                ids=map[val][1]
            for i,m in enumerate(mapCols):
                if ids[i]!='':
                    newRows[m]=ids[i]
                else:
                    newRows[m]=''
        except:
            for i,m in enumerate(mapCols):
                newRows[m]='Category not assigned'
        dfn=pd.concat([dfNonTarg,pd.DataFrame(newRows)])
    #st.write('Traverse for Totals:')
    #st.write(dfn)
    return dfn
   
def illRangeWeekGet(dfIlls):
    return [(dfIlls['dlast']-relativedelta.relativedelta(days=7)).strftime('%Y-%m-%d'),dfIlls['dlast'].strftime('%Y-%m-%d')]
def illRangeMonthGet(dfIlls):
    return[(dfIlls['dlast']-relativedelta.relativedelta(days=30)).strftime('%Y-%m-%d'),dfIlls['dlast'].strftime('%Y-%m-%d')]

def strToDate(x,format):
    try:
        x=datetime.strptime(x,format)
        #return datetime.strftime(x,'%Y')
        return x
    except Exception as e:
        st.write(e)
        st.write(x)
        return x

def strToStr(x,format,format2):
    try:
        #x=datetime.strftime(x,format)
        #return datetime.strftime(x,'%Y')
        return datetime.strftime(x,format2)
    except:
        #st.write(x)
        return x

def xrange1Get():
    return [(datetime.today()-timedelta(days=7)).strftime('%Y-%m-%d'),datetime.today().strftime('%Y-%m-%d')]
def xrange2Get():
    return [(datetime.today()-relativedelta.relativedelta(months=1)).strftime('%Y-%m-%d'),datetime.today().strftime('%Y-%m-%d')]

#Funcs specific to one or more visualizations
def analyticsPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Analytics daily'
    i='analytics'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)].rename(columns={'Object Type':'Type of use'},inplace=True)
    dfAAs['dfAA'+str(i)]['Num of Queries']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Num of Queries'])
    dfAAs['dfAA'+str(i)].loc[dfAAs['dfAA'+str(i)]['User Record Type']=='Staff','Type of use']='API'
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].pivot_table(values=['Num of Queries'],index=['Type of use','Query Date'],fill_value=0,aggfunc='sum')
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].reset_index()
    drange=[dfAAs['dfAA'+str(i)]['Query Date'].min(),dfAAs['dfAA'+str(i)]['Query Date'].max()]
    dfAAs['dfAA'+str(i)]=drangeImpute(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Type of use'].unique(),'Type of use','Num of Queries','Query Date',drange,'%Y-%m-%d')
    dfAAs['dfAA'+str(i)+'W']=dResample(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Type of use'].unique(),'Type of use','W','Num of Queries','Query Date','%Y-%m-%d')
    return dfAAs

def analyticsDisplay(dfAAs):
    i='analytics'
    fig=px.line(dfAAs['dfAA'+str(i)], x='Query Date', y='Num of Queries',color='Type of use',title='Alma Analytics usage',color_discrete_sequence=colors)
    fig2=px.bar(dfAAs['dfAA'+str(i)], x='Query Date', y='Num of Queries',color='Type of use',title='Alma Analytics usage',color_discrete_sequence=colors)
    for f in [fig,fig2]:
        f.update_traces({'name': 'Oracle platform'}, selector={'name': 'No object assigned'})
        f.update_traces({'name': 'Alma dashboard'}, selector={'name': 'Dashboard'})
        f.update_traces({'name': 'Retrieved from Alma'}, selector={'name': 'Report'})
        f.update_layout(
            #yaxis_range=[0, df2_1['y'].max()],
            xaxis_range=[(datetime.today()-timedelta(days=30)).strftime('%Y-%m-%d'),datetime.today().strftime('%Y-%m-%d')],
            #yaxis_range=[0,100],
            #yaxis_type='log',
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Queries'
        )
        f.add_annotation(showarrow=False,xref='x domain',yref='y domain',x=.5,y=-.2,text="Does not include API access to Analytics (for this dashboard)")
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Type of use','Query Date','Num of Queries',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def analyticsMonthlyPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Analytics monthly'
    i=2
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)].rename(columns={'Object Type':'Type of use'},inplace=True)
    dfAAs['dfAA'+str(i)].loc[dfAAs['dfAA'+str(i)]['User Record Type']=='Staff','Type of use']='API'
    dfAAs['dfAA'+str(i)]['Num of Queries']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Num of Queries'])
    dfanMPiv=dfAAs['dfAA'+str(i)].pivot_table(values=['Num of Queries'],index=['Subject Area'],fill_value=0,aggfunc='sum')
    dfanMPiv=dfanMPiv.reset_index()
    dfanMPiv=dfanMPiv.sort_values(by='Num of Queries', na_position='last', ascending=False)
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].pivot_table(values=['Num of Queries'],index=['Type of use','Query Year-Month'],fill_value=0,aggfunc='sum')
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].reset_index()
    dfAAs['analyticsSPiv']=dfanMPiv
    return dfAAs

def analyticsMonthlyDisplay(dfAAs):
    fig=px.line(dfAAs['dfAA2'], x='Query Year-Month', y='Num of Queries',color='Type of use',title='Analytics Usage')
    fig.update_traces({'name': 'Oracle platform'}, selector={'name': 'No object assigned'})
    fig.update_traces({'name': 'Alma dashboard'}, selector={'name': 'Dashboard'})
    fig.update_traces({'name': 'Retrieved from Alma'}, selector={'name': 'Report'})
    fig.update_layout(
        showlegend=True,
        xaxis_range=[(datetime.today()-relativedelta.relativedelta(months=12)).strftime('%Y-%m'),datetime.today().strftime('%Y-%m')],
        hovermode='closest',
        xaxis_title='Date',
        yaxis_title='Queries'
    )
    fig.update_xaxes(showgrid=True)
    favButton('analyticsMonthly','standalone')
    st.plotly_chart(fig)
    
def analyticsMonthlyPDisplay(dfAAs):
    fig=px.pie(dfAAs['analyticsSPiv'], values='Num of Queries', names='Subject Area', title='Analytics queries by subject area:<br>Last 12 months',color_discrete_sequence=colorsPie)
    favButton('analyticsMonthlyP','standalone')
    st.plotly_chart(fig)

def apiPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/API daily'
    i='api'
    dfAAs=dfAAinit(dfAAs,apath,i)
    drange=[dfAAs['dfAA'+str(i)]['Execution Date'].min(),dfAAs['dfAA'+str(i)]['Execution Date'].max()]
    dfAAs['dfAA'+str(i)]=drangeImpute(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Application Name'].unique(),'Application Name','API Usage - Total','Execution Date',drange,'%Y-%m-%d')
    dfAAs['dfAA'+str(i)]['API Usage - Total']=pd.to_numeric(dfAAs['dfAA'+str(i)]['API Usage - Total'])
    #st.write(dfAAs['dfAA'+str(i)]['API Usage - Total'])
    dfAAs['dfAA'+str(i)+'W']=dResample(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Application Name'].unique(),'Application Name','W','API Usage - Total','Execution Date','%Y-%m-%d')
    return dfAAs

def apiDisplay(dfAAs):
    i='api'
    fig=px.line(dfAAs['dfAA'+str(i)], x='Execution Date', y='API Usage - Total',color='Application Name',title='Alma API usage')
    fig2=px.bar(dfAAs['dfAA'+str(i)], x='Execution Date', y='API Usage - Total',color='Application Name',title='Alma API usage')
    for f in [fig,fig2]:
        f.update_traces(hovertemplate=None,opacity=.8)
        f.update_traces({'name': 'Caiasoft inventory sync'}, selector={'name': 'Caiasoft'})
        f.update_traces({'name': 'Caiasoft requests push from Alma'}, selector={'name': 'Caiasoft export job'})
        f.update_traces({'name': 'Data dashboard'}, selector={'name': 'Alma Analytics'})
        f.update_layout(
            #yaxis_range=[0, df2_1['y'].max()],
            xaxis_range=[(datetime.today()-timedelta(days=30)).strftime('%Y-%m-%d'),datetime.today().strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Calls/Uses'
        )
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Application Name','Execution Date','API Usage - Total',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def aspacePrep(dfLocals):
    dfas=pd.read_csv('aspace.csv')
    dfas=dfas.melt(id_vars=['Date']+['Repository'],var_name='Type',value_name='Count')
    dfas['Repository and Measure']=dfas['Repository']+' - '+dfas['Type']
    dfForTotaling=dfas[dfas['Type'].str.contains("New")]
    dfForTotaling['Repository and Measure']=dfForTotaling['Repository and Measure'].str.replace('New ', '')
    dfLocals['aspaceCatalogingTotals']=hierarchyTraverseforTStoTotals(dfForTotaling,asDict,['Group1','Group2'],'Repository and Measure','Date','Count')
    dfLocals['aspaceCataloging1']=hierarchyTraverseforTS(dfForTotaling,asDict,['Group1','Group2'],'Group1','Repository and Measure','Date','Count')
    drange=[dfas['Date'].min(),dfas['Date'].max()]
    dfLocals['aspaceCounts']=dfas[~dfas['Type'].str.contains("New")]
    dfLocals['aspaceCataloging']=dfas
    dfLocals['aspaceCataloging1W']=dResample(dfLocals['aspaceCataloging1'],dfLocals['aspaceCataloging1']['Group1'].unique(),'Group1','W','Count','Date','%Y-%m-%d')
    dfLocals['aspaceDrange']=drange
    return dfLocals

def aspaceCountsDisplay(dfLocals):
    fig=go.Figure(data=[go.Table(
        header=dict(values=['Repository','Measure','Count']),
        cells=dict(values=[dfLocals['aspaceCounts'][dfLocals['aspaceCounts']['Date']==(datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')]['Repository'],dfLocals['aspaceCounts'][dfLocals['aspaceCounts']['Date']==(datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')]['Type'],dfLocals['aspaceCounts'][dfLocals['aspaceCounts']['Date']==(datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')]['Count']])
    )])
    fig.update_layout(margin=dict(t=90,b=10),height=300,title='ArchivesSpace collection figures')
    favButton('aspaceCounts','standalone')
    st.plotly_chart(fig)
    
def aspaceCatalogingDisplay(dfLocals):
    #Below line if you want to plot from raw data without rollup
    #fig=px.line(dfLocals['aspaceCataloging'][dfLocals['aspaceCataloging']['Type'].str.contains("New")], x='Date', y='Count',color='Repository and Measure',title='ArchivesSpace new resources',markers=True)
    i='aspaceCataloging1'
    fig=px.line(dfLocals['aspaceCataloging1'], x='Date', y='Count',color='Group1',title='ArchivesSpace new resources',color_discrete_sequence=colors,markers=True)
    fig2=px.bar(dfLocals['aspaceCataloging1'], x='Date', y='Count',color='Group1',title='ArchivesSpace new resources',color_discrete_sequence=colors)
    for f in [fig,fig2]:
        f.update_traces(hovertemplate=None,opacity=.8)
        f.update_layout(
            #yaxis_range=[0, df2_1['y'].max()],
            xaxis_range=[(datetime.today()-timedelta(days=30)).strftime('%Y-%m-%d'),datetime.today().strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Count',
            yaxis_range=[0, None],
            legend_title_text='Type'
        )
        f=buttonGen(f,[dfLocals['aspaceCataloging1'],dfLocals['aspaceCataloging1W']],[xrange1Get(),xrange2Get()],'Group1','Date','Count',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)
    
def aspaceCatalogingTotalsDisplay(dfLocals):
    sbLists=mapToLabelParent(dfLocals['aspaceCatalogingTotals'],asDict,['Group1','Group2'],'Repository and Measure','Object types','Count')
    fig2=px.sunburst(
        ids=sbLists['ids'],
        names=sbLists['labels'],
        parents=sbLists['parents'],
        values=sbLists['values'],
        branchvalues='remainder',
        color=sbLists['ids'],
        color_discrete_map=colorsGen('ASObjects','parent-self')
    )
    fig2.update_layout(
        title='ArchivesSpace New Resources'
    )
    favButton('aspaceCatalogingTotals','standalone')
    st.plotly_chart(fig2)

def catalogingPrep(dfAAs):
    i='Cataloging'
    dfAAs=dfAAinit(dfAAs,'/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Cataloging daily','Cataloging')
    dfAAs['dfAACataloging'].rename(columns={'Num of Titles with Physical Items (Active)':'Physical Titles','Num of Titles with Digital Representations (Active)':'Digital Titles','Num of Titles with Electronic Portfolios (Active)':'Electronic Titles'},inplace=True)
    dfAAs['dfAACataloging']['All other new titles']=pd.to_numeric(dfAAs['dfAACataloging']['Num of Titles (All)'])-pd.to_numeric(dfAAs['dfAACataloging']['Physical Titles'])-pd.to_numeric(dfAAs['dfAACataloging']['Electronic Titles'])-pd.to_numeric(dfAAs['dfAACataloging']['Digital Titles'])
    dfAAs['dfAACataloging'].drop(['Num of Titles (All)'], axis=1, inplace=True)
    dfAAs['dfAACataloging']=dfAAs['dfAACataloging'].melt(id_vars=['Title Creation Date']+['0'],var_name='Type',value_name='Titles')
    dfAAs['dfAA'+str(i)+'W']=dResample(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Type'].unique(),'Type','W','Titles','Title Creation Date','%Y-%m-%d')
    return dfAAs

def catalogingDisplay(dfAAs):
    i='Cataloging'
    fig=px.line(dfAAs['dfAACataloging'], x='Title Creation Date', y='Titles',color='Type',title='New titles added to Alma',color_discrete_sequence=colors)
    fig2=px.bar(dfAAs['dfAACataloging'], x='Title Creation Date', y='Titles',color='Type',title='New titles added to Alma',color_discrete_sequence=colors)
    for f in [fig,fig2]:
        f.update_traces(hovertemplate=None,opacity=.8)
        f.update_layout(
            #yaxis_range=[0, df2_1['y'].max()],
            xaxis_range=[(datetime.today()-timedelta(days=30)).strftime('%Y-%m-%d'),datetime.today().strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Titles'
        )
        f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Type','Title Creation Date','Titles',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)
    
def circTotalsPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Circulation daily'
    i='circTotals'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]['Loans (In House + Not In House)']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Loans (In House + Not In House)'])
    drange=[dfAAs['dfAA'+str(i)]['Loan Date'].min(),dfAAs['dfAA'+str(i)]['Loan Date'].max()]
    dfAAs['dfAA'+str(i)]=drangeImpute(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Library Name'].unique(),'Library Name','Loans (In House + Not In House)','Loan Date',drange,'%Y-%m-%d')
    dfAAs['dfAA'+str(i)+'W']=dResample(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Library Name'].unique(),'Library Name','W','Loans (In House + Not In House)','Loan Date','%Y-%m-%d')
    return dfAAs
 
def circTotalsDisplay(dfAAs):
    #st.write(dfAAs.keys())
    #st.write(dfAAs['dfAAcircTotals'])
    i='circTotals'
    fig=px.line(dfAAs['dfAA'+str(i)], x='Loan Date', y='Loans (In House + Not In House)',color='Library Name',color_discrete_map=colorsGen('Library','simple'),title='Circulation by Library')
    fig2=px.bar(dfAAs['dfAA'+str(i)], x='Loan Date', y='Loans (In House + Not In House)',color='Library Name',color_discrete_map=colorsGen('Library','simple'),title='Circulation by Library')
    for f in [fig, fig2]:
        f.update_layout(
            xaxis_range=xrange2Get(),
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Loans'
        )
        fig.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Library Name','Loan Date','Loans (In House + Not In House)',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def circLocPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Circulation loc daily'
    i='circLoc'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]['Loans (In House + Not In House)']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Loans (In House + Not In House)'])
    drange=[dfAAs['dfAA'+str(i)]['Loan Date'].min(),dfAAs['dfAA'+str(i)]['Loan Date'].max()]
    dfAAs['dfAA'+str(i)]=drangeImpute(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Location Name'].unique(),'Location Name','Loans (In House + Not In House)','Loan Date',drange,'%Y-%m-%d')
    
    dfAAs['dfAAcircLoc1']=hierarchyTraverseforTS(dfAAs['dfAA'+str(i)],lDict,['Group1','Group2','Group 3'],'Group1','Location Name','Loan Date','Loans (In House + Not In House)')
    dfAAs['dfAAcircLocTotals']=hierarchyTraverseforTStoTotals(dfAAs['dfAA'+str(i)],lDict,['Group1','Group2','Group3'],'Location Name','Loan Date','Loans (In House + Not In House)')
    #st.write(dfAAs['dfAAcircLoc1'])
    #st.write(dfAAs['dfAAcircLocTotals'])
    #dfAAs['dfAA'+str(i)]['Loans (In House + Not In House)']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Loans (In House + Not In House)'])
    dfAAs['dfAAcircLoc1W']=dResample(dfAAs['dfAAcircLoc1'],dfAAs['dfAAcircLoc1']['Location Name'].unique(),'Location Name','W','Loans (In House + Not In House)','Loan Date','%Y-%m-%d')
    return dfAAs
    
def circLocDisplay(dfAAs):
    i='circLoc1'
    fig=px.line(dfAAs['dfAA'+str(i)], x='Loan Date', y='Loans (In House + Not In House)',color='Group1',title='Circulation by Format',color_discrete_sequence=colors)
    fig2=px.bar(dfAAs['dfAA'+str(i)], x='Loan Date', y='Loans (In House + Not In House)',color='Group1',title='Circulation by Format',color_discrete_sequence=colors)
    fig.update_layout(legend_title_text="Format")
    fig2.update_layout(legend_title_text="Format")
    for f in [fig, fig2]:
        fig.update_traces(hovertemplate=None,opacity=.8)
        fig.update_layout(
            xaxis_range=xrange2Get(),
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Loans'
        )
        fig.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Group1','Loan Date','Loans (In House + Not In House)',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def circLocTotalsDisplay(dfAAs):
    i='circLocTotals'
    #fig=px.sunburst(dfAAs['dfAA'+str(i)],path=['Group1','Group2','Group3'],values='Loans (In House + Not In House)',title='Circulation by Specific Location: Past 30 days')
    #fig.update_layout(legend_title_text="Format")
    favButton(i,'standalone')
    #st.plotly_chart(fig)
    sbLists=mapToLabelParent(dfAAs['dfAA'+str(i)],lDict,['Group1','Group2','Group3'],'Location Name','Location types','Loans (In House + Not In House)')
    fig2=px.sunburst(
        ids=sbLists['ids'],
        names=sbLists['labels'],
        parents=sbLists['parents'],
        values=sbLists['values'],
        branchvalues='remainder',
        color=sbLists['ids'],
        color_discrete_map=colorsGen('AlmaLocation','parent-self')
    )
    fig2.update_layout(
        title='Circulation by Specific Location: Past 30 days'
    )
    st.plotly_chart(fig2)
   
def circUGPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Circulation UG daily'
    i='circUG'
    dfAAs=dfAAinit(dfAAs,apath,i)
    drange=[dfAAs['dfAA'+str(i)]['Loan Date'].min(),dfAAs['dfAA'+str(i)]['Loan Date'].max()]
    dfAAs['dfAA'+str(i)]=drangeImpute(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Patron Group'].unique(),'Patron Group','Loans (Not In House)','Loan Date',drange,'%Y-%m-%d')
    dfAAs['dfAA'+str(i)]['Loans (Not In House)']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Loans (Not In House)'])
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)][dfAAs['dfAA'+str(i)]['Patron Group']!='Library Dept']
    dfAAs['dfAAcircUG1']=hierarchyTraverseforTS(dfAAs['dfAA'+str(i)],gDict,['Group1','Group2','Group3'],'Group1','Patron Group','Loan Date','Loans (Not In House)')
    
    dfAAs['dfAAcircUGTotals']=hierarchyTraverseforTStoTotals(dfAAs['dfAA'+str(i)],gDict,['Group1','Group2','Group3'],'Patron Group','Loan Date','Loans (Not In House)')
    
    #This was some manual grouping of just 'other' category from before more comprehensive user category & grouping was written. Could still be useful for when only minimal grouping is required.
    #df_ugOk=dfAAs['dfAA'+str(i)][~dfAAs['dfAA'+str(i)]['Patron Group'].str.contains('Williamstown Residents|Clark Fellow|Graduates with materials|Surrounding Towns|Nearby College Faculty|Contracted Musicians|Retirees \(Williams\)|Research Associate|Fac/Admin/Staff/Stu Spouse|Alumni & Spouse')]
    #df_ugGrp=dfAAs['dfAA'+str(i)][dfAAs['dfAA'+str(i)]['Patron Group'].str.contains('Williamstown Residents|Clark Fellow|Graduates with materials|Surrounding Towns|Nearby College Faculty|Contracted Musicians|Retirees \(Williams\)|Research Associate|Fac/Admin/Staff/Stu Spouse|Alumni & Spouse')]
    #for val in df_ugGrp['Loan Date'].unique():
    #    df_ugOk=pd.concat([df_ugOk,pd.DataFrame({'0':['0'],'Loan Date':[val],'Patron Group':['Community Borrowers'],'Loans (Not In House)':[df_ugGrp[df_ugGrp['Loan Date']==val]['Loans (Not In House)'].sum()]})])
    #dfAAs['dfAA'+str(i)]=df_ugOk
    
    dfAAs['dfAAcircUG1W']=dResample(dfAAs['dfAAcircUG1'],dfAAs['dfAAcircUG1']['Group1'].unique(),'Group1','W','Loans (Not In House)','Loan Date','%Y-%m-%d')
    return dfAAs

def circUGDisplay(dfAAs):
    i='circUG1'
    fig=px.line(dfAAs['dfAA'+str(i)], x='Loan Date', y='Loans (Not In House)',color='Group1',color_discrete_map=colorsGen('UserGroup','simple'),title='Circulation by User Group')
    fig2=px.bar(dfAAs['dfAA'+str(i)], x='Loan Date', y='Loans (Not In House)',color='Group1',color_discrete_map=colorsGen('UserGroup','simple'),title='Circulation by User Group')
    fig.update_layout(legend_title_text="User Group")
    fig2.update_layout(legend_title_text="User Group")
    for f in [fig, fig2]:
        fig.update_traces(hovertemplate=None,opacity=.8)
        fig.update_layout(
            xaxis_range=xrange2Get(),
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Loans'
        )
        fig.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Group1','Loan Date','Loans (Not In House)',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def circUGTotalsDisplay(dfAAs):
    i='circUGTotals'
    #fig=px.sunburst(dfAAs['dfAA'+str(i)],path=['Group2','Group1','Patron Group'],values='Loans (Not In House)',title='Circulation by Specific User Group: Past 30 days')
    #fig.update_layout(legend_title_text="Format")
    favButton(i,'standalone')
    #st.plotly_chart(fig
    
    sbLists=mapToLabelParent(dfAAs['dfAA'+str(i)],gDict,['Group1','Group2','Group3'],'Patron Group','User types','Loans (Not In House)')
    fig2=px.sunburst(
        ids=sbLists['ids'],
        names=sbLists['labels'],
        parents=sbLists['parents'],
        values=sbLists['values'],
        branchvalues='remainder',
        color=sbLists['ids'],
        color_discrete_map=colorsGen('UserGroup','parent-self'),
        title='Circulation by Specific User Group: Past 30 days'
    )

    #fig2=go.Figure(go.Sunburst(
    #    ids=sbLists['ids'],
    #    labels=sbLists['labels'],
    #    parents=sbLists['parents'],
    #    values=sbLists['values'],
    #    branchvalues='remainder',
    #    marker=dict(colors=colorsGen('UserGroup'))
    #    ))
    #fig2.update_layout(
    #    title='Circulation by Specific User Group: Past 30 days',
    #)
    st.plotly_chart(fig2)

def counterPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/COUNTER monthly'
    i='counter'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].melt(id_vars=['Usage Date Year-Month']+['0'],var_name='Measure',value_name='Usage')
    dfAAs['dfAA'+str(i)+'W']=dResample(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Measure'].unique(),'Measure','W','Usage','Usage Date Year-Month','%Y-%m-%d')

    return dfAAs
    
def counterDisplay(dfAAs):
    i='counter'
    fig=px.line(dfAAs['dfAA'+str(i)], x='Usage Date Year-Month', y='Usage',color='Measure',title='EResource Usage',color_discrete_sequence=colors)
    fig2=px.bar(dfAAs['dfAA'+str(i)], x='Usage Date Year-Month', y='Usage',color='Measure',title='EResource Usage',color_discrete_sequence=colors)
    for f in [fig,fig2]:
        f.update_traces({'name': 'Multimedia views (C5 IR_M1 Total Item Requests)'}, selector={'name': 'IR_M1 - Total Item Requests'})
        f.update_traces({'name': 'Book views (C5 TR_B1 Unique Title Requests)'}, selector={'name': 'TR_B1 - Unique Title Requests'})
        f.update_traces({'name': 'Journal content views (C5 TR_J1 Unique Item Requests)'}, selector={'name': 'TR_J1 - Unique Item Requests'})
        f.update_layout(
            showlegend=True,
            xaxis_range=[(datetime.today()-relativedelta.relativedelta(months=24)).strftime('%Y-%m'),datetime.today().strftime('%Y-%m')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Uses (see legend)'
        )
        f.add_annotation(showarrow=False,xref='x domain',yref='y domain',x=.5,y=-.25,text='Latest month on chart may be missing data from some vendors')
        f.update_xaxes(showgrid=True)
        #f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Measure','Usage Date Year-Month','Usage',['Daily','Weekly'],['1 week','1 month'])
        #f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Measure','Usage Date Year-Month','Usage',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def digitalPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Digital daily'
    i='digital'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].melt(id_vars=['Request Date']+['0'],var_name='Measure',value_name='Usage')
    dfAAs['dfAA'+str(i)+'W']=dResample(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Measure'].unique(),'Measure','W','Usage','Request Date','%Y-%m-%d')
    return dfAAs
    
def digitalDisplay(dfAAs):
    i='digital'
    fig=px.line(dfAAs['dfAA'+str(i)], x='Request Date', y='Usage',color='Measure',title='Digital Usage in Alma',color_discrete_sequence=colors)
    fig2=px.bar(dfAAs['dfAA'+str(i)], x='Request Date', y='Usage',color='Measure',title='Digital Usage in Alma',color_discrete_sequence=colors)
    for f in [fig,fig2]:
        f.update_traces({'name': 'File downloads'}, selector={'name': 'Num of digital file downloads'})
        f.update_traces({'name': 'File views'}, selector={'name': 'Num of digital file views'})
        f.update_traces({'name': 'Representation views'}, selector={'name': 'Num of digital representation views'})
        f.update_traces(hovertemplate=None,opacity=.8)
        f.update_layout(
            xaxis_range=[(datetime.today()-timedelta(days=14)).strftime('%Y-%m-%d'),datetime.today().strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Usage'
        )
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Measure','Request Date','Usage',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def gateCountGather(creds,ssid,lib,values2_1):
    #Todo: handle first 14 days of new year
    for i,n in enumerate(range(int((datetime.today()-timedelta(days=14)).strftime('%m')),int(datetime.today().strftime('%m'))+1)):
        if i==0 and not values2_1:
            newValues=spreadsheetGet(ssid,creds,datetime.strptime(str(n),'%m').strftime('%B')+RANGE_3)
        else:
            newValues=spreadsheetGet(ssid,creds,datetime.strptime(str(n),'%m').strftime('%B')+'!A3'+RANGE_3[3:])
        for i2,v in enumerate(newValues):
            if len(v)>=4:
                if i==0 and not values2_1 and i2==0:
                    v.append('id')
                else:
                    v.append(lib)
        #st.write(newValues)
        values2_1 = values2_1+newValues
    return values2_1

def gateCountInit(values2_1,lib):
    df2_1=dfInit(values2_1).copy()
    df2_1['Patrons']=pd.to_numeric(df2_1['Patrons'])
    df2_1=df2_1.rename(columns={'Date':'x','Patrons':'y'})
    #Some dates use 2-digit years
    for index, row in df2_1.iterrows():
        try:
            if row['x'][-3:-2]=='/':
                df2_1.at[index,'x']=row['x'][:-3]+'/20'+row['x'][-2:]
                #st.write(df2_1.at[index,'x'])
        except:
            ph='ph'
    #st.write(df2_1)
    df2_1X=df2_1['x'].to_frame().map(dtToStr,None,format='%m/%d/%Y',format2='%Y-%m-%d')
    df2_1['x']=df2_1X['x']
    hoursTd=[]
    hoursTm=[]
    lastDate=''
    #pm=False
    #print(df2_1)
    df2_1_s=df2_1.copy().iloc[0:0]
    for index, row in df2_1.iterrows():
        if row['x'] is not None and row['x']!='' and row['x']!='Total for Month' and row['x']!='Date':
            if lastDate!="":
                for h in range(0,24):
                    hS=str(h).zfill(2)
                    if hS not in hoursTd:
                        #Insert is messing up index
                        df2_1_s=pd.concat([df2_1_s,pd.DataFrame({'x':lastDate+' '+hS,'Hour':hS,'Door Count':['0'],'y':0,'id':lib}).set_axis(df2_1.columns,axis=1)],axis=0,ignore_index=True)
            #Reset the day
            lastDate=row['x']
            hoursTd=hoursTm.copy()
            hoursTm=[]
            pm=False
        else:
            df2_1.at[index,'x']=lastDate
        if math.isnan(row['y']) or row['Hour']=='Total' or row['x']=='Total for Month' or row['x']=='Date' or row['Hour'] is None or row['Hour']=='' or row['y']<0 or row['y']>10000:
            df2_1.drop(index, inplace=True)
        else:
            if ':30' in row['Hour']:
                df2_1.at[index,'Hour']=str(int(row['Hour'][:row['Hour'].index(':')])+1)
                #st.write(df2_1.at[index,'Hour'])
            if pm==True:
                try:
                    if df2_1.at[index,'Hour'] != '12':
                        df2_1.at[index,'Hour']=str(int(df2_1.at[index,'Hour'])+12)
                    else:
                        df2_1.at[index,'Hour']='00'
                        newDate=df2_1.at[index,'x']
                        try:                        
                            newDate=datetime.strptime(newDate,'%Y-%m-%d')+timedelta(days=1)
                        except:
                            #st.write(row)
                            #st.write(newDate)
                            st.write('Error: '+df2_1.loc[index])
                            #st.write(df2_1)
                        df2_1.at[index,'x']=datetime.strftime(newDate,'%Y-%m-%d')
                        #df2_1.at[index,'Hour']='24'
                except:
                    st.write('Error at index'+str(index)+': '+str(df2_1.at[index,'Hour'])+ ' length '+str(len(df2_1.at[index,'Hour'])))
            df2_1.at[index,'Hour']=df2_1.at[index,'Hour'].zfill(2)
            if df2_1.at[index,'Hour']!='00':
                hoursTd.append(df2_1.at[index,'Hour'])
            else:
                hoursTm.append(df2_1.at[index,'Hour'])
            df2_1.at[index,'x']=df2_1.at[index,'x']+' '+df2_1.at[index,'Hour']
            if row['Hour']=='12':
                pm=True
    df2_1=pd.concat([df2_1,df2_1_s],axis=0,ignore_index=True)
    df2_1.sort_values(by=['x'],inplace=True)
    print(df2_1)
    data2_1=[]
    for v in df2_1['id'].unique().tolist():
        data2_1.append({'id':v,'data':df2_1.loc[df2_1['id']==v].to_dict(orient='records')})
    return df2_1

def gateCountPrep(dfGGs):
    creds=googleCreds()
    values2_1=gateCountGather(creds,SPREADSHEET_ID2,'Sawyer',[])
    values2_2=gateCountGather(creds,SPREADSHEET_ID3,'Schow',[])
    df2_1=gateCountInit(values2_1,'Sawyer')
    df2_2=gateCountInit(values2_2,'Schow')
    df2_3=pd.concat([df2_1,df2_2])
    drange=[df2_3[df2_3['y']!=0]['x'].min(),df2_3[df2_3['y']!=0]['x'].max()]
    #st.write(drange)
    #st.write(df2_3)
    dfGGs['df2_3']=drangeImpute(df2_3,df2_3['id'].unique(),'id','y','x',drange,'%Y-%m-%d %H')
    #st.write(df2_3)
    dfGGs['df2_3d']=dResample(df2_3,df2_3['id'].unique(),'id','D','y','x','%Y-%m-%d %H')
    return dfGGs

def gateCountYearly():
    values = spreadsheetGet(SPREADSHEET_ID,creds,RANGE_NAME)
    df=dfInit(values).copy()
    df['Gate count']=pd.to_numeric(df['Gate count'].str.replace(',',''))
    df2=df.copy()
    df2=df2.rename(columns={'Year ending in:':'x','Library':'id','Gate count':'y'})
    df2X=df2['x'].to_frame().map(dtToStr,None,format='%m/%d/%Y',format2='%Y')
    df2['x']=df2X['x']
    df2.sort_values(by=['x'],inplace=True)
    data=[]
    for v in df2['id'].unique().tolist():
        data.append({'id':v,'data':df2.loc[df2['id']==v].to_dict(orient='records')})
    return data

def gateCountDisplay(dfGGs):
    dfGGs['df2_3']['x']=pd.to_datetime(dfGGs['df2_3']['x'])
    dfGGs['df2_3d']['x']=pd.to_datetime(dfGGs['df2_3d']['x'])
    fig=px.line(dfGGs['df2_3'], x='x', y='y',color='id',color_discrete_map=colorsGen('Library','simple'),title='Gate Counts')
    fig2=px.bar(dfGGs['df2_3'], x='x', y='y',color='id',color_discrete_map=colorsGen('Library','simple'),title='Gate Counts')
    #fig.update_traces(hovertemplate=None,opacity=.8)
    unique_ids = dfGGs['df2_3']['id'].unique()
    trace_indices = {id_val: i for i, id_val in enumerate(unique_ids)}
    for f in [fig, fig2]:
        f.update_xaxes(type='date',autorange=False,showgrid=True)
        f.update_layout(
            #yaxis_range=[0, df2_1['y'].max()],
            xaxis_range=xrange1Get(),
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Visitors',
            legend_title_text='Library'
            )
        f.update_layout(
            updatemenus=[
                dict(
                    buttons=list([
                        dict(
                            args=[
                                {"x": [dfGGs['df2_3'][dfGGs['df2_3']['id'] == id_val]['x'].tolist() for id_val in unique_ids],
                                 "y": [dfGGs['df2_3'][dfGGs['df2_3']['id'] == id_val]['y'].tolist() for id_val in unique_ids]},
                                [i for i in range(len(unique_ids))]  # Target all traces
                            ],
                            label="Hourly",
                            method="restyle"
                        ),
                        dict(
                            args=[
                                {"x": [dfGGs['df2_3d'][dfGGs['df2_3d']['id'] == id_val]['x'].tolist() for id_val in unique_ids],
                                 "y": [dfGGs['df2_3d'][dfGGs['df2_3d']['id'] == id_val]['y'].tolist() for id_val in unique_ids]},
                                [i for i in range(len(unique_ids))]  # Target all traces
                            ],
                            label="Daily",
                            method="restyle"
                        ),
                    ]),
                    direction="down",
                    showactive=True,
                    xanchor="left",
                    yanchor="top",
                    x=-.05, y=1.1
                ),
                dict(
                    buttons=list([
                        dict(
                            args=[{"xaxis.range":xrange1Get()}],
                            label="1 week",
                            method="relayout"
                        ),
                        dict(
                            args=[{"xaxis.range":xrange2Get()}],
                            label="1 month",
                            method="relayout"
                        )
                    ]),
                    direction="down",
                    showactive=True,
                    xanchor="left",
                    yanchor="top",
                    x=.1,y=1.1
                ),
                
                #dict(
                #    buttons=list([
                #        dict(
                #            args=[{"type":"scatter","mode":"lines"}],
                #            label="Line",
                #            method="relayout"
                #        ),
                #        dict(
                #            args=[{"type":"bar","barmode":"group"}],
                #            label="Bars",
                #            method="relayout"
                #        )
                #    ]),
                #    direction="down",
                #    showactive=True,
                #    xanchor="left",
                #    yanchor="top",
                #    x=.25,y=1.1
                #)
            ]
        )
        f.update_layout(
            annotations=[
                dict(text="Time unit",x=-.05,y=1.18,showarrow=False,xref='paper',yref='paper'),
                dict(text="Time length",x=.1,y=1.18,showarrow=False,xref='paper',yref='paper'),
                #dict(text="Chart type",x=.25,y=1.18,showarrow=False,xref='paper',yref='paper')
            ]
        )
    col1_1,col1_2,col1_3,col1_4=st.columns(4)
    
    with col1_1:
        gateType = st.selectbox(
            "Chart type:",
            options=['Line', 'Bar'],
            index=0,
            key='gate'
        )
    with col1_4:
        favButton('gateCount','inline')
    with st.empty():
        if gateType=='Line':
            st.plotly_chart(fig)
        if gateType=='Bar':
            st.plotly_chart(fig2)

def illPrep(dfIlls):
    creds=googleCreds()
    values = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_4)
    values2 = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_5)
    values3 = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_6)
    values4 = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_7)
    values5 = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_8)
    values6 = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_9)
    values7 = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_10)
    dfIll=dfInit(values).copy()
    dfIll2=dfInit(values2).copy()
    dfIll3=dfInit(values3).copy()
    dfIll4=dfInit(values4).copy()
    dfIll5=dfInit(values5).copy()
    dfIll6=dfInit(values6).copy()
    dfIll7=dfInit(values7).copy()
    dfIllBorrowing=pd.concat([dfIll,dfIll2,dfIll3,dfIll4,dfIll5,dfIll6,dfIll7])
    dfIllBorrowing['Creation Date']=pd.to_datetime(dfIllBorrowing['Creation Date'],errors='raise',format='mixed')
    dfIllBorrowing['Transaction Date']=pd.to_datetime(dfIllBorrowing['Transaction Date'],errors='coerce',format='mixed')
    
    dfIllBorrowing=dfIllBorrowing.sort_values(by='Creation Date', na_position='last', ascending=False)
    dlast=dfIllBorrowing.iloc[0]['Creation Date']
    drange=[dlast-relativedelta.relativedelta(months=3),dlast]
    dfIlls['dlast']=dlast
    dfIlls['drange']=drange
    
    dfIllEtypes=dfIllBorrowing.copy()
    dfIllEtypes=pd.DataFrame(dfIllEtypes[(dfIllEtypes['Request Type']=='Article') & (dfIllEtypes['Creation Date']>drange[0])]['Document Type'].value_counts()).reset_index(drop=False)
    dfIlls['illBEtypes']=dfIllEtypes
    
    dfIllPtypes=dfIllBorrowing.copy()
    dfIllPtypes=pd.DataFrame(dfIllPtypes[(dfIllPtypes['Request Type']=='Loan') & (dfIllPtypes['Creation Date']>drange[0])]['Document Type'].value_counts()).reset_index(drop=False)
    dfIlls['illBPtypes']=dfIllPtypes
    
    dfIllETS=dfIllBorrowing.copy()
    dfIllETS=pd.DataFrame(dfIllETS[(dfIllETS['Creation Date']>drange[0]) & (dfIllETS['Request Type']=='Article')]['Transaction Status'].value_counts()).reset_index(drop=False)
    dfIlls['illBETS']=dfIllETS
    
    dfIllPTS=dfIllBorrowing.copy()
    dfIllPTS=pd.DataFrame(dfIllPTS[(dfIllPTS['Creation Date']>drange[0]) & (dfIllPTS['Request Type']=='Loan')]['Transaction Status'].value_counts()).reset_index(drop=False)
    dfIlls['illBPTS']=dfIllPTS
    
    #Daily timeseries
    dfIllDaily=dfIllBorrowing.copy()
    dfIllDaily=dfIllDaily[(dfIllDaily['Creation Date']>drange[0])]
    dfIllDaily['Creation Date2']=''
    dfIllDaily['Requests']=1
    dfIllDaily['Creation Date2']=dfIllDaily['Creation Date'].to_frame().map(strToStr,None,format='%m/%d/%Y %H:%M:%S',format2='%Y-%m-%d')
    dfIllDailyRDT=dfIllDaily.pivot_table(values=['Requests'],index=['Creation Date2','Request Type','Document Type'],fill_value=0,aggfunc='sum').copy()
    dfIllDailyRDT=dfIllDailyRDT.reset_index()
    dfIllDailyRDT.loc[dfIllDailyRDT['Request Type']=='Article','Request Type']='Electronic'
    dfIllDailyRDT.loc[dfIllDailyRDT['Request Type']=='Loan','Request Type']='Physical'
    dfIllDailyRDT['RDT']=dfIllDailyRDT['Request Type']+' - '+dfIllDailyRDT['Document Type']
    dfIllDailyRDT=drangeImpute(dfIllDailyRDT,dfIllDailyRDT['RDT'].unique(),'RDT','Requests','Creation Date2',drange,'%Y-%m-%d')
    dfIlls['illBDailyRDT']=hierarchyTraverseforTS(dfIllDailyRDT,illBRDTDict,['Group1','Group2','Group3'],'Group1','RDT','Creation Date2','Requests')
    dfIlls['illBDailyRDTW']=dResample(dfIlls['illBDailyRDT'],dfIlls['illBDailyRDT']['Group1'].unique(),'Group1','W','Requests','Creation Date2','%Y-%m-%d')
    dfIlls['illBRDTTotals']=hierarchyTraverseforTStoTotals(dfIllDailyRDT,illBRDTDict,['Group1','Group2','Group3'],'RDT','Creation Date2','Requests')
    #dfAAs['dfAAcircLoc1']=hierarchyTraverseforTS(dfAAs['dfAA'+str(i)],lDict,['Group1','Group2','Group 3'],'Group1','Location Name','Loan Date','Loans (In House + Not In House)')


    #st.write('illBDailyRDT')

    dfIllDailyS=dfIllDaily.pivot_table(values=['Requests'],index=['Creation Date2','Status'],fill_value=0,aggfunc='sum').copy()
    dfIllDailyS=dfIllDailyS.reset_index()
    dfIllDailyS=drangeImpute(dfIllDailyS,dfIllDailyS['Status'].unique(),'Status','Requests','Creation Date2',drange,'%Y-%m-%d')
    dfIlls['illBDailyS']=dfIllDailyS
    dfIlls['illBDailySW']=dResample(dfIlls['illBDailyS'],dfIlls['illBDailyS']['Status'].unique(),'Status','W','Requests','Creation Date2','%Y-%m-%d')

    
    dfIllDailySID=dfIllDaily.pivot_table(values=['Requests'],index=['Creation Date2','System ID'],fill_value=0,aggfunc='sum').copy()
    dfIllDailySID=dfIllDailySID.reset_index()
    dfIllDailySID=drangeImpute(dfIllDailySID,dfIllDailySID['System ID'].unique(),'System ID','Requests','Creation Date2',drange,'%Y-%m-%d')
    dfIlls['illBDailySID']=dfIllDailySID
    dfIlls['illBDailySIDW']=dResample(dfIlls['illBDailySID'],dfIlls['illBDailySID']['System ID'].unique(),'System ID','W','Requests','Creation Date2','%Y-%m-%d')


    #Transit time
    dfIllTT=dfIllBorrowing.copy()
    dfIllTT=pd.DataFrame(dfIllTT[(dfIllTT['Transaction Status']=='Delivered to Web') & (dfIllTT['Creation Date']>drange[0])])
    dfIllTT['Transaction Date']=pd.to_datetime(dfIllTT['Transaction Date'],errors='coerce',format='%m/%d/%Y %H:%M:%S')
    dfIllTT['Turnaround Time']=''
    for index, row in dfIllTT.iterrows():
        diff=(row['Transaction Date']-row['Creation Date']).total_seconds()/60
        dfIllTT.at[index,'Turnaround Time']=diff
    dfIlls['illBTT']=dfIllTT
    #st.write(dfIllTT)
    
    #LSF
    dfIllDD=dfIllBorrowing.copy()
    dfIllDD=pd.DataFrame(dfIllDD[(dfIllDD['Process Type']=='Doc Del') & ((dfIllDD['Location'].str.contains('LSF')) | (dfIllDD['Location'].str.contains('awyer')) | (dfIllDD['Location'].str.contains('chow'))) & (dfIllDD['Creation Date']>drange[0])][['Document Type','System ID','Creation Date','Transaction Date','Location']])
    #dfIlls['iLLDDDaily']=dfILLDDDaily
    
    values8 = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_11)
    values9 = spreadsheetGet(SPREADSHEET_ID4,creds,RANGE_12)
    dfIll8=dfInit(values8).copy()
    dfIll9=dfInit(values9).copy()
    dfIllLending=pd.concat([dfIll8,dfIll9])
    dfIllLending['Creation Date']=pd.to_datetime(dfIllLending['Creation Date'],errors='raise',format='mixed')
    dfIllLending['Transaction Date']=pd.to_datetime(dfIllLending['Transaction Date'],errors='coerce',format='mixed')
    
    dfIllLendingDD=dfIllLending.copy()
    dfIllLendingDD=pd.DataFrame(dfIllLendingDD[(dfIllLendingDD['Request Type']=='Article') & ((dfIllLendingDD['Location'].str.contains('LSF')) | (dfIllLendingDD['Location'].str.contains('awyer')) | (dfIllLendingDD['Location'].str.contains('chow'))) & (dfIllLendingDD['Creation Date']>drange[0])][['Document Type','System ID','Creation Date','Transaction Date','Location']])
    dfIllDDDaily=pd.concat([dfIllDD,dfIllLendingDD])
    dfIllDDDaily['Library']=''
    dfIllDDDaily.loc[dfIllDDDaily['Location'].str.contains('LSF'),'Library']='LSF'
    dfIllDDDaily.loc[dfIllDDDaily['Location'].str.contains('awyer'),'Library']='Sawyer'
    dfIllDDDaily.loc[dfIllDDDaily['Location'].str.contains('chow'),'Library']='Schow'
    dfIllDDDaily['Requests']=1
    dfIllDDDaily['Creation Date2']=dfIllDDDaily['Creation Date'].to_frame().map(strToStr,None,format='%m/%d/%Y %H:%M:%S',format2='%Y-%m-%d')
    dfIllDDDaily=dfIllDDDaily.pivot_table(values=['Requests'],index=['Creation Date2','Library'],fill_value=0,aggfunc='sum').copy()
    dfIllDDDaily=dfIllDDDaily.reset_index()
    dfIllDDDaily=drangeImpute(dfIllDDDaily,dfIllDDDaily['Library'].unique(),'Library','Requests','Creation Date2',drange,'%Y-%m-%d')
    dfIlls['illDDDaily']=dfIllDDDaily
    dfIlls['illDDDailyW']=dResample(dfIlls['illDDDaily'],dfIlls['illDDDaily']['Library'].unique(),'Library','W','Requests','Creation Date2','%Y-%m-%d')

    
    dfIllLEtypes=dfIllLending.copy()
    dfIllLEtypes=pd.DataFrame(dfIllLEtypes[(dfIllLEtypes['Request Type']=='Article') & (dfIllLEtypes['Creation Date']>drange[0])]['Document Type'].value_counts()).reset_index(drop=False)
    dfIllLEtypes.loc[dfIllLEtypes['Document Type']=='','Document Type']='No information'
    dfIlls['illLEtypes']=dfIllLEtypes
    
    dfIllLPtypes=dfIllLending.copy()
    dfIllLPtypes=pd.DataFrame(dfIllLPtypes[(dfIllLPtypes['Request Type']=='Loan') & (dfIllLPtypes['Creation Date']>drange[0])]['Document Type'].value_counts()).reset_index(drop=False)
    dfIllLPtypes.loc[dfIllLPtypes['Document Type']=='','Document Type']='No information'
    dfIlls['illLPtypes']=dfIllPtypes

    dfIllLDaily=dfIllLending.copy()
    dfIllLDaily=dfIllLDaily[(dfIllLDaily['Creation Date']>drange[0])]
    dfIllLDaily['Creation Date2']=''
    dfIllLDaily['Requests']=1
    dfIllLDaily['Creation Date2']=dfIllLDaily['Creation Date'].to_frame().map(strToStr,None,format='%m/%d/%Y %H:%M:%S',format2='%Y-%m-%d')
    dfIllLDailyRDT=dfIllLDaily.pivot_table(values=['Requests'],index=['Creation Date2','Request Type','Document Type'],fill_value=0,aggfunc='sum').copy()
    dfIllLDailyRDT=dfIllLDailyRDT.reset_index()
    dfIllLDailyRDT.loc[dfIllLDailyRDT['Request Type']=='Article','Request Type']='Electronic'
    dfIllLDailyRDT.loc[dfIllLDailyRDT['Request Type']=='Loan','Request Type']='Physical'
    dfIllLDailyRDT['RDT']=dfIllLDailyRDT['Request Type']+' - '+dfIllLDailyRDT['Document Type']
    dfIllLDailyRDT=drangeImpute(dfIllLDailyRDT,dfIllLDailyRDT['RDT'].unique(),'RDT','Requests','Creation Date2',drange,'%Y-%m-%d')
    dfIlls['illLDailyRDT']=dfIllLDailyRDT
    #dfIlls['illLDailyRDTW']=dResample(dfIlls['illLDailyRDT'],dfIlls['illLDailyRDT']['RDT'].unique(),'RDT','W','Requests','Creation Date2','%Y-%m-%d')
    dfIlls['illLDailyRDT']=hierarchyTraverseforTS(dfIllLDailyRDT,illBRDTDict,['Group1','Group2','Group3'],'Group1','RDT','Creation Date2','Requests')
    dfIlls['illLDailyRDTW']=dResample(dfIlls['illLDailyRDT'],dfIlls['illLDailyRDT']['Group1'].unique(),'Group1','W','Requests','Creation Date2','%Y-%m-%d')
    dfIlls['illLRDTTotals']=hierarchyTraverseforTStoTotals(dfIllLDailyRDT,illBRDTDict,['Group1','Group2','Group3'],'RDT','Creation Date2','Requests')


    dfIllLSID=dfIllLending.copy()
    dfIllLSID=pd.DataFrame(dfIllLSID[(dfIllLSID['Creation Date']>drange[0])]['System ID'].value_counts()).reset_index(drop=False)
    dfIlls['illLSID']=dfIllLSID
    
    return dfIlls

def illBEtypesDisplay(dfIlls):
    fig=px.pie(dfIlls['illBEtypes'], values='count', names='Document Type',
        color='Document Type',color_discrete_map=colorsGen('illFormat','simple'),
        title='ILL Electronic Borrowing Request Types: <br>'+datetime.strftime(dfIlls['drange'][0],'%B %d, %Y')+'-'+datetime.strftime(dfIlls['drange'][1],'%B %d, %Y'))
    favButton('illBEtypes','standalone')
    st.plotly_chart(fig)

def illBDailyRDTDisplay(dfIlls):
    i='illBDailyRDT'
    #fig=px.line(dfIlls['illBDailyRDT'], x='Creation Date2', y='Requests',title='ILL borrowing by type: daily',color='Request Type')
    #st.write(dfIlls['illBDailyRDT'])
    fig=px.line(dfIlls['illBDailyRDT'], x='Creation Date2', y='Requests',title='ILL borrowing by format',color='Group1',color_discrete_map=colorsGen('illRDT','simple'))
    fig2=px.bar(dfIlls['illBDailyRDT'], x='Creation Date2', y='Requests',title='ILL borrowing by format',color='Group1',color_discrete_map=colorsGen('illRDT','simple'))
    for f in [fig, fig2]:
        f.update_layout(
            showlegend=True,
            xaxis_range=[(dfIlls['dlast']-relativedelta.relativedelta(days=60)).strftime('%Y-%m-%d'),dfIlls['dlast'].strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Requests',
            legend_title_text='Type'
        )
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfIlls['illBDailyRDT'],dfIlls['illBDailyRDTW']],[illRangeWeekGet(dfIlls),illRangeMonthGet(dfIlls)],
            'Group1','Creation Date2','Requests',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)
    
def illBDailyRDTTotalsDisplay(dfIlls):
    #Check on data window
    #st.write(dfIlls['illBRDTTotals'])
    favButton('illBDailyRDTTotals','standalone')
    sbLists=mapToLabelParent(dfIlls['illBRDTTotals'],illBRDTDict,['Group1','Group2'],'RDT','Types','Requests')
    fig=px.sunburst(
        ids=sbLists['ids'],
        names=sbLists['labels'],
        parents=sbLists['parents'],
        values=sbLists['values'],
        branchvalues='remainder',
        color=sbLists['ids'],
        color_discrete_map=colorsGen('illRDT','parent-self'),
        title='ILL borrowing by specific format'
        )
    fig.update_layout(
        legend_title_text='Type',
        title='ILL borrowing by specific format'
    )
    st.plotly_chart(fig)

def illBDailySDisplay(dfIlls):
    i='illBDailyS'
    fig=px.line(dfIlls['illBDailyS'], x='Creation Date2', y='Requests',title='ILL borrowing by user',color='Status',color_discrete_map=colorsGen('UserGroup','simple'))
    fig2=px.bar(dfIlls['illBDailyS'], x='Creation Date2', y='Requests',title='ILL borrowing by user',color='Status',color_discrete_map=colorsGen('UserGroup','simple'))
    for f in [fig, fig2]:
        f.update_layout(
            showlegend=True,
            xaxis_range=[(dfIlls['dlast']-relativedelta.relativedelta(days=60)).strftime('%Y-%m-%d'),dfIlls['dlast'].strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Requests'
        )
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfIlls[i],dfIlls[i+'W']],[illRangeWeekGet(dfIlls),illRangeMonthGet(dfIlls)],'Status','Creation Date2','Requests',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def illBDailySIDDisplay(dfIlls):
    i='illBDailySID'
    fig=px.line(dfIlls['illBDailySID'], x='Creation Date2', y='Requests',title='ILL borrowing by fulfillment network',color='System ID',color_discrete_sequence=colors)
    fig2=px.bar(dfIlls['illBDailySID'], x='Creation Date2', y='Requests',title='ILL borrowing by fulfillment network',color='System ID',color_discrete_sequence=colors)
    for f in [fig,fig2]:
        f.update_traces({'name': 'Other'}, selector={'name': 'OTH'})
        f.update_layout(
            showlegend=True,
            xaxis_range=[(dfIlls['dlast']-relativedelta.relativedelta(days=60)).strftime('%Y-%m-%d'),dfIlls['dlast'].strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Requests'
        )
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfIlls[i],dfIlls[i+'W']],[illRangeWeekGet(dfIlls),illRangeMonthGet(dfIlls)],'System ID','Creation Date2','Requests',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def illBETSDisplay(dfIlls):
    fig=px.pie(dfIlls['illBETS'], values='count', names='Transaction Status', 
        color='Transaction Status',color_discrete_map=colorsGen('illStatus','simple'),
        title='ILL Electronic Borrowing Request Statuses: <br>'+datetime.strftime(dfIlls['drange'][0],'%B %d, %Y')+'-'+datetime.strftime(dfIlls['drange'][1],'%B %d, %Y'))
    favButton('illBETS','standalone')
    st.plotly_chart(fig)

def illBPTSDisplay(dfIlls):
    fig=px.pie(dfIlls['illBPTS'], values='count', names='Transaction Status',
        color='Transaction Status',color_discrete_map=colorsGen('illStatus','simple'),
        title='ILL Physical Borrowing Request Statuses: <br>'+datetime.strftime(dfIlls['drange'][0],'%B %d, %Y')+'-'+datetime.strftime(dfIlls['drange'][1],'%B %d, %Y'))
    favButton('illBPTS','standalone')
    st.plotly_chart(fig)

def illBPtypesDisplay(dfIlls):
    fig=px.pie(dfIlls['illBPtypes'], values='count', names='Document Type',
        color='Document Type',color_discrete_map=colorsGen('illFormat','simple'),
        title='ILL Physical Borrowing Request Types: <br>'+datetime.strftime(dfIlls['drange'][0],'%B %d, %Y')+'-'+datetime.strftime(dfIlls['drange'][1],'%B %d, %Y'))
    favButton('illBPtypes','standalone')
    st.plotly_chart(fig)

def illBTTDisplay(dfIlls):
    minBins=[-1,5,10,30,60,120,300,1440,10080,86400]
    #st.write(dfIlls['illBTT'])
    hist_data=(
        pd.cut(dfIlls['illBTT']['Turnaround Time'],minBins,labels=['5 minutes or less','5-10 minutes','10-30 minutes','30-60 minutes','1-2 hours','2-5 hours','5h to 1 day','1-7 days','1+ weeks']).sort_values().astype(str)
    )
    fig=px.histogram(hist_data,labels={'count':'Requests','value':'Turnaround Time','variable':'variable'},title='Electronic borrowing turnaround times:<br>'+datetime.strftime(dfIlls['drange'][0],'%B %d, %Y')+'-'+datetime.strftime(dfIlls['drange'][1],'%B %d, %Y'))
    fig.update_layout(showlegend=False)
    favButton('illBTT','standalone')
    st.plotly_chart(fig)

def illDDDailyDisplay(dfIlls):
    i='illDDDaily'
    fig=px.line(dfIlls['illDDDaily'], x='Creation Date2', y='Requests',title='Document scans (borrowing and lending)',color='Library',color_discrete_sequence=colors)
    fig2=px.bar(dfIlls['illDDDaily'], x='Creation Date2', y='Requests',title='Document scans (borrowing and lending)',color='Library',color_discrete_sequence=colors)
    for f in [fig,fig2]:
        f.update_layout(
            showlegend=True,
            xaxis_range=[(dfIlls['dlast']-relativedelta.relativedelta(days=60)).strftime('%Y-%m-%d'),dfIlls['dlast'].strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Requests'
        )
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfIlls[i],dfIlls[i+'W']],[illRangeWeekGet(dfIlls),illRangeMonthGet(dfIlls)],'Library','Creation Date2','Requests',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def illLEtypesDisplay(dfIlls):
    fig=px.pie(dfIlls['illLEtypes'], values='count', names='Document Type', title='ILL Electronic Lending Request Types: <br>'+datetime.strftime(dfIlls['drange'][0],'%B %d, %Y')+'-'+datetime.strftime(dfIlls['drange'][1],'%B %d, %Y'),
        color='Document Type',color_discrete_map=colorsGen('illFormat','simple'))
    favButton('illLEtypes','standalone')
    st.plotly_chart(fig)
    
def illLSIDDisplay(dfIlls):
    fig=px.pie(dfIlls['illLSID'], values='count', names='System ID', title='ILL Lending by Fulfillment Network: <br>'+datetime.strftime(dfIlls['drange'][0],'%B %d, %Y')+'-'+datetime.strftime(dfIlls['drange'][1],'%B %d, %Y'),
        color='System ID',color_discrete_map=colorsGen('illNetwork','simple'))
    favButton('illLSID','standalone')
    st.plotly_chart(fig)
    
def illLPtypesDisplay(dfIlls):
    fig=px.pie(dfIlls['illLPtypes'], values='count', names='Document Type', title='ILL Physical Lending Request Types: <br>'+datetime.strftime(dfIlls['drange'][0],'%B %d, %Y')+'-'+datetime.strftime(dfIlls['drange'][1],'%B %d, %Y'),
        color='Document Type',color_discrete_map=colorsGen('illFormat','simple'))
    favButton('illLPtypes','standalone')
    st.plotly_chart(fig)

def illLDailyRDTDisplay(dfIlls):
    i='illLDailyRDT'
    fig=px.line(dfIlls['illLDailyRDT'], x='Creation Date2', y='Requests',title='ILL lending by format',color='Group1',color_discrete_map=colorsGen('illRDT','simple'))
    fig2=px.bar(dfIlls['illLDailyRDT'], x='Creation Date2', y='Requests',title='ILL lending by format',color='Group1',color_discrete_map=colorsGen('illRDT','simple'))
    for f in [fig,fig2]:
        f.update_traces({'name': 'Electronic - No type provided'}, selector={'name': 'Electronic - '}),
        f.update_traces({'name': 'Physical - No type provided'}, selector={'name': 'Physical - '}),
        f.update_layout(
            showlegend=True,
            xaxis_range=[(dfIlls['dlast']-relativedelta.relativedelta(days=60)).strftime('%Y-%m-%d'),dfIlls['dlast'].strftime('%Y-%m-%d')],
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Requests',
            legend_title_text='Format'
        )
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfIlls[i],dfIlls[i+'W']],[illRangeWeekGet(dfIlls),illRangeMonthGet(dfIlls)],'Group1','Creation Date2','Requests',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)
    
def illLDailyRDTTotalsDisplay(dfIlls):
    favButton('illLDailyRDTTotals','standalone')
    sbLists=mapToLabelParent(dfIlls['illLRDTTotals'],illBRDTDict,['Group1','Group2'],'RDT','Types','Requests')
    fig=px.sunburst(
        ids=sbLists['ids'],
        names=sbLists['labels'],
        parents=sbLists['parents'],
        values=sbLists['values'],
        branchvalues='remainder',
        color=sbLists['ids'],
        color_discrete_map=colorsGen('illRDT','parent-self'),
        title='ILL lending by specific format'
        )
    fig.update_layout(
        legend_title_text='Type',
        title='ILL lending by specific format'
    )
    st.plotly_chart(fig)

def lrSourcesPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Top link resolver sources'
    i='lrSources'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]['Number of Requests']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Number of Requests'])
    return dfAAs

def lrSourcesDisplay(dfAAs):
    i='lrSources'
    s1=dfAAs['dfAA'+str(i)].sort_values(by='Number of Requests', na_position='last', ascending=False).head(5)
    fig=go.Figure(data=[go.Table(
        header=dict(values=['Requests','Requests resulting in full text click','Source']),
        cells=dict(values=[s1['Number of Requests'],s1['Number of Clicked Requests'],s1['Source Type']])
    )])
    fig.update_layout(margin=dict(t=90,b=10),height=300,title='Top 5 sources for <br>inbound link resolver requests:<br>Last 30 days')
    favButton('lrSources','standalone')
    st.plotly_chart(fig)

def lrPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Link resolver daily'
    i='lr'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]['Inbound requests that found outbound full text']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Number of Requests'])-pd.to_numeric(dfAAs['dfAA'+str(i)]['Number of Requests Without Services'])
    dfAAs['dfAA'+str(i)].rename(columns={'Number of Requests Without Services':'Inbound requests that found no outbound full text','Number of Clicked Services (total)':'Outbound clicks (total)','Number of Clicked Requests':'Inbound requests that led to outbound full text clicks','Number of Requests':'Inbound requests (total)'},inplace=True)
    dfAAs['dfAA'+str(i)].drop(['% Clicks from Requests','% Requests Without Services from Requests'], axis=1, inplace=True)
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].melt(id_vars=['Request Date']+['0'],var_name='Measure',value_name='Usage')
    dfAAs['dfAA'+str(i)+'W']=dResample(dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)]['Measure'].unique(),'Measure','W','Usage','Request Date','%Y-%m-%d')

    return dfAAs

def lrDisplay(dfAAs):
    i='lr'
    fig=px.line(dfAAs['dfAA'+str(i)], x='Request Date', y='Usage',title='Link resolver usage',color='Measure',color_discrete_sequence=colors)
    fig2=px.bar(dfAAs['dfAA'+str(i)], x='Request Date', y='Usage',title='Link resolver usage',color='Measure',color_discrete_sequence=colors)
    for f in [fig,fig2]:
        f.add_annotation(showarrow=False,xref='x domain',yref='y domain',x=.5,y=-.15,text="Note that AGS and ILL do not count as 'Outbound Full Text'")
        f.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfAAs['dfAA'+str(i)],dfAAs['dfAA'+str(i)+'W']],[xrange1Get(),xrange2Get()],'Measure','Request Date','Usage',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def requestsLsfPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Requests LSF daily'
    i='requestsLsf'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]['# of requests']=pd.to_numeric(dfAAs['dfAA'+str(i)]['# of requests'])
    dfAAs['dfAA'+str(i)]['Average Total Request Time (Hours)']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Average Total Request Time (Hours)'])
    dfAAs['dfLsfReqTotals']=dfAAs['dfAA'+str(i)][['# of requests','Request Date']].groupby('Request Date').agg({'# of requests':'sum'}).reset_index()
    def weightRT(group):
        d=group['Average Total Request Time (Hours)']
        w=group['# of requests']
        return round((d*w).sum()/w.sum(),0)
    dfAAs['dfLsfReqTypeTimes']=dfAAs['dfAA'+str(i)][['# of requests','Request Type Description','Average Total Request Time (Hours)']].groupby('Request Type Description').apply(weightRT).reset_index()
    dfAAs['dfLsfReqTypeTotals']=dfAAs['dfAA'+str(i)][['# of requests','Request Type Description','Average Total Request Time (Hours)']].groupby('Request Type Description').agg({'# of requests':'sum'}).reset_index()
    #st.write(dfAAs['dfLsfReqTotals'])
    drange=[dfAAs['dfLsfReqTotals']['Request Date'].min(),(datetime.today()-timedelta(days=1)).strftime('%Y-%m-%d')]
    dfAAs['dfLsfReqTotals']=drangeImpute(dfAAs['dfLsfReqTotals'],'whole','whole','# of requests','Request Date',drange,'%Y-%m-%d')
    dfAAs['dfLsfReqTotals']['# of requests']=pd.to_numeric(dfAAs['dfLsfReqTotals']['# of requests'])
    dfAAs['dfLsfReqTotals']['Request Type Description']='All requests'
    dfAAs['dfLsfReqTotalsW']=dResample(dfAAs['dfLsfReqTotals'],dfAAs['dfLsfReqTotals']['Request Type Description'].unique(),'Request Type Description','W','# of requests','Request Date','%Y-%m-%d')
    return dfAAs
   
def requestsLsfDisplay(dfAAs):
    i='requestsLsf'
    fig=px.line(dfAAs['dfLsfReqTotals'], x='Request Date', y='# of requests',title='Requests to LSF',color_discrete_sequence=colors)
    fig2=px.bar(dfAAs['dfLsfReqTotals'], x='Request Date', y='# of requests',title='Requests to LSF',color_discrete_sequence=colors)
    for f in [fig, fig2]:
        fig.update_traces(hovertemplate=None,opacity=.8)
        fig.update_layout(
            xaxis_range=xrange2Get(),
            hovermode='closest',
            xaxis_title='Date',
            yaxis_title='Loans'
        )
        fig.update_xaxes(showgrid=True)
        f=buttonGen(f,[dfAAs['dfLsfReqTotals'],dfAAs['dfLsfReqTotalsW']],[xrange1Get(),xrange2Get()],'Request Type Description','Request Date','# of requests',['Daily','Weekly'],['1 week','1 month'])
    lineBarGen(i,fig,fig2)

def requestsLsfCountsDisplay(dfAAs):
    favButton('requestsLsfCounts','standalone')
    col1b,col2b=st.columns(2)
    with col1b:
        fig=go.Figure(data=[go.Table(
            header=dict(values=['Request Type','Requests']),
            cells=dict(values=[dfAAs['dfLsfReqTypeTotals']['Request Type Description'],dfAAs['dfLsfReqTypeTotals']['# of requests']])
        )])
        fig.update_layout(margin=dict(t=50,b=10),height=200,title='LSF requests by type: Last 30 days')
        st.plotly_chart(fig)
    with col2b:
        fig=go.Figure(data=[go.Table(
            header=dict(values=['Request Type','Average Hours to Complete']),
            cells=dict(values=[dfAAs['dfLsfReqTypeTimes']['Request Type Description'],dfAAs['dfLsfReqTypeTimes'][0]])
        )])
        fig.update_layout(margin=dict(t=50,b=10),height=200,title='LSF average request times (in hours): Last 30 days')
        st.plotly_chart(fig)  

def topAnalyticsPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Top analytics'
    i='topAnalytics'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]['Num of Queries']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Num of Queries'])
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].sort_values(by=('Num of Queries'), na_position='last', ascending=False).head(5)
    return dfAAs

def topAnalyticsDisplay(dfAAs):
    i='topAnalytics'
    fig=go.Figure(data=[go.Table(
        header=dict(values=['Queries','Report name','Subject Area']),
        cells=dict(values=[dfAAs['dfAA'+str(i)]['Num of Queries'],dfAAs['dfAA'+str(i)]['Report Path'],dfAAs['dfAA'+str(i)]['Subject Area']])
    )])
    fig.update_layout(margin=dict(t=50,b=10),height=200,title='Top 5 analytics for last 30 days')
    favButton('topAnalytics','standalone')
    st.plotly_chart(fig)

def topCounterPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Top JR BR IR'
    i='topCounter'
    dfAAs=dfAAinit(dfAAs,apath,i)
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].melt(id_vars=['Usage Date Year-Month']+['0']+['Platform'],var_name='Measure',value_name='Usage')
    yml=np.sort(dfAAs['dfAA'+str(i)]['Usage Date Year-Month'].unique())
    dfAAs['targYM']=yml[len(yml)-2:-1][0]
    dfAAs['prevTargYM']=yml[len(yml)-3:-2][0]
    dfAAs['dfAA'+str(i)]['Usage']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Usage'])
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)][(dfAAs['dfAA'+str(i)]['Usage Date Year-Month']==dfAAs['targYM']) | (dfAAs['dfAA'+str(i)]['Usage Date Year-Month']==dfAAs['prevTargYM'])]
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].pivot_table(columns='Usage Date Year-Month',values=['Usage'],index=['Platform','Measure'],fill_value=0,aggfunc='sum')
    dfAAs['dfAA'+str(i)]=dfAAs['dfAA'+str(i)].reset_index()
    return dfAAs

def topCounterJ1Display(dfAAs):
    i='topCounter'
    j1=dfAAs['dfAA'+str(i)][dfAAs['dfAA'+str(i)]['Measure']=='TR_J1 - Unique Item Requests'].sort_values(by=('Usage',dfAAs['targYM']), na_position='last', ascending=False).head(5)
    fig=go.Figure(data=[go.Table(
        header=dict(values=['Usage','Prior month (for comparison)','Platform']),
        cells=dict(values=[j1[('Usage',dfAAs['targYM'])],j1[('Usage',dfAAs['prevTargYM'])],j1['Platform']])
    )])
    fig.update_layout(margin=dict(t=50,b=10),height=200,title='Top 5 platforms for <br>J1 (ejournal) requests in '+datetime.strptime(dfAAs['targYM'],'%Y-%m').strftime('%B %Y'))
    favButton('topCounterJ1','standalone')
    st.plotly_chart(fig)
    
def topCounterM1Display(dfAAs):
    i='topCounter'
    m1=dfAAs['dfAA'+str(i)][dfAAs['dfAA'+str(i)]['Measure']=='IR_M1 - Total Item Requests'].sort_values(by=('Usage',dfAAs['targYM']), na_position='last', ascending=False).head(5) 
    fig=go.Figure(data=[go.Table(
        header=dict(values=['Usage','Prior month (for comparison)','Platform']),
        cells=dict(values=[m1[('Usage',dfAAs['targYM'])],m1[('Usage',dfAAs['prevTargYM'])],m1['Platform']])
    )])
    fig.update_layout(margin=dict(t=50,b=10),height=200,title='Top 5 platforms for <br>M1 (emedia) requests in '+datetime.strptime(dfAAs['targYM'],'%Y-%m').strftime('%B %Y'))
    favButton('topCounterM1','standalone')
    st.plotly_chart(fig)
    
def topCounterB1Display(dfAAs):
    i='topCounter'
    b1=dfAAs['dfAA'+str(i)][dfAAs['dfAA'+str(i)]['Measure']=='TR_B1 - Unique Title Requests'].sort_values(by=('Usage',dfAAs['targYM']), na_position='last', ascending=False).head(5)
    fig=go.Figure(data=[go.Table(
        header=dict(values=['Usage','Prior month (for comparison)','Platform']),
        cells=dict(values=[b1[('Usage',dfAAs['targYM'])],b1[('Usage',dfAAs['prevTargYM'])],b1['Platform']])
    )])
    fig.update_layout(margin=dict(t=50,b=10),height=200,title='Top 5 platforms for <br>B1 (ebook) requests in '+datetime.strptime(dfAAs['targYM'],'%Y-%m').strftime('%B %Y'))
    favButton('topCounterB1','standalone')
    st.plotly_chart(fig)
   
def topDigitalPrep(dfAAs):
    apath='/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Top digital'
    i='topDigital'
    dfAAs=dfAAinit(dfAAs,apath,i)
    #Williams Record subcollections are best rolled up
    dfAAs['dfAA'+str(i)]['Num of digital representation views']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Num of digital representation views'])
    dfAAs['dfAA'+str(i)]['Num of digital file views']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Num of digital file views'])
    dfAAs['dfAA'+str(i)]['Num of digital file downloads']=pd.to_numeric(dfAAs['dfAA'+str(i)]['Num of digital file downloads'])
    df_Rec=dfAAs['dfAA'+str(i)][dfAAs['dfAA'+str(i)]['Collection Name'].str.contains('Williams Record')]
    df_NoRec=dfAAs['dfAA'+str(i)][~dfAAs['dfAA'+str(i)]['Collection Name'].str.contains('Williams Record')]
    df_NoRec.loc[len(df_NoRec)]={'0':'0','Collection Name':'Williams Record','Num of digital representation views':df_Rec['Num of digital representation views'].sum(),'Num of digital file views':df_Rec['Num of digital file views'].sum(),'Num of digital file downloads':df_Rec['Num of digital file downloads'].sum()}
    dfAAs['dfAA'+str(i)]=df_NoRec
    dfAAs['dfAA'+str(i)].rename(columns={'Num of digital representation views':'Representation views','Num of digital file views':'File views','Num of digital file downloads':'File downloads'},inplace=True)
    return dfAAs

def topDigitalDisplay(dfAAs):
    i='topDigital'
    d1=dfAAs['dfAA'+str(i)].sort_values(by='Representation views', na_position='last', ascending=False).head(5)
    fig=go.Figure(data=[go.Table(
        header=dict(values=['Collection','File Views','File Downloads','Representation Views']),
        cells=dict(values=[d1['Collection Name'],d1['File views'],d1['File downloads'],d1['Representation views']])
    )])
    fig.update_layout(margin=dict(t=90,b=10),height=300,title='Top 5 viewed digital collections:<br>Last 30 days')
    favButton('topDigital','standalone')
    st.plotly_chart(fig)
   
def main():
    #st.write('Please allow ~20 seconds for this dashboard to load')
    #Gather and prepare the data
    ph=ph
if __name__ == '__main__':
    main()
    