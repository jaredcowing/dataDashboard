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
pip install PyYAML
pip install streamlit-authenticator
'''

import streamlit as st
st.set_page_config(
    page_title="Dashboard Home",
    page_icon="👋"
    )
import streamlit_authenticator as stauth
import yaml
from yaml.loader import SafeLoader
import defs

def main():
    #st.sidebar.success("Select a page above")
    defs.authBegin()
    if st.session_state.get('authentication_status')==True:
        defs.callFavorites()
dfAAs={}
#dfAAs=defs.circUGPrep(dfAAs,'/shared/Williams College/Reports from Walter/Systems/Dashboard staging/Circulation UG daily',8)
#defs.circUGDisplay(dfAAs)

if __name__ == '__main__':
    #with st.empty():
        #acct=['','']
        #un = st.text_input('Username:', value='')
        #pwd = st.text_input('Password:', value='', type='password')
        
       # acct == defs.checkUNPW(un,pwd)
       #if acct[0]=='ok':
       #     st.write('')
    #if acct[0]=='ok':
    main()