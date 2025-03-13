#from pympler.util.bottle import response
#from matplotlib.pyplot import title
from streamlit import session_state

from loginHandling import FireBaseAuth
from dataCleaning import Clean
from accountManagement import Management
from retrieveData import Retrieval
from firebase_setup import FireBaseApp

import streamlit as st
import plotly.express as px
import plotly.graph_objs as go
#import matplotlib as plt
#import matplotlib.pyplot as plt

st.set_page_config(page_title='Sponge Hydration Dashboard', layout="wide")

firebase_auth = FireBaseAuth()
data_clean = Clean()
management = Management()
retrieval = Retrieval()

if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "selected_user" not in st.session_state:
    st.session_state["selected_user"] = None

class Login:
    def __init__(self):
        self.handle_login = firebase_auth

    def allowAccess(self):
        self.handle_login.login()

    def run(self):
        self.allowAccess()


class showData:
    def __init__(self):
        self.get_data = Clean()

    def createDayData(self):
        self.get_data.createDayData()

    def showData(self):
        st.write()


def main():
    #make sure authentication took place
    if not st.session_state.get("authenticated", False):
        firebase_auth.login()
        return

    st.title('Sponge Hydration Dashboard')

    #handle nickname management
    st.sidebar.title("Manage users")
    with st.sidebar.form(key="create_new_account_form"):
        name = st.text_input("Name")
        weight = st.number_input("Weight (lbs)", min_value=0, step=1, format='%d')
        height = st.number_input("Height (inches)", min_value=0,step=1, format='%d')
        birthday = st.date_input("Birthday")
        gender = st.selectbox("Gender", ["Male", "Female", "Other"])
        deviceSerial = st.text_input("Device ID")
        submitted = st.form_submit_button("Create Account")

        if submitted:
            if not all([name, weight, height, birthday, gender]):
                st.error('Please fill out all fields to create account')
            else:
                response = management.createUser(
                    deviceSerial=deviceSerial,
                    height=height,
                    weight=weight,
                    name=name,
                    birthday=birthday,
                    gender=gender,
                    groupName=retrieval.getUserGroup()
                )
                st.error(response)


    ##TODO: Default view 3 days
    filter_days = 0
    #handle data display
    # st.sidebar.title("Filter Options")
    # if st.sidebar.checkbox("Show Today"):
    #     filter_days = 1
    # elif st.sidebar.checkbox("Show Last 3 Days"):
    #     filter_days = 3
    # elif st.sidebar.checkbox("Show Last Week"):
    #     filter_days = 7

    tables = data_clean.tableDayData()
    # if filter_days > 0:
    #     tables = data_clean.filterRecentDays(filter_days)
    sorted_users = data_clean.sortbyAverageOunces(tables)

    ##THIS IS THE LOGIC FOR SHOWING 3 USERS ACROSS THE SCREEN
    num_users = len(sorted_users)
    #loop through users in groups of 3
    for i in range(0, num_users, 3):
        cols = st.columns(3, gap="small")#make row w 3 columns

        #for each user in this row
        for x, username in enumerate(sorted_users[i:i+3]):
            df = tables[username]
            nickname_response = retrieval.getName(username)
            nickname = nickname_response.get(username)
            display_name = nickname if nickname else username

            last_3_days = df.sort_values("Date", ascending=False).head(3)
            last_3_avg = last_3_days["Ounces"].mean()

            #make the name into a clickable button
            if cols[x].button(f"{display_name}\n(Last 3 Days Avg: {last_3_avg:.1f})", key=username):
                st.session_state.selected_user = username
                st.rerun()

            if session_state.get("selected_user") == username:
                fig = px.line(df, x='Date', y='Ounces', title=f'Ounces Consumed by {display_name}')
                fig.update_layout(xaxis_title='Date', yaxis_title='Ounces')
                cols[x].plotly_chart(fig)
            else:
                cols[x].dataframe(last_3_days, hide_index=True)


    # #THIS IS FOR THE OLD VIEW
    # for username in sorted_users:
    #     df = tables[username]
    #     nickname_response = retrieval.getName(username)
    #     nickname = nickname_response.get(username)
    #     display_name = nickname if nickname else username
    #
    #     #to show the graph next to the user's table we divide the page into two columns
    #     col1, col2 = st.columns([1,1])
    #
    #     with col1:
    #         #col1 is the standard table view
    #         if st.button(f"{display_name} (Average Ounces: {df['Ounces'].mean():.1f})", key=username):
    #             st.session_state.selected_user = username
    #
    #         if df.empty:
    #             st.write("No data available for the selected time period.")
    #         else:
    #             st.dataframe(df, hide_index=True)
    #
    #     with col2:
    #         #col2 shows the graph when the username is selected
    #         if st.session_state.get("selected_user") == username:
    #             fig = px.line(df, x='Date', y='Ounces', title=f'Ounces Consumed by {display_name}')
    #             fig.update_layout(xaxis_title='Date', yaxis_title='Ounces')
    #             st.plotly_chart(fig)
    #
    # if 'selected_user' not in st.session_state:
    #     st.session_state.selected_user = None



    #     if st.button(f"{display_name} (Average Ounces: {df['Ounces'].mean():.1f})"):
    #         st.session_state.selected_user = username
    #     #st.subheader(f"{display_name} (Average Ounces: {df['Ounces'].mean():.1f})")
    #
    #     if df.empty:
    #         st.write("No data available for the selected time period.")
    #     else:
    #         st.dataframe(df, hide_index=True)
    #
    #
    # if st.session_state.selected_user:
    #     print(f'{st.session_state.selected_user} has been selected')
    #     selected_df = tables[st.session_state.selected_user]
    #     print(selected_df)
    #
    #     fig = px.line(selected_df, x='Date', y='Ounces', title=f'Ounces Consumed by {st.session_state.selected_user}')
    #     fig.update_layout(xaxis_title='Date', yaxis_title='Ounces')
    #     st.plotly_chart(fig)



##TODO: Add API function to add 0oz to every user for each day

main()
#app = main()
#app.run()