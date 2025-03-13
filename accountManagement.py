import requests
import streamlit as st

## TODO: Add account management to API, allow users to add/delete devices

#function to create user

class Management:
    def __init__(self):
        self.APIurl = st.secrets["baseURL"]
        self.api_response : str

    def printData(self):
        print(self.APIurl)

    #get new custID
    def newCustID(self):
        params = {'Type': 'newcustid'}
        try:
            response = requests.get(f"{self.APIurl}/sponge", params=params)
            #response.raise_for_status()
            self.api_response = response.json()
            #self.cust_id = self.api_response
            print("New Customer ID:", type(self.api_response))
            return self.api_response
        except requests.exceptions.RequestException as e:
            print(f"Error fetching new customer ID: {e}")
            return None

    def createUser(self, deviceSerial, height, weight, name, birthday, gender, groupName):
        """
        Adds a new user using provided details.
        :param deviceSerial: Serial number of the device
        :param height: User's height
        :param weight: User's weight
        :param name: User's name
        :param birthday: User's birthdate
        :param custID: Customer ID
        :return: API response JSON
        """
        CustomerID = self.newCustID()
        params = {
            'CustID': CustomerID,
            'Name': name,
            'FireID': CustomerID,
            'DeviceSerial': deviceSerial,
            'Gender': gender,
            'GroupName': groupName,
            'Height': height,
            'Weight': weight,
            'Birthday': birthday,
            'Type': 'makecaregiverid'
        }
        try:
            response = requests.get(f"{self.APIurl}/sponge", params=params)
            response.raise_for_status()
            return response.json()
        except requests.exceptions.RequestException as e:
            print(f"Error adding user: {e}")
            return None

    def createCaregiverID(self):
        customerID = self.newCustID()
        ##TODO: This will be input from UI
        """
        add_user_response = manager.createUser(
        deviceSerial="test",
        height="6-00",
        weight=1,
        name="test",
        birthday="1999-17-10",
        custID=customerID,
        fireID=customerID,
        gender="test",
        groupName="test"
        )
        """
        #print("User added successfully:", add_user_response)

    ##TODO: The following functions can eventually be consolidated to one...
    def changeNickName(self, CustID, NickName):
        params = {'Type': 'changeNickName', 'NickName': NickName, 'CustID': CustID}
        try:
            response = requests.get(f"{self.APIurl}/sponge", params=params)
            response = response.json()
            print("New nickname:", response)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error adding user: {e}")
            return None

    @st.fragment()
    def updateUserRoom(self, userID, room):
        params = {'Type': 'updateRoom', 'CustID': userID, 'Room': room}
        try:
            response = requests.get(f"{self.APIurl}/sponge", params=params)
            response = response.json()
            print("New nickname:", response)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error adding user: {e}")
            return None

    @st.fragment()
    def updateUserNurse(self, type, userID, nurse):
        params = {'Type': type, 'CustID': userID, 'Nurse': nurse}
        try:
            response = requests.get(f"{self.APIurl}/sponge", params=params)
            response = response.json()
            print("New nurse:", response)
            return response
        except requests.exceptions.RequestException as e:
            print(f"Error adding user: {e}")
            return None

if __name__ == "__main__":
    manager = Management()
    #cust_id = manager.newCustID()
    nickName = manager.changeNickName(CustID='McVV6ASBeHTtMoC55ocfJF34kv42', NickName='domtest')
    '''
    add_user_response = manager.createUser(
        deviceSerial="test",
        height="6-00",
        weight=1,
        name="test",
        birthday="1999-17-10",
        custID=cust_id,
        fireID=cust_id,
        gender="test",
        groupName="test"
    )
    if add_user_response:
        print("User added successfully:", add_user_response)
    else:
        print("Failed to add user.")
    '''