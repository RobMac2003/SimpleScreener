import copy
import requests
import dataFetch


class Screener:
    tickers = []
    originalTickers = []
    api_key = 'YOUR_API_KEY'
    date = '2023-01-06'  # Set the date for which to retrieve the closing price (in YYYY-MM-DD format)
    df = dataFetch.DataFetch

    def __init__(self, tickers):
        self.tickers = tickers
        self.originalTickers = copy.deepcopy(tickers)

    def update_ticker(self):
        self.tickers = copy.copy(self.originalTickers)

    def get_market_cap(self, index):  # returns a the market cap of specified index
        last = self.df.read_json_list('WeeklyData')[index]['Meta Data'][
            '3. Last Refreshed']  # get date of last price point stored in weeklyData file
        price = float(self.df.read_json_list('WeeklyData')[index]['Weekly Adjusted Time Series'][last][
                          '4. close'])  # get latest closing price
        return price * int(
            self.df.read_json_list('BalanceSheetData')[index]['annualReports'][0]['commonStockSharesOutstanding'])

    def get_price_to_metric_ratio_inc(self, index,
                                      mType):  # gets any price ratio availabe from incomeData for specified index
        metric = float(self.df.read_json_list('incomeData')[index]['annualReports'][0][mType])
        price = self.get_market_cap(index)
        return price / metric

    def get_price_to_book_ratio(self, index):
        metric = int(self.df.read_json_list('BalanceSheetData')[index]['annualReports'][0]['totalShareholderEquity'])
        price = self.get_market_cap(index)
        return price / metric

    def get_roe(self, index):
        share_holder_equity = int(
            self.df.read_json_list('BalanceSheetData')[index]['annualReports'][0]['totalShareholderEquity'])
        net_income = float(self.df.read_json_list('incomeData')[index]['annualReports'][0]['netIncome'])
        return net_income / share_holder_equity

    def get_debt_to_equity(self, index):
        debt = int(self.df.read_json_list('BalanceSheetData')[index]['annualReports'][0]['shortLongTermDebtTotal'])
        share_holder_equity = int(
            self.df.read_json_list('BalanceSheetData')[index]['annualReports'][0]['totalShareholderEquity'])
        return debt / share_holder_equity

    def remove_from_list(self, index):  # removes specified index from tickers list using the index provided in the list
        for i in range(len(self.tickers)):
            if self.tickers[i][1] == index:
                del self.tickers[i]
                break

    def filter_by_price_to_book_ratio(self, parameter):
        new_list = []
        if parameter[0] == '<':
            for i in self.tickers:
                if self.get_price_to_book_ratio(i[1]) > int(parameter[1:]):
                    new_list.append(i)
        else:
            for i in self.tickers:
                if self.get_price_to_book_ratio(i[1]) < int(parameter[1:]):
                    new_list.append(i)
        for i in new_list:
            self.remove_from_list(i[1])

    def filter_by_debt_equity(self, box_selection):
        new_list = []
        over = True
        perc = 0.0
        box_selection_dict = {
            "Low(<0.1)": (0.1, False),
            "Under 1": (1, False),
            "High(>0.5)": (0.5, True),
            "Over 1": (1, True),
            "Over 3": (3.0, True)
        }

        if box_selection in box_selection_dict:
            perc = box_selection_dict[box_selection][0]
            over = box_selection_dict[box_selection][1]
        else:
            print('error undefined input: ', box_selection)
        if over:
            for i in self.tickers:
                if self.get_debt_to_equity(i[1]) < perc:
                    new_list.append(i)
        else:
            for i in self.tickers:
                if self.get_debt_to_equity(i[1]) > perc:
                    new_list.append(i)
        for i in new_list:
            self.remove_from_list(i[1])

    def filter_by_price_metric_inc(self, parameter,
                                   mType):  # filter list of tickers by metric parameter and removes any under or
        # over threshold parameter
        new_list = []
        if parameter[0] == '<':
            for i in self.tickers:
                if self.get_price_to_metric_ratio_inc(i[1], mType) > int(parameter[1:]):
                    new_list.append(i)
        else:
            for i in self.tickers:
                if self.get_price_to_metric_ratio_inc(i[1], mType) < int(parameter[1:]):
                    new_list.append(i)
        for i in new_list:
            self.remove_from_list(i[1])

    def filter_by_market_cap(self,
                             input):  # takes string input and filters removes market cap under or over the threshold
        new_list = []
        input_values = {
            "Over 100 m": (100000000, True),
            "Over 1B": (1000000000, True),
            "Over 30B": (30000000000, True),
            "Under 50m": (50000000, False),
            "Under 100 m": (100000000, False),
            "Under 1B": (1000000000, False),
            "Under 30B": (30000000000, False)
        }
        if not input_values[input][1]:
            for i in self.tickers:
                if self.get_market_cap(i[1]) > input_values[input][0]:
                    new_list.append(i)
        elif input_values[input][1] == True:
            for i in self.tickers:
                if self.get_market_cap(i[1]) < input_values[input][0]:
                    new_list.append(i)
        for i in new_list:
            self.remove_from_list(i[1])

    def translate_change_box(self, input):
        percentage = 0.0
        positive = True
        mapping_dict = {
            "+15%": 0.15,
            "+30%": 0.30,
            "+50%": 0.50,
            "+100%": 1.0,
            "+150%": 1.50,
            "+200%": 2.0,
            "+500%": 5.0,
            "+positive": 0,
            "-negative": 0,
            "-15%": -0.15,
            "-30%": -0.30,
            "-50%": -0.50,
            "-70%": -0.70
        }
        if input in mapping_dict:
            percentage = mapping_dict[input]
        else:
            print('error undefined input: ', input)
        if percentage < 0:
            positive = False
        elif input == "-negative":
            positive = False
        return [positive, percentage]

    def filter_by_change(self, input, m_type, years):
        dict = {
            "netIncome": 'incomeData',
            "totalRevenue": 'incomeData',
            'commonStockSharesOutstanding': 'BalanceSheetData',
            'totalShareholderEquity': 'BalanceSheetData',
            "shortLongTermDebtTotal": 'BalanceSheetData',
            'ebitda': 'incomeData'
        }
        new_list = []
        if m_type in dict:
            for i in self.tickers:
                try:
                    base = float(self.df.read_json_list(dict[m_type])[i[1]]['annualReports'][years][m_type])
                    end_year = float(self.df.read_json_list(dict[m_type])[i[1]]['annualReports'][0][m_type])

                    if self.translate_change_box(input)[0] and end_year > base:
                        # print(i, 'perc = ', (end_year - base) / base, 'base = ', base, 'end_year =', end_year)
                        if (end_year - base) / base < self.translate_change_box(input)[1]:
                            # print(i,'perc = ',(end_year - base)/base,'base = ',base,'end_year =',end_year)
                            new_list.append(i)
                    elif self.translate_change_box(input)[0] == False and end_year < base:
                        # print(i, 'perc = ', (base-end_year) / base, 'base = ', base, 'end_year =', end_year)
                        if (base - end_year) / base < self.translate_change_box(input)[1] * -1:
                            new_list.append(i)
                    else:
                        new_list.append(i)
                except IndexError:
                    print('index out of bounds, company probably does not have financials that far back')
        else:
            print('error undefined m_type', m_type)
        for i in new_list:
            self.remove_from_list(i[1])

    def x_Weeks_Perc(self, x, ticker):  # returns as a decimal the amount up or down a stock is from x weeks ago
        # Make a GET request to the Alpha Vantage API to retrieve the historical data for the stock
        response = requests.get(
            f'https://www.alphavantage.co/query?function=TIME_SERIES_WEEKLY_ADJUSTED&symbol={ticker}&apikey={self.api_key}')

        # Parse the JSON response
        data = response.json()
        print(data)
        # getting date and it's iterator in list of keys
        try:
            d_keys = list(data['Weekly Adjusted Time Series'].keys())
            d_iterator = d_keys.index('2023-01-06')
        except:
            print('error ticker ', ticker, ' not found')
            return 0

        # Extract the data for the specified date
        date_data = data['Weekly Adjusted Time Series'][self.date]
        date_data1 = data['Weekly Adjusted Time Series'][d_keys[d_iterator + x]]

        # Extract the closing price from the data
        closing_price = float(date_data['4. close'])
        closing_price1 = float(date_data1['4. close'])
        # print(f'The closing price for {ticker} on {self.date} was ${closing_price:.2f}')
        return (closing_price - closing_price1) / closing_price

    def x_weeks_up(self, x):  # remove stocks from list if they are not up from x weeks ago

        for ticker in self.tickers:
            print(ticker)
            if self.x_Weeks_Perc(x, ticker) <= 0:
                self.tickers.remove(ticker)

    def filter_by_roe(self, input):
        list_to_be_removed = []
        if self.translate_change_box(input)[0]:
            for ticker in self.tickers:
                if self.get_roe(ticker[1]) < self.translate_change_box(input)[1]:
                    list_to_be_removed.append(ticker)
        else:
            for ticker in self.tickers:
                if self.get_roe(ticker[1]) > self.translate_change_box(input)[1]:
                    list_to_be_removed.append(ticker)

        for i in list_to_be_removed:
            self.remove_from_list(i[1])

    def filter_by_change_in_eps(self, input, years):
        new_list = []
        for i in self.tickers:
            try:
                base = float(self.df.read_json_list('earningsData')[i[1]]['annualEarnings'][years + 1]["reportedEPS"])
                end_year = float(self.df.read_json_list('earningsData')[i[1]]['annualEarnings'][1]["reportedEPS"])

                if self.translate_change_box(input)[0] and end_year > base:
                    if (end_year - base) / base < self.translate_change_box(input)[1]:
                        new_list.append(i)
                elif self.translate_change_box(input)[0] == False and end_year < base:
                    if (base - end_year) / base < self.translate_change_box(input)[1] * -1:
                        new_list.append(i)
                else:
                    new_list.append(i)
            except IndexError:
                print('index out of bounds, company probably does not have financials that far back')
        for i in new_list:
            self.remove_from_list(i[1])

    def get_margin(self, margin_type, index):
        revenue = float(self.df.read_json_list('incomeData')[index]['annualReports'][0]['totalRevenue'])
        income = float(self.df.read_json_list('incomeData')[index]['annualReports'][0][margin_type])
        return income / revenue

    def filter_by_margin(self, margin_type, box_selection):
        list_to_be_removed = []
        if self.translate_change_box(box_selection)[0]:
            for ticker in self.tickers:
                if self.get_margin(margin_type, ticker[1]) < self.translate_change_box(box_selection)[1]:
                    list_to_be_removed.append(ticker)
        else:
            for ticker in self.tickers:
                if self.get_margin(margin_type, ticker[1]) > self.translate_change_box(box_selection)[1]:
                    list_to_be_removed.append(ticker)

        for i in list_to_be_removed:
            self.remove_from_list(i[1])
