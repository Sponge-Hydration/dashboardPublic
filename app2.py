'''
appTest.py refactored and reorganized
'''
from tokenize import group

import streamlit as st
import plotly.express as px
import pandas as pd
from streamlit import columns
from st_aggrid import AgGrid, GridOptionsBuilder

#from appTest import sorted_users
from loginHandling import FireBaseAuth
from dataCleaning import Clean
from accountManagement import Management
from retrieveData import Retrieval


#st.set_page_config(page_title="Sponge Hydration Dashboard", layout="wide")

class App():
    def __init__(self):
        self.firebase_auth = FireBaseAuth()
        self.management = Management()
        self.setup_page()
        self.initialize_session_state()
        self.retrieval = None #this has to be none until authentication is completed
        self.data_clean = None #this also has to wait until authentication is complete

    def setup_page(self):
        st.set_page_config(page_title="Sponge Hydration Dashboard", layout="wide")
        self.load_sidebar_css()

    def load_sidebar_css(self):
        with open("sidebar.css", "r") as f:
            css = f"<style>{f.read()}</style>"
            st.markdown(css, unsafe_allow_html=True)

    def initialize_session_state(self):
        defaults = {
            "authenticated": False,
            "selected_user": None,
            "sidebar_tab": "Dashboard",
            "graph_filter": "1 Week",
            "data_updated": False
        }

        for key, value in defaults.items():
            if key not in st.session_state:
                st.session_state[key] = value

    def authenticate(self):
        print(f"Authenticate called. Current state: {st.session_state.get('authenticated')}")
        if not st.session_state.get("authenticated", False):
            print("User not authenticated. Calling login...")
            self.firebase_auth.login()
            print(f"After login. State is now: {st.session_state.get('authenticated')}")
            st.session_state["authenticated"] = True
            print("User authenticated. Rerunning...")
            st.rerun()
        else:
            print("User already authenticated.")

    def create_retrieval(self):
        #this runs after authentication to prevent group loading error
        if self.retrieval is None:
            self.retrieval = Retrieval()

    def create_data_clean(self, retrieve):
         if self.data_clean is None:
            self.data_clean = Clean(retrieve)

    def get_hydration_data(self, nurses, rooms):
        tables = self.data_clean.tableDayData()
        sorted_users = self.data_clean.sortbyAverageOunces(tables)
        print(f'Rooms in get_hydration_data: {rooms}')
        return tables, sorted_users, nurses, rooms

    def get_nurses(self):
        nurses = self.data_clean.sortNurses()
        print(f'nurses: {nurses}')
        return nurses

    def get_rooms(self):
        rooms = self.data_clean.sortRooms()
        print(f'rooms in get_rooms: {rooms}')
        return rooms

    def render_sidebar(self):
        st.sidebar.title("Navigation")
        tab_buttons = {
            "Dashboard": "📊 Dashboard",
            "Create New User": "➕ Create User",
            "Profile": "👤 Profile",
            "Update User": "🔄 Update User"
        }

        for tab_name, tab_label in tab_buttons.items():
            if st.sidebar.button(tab_label, key=tab_name):
                st.session_state["sidebar_tab"] = tab_name
                #st.rerun()

    def render_dashboard(self):
        nurses = self.get_nurses()
        rooms = self.get_rooms()
        names_dict = self.retrieval.getName()  # grab the names dict
        #print(f'names_dict: {names_dict}')
        tables, sorted_users, nurses_dict, rooms_dict = self.get_hydration_data(nurses, rooms)
        st.markdown("## 🩺 Patient Hydration Overview")

        data_list = []

        for idx, username in enumerate(sorted_users):
            df = tables[username]
            display_name = names_dict.get(username, username)
            last_3_days = df.sort_values("Date", ascending=False).head(3)
            last_7_days = df.sort_values("Date", ascending=False).head(7)

            total_3_days = last_3_days["Ounces"].sum()
            total_7_days = last_7_days["Ounces"].sum()
            total_today = df[df["Date"] == df["Date"].max()]["Ounces"].sum()

            user_nurses = ", ".join(nurses_dict.get(username, ["N/A"]))
            user_rooms = ", ".join(rooms_dict.get(username, ['N/A']))

            # Add username to the data_list.
            data_list.append(
                [display_name, user_rooms, user_nurses, total_7_days,
                 total_3_days, total_today, username])  # username added here.

        df_display = pd.DataFrame(data_list, columns=[
            "Name", "Location", "Nurse",
            "7-Day Total", "3-Day Total",
            "Today", "username"  # username column also here.
        ])

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            selected_nurse = st.selectbox("Filter by Nurse:", ["All"] + list(
                df_display["Nurse"].unique()), key="nurse_filter")
        with col2:
            selected_room = st.selectbox("Filter by Room:", ["All"] + list(df_display["Location"].unique()), key="room_filter")

        filtered_df = self.filter_table(df_display, selected_nurse, selected_room)

        left_column, right_column = st.columns(2)
        with left_column:
            # Grid options START HERE
            print(f'filtered df cols: {filtered_df.columns}')
            gb = GridOptionsBuilder.from_dataframe(
                filtered_df)  # keep the username column in the dataframe here.
            gb.configure_selection(selection_mode="single", use_checkbox=False)
            gb.configure_column("username",hide=True)  # Hide the "username" column
            gridOptions = gb.build()

            scale = 30 + (len(names_dict) * 30)
            print(f'this is scale: {scale}')

            # Render the grid
            grid_response = AgGrid(
                filtered_df,
                gridOptions=gridOptions,
                update_mode="MODEL_CHANGED",
                theme="streamlit",
                fit_columns_on_grid_load=True,
                height=scale
            )

            # Ensure grid_response contains "selected_rows"
            if grid_response and "selected_rows" in grid_response:
                selected_rows = pd.DataFrame(grid_response["selected_rows"])  # Convert to DataFrame

                if not selected_rows.empty:  # Correct way to check if DataFrame has rows
                    selected_user = selected_rows.iloc[0].get("username")  # Get first selected row's username
                    if selected_user and st.session_state.get("selected_user") != selected_user:
                        st.session_state["selected_user"] = selected_user
                        #st.rerun()  # Force UI update

            if st.session_state.get("selected_user"):
                selected_user_id = st.session_state["selected_user"]
                print(f'_____________{selected_user_id}____________')
                self.display_user_graph(selected_user_id, tables, names_dict)

    def display_user_graph(self, user_id, tables, names_dict):
        if user_id not in tables:
            st.write("No data available for the selected user")
            return

        user_data = tables[user_id]

        if isinstance(user_data, pd.DataFrame):  # Ensure it's a DataFrame
            if "Date" in user_data.columns and "Ounces" in user_data.columns:
                user_data["Date"] = pd.to_datetime(user_data["Date"])
                user_data = user_data.sort_values("Date")

                fig = px.line(user_data, x="Date", y="Ounces",
                              title=f"Hydration Data for {names_dict.get(user_id, user_id)}")
                st.plotly_chart(fig)

            else:
                st.write("Missing required columns in the user data.")
        else:
            st.write("User data format is incorrect.")

        if st.button("Clear"):
            st.session_state["selected_user"] = None
            #st.rerun()

    #@st.cache_data(ttl="6h")
    def filter_table(self, df, nurse, room):
        if nurse != "All":
            df = df[df["Nurse"] == nurse]
        if room != "All":
            df = df[df["Location"] == room]
        return df

    def run(self):
        print(f"Run called. Current state: {st.session_state}")
        if st.session_state["screen"] == "login":
            self.display_login_form()
        elif st.session_state["screen"] == "dashboard":
            self.create_retrieval()
            if self.retrieval:
                self.retrieval.getUserGroup()
                self.create_data_clean(self.retrieval)
            self.render_sidebar()
            selected_tab = st.session_state["sidebar_tab"]

            if selected_tab == "Dashboard":
                self.render_dashboard()
            elif selected_tab == "Create New User":
                self.create_user()
            elif selected_tab == "Profile":
                self.show_profile()
            elif selected_tab == "Update User":
                self.update_user()
                #self.render_dashboard()

    def display_login_form(self):
        st.title("Login to the Sponge Hydration Dashboard")
        with st.form('login'):
            email = st.text_input("Email", key="email_input")
            password = st.text_input("Password", type="password",
                                     key="password_input")
            login = st.form_submit_button("Login")
            if login:
                try:
                    user = self.firebase_auth.auth_client.sign_in_with_email_and_password(
                        email, password)
                    st.session_state["authenticated"] = True
                    st.session_state["user_email"] = user["email"]
                    st.session_state["id_token"] = user["idToken"]
                    st.session_state["user_id"] = user["localId"]
                    st.session_state["screen"] = "dashboard"
                    st.rerun()

                except Exception as e:
                    st.error(
                        f"Authentication failed. Please check your credentials. Error: {e}")
                    st.session_state["authenticated"] = False
                    print(f"Login Failure, error: {e}")


    def create_user(self):
        st.sidebar.subheader("Create New User")
        with st.sidebar.form(key="create_new_account_form"):
            name = st.text_input("Name")
            weight = st.number_input("Weight (lbs)", min_value=0, step=1, format='%d')
            height = st.number_input("Height (inches)", min_value=0, step=1, format='%d')
            birthday = st.date_input("Birthday")
            gender = st.selectbox("Gender", ["Male", "Female", "Other"])
            deviceSerial = st.text_input("Device ID")
            nurse = st.text_input("Assigned Nurse")
            room = st.text_input("Room Number")
            submitted = st.form_submit_button("Create Account")

            if submitted:
                if not all([name, weight, height, birthday, gender, nurse, room]):
                    st.error("Please fill out all fields to create an account")
                else:
                    response = self.management.createUser(
                        deviceSerial=deviceSerial,
                        height=height,
                        weight=weight,
                        name=name,
                        birthday=birthday,
                        gender=gender,
                        groupName=st.session_state["user_group"],
                        nurse=nurse,
                        room=room
                    )
                    st.success("User created successfully!" if not response else response)
                    #st.rerun()

    #TODO: Update user nurse
    def update_user(self):
        st.sidebar.subheader("Update Patient Room or Nurse")

        names_dict = self.retrieval.getName()
        user_ids = list(names_dict.keys())
        user_names = list(names_dict.values())

        selected_user_name = st.sidebar.selectbox("Select User:", user_names)
        selected_user_id = user_ids[user_names.index(selected_user_name)]

        nurses = self.get_nurses()
        user_nurses = nurses.get(selected_user_id, [])

        new_room = st.sidebar.text_input("New Room Number:")
        if st.sidebar.button("Update Room"):
            if new_room:
                response = self.management.updateUserRoom(userID=selected_user_id, room=new_room)
                if 'success' in response:
                    st.sidebar.success('success')
                else:
                    st.sidebar.error("Please try again")
                    #st.rerun()
            else:
                st.sidebar.error("Please try again.")

        new_nurse = st.sidebar.text_input("Add Nurse:")

        #col1, col2 = st.sidebar.columns(2)
        #with col1:
        if st.sidebar.button("Add Nurse"):
            if new_nurse:
                response = self.management.updateUserNurse(type='updateNurse', userID=selected_user_id, nurse=new_nurse)
                if 'success' in response:
                    st.sidebar.success('success')
                else:
                    st.sidebar.error("Please try again")
                    #st.rerun()
            else:
                st.sidebar.error("Please try again.")
        #with col2:
        remove_nurse = st.sidebar.selectbox("Remove Nurse:", user_nurses)
        if st.sidebar.button("Remove Nurse"):
            if remove_nurse:
                response = self.management.updateUserNurse(type='removeNurse', userID=selected_user_id, nurse=remove_nurse)
                if 'success' in response:
                    st.sidebar.success('success')
                    #st.rerun()
                else:
                    st.sidebar.error("Please try again")
                    #st.rerun()
            else:
                st.sidebar.error("Please select a nurse to remove.")

        self.render_dashboard()

    def show_profile(self):
        st.sidebar.subheader("User Profile")
        user_email = "john.doe@example.com"
        user_role = "Nurse Supervisor"
        st.sidebar.write(f"**Email:** {user_email}")
        st.sidebar.write(f"**Role:** {user_role}")

if __name__ == "__main__":
    app = App()
    app.run()