from google.auth.transport.requests import Request as GRequest
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

import pandas as pd
#from streamlit_elements import elements, mui, html
import os
import urllib
import requests
from requests import Session, Request
from urllib.parse import urlencode, quote_plus, quote
#from streamlit_elements import nivo
from datetime import datetime, timedelta
#from dateutil import relativedelta
#import seaborn as sn
#import matplotlib.pyplot as plt
#import xml.etree.ElementTree as ET
#import re
#import plotly.express as px
#import plotly.graph_objects as go
import json
import csv

# If modifying these scopes, delete the file token.json.
SCOPES = ['https://www.googleapis.com/auth/spreadsheets.readonly','https://www.googleapis.com/auth/drive.file']
api_key='redacted'
# The ID and range of a sample spreadsheet.
SPREADSHEET_ID = 'redacted'


#RANGE_NAME = 'Sheet1!A6:E200'
RANGE_ASPACE = 'Aspace Collection Stats!A1:F500'

aspaceOn=True
def aspaceInit (dfASs,i,path,base,headers,queryParams):
    dfASs['dfAS'+str(i)]=[]
    for r in ['2','4']:
        url=base+'/repositories/'+str(r)+path
        #queryParams='?'+urlencode({'q[]':n,'type[]':'top_container','page':'1'})
        response_body=requests.get(url+queryParams,headers=headers,verify=True)
        #st.write(url+queryParams)
        #print(response_body.text)
        rj=json.loads(response_body.text)

        #Will need to concat from both repos, better to do that within the func
        dfASs['dfAS'+str(i)].append(rj)
    return dfASs

def spreadsheetGet(id,creds,range):
    try:
        service = build('sheets', 'v4', credentials=creds)
        # Call the Sheets API
        #st.write(id+range)
        sheet = service.spreadsheets()
        result = sheet.values().get(spreadsheetId=id,range=range).execute()
        values = result.get('values', [])
        return values
    except HttpError as err:
        print(err)

def spreadsheetPost(id,creds,rowi,vals):
    try:
        service = build('sheets','v4',credentials=creds)
        sheet = service.spreadsheets()
        resource={
            "majorDimension":"ROWS",
            "values":[['test','test2']]
        }
        result=sheet.values().append(insertDataOption='INSERT_ROWS',spreadsheetId=id,range="Aspace Collection Stats!A"+str(rowi)+":F"+str(rowi),body=vals).execute()
        print(result)
    except HttpError as err:
        print(err)

def dtToStr(x,format,format2):
    try:
        x=datetime.strptime(x,format)
        #return datetime.strftime(x,'%Y')
        return datetime.strftime(x,format2)
    except:
        return x

def main():   
    #Gather and prepare the data
    aspaths=[
    '/accessions',
    '/archival_objects',
    #Get list of classifications per repo /repositories/:repo_id/classifications
    '/digital_objects',
    '/top_containers'
    ]
    asparams=[
    '?'+urlencode({'all_ids':'true'}),
    '?'+urlencode({'all_ids':'true'}),
    '?'+urlencode({'all_ids':'true'}),
    '?'+urlencode({'all_ids':'true'})
    ]

    #Get aspace session before individual calls
    un="redacted"
    pw="redacted"
    base='your API url'
    url2=base+'/users/'+un+'/login'
    queryParams='?'+urlencode({quote_plus('password'):pw})
    #st.write(url2+queryParams)
    response_body=requests.post(url2+queryParams,verify=True)
    print(response_body.text)
    rj=json.loads(response_body.text)
    session=rj['session']
    #st.write(session)
    dfASs={}
    headers={'X-ArchivesSpace-Session':session}
    
    #values = spreadsheetGet(SPREADSHEET_ID,creds,RANGE_ASPACE) 
    for i,aspath in enumerate(aspaths):
        dfASs=aspaceInit(dfASs,i,aspath,base,headers,asparams[i])
        #st.write(values)
        #st.write(dfASs['dfAS'+str(i)])
        #if i==0:
        #    st.write("Accessions in ArchivesSpace: "+str(len(dfASs['dfAS0'][0])+len(dfASs['dfAS0'][1])))
        #if i==1:
        #    st.write("Archival Objects in ArchivesSpace: "+str(len(dfASs['dfAS1'][0])+len(dfASs['dfAS1'][1])))
        #if i==2:
        #    st.write("Digital Objects in ArchivesSpace: "+str(len(dfASs['dfAS2'][0])+len(dfASs['dfAS2'][1])))
        #if i==3:
        #    st.write("Top Containers in ArchivesSpace: "+str(len(dfASs['dfAS3'][0])+len(dfASs['dfAS3'][1])))
    ss=[]
    repos=['College Archives','Chapin Library']
    newfile=False
    try:
        with open('/opt/scripts/dashboard/aspace.csv',encoding='utf8') as file:
            reader=csv.reader(file)
            for i,row in enumerate(reader):
                if i!=0:
                    ss.append(row)
    except:
        print('starting new file...')
        newfile=True
    todayRun=False
    for i,r in enumerate(ss):
        if datetime.today().strftime('%Y-%m-%d') in r[0]:
            todayRun=True
        #if i>1:
            #If we get more repos, start splitting dfs to make this calculation more durable
        #    r.extend([int(r[2])-int(ss[i-2][2]),int(r[3])-int(ss[i-2][3]),int(r[4])-int(ss[i-2][4]),int(r[5])-int(ss[i-2][5])])
        #else:
        #    r.extend([0,0,0,0])
    if todayRun==False:
        for c in range(2):
            if newfile==False:
                new2=len(dfASs['dfAS0'][c])-int(ss[len(ss)-2][2])
                new3=len(dfASs['dfAS1'][c])-int(ss[len(ss)-2][3])
                new4=len(dfASs['dfAS2'][c])-int(ss[len(ss)-2][4])
                new5=len(dfASs['dfAS3'][c])-int(ss[len(ss)-2][5])
            else:
                new2=0
                new3=0
                new4=0
                new5=0
            ss.append([datetime.today().strftime('%Y-%m-%d'),repos[c],len(dfASs['dfAS0'][c]),len(dfASs['dfAS1'][c]),len(dfASs['dfAS2'][c]),len(dfASs['dfAS3'][c]),
            new2,new3,new4,new5])
    dfss=pd.DataFrame(ss)
    dfss.rename(columns={0:'Date',1:'Repository',2:'Accessions',3:'Archival Objects',4:'Digital Objects',5:'Top Containers',6:'New Accessions',7:'New Archival Objects',8:'New Digital Objects',9:'New Top Containers'},inplace=True)
    #dfss.to_csv('aspace.csv',index=False,header=['Date','Repository','Accessions','Archival Objects','Digital Objects','Top Containers'])
    dfss.to_csv('/opt/scripts/dashboard/aspace.csv',index=False)
    #st.write(dfss)
    payload={
        "majorDimension":"ROWS",
        "values":[
            [datetime.today().strftime('%Y-%m-%d'),repos[0],len(dfASs['dfAS0'][0]),len(dfASs['dfAS1'][0]),len(dfASs['dfAS2'][0]),len(dfASs['dfAS3'][0])]
        ]
        #[datetime.today().strftime('%Y-%m-%d'),'Chapin',['dfAS0'][1],['dfAS1'][1],['dfAS2'][1],['dfAS3'][1]]
    }
    #test=spreadsheetPost(SPREADSHEET_ID,creds,len(values),payload)

if __name__ == '__main__':
    main()
    