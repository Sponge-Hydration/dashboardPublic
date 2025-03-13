import streamlit as st
import plotly.express as px
import pandas as pd
from loginHandling import FireBaseAuth
from dataCleaning import Clean
from accountManagement import Management
from retrieveData import Retrieval

# Load Sidebar CSS
def load_sidebar_css():
    with open("sidebar.css", "r") as f:
        css = f"<style>{f.read()}</style>"
        st.markdown(css, unsafe_allow_html=True)

# Set Page Configuration
st.set_page_config(page_title="Sponge Hydration Dashboard", layout="wide")

# Load Sidebar CSS
load_sidebar_css()

# Firebase Setup
firebase_auth = FireBaseAuth()
data_clean = Clean()
management = Management()
retrieval = Retrieval()

# 🔹 Ensure session states exist
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "selected_user" not in st.session_state:
    st.session_state["selected_user"] = None
if "sidebar_tab" not in st.session_state:
    st.session_state["sidebar_tab"] = "Dashboard"
if "graph_filter" not in st.session_state:
    st.session_state["graph_filter"] = "1 Week"  # Default filter
if "data_updated" not in st.session_state:
    st.session_state["data_updated"] = False

# Authentication Check
if not st.session_state.get("authenticated", False):
    firebase_auth.login()
    st.stop()

# 🔹 Cache Data Fetching
@st.cache_data(ttl=60)
def get_hydration_data():
    tables = data_clean.tableDayData()
    sorted_users = data_clean.sortbyAverageOunces(tables)
    return tables, sorted_users

tables, sorted_users = get_hydration_data()
print(tables)
print(sorted_users)
# 🔹 Sidebar Navigation
st.sidebar.title("Navigation")

# Sidebar Tabs with Modern Buttons
tab_buttons = {
    "Dashboard": "📊 Dashboard",
    "Create New User": "➕ Create User",
    "Profile": "👤 Profile"
}

for tab_name, tab_label in tab_buttons.items():
    if st.sidebar.button(tab_label, key=tab_name):
        st.session_state["sidebar_tab"] = tab_name
        st.rerun()

selected_tab = st.session_state["sidebar_tab"]

# 🔹 Sidebar Content Based on Selected Tab
if selected_tab == "Dashboard":
    # st.sidebar.info("Click to refresh data ⬇️")
    # if st.sidebar.button("Refresh Data 🔄"):
    get_hydration_data.clear()
    st.session_state["data_updated"] = True
    # st.rerun()

elif selected_tab == "Create New User":
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
                response = management.createUser(
                    deviceSerial=deviceSerial,
                    height=height,
                    weight=weight,
                    name=name,
                    birthday=birthday,
                    gender=gender,
                    groupName=retrieval.getUserGroup(),
                    nurse=nurse,
                    room=room
                )
                st.success("User created successfully!" if not response else response)
                st.rerun()

elif selected_tab == "Profile":
    st.sidebar.subheader("User Profile")
    user_email = "john.doe@example.com"  # Placeholder, replace with real user data
    user_role = "Nurse Supervisor"  # Replace with actual role
    st.sidebar.write(f"**Email:** {user_email}")
    st.sidebar.write(f"**Role:** {user_role}")

# 🔹 Prepare Data for Table Display
st.markdown("## 🩺 Patient Hydration Overview")

data_list = []

# Unique placeholders for Nurse & Room per user
placeholder_nurses = ["Nurse Alice", "Nurse Bob", "Nurse Charlie"]
placeholder_rooms = ["Room 101", "Room 102", "Room 103"]

for idx, username in enumerate(sorted_users):
    df = tables[username]
    nickname_response = retrieval.getName(username)
    display_name = nickname_response.get(username) if nickname_response else username

    last_3_days = df.sort_values("Date", ascending=False).head(3)
    last_7_days = df.sort_values("Date", ascending=False).head(7)

    total_3_days = last_3_days["Ounces"].sum()
    total_7_days = last_7_days["Ounces"].sum()
    total_today = df[df["Date"] == df["Date"].max()]["Ounces"].sum()

    location = placeholder_rooms[idx % len(placeholder_rooms)]
    nurse = placeholder_nurses[idx % len(placeholder_nurses)]

    data_list.append([display_name, location, nurse, total_7_days, total_3_days, total_today])

df_display = pd.DataFrame(
    data_list, columns=["Name", "Location", "Nurse", "7-Day Total", "3-Day Total", "Today"]
)

# 🔹 Filtering the Table Based on Nurse or Room Selection
col1, col2 = st.columns([1, 1])

with col1:
    selected_nurse = st.selectbox("Filter by Nurse:", ["All"] + list(df_display["Nurse"].unique()))
with col2:
    selected_room = st.selectbox("Filter by Room:", ["All"] + list(df_display["Location"].unique()))

@st.cache_data(ttl=60)
def filter_table(df, nurse, room):
    if nurse != "All":
        df = df[df["Nurse"] == nurse]
    if room != "All":
        df = df[df["Location"] == room]
    return df

filtered_df = filter_table(df_display, selected_nurse, selected_room)

# 🔹 Display Filtered Data Table
st.dataframe(filtered_df, hide_index=True)

# 🔹 Hydration Graph Filter (Horizontal Layout)
st.markdown("### 📊 Hydration Trend Analysis")
col1, col2 = st.columns([1, 3])

with col1:
    graph_filter_options = ["3 Days", "1 Week", "1 Month", "1 Year", "All"]
    selected_graph_filter = st.selectbox("Select Time Range:", graph_filter_options, index=1)

with col2:
    selected_user = st.selectbox("Select a user:", filtered_df["Name"].tolist() if not filtered_df.empty else [])

# 🔹 Function to Filter Graph Data Based on Time Range
@st.cache_data(ttl=60)
def filter_graph_data(df, time_range):
    if time_range == "3 Days":
        return df.sort_values("Date", ascending=False).head(3)
    elif time_range == "1 Week":
        return df.sort_values("Date", ascending=False).head(7)
    elif time_range == "1 Month":
        return df.sort_values("Date", ascending=False).head(30)
    elif time_range == "1 Year":
        return df.sort_values("Date", ascending=False).head(365)
    else:
        return df

# 🔹 Always Visible Graph (No Expander)
if selected_user:
    st.write(selected_user)
    # Get User ID from filtered_df
    user_id_row = sorted_users[sorted_users["Name"] == selected_user]

    if not user_id_row.empty:
        user_id = user_id_row.index[0]  # Assuming index stores user IDs
        df_selected = tables[user_id]

        df_filtered = filter_graph_data(df_selected, selected_graph_filter)

        fig = px.line(df_filtered, x="Date", y="Ounces", title=f"Hydration Trend: {selected_user}")
        fig.update_layout(xaxis_title="Date", yaxis_title="Ounces")

        st.plotly_chart(fig)

