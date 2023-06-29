import json
import requests


class DataFetch:
    api_key = 'YOUR_API_KEY' # replace with your own key from www.alphavantage.co

    def append_list(self, file_path, data):  # writes list to specified file name
        # Join the elements of the list into a single string, separated by a comma
        data_string = ','.join(data)
        # Open the file in append mode
        with open(file_path, 'a') as file:
            # Write the string to the file
            file.write(data_string + '\n')

    def get_data_for_ticker(self, ticker):  # writes 4 lists to the 4 seperate datafiles:
        # Make a GET request to the Alpha Vantage API to retrieve the historical data for the stock
        response = requests.get(
            f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol={ticker}&apikey={self.api_key}')
        # Parse the JSON response
        data = response.json()
        # getting date and it's iterator in list of keys
        try:
            d_keys = list(data['Weekly Adjusted Time Series'].keys())
            # d_iterator = d_keys.index('2023-01-06')
        except:
            print('error ticker ', ticker, ' not found')
            return 0
        self.append_json('WeeklyData', data)

        # get income data
        response1 = requests.get(
            f'https://www.alphavantage.co/query?function=INCOME_STATEMENT&symbol={ticker}&apikey={self.api_key}')
        data1 = response1.json()
        self.append_json('incomeData', data1)
        # get balance sheet data
        response2 = requests.get(
            f'https://www.alphavantage.co/query?function=BALANCE_SHEET&symbol={ticker}&apikey={self.api_key}')
        data2 = response2.json()
        self.append_json('balanceSheetData', data2)
        # get earnings data
        response3 = requests.get(
            f'https://www.alphavantage.co/query?function=EARNINGS&symbol={ticker}&apikey={self.api_key}')
        data3 = response3.json()
        self.append_json('earningsData', data3)
        return 0

    def append_json(file_path, data_dict):
        # Convert the data to a JSON string
        data_string = json.dumps(data_dict)
        # Open the file in append mode
        with open(file_path, 'a') as file:
            # Write the data to the file
            file.write(data_string + '\n')

    def read_list_of_lists(file_path):
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Read the contents of the file into a list
            lines = file.readlines()
        # Split the lines on the delimiter and convert the elements to integers
        data = [line.strip().split(',') for line in lines]
        return data

    def read_json_list(file_path):
        # Open the file in read mode
        with open(file_path, 'r') as file:
            # Read the contents of the file into a string
            data_string = file.read()
        # Split the string into a list of JSON strings
        json_strings = data_string.split('\n')
        # Convert the list of strings to a list of dictionaries
        data = []
        for i in range(len(json_strings) - 1):
            data.append(json.loads(json_strings[i]))
        return data
