import streamlit as st
import requests
from loginHandling import FireBaseAuth

class Retrieval:
    def __init__(self):
        self.APIurl = st.secrets["baseURL"]
        self.firebase_auth = FireBaseAuth()
        self.CustID = self.firebase_auth.userID()

    #JSONify the data...
    def getRequests(self, params):
        try:
            response = requests.get(f"{self.APIurl}/sponge", params=params)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(e)

    #get the group a user belongs to
    #@cached_property
    def getUserGroup(self):
        #this will make it so we don't have to keep repeatedly calling this function
        if "user_group" not in st.session_state or st.session_state["user_group"] is None:
        #print(self.CustID)
            params = {'Type': 'getusergroup', 'CustID':self.CustID}
            group_raw = self.getRequests(params=params) # {"Groups": ["test"]}
            #print(f'group_raw_search: {group_raw}')
            st.session_state["user_group"] = group_raw["Groups"][0]
            #print(f'good test for group: {self.group}')
            #return self.group
            return st.session_state["user_group"]

    #get all data for all group members
    #@st.cache_data(ttl=900) #refresh in 15 mins
    @st.fragment()
    def getGroupData(self):
        group = st.session_state["user_group"]
        params = {'Type':'getgroupdata', 'GroupName':group}
        return self.getRequests(params=params)

    @st.fragment()
    def getNicknames(self, CustID):
        from warnings import warn
        warn('!!getNicknames is a deprecated function of class Retrieval!!')
        params = {'Type':'getNickName', 'CustID':CustID}
        return self.getRequests(params=params)

    @st.fragment()
    def getName(self):
        group = st.session_state["user_group"]
        params = {'Type':'getNamesByGroup', 'GroupName':group}
        return self.getRequests(params=params)

    @st.fragment()
    def getNurses(self):
        group = st.session_state["user_group"]
        #print(f'this is the group: {group}')
        params = {'Type':'getNurseByGroup', 'GroupName':group}
        return self.getRequests(params=params)

    @st.fragment()
    def getRooms(self):
        group = st.session_state["user_group"]
        params = {'Type':'getRoomByGroup', 'GroupName':group}
        return self.getRequests(params=params)

if __name__ == "__main__":
    retrieve = Retrieval()
    retrieve.getNicknames(CustID='McVV6ASBeHTtMoC55ocfJF34kv42')