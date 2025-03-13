import diskcache as dc
import pandas as pd
import numpy as np

cache = dc.Cache("./cache")

class Clean:
    def __init__(self, retrieve):
        self.retrieve = retrieve
        self.group_data = self.retrieve.getGroupData()
        self.nurses = self.retrieve.getNurses()
        self.rooms = self.retrieve.getRooms()
        print(f'initial self.rooms: {self.rooms}')
        self.timeSeries_data = {}

    def createRoomData(self):
        data = self.rooms

    #return only total ounces by day, not seconds data
    def createDayData(self) -> dict:
        data = self.group_data
        #print(f'this is group data: {data}')
        day_data = {}
        for cust, values in data.items():
            day_data[cust] = []
            #print(f'key:{keys},\n values:{values}')
            for date, amount in values.items():
                day_data[cust].append([date, amount[0][1]])
        return day_data


    def createDayTable(self) -> dict:
        data = self.createDayData()
        processed_data = {}
        for custID, user_data in data.items():
            print(f'processing {custID}')
            flattened_list = [item for sublist in user_data for item in sublist]
            dates = flattened_list[::2]
            ounces = flattened_list[1::2]
            df = pd.DataFrame(np.column_stack([dates, ounces]),
                              columns=['Date', 'Ounces'])
            df['Date'] = pd.to_datetime(df['Date'], format='mixed')
            df['Ounces'] = pd.to_numeric(df['Ounces'], errors='coerce')
            df.set_index('Date', inplace=True)
            processed_data[custID] = df
        return processed_data

    #show only ounces by seconds, not day data
    def createTimeseries(self):
        data = self.group_data
        #print(data)
        for cust, dates in data.items():
            for date, amounts in dates.items():
                dates[date] = [amount for amount in amounts if amount[0] != '-1']
        return data

    def tableDayData(self):
        #generate tables for all users
        tables = {}
        data = self.createDayTable()

        for username, df in data.items():
            #reset index to include 'Date' as a column
            df = df.reset_index()
            df['Ounces'] = df['Ounces'].round(1)
            df.index = range(len(df))
            df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
            df = df.iloc[::-1].reset_index(drop=True)
            tables[username] = df
        return tables


    def filterRecentDays(self, days: int) -> dict:
        data = self.tableDayData()
        cutoff_date = pd.Timestamp.now() - pd.Timedelta(days=days)
        filtered_data = {}

        for username, df in data.items():

            if not isinstance(df.index, pd.DatetimeIndex):

                df['Date'] = pd.to_datetime(df['Date'], errors='coerce')
                df.set_index('Date', inplace=True)


            print(f"Filtering data for {username}")
            print(f"Cutoff date: {cutoff_date}")
            print(f"Index (before filtering): {df.index}")

            filtered_df = df[df.index >= cutoff_date]

            filtered_df.reset_index(inplace=True)

            #print(f"Filtered data shape for {username}: {filtered_df.shape}")

            filtered_df['Date'] = filtered_df['Date'].dt.strftime('%Y-%m-%d')
            #print(filtered_df.head())
            filtered_data[username] = filtered_df

        return filtered_data


    def sortbyAverageOunces(self, data: dict) -> list:
        averages = [(username, df["Ounces"].mean() if not df.empty else 0) for username, df in data.items()]

        #sort in ascending order
        averages.sort(key=lambda x: x[1])

        return [username for username, _ in averages]


    def sortNurses(self):
        nurses = self.nurses
        print(f'raw nurses: {nurses}')
        result = {}
        for key, value in nurses.items():
            if key not in ["status", "group"]:  # Skip non CustID keys
                result[key] = value
        print(f'sortNurses: {result}')
        return result

    def sortRooms(self):
        rooms = self.rooms
        print(f'sort rooms rooms: {rooms}')
        result = {}
        for key, value in rooms.items():
            if key not in ["status", "group"]:  # Skip non CustID keys
                result[key] = value
        print(f'sortRooms: {result}')
        return result


    # def graphDayData(self) -> dict:
    #     data = self.createDayData()
    #     processed_data = {}
    #     for custID, user_data in data.items():
    #         print(f'processing {custID}')
    #         parsed_data = []
    #         flattened_list = [item for sublist in user_data for item in
    #                           sublist]
    #         dates = flattened_list[::2]
    #         ounces = flattened_list[1::2]
    #         df = pd.DataFrame(np.column_stack([dates, ounces]), columns=['Date', 'Ounces'])
    #         df['Date'] = pd.to_datetime(df['Date'])
    #         df['Ounces'] = pd.to_numeric(df['Ounces'], errors='coerce')
    #         df.set_index('Date', inplace=True)
    #         processed_data[custID] = df
    #     return processed_data


if __name__ == '__main__':
    cleanData = Clean()
    #print(cleanData.createDayData())
    print(cleanData.tableDayData())