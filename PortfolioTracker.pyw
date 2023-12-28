import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno, showinfo
from transformers import GPT2LMHeadModel, GPT2Tokenizer

import pandas as pd
import yfinance as yf
import time
import os
import sys
import datetime
import subprocess
import platform


class Stock:
    def __init__(self, symbol: str, name: str, shares: float, avg_price: float):
        self.symbol = symbol
        self.name = name
        self.shares = shares
        self.avg_price = avg_price
        self.initial_value = shares * avg_price
        self.absolute_gain = 0.0
        self.relative_gain = 0.0
        self.daily_abs_gain = 0.0
        self.daily_rel_gain = 0.0
        self.current_price = 0.0
        self.current_value = 0.0
        self.calculate_gain()
        return

    def calculate_gain(self):
        self.absolute_gain = 0.0
        self.relative_gain = 0.0
        self.daily_abs_gain = 0.0
        self.daily_rel_gain = 0.0
        self.current_price = 0.0
        self.current_value = 0.0
        stock_data = yf.download(self.symbol, period="1d", interval="5m", prepost=True)
        open_price = yf.Ticker(self.symbol).info['previousClose']
        self.current_price = stock_data['Close'].iloc[-1]
        self.absolute_gain = (self.current_price - self.avg_price) * self.shares
        self.relative_gain = (self.absolute_gain / self.initial_value) * 100
        self.daily_abs_gain = (self.current_price - open_price) * self.shares
        self.daily_rel_gain = (self.daily_abs_gain / self.initial_value) * 100
        self.current_value = self.current_price * self.shares
        return


class Portfolio:
    def __init__(self):
        self.securities = []
        self.total_value = 0.0
        self.total_abs_gain = 0.0
        self.total_rel_gain = 0.0
        self.total_daily_abs_gain = 0.0
        self.total_daily_rel_gain = 0.0
        self.total_initial_value = 0.0
        return

    def calculate_total_gain(self):
        self.total_abs_gain = 0.00
        self.total_rel_gain = 0.00
        self.total_daily_abs_gain = 0.0
        self.total_daily_rel_gain = 0.0
        self.total_value = 0.0
        self.total_initial_value = 0.0
        for position in self.securities:
            self.total_value = self.total_value + position.current_value
            self.total_initial_value = self.total_initial_value + position.initial_value
        self.total_value = round(self.total_value, 2)
        for stock in self.securities:
            self.total_abs_gain = self.total_abs_gain + stock.absolute_gain
        self.total_abs_gain = round(self.total_abs_gain, 2)
        self.total_rel_gain = round((self.total_abs_gain / self.total_initial_value) * 100, 2)
        for security in self.securities:
            self.total_daily_abs_gain = self.total_daily_abs_gain + security.daily_abs_gain
        self.total_daily_abs_gain = round(self.total_daily_abs_gain, 2)
        self.total_daily_rel_gain = round(self.total_daily_abs_gain / self.total_initial_value, 2)
        return

    def add_security(self, security: Stock):
        self.securities.append(security)
        self.total_value += round(security.current_value, 2)
        self.calculate_total_gain()
        return

    def get_security_by_symbol(self, symbol: str):
        for security in self.securities:
            if security.symbol == symbol:
                return security
        return -1


def update_window():
    global table_frame, stats_frame, actions_frame, table, refresh_interval, portfolio, last_refreshed_text
    table_frame.destroy()
    stats_frame.destroy()
    actions_frame.destroy()
    last_refreshed_text.destroy()
    for stock in portfolio.securities:
        stock.calculate_gain()
    refresh_interval = root.after(5000, update_window)
    portfolio.calculate_total_gain()
    table_frame = tk.Frame(root)
    table = ttk.Treeview(table_frame, columns=(
        "Symbol", "Name", "Price", "Shares", "Value", "Initial Value", "Cost/Share", "Total Change $", "Total Change %",
        "Day Change $", "Day Change %"), height=len(portfolio.securities))
    table.bind('<<TreeviewSelect>>', on_stock_selected)
    table.heading("Symbol", text="Symbol")
    table.heading("Name", text="Name")
    table.heading("Price", text="Price")
    table.heading("Shares", text="Shares")
    table.heading("Value", text="Value")
    table.heading("Initial Value", text="Initial Value")
    table.heading("Cost/Share", text="Cost/Share")
    table.heading("Total Change $", text="Total Change $")
    table.heading("Total Change %", text="Total Change %")
    table.heading("Day Change $", text="Day Change $")
    table.heading("Day Change %", text="Day Change %")
    for stock in portfolio.securities:
        table.insert("", tk.END, values=[stock.symbol, stock.name, round(stock.current_price, 2), stock.shares,
                                         round(stock.current_value, 2), round(stock.initial_value, 2), stock.avg_price,
                                         round(stock.absolute_gain, 2), round(stock.relative_gain, 2),
                                         round(stock.daily_abs_gain, 2), round(stock.daily_rel_gain, 2)])
    table.column("#0", width=0)
    table.column("#1", width=50)
    table.column("#2", width=225)
    table.column("#3", width=115)
    table.column("#4", width=115)
    table.column("#5", width=115)
    table.column("#6", width=115)
    table.column("#7", width=115)
    table.column("#8", width=115)
    table.column("#9", width=115)
    table.column("#10", width=115)
    table.column("#11", width=115)
    stats_frame = tk.Frame(root)
    total_value_label = tk.Label(stats_frame, text=f"Value: ${portfolio.total_value}", font=("Arial", 20))
    daily_gain_label = tk.Label(stats_frame,
                                text=f"Daily: ${portfolio.total_daily_abs_gain} ({portfolio.total_daily_rel_gain}%)",
                                font=("Arial", 18))
    total_gain_label = tk.Label(stats_frame, text=f"Total: ${portfolio.total_abs_gain} ({portfolio.total_rel_gain}%)",
                                font=("Arial", 18))
    total_value_label.grid(column=0, row=0, padx=5, pady=5)
    daily_gain_label.grid(column=0, row=1, padx=5, pady=5)
    total_gain_label.grid(column=0, row=2, padx=5, pady=5)
    actions_frame = tk.Frame(root)
    refreshed_time = time.strftime('%l:%M:%S')
    last_refreshed_text = tk.Label(root, text=f"↻ {refreshed_time}", font=("Arial", 10))
    log_transaction_label = tk.Label(actions_frame, text="Portfolio", font=("Arial", 18))
    log_transaction_label.grid(column=0, row=1, columnspan=3, padx=5, pady=5)
    log_buy_button = tk.Button(actions_frame, text="+ Buy", command=log_buy)
    log_buy_button.grid(column=0, row=2, padx=5, pady=5)
    log_sell_button = tk.Button(actions_frame, text="- Sell", command=log_sell)
    log_sell_button.grid(column=1, row=2, padx=5, pady=5)
    edit_file_button = tk.Button(actions_frame, text="✎ Edit", command=edit_holdings_file)
    edit_file_button.grid(column=2, row=2, padx=5, pady=5)
    analysis_tools_label = tk.Label(actions_frame, text="Tools", font=("Arial", 18))
    analysis_tools_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
    dividend_tracker_button = tk.Button(actions_frame, text="Dividends", command=dividend_tracker)
    dividend_tracker_button.grid(column=0, row=4, padx=5, pady=5)
    benchmark_tool_button = tk.Button(actions_frame, text="Benchmark", command=benchmark_portfolio_performance)
    benchmark_tool_button.grid(column=1, row=4, padx=5, pady=5)
    summary_button = tk.Button(actions_frame, text="Summary", command=portfolio_summary)
    summary_button.grid(column=2, row=4, padx=5, pady=5)
    stats_frame.pack(padx=10, pady=10)
    table.pack()
    table_frame.pack(padx=10, pady=10)
    last_refreshed_text.pack(padx=5, pady=5)
    actions_frame.pack(padx=10, pady=10)
    print("Refresh complete")
    return


def load_app():
    global root, loading_label, portfolio, stats_frame, table_frame, actions_frame, table, refresh_interval, last_refreshed_text, other_loading_label
    df = pd.read_csv("portfolio-holdings.csv", header=0)
    for i in range(len(df)):
        symbol = df.loc[i, 'Symbol']
        name = df.loc[i, 'Name']
        shares = df.loc[i, 'Shares']
        avg_price = df.loc[i, 'AvgPrice']
        new_stock = Stock(symbol, name, shares, avg_price)
        portfolio.add_security(new_stock)
    loading_label.destroy()
    other_loading_label.destroy()
    cancel_button.destroy()
    table.config(height=len(portfolio.securities))
    table.bind('<<TreeviewSelect>>', on_stock_selected)
    table.heading("Symbol", text="Symbol")
    table.heading("Name", text="Name")
    table.heading("Price", text="Price")
    table.heading("Shares", text="Shares")
    table.heading("Value", text="Value")
    table.heading("Initial Value", text="Initial Value")
    table.heading("Cost/Share", text="Cost/Share")
    table.heading("Total Change $", text="Total Change $")
    table.heading("Total Change %", text="Total Change %")
    table.heading("Day Change $", text="Day Change $")
    table.heading("Day Change %", text="Day Change %")
    for stock in portfolio.securities:
        table.insert("", tk.END, values=[stock.symbol, stock.name, round(stock.current_price, 2), stock.shares,
                                         round(stock.current_value, 2), round(stock.initial_value, 2), stock.avg_price,
                                         round(stock.absolute_gain, 2), round(stock.relative_gain, 2),
                                         round(stock.daily_abs_gain, 2), round(stock.daily_rel_gain, 2)])
    table.column("#0", width=0)
    table.column("#1", width=50)
    table.column("#2", width=225)
    table.column("#3", width=115)
    table.column("#4", width=115)
    table.column("#5", width=115)
    table.column("#6", width=115)
    table.column("#7", width=115)
    table.column("#8", width=115)
    table.column("#9", width=115)
    table.column("#10", width=115)
    table.column("#11", width=115)
    portfolio.calculate_total_gain()
    total_value_label = tk.Label(stats_frame, text=f"Value: ${portfolio.total_value}", font=("Arial", 20))
    daily_gain_label = tk.Label(stats_frame,
                                text=f"Daily: ${portfolio.total_daily_abs_gain} ({portfolio.total_daily_rel_gain}%)",
                                font=("Arial", 18))
    total_gain_label = tk.Label(stats_frame, text=f"Total: ${portfolio.total_abs_gain} ({portfolio.total_rel_gain}%)",
                                font=("Arial", 18))
    total_value_label.grid(column=0, row=0, padx=5, pady=5)
    daily_gain_label.grid(column=0, row=1, padx=5, pady=5)
    total_gain_label.grid(column=0, row=2, padx=5, pady=5)
    log_transaction_label = tk.Label(actions_frame, text="Portfolio", font=("Arial", 18))
    log_transaction_label.grid(column=0, row=1, columnspan=3, padx=5, pady=5)
    log_buy_button = tk.Button(actions_frame, text="+ Buy", command=log_buy)
    log_buy_button.grid(column=0, row=2, padx=5, pady=5)
    log_sell_button = tk.Button(actions_frame, text="- Sell", command=log_sell)
    log_sell_button.grid(column=1, row=2, padx=5, pady=5)
    edit_file_button = tk.Button(actions_frame, text="✎ Edit", command=edit_holdings_file)
    edit_file_button.grid(column=2, row=2, padx=5, pady=5)
    analysis_tools_label = tk.Label(actions_frame, text="Tools", font=("Arial", 18))
    analysis_tools_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
    dividend_tracker_button = tk.Button(actions_frame, text="Dividends", command=dividend_tracker)
    dividend_tracker_button.grid(column=0, row=4, padx=5, pady=5)
    benchmark_tool_button = tk.Button(actions_frame, text="Benchmark", command=benchmark_portfolio_performance)
    benchmark_tool_button.grid(column=1, row=4, padx=5, pady=5)
    summary_button = tk.Button(actions_frame, text="Summary", command=portfolio_summary)
    summary_button.grid(column=2, row=4, padx=5, pady=5)
    stats_frame.pack(padx=10, pady=10)
    table.pack(padx=10, pady=10)
    table_frame.pack(padx=10, pady=10)
    last_refreshed_text.pack(padx=5, pady=5)
    actions_frame.pack(padx=10, pady=10)
    refresh_interval = root.after(5000, update_window)
    print("Loading complete")
    return


def log_buy():
    buy_window = tk.Toplevel(root)
    buy_window.geometry("200x300")
    buy_window.title("Log Buy")
    buy_window_title = tk.Label(buy_window, text="Add Buy to Portfolio")
    buy_window_title.pack(padx=5, pady=5)
    symbol_label = tk.Label(buy_window, text="Stock Symbol")
    symbol_label.pack(padx=5, pady=5)
    symbol_var = tk.StringVar()
    symbol_entry = tk.Entry(buy_window, textvariable=symbol_var, width=10)
    symbol_entry.pack(padx=5, pady=5)
    shares_label = tk.Label(buy_window, text="# of Shares")
    shares_label.pack(padx=5, pady=5)
    shares_var = tk.StringVar()
    shares_entry = tk.Entry(buy_window, textvariable=shares_var, width=10)
    shares_entry.pack(padx=5, pady=5)
    buy_price_label = tk.Label(buy_window, text="Cost/Share")
    buy_price_label.pack(padx=5, pady=5)
    buy_price_var = tk.StringVar()
    buy_price_entry = tk.Entry(buy_window, textvariable=buy_price_var, width=10)
    buy_price_entry.pack(padx=5, pady=5)
    submit_wait_var = tk.IntVar()
    submit_wait_var.set(0)
    submit_button = tk.Button(buy_window, text="Confirm", command=lambda: submit_wait_var.set(1))
    submit_button.pack(padx=5, pady=5)
    buy_window.wait_variable(submit_wait_var)
    symbol = symbol_var.get().upper()
    shares = float(shares_var.get())
    buy_price = float(buy_price_var.get())
    symbol_list = []
    name_list = []
    shares_list = []
    price_list = []
    for stock in portfolio.securities:
        symbol_list.append(stock.symbol)
        name_list.append(stock.name)
        shares_list.append(stock.shares)
        price_list.append(stock.avg_price)
    symbol_list.append(symbol)
    name_list.append(yf.Ticker(symbol).info["shortName"])
    for stock in portfolio.securities:
        if stock.symbol == symbol:
            old_value = stock.initial_value
            old_shares = stock.shares
            new_shares = shares + old_shares
            new_buy_price = (old_value + (shares * buy_price)) / (old_shares + shares)
            shares_list.append(new_shares)
            price_list.append(new_buy_price)
            new_data = {"Symbol": symbol_list, "Name": name_list, "Shares": shares_list, "AvgPrice": price_list}
            new_df = pd.DataFrame(new_data)
            new_df.to_csv("portfolio-holdings.csv")
            buy_window.destroy()
            restart_app(None)
            return
    shares_list.append(shares)
    price_list.append(buy_price)
    new_data = {"Symbol": symbol_list, "Name": name_list, "Shares": shares_list, "AvgPrice": price_list}
    new_df = pd.DataFrame(new_data)
    new_df.to_csv("portfolio-holdings.csv")
    buy_window.destroy()
    restart_app(None)
    return


def sell_all_shares(window, stock):
    window.destroy()
    sell_confirm = askyesno(title="Sold All Shares?",
                            message=f"Did you sell all {stock.shares} shares? This will remove all information about {stock.name} from your portfolio data!")
    if sell_confirm:
        symbol_list = []
        name_list = []
        shares_list = []
        price_list = []
        for security in portfolio.securities:
            if security == stock:
                pass
            else:
                symbol_list.append(security.symbol)
                name_list.append(security.name)
                shares_list.append(security.shares)
                price_list.append(security.avg_price)
        new_data = {"Symbol": symbol_list, "Name": name_list, "Shares": shares_list, "AvgPrice": price_list}
        new_df = pd.DataFrame(new_data)
        new_df.to_csv("portfolio-holdings.csv")
        restart_app(None)
        return
    else:
        log_sell()


def log_sell():
    sell_window = tk.Toplevel(root)
    sell_window.geometry("200x300")
    sell_window.title("Log Sell")
    stock_label = tk.Label(sell_window, text="Select Stock")
    stock_label.pack(padx=5, pady=5)
    stock_options = []
    for stock in portfolio.securities:
        stock_options.append(stock.symbol)
    selected_stock = tk.StringVar(sell_window)
    selected_stock.set(stock_options[0])
    stock_dropdown = ttk.Combobox(sell_window, textvariable=selected_stock, values=stock_options, state="readonly")
    stock_dropdown.pack()
    shares_label = tk.Label(sell_window, text="# of Shares")
    shares_label.pack(padx=5, pady=5)
    shares_var = tk.StringVar()
    shares_entry = tk.Entry(sell_window, textvariable=shares_var, width=10)
    shares_entry.pack(padx=5, pady=5)
    submit_wait_var = tk.IntVar()
    submit_wait_var.set(0)
    submit_button = tk.Button(sell_window, text="Confirm", command=lambda: submit_wait_var.set(1))
    submit_button.pack(padx=5, pady=5)
    sell_all_shares_button = tk.Button(sell_window, text="Sell All Shares", command=lambda: sell_all_shares(sell_window,
                                                                                                            portfolio.get_security_by_symbol(
                                                                                                                selected_stock.get())))
    sell_all_shares_button.pack(padx=5, pady=5)
    sell_window.wait_variable(submit_wait_var)
    shares = float(shares_var.get())
    sold_stock: Stock = portfolio.get_security_by_symbol(selected_stock.get())
    symbol_list = []
    name_list = []
    shares_list = []
    price_list = []
    if sold_stock.shares == shares:
        for security in portfolio.securities:
            if security == sold_stock:
                pass
            else:
                symbol_list.append(security.symbol)
                name_list.append(security.name)
                shares_list.append(security.shares)
                price_list.append(security.avg_price)
        pass
    else:
        new_shares = sold_stock.shares - shares
        for security in portfolio.securities:
            symbol_list.append(security.symbol)
            name_list.append(security.name)
            price_list.append(security.avg_price)
            if security == sold_stock:
                shares_list.append(new_shares)
                pass
            else:
                shares_list.append(security.shares)
                pass
        pass
    new_data = {"Symbol": symbol_list, "Name": name_list, "Shares": shares_list, "AvgPrice": price_list}
    new_df = pd.DataFrame(new_data)
    new_df.to_csv("portfolio-holdings.csv")
    sell_window.destroy()
    restart_app(None)
    return


def on_stock_selected(event):
    global table
    selected_item = table.selection()[0]
    item_values = table.item(selected_item)['values']
    symbol = item_values[0]
    stock: Stock = portfolio.get_security_by_symbol(symbol)
    stock_window = tk.Toplevel(root)
    stock_window.geometry("1250x1000")
    stock_window.title(f"{stock.symbol} - {stock.name}")
    stock_title_label = tk.Label(stock_window, text=f"{stock.name}\n{stock.symbol}", font=("Arial", 30))
    stock_title_label.grid(padx=10, pady=10, column=0, row=0, columnspan=2)
    tinfo = yf.Ticker(stock.symbol).info
    for i in tinfo:
        print(i)
    info_frame = tk.LabelFrame(stock_window, text="Information")
    try:
        tk.Label(info_frame,
                 text=f"{tinfo['website']}\n{tinfo['longBusinessSummary']}\n\n{tinfo['industry']} - {tinfo['sector']}",
                 wraplength=595, width=65, height=25).pack(padx=5, pady=5)
        pass
    except Exception:
        tk.Label(info_frame,
                 text=f"FUND\n\n{tinfo['longBusinessSummary']}\n\nCategory: {tinfo['category']}\n\n",
                 wraplength=595, width=65, height=25).pack(padx=5, pady=5)
        pass
    info_frame.grid(padx=5, pady=5, column=0, row=1)
    price_info_frame = tk.LabelFrame(stock_window, text="Market Data")
    tk.Label(price_info_frame,
             text=f"-----Metrics-----\nCurrent Price: {stock.current_price}\nClose: {tinfo['previousClose']}\nOpen: "
                  f"{tinfo['open']}\nDay Low: {tinfo['dayLow']}\nDay High: {tinfo['dayHigh']}\n52-day Low: "
                  f"{tinfo['fiftyTwoWeekLow']}\n52-Week High: {tinfo['fiftyTwoWeekHigh']}\nVolume: "
                  f"{tinfo['volume']}\n\n\n-----Holdings-----\nShares: {stock.shares}\nAvg. Price/Share: {stock.avg_price}\n"
                  f"Value: {stock.current_value}\nInitial Value: {stock.initial_value}\n"
                  f"Total Change: {stock.absolute_gain} ({stock.relative_gain}%)\n"
                  f"Daily Change: {stock.daily_abs_gain} ({stock.daily_rel_gain}%)", wraplength=595, width=65,
             height=25).pack(padx=5, pady=5)
    price_info_frame.grid(padx=5, pady=5, column=1, row=1)
    dividend_frame = tk.LabelFrame(stock_window, text="Dividends")
    if "dividendYield" in tinfo:
        tk.Label(dividend_frame,
                 text=f"Rate: {tinfo['dividendRate']}\n\nYield: {tinfo['dividendYield']}\n\n5y Avg. Yield: {tinfo['fiveYearAvgDividendYield']}\n\n"
                      f"Ex-Div. Date: {datetime.datetime.fromtimestamp(int(tinfo['exDividendDate'])).strftime("%Y-%m-%d %H:%M:%S")}\n\nPayout Ratio: {tinfo['payoutRatio']}\n\n"
                      f"Last Div. Value: {tinfo['lastDividendValue']}\n\nLast Div. Date: {datetime.datetime.fromtimestamp(int(tinfo['lastDividendDate'])).strftime("%Y-%m-%d %H:%M:%S")}",
                 wraplength=595, width=65, height=25).pack(padx=5, pady=5)
        pass
    else:
        tk.Label(dividend_frame,
                 text=f"No Dividend Data",
                 wraplength=595, width=65, height=25).pack(padx=5, pady=5)
        pass
    dividend_frame.grid(padx=5, pady=5, column=0, row=2)
    tool_frame = tk.Frame(stock_window)
    dev_label = tk.Label(tool_frame, text="In development...")
    dev_label.pack(padx=10, pady=10)
    # TODO add tools
    tool_frame.grid(padx=5, pady=5, column=1, row=2)
    stock_window.after(15000, lambda: update_stock_window(stock_window, stock))
    return


def update_stock_window(window, stock):
    window.destroy()
    stock_window = tk.Toplevel(root)
    stock_window.geometry("1250x1000")
    stock_window.title(f"{stock.symbol} - {stock.name}")
    stock_title_label = tk.Label(stock_window, text=f"{stock.name}\n{stock.symbol}", font=("Arial", 30))
    stock_title_label.grid(padx=10, pady=10, column=0, row=0, columnspan=2)
    tinfo = yf.Ticker(stock.symbol).info
    for i in tinfo:
        print(i)
    info_frame = tk.LabelFrame(stock_window, text="Information")
    try:
        tk.Label(info_frame,
                 text=f"{tinfo['website']}\n{tinfo['longBusinessSummary']}\n\n{tinfo['industry']} - {tinfo['sector']}",
                 wraplength=595, width=65, height=25).pack(padx=5, pady=5)
        pass
    except Exception:
        tk.Label(info_frame,
                 text=f"FUND\n\n{tinfo['longBusinessSummary']}\n\nCategory: {tinfo['category']}\n\n",
                 wraplength=595, width=65, height=25).pack(padx=5, pady=5)
        pass
    info_frame.grid(padx=5, pady=5, column=0, row=1)
    price_info_frame = tk.LabelFrame(stock_window, text="Market Data")
    tk.Label(price_info_frame,
             text=f"-----Metrics-----\nCurrent Price: {stock.current_price}\nClose: {tinfo['previousClose']}\nOpen: "
                  f"{tinfo['open']}\nDay Low: {tinfo['dayLow']}\nDay High: {tinfo['dayHigh']}\n52-day Low: "
                  f"{tinfo['fiftyTwoWeekLow']}\n52-Week High: {tinfo['fiftyTwoWeekHigh']}\nVolume: "
                  f"{tinfo['volume']}\n\n\n-----Holdings-----\nShares: {stock.shares}\nAvg. Price/Share: {stock.avg_price}\n"
                  f"Value: {stock.current_value}\nInitial Value: {stock.initial_value}\n"
                  f"Total Change: {stock.absolute_gain} ({stock.relative_gain}%)\n"
                  f"Daily Change: {stock.daily_abs_gain} ({stock.daily_rel_gain}%)", wraplength=595, width=65,
             height=25).pack(padx=5, pady=5)
    price_info_frame.grid(padx=5, pady=5, column=1, row=1)
    dividend_frame = tk.LabelFrame(stock_window, text="Dividends")
    if "dividendYield" in tinfo:
        tk.Label(dividend_frame,
                 text=f"Rate: {tinfo['dividendRate']}\n\nYield: {tinfo['dividendYield']}\n\n5y Avg. Yield: {tinfo['fiveYearAvgDividendYield']}\n\n"
                      f"Ex-Div. Date: {datetime.datetime.fromtimestamp(int(tinfo['exDividendDate'])).strftime("%Y-%m-%d %H:%M:%S")}\n\nPayout Ratio: {tinfo['payoutRatio']}\n\n"
                      f"Last Div. Value: {tinfo['lastDividendValue']}\n\nLast Div. Date: {datetime.datetime.fromtimestamp(int(tinfo['lastDividendDate'])).strftime("%Y-%m-%d %H:%M:%S")}",
                 wraplength=595, width=65, height=25).pack(padx=5, pady=5)
        pass
    else:
        tk.Label(dividend_frame,
                 text=f"No Dividend Data",
                 wraplength=595, width=65, height=25).pack(padx=5, pady=5)
        pass
    dividend_frame.grid(padx=5, pady=5, column=0, row=2)
    tool_frame = tk.Frame(stock_window)
    dev_label = tk.Label(tool_frame, text="In development...")
    dev_label.pack(padx=10, pady=10)
    # TODO add tools
    tool_frame.grid(padx=5, pady=5, column=1, row=2)
    stock_window.after(15000, lambda: update_stock_window(stock_window, stock))
    return


def dividend_tracker():
    return  # TODO


def benchmark_portfolio_performance():
    return  # TODO


def edit_holdings_file():
    showinfo(title="Edit Holdings", message="Holdings file will be opened in default system app.")
    if platform.system() == 'Darwin':
        subprocess.call(('open', "portfolio-holdings.csv"))
    elif platform.system() == 'Windows':
        os.startfile("portfolio-holdings.csv")
    else:
        subprocess.call(('xdg-open', "portfolio-holdings.csv"))
    return


def portfolio_summary():
    return  # TODO


def restart_app(event):
    global table_frame, stats_frame, actions_frame
    table_frame.destroy()
    stats_frame.destroy()
    actions_frame.destroy()
    restarting_text = tk.Label(root, text="Restarting...", font=("Arial", 30))
    restarting_text.pack(pady=150)
    print("Restarting")
    time.sleep(1)
    os.execv(sys.executable, [sys.executable] + sys.argv)


def quit_app(event):
    print("Quitting")
    root.destroy()
    sys.exit(0)


portfolio = Portfolio()
root = tk.Tk()
root.title("Stonks 📈")
root.geometry("1350x800")
root.protocol("WM_DELETE_WINDOW", lambda: quit_app(None))
root.bind("<r>", restart_app)
root.bind("<F5>", restart_app)
root.bind("<Escape>", quit_app)
if os.path.exists("portfolio-holdings.csv"):
    loading_label = tk.Label(root, text="Loading...", font=("Arial", 30))
    loading_label.pack(pady=150)
    other_loading_label = tk.Label(root, text="Download might take a couple seconds", font=("Arial", 15))
    other_loading_label.pack()
    cancel_button = tk.Button(root, text="Cancel", command=lambda: quit_app(None))
    cancel_button.pack(padx=20, pady=20)
    root.after(100, load_app)
else:
    error_label = tk.Label(root, text=f"Error: Portfolio data not found\nPlace portfolio-holdings.csv in {os.getcwd()}",
                           font=("Arial", 30))
    error_label.pack(pady=150)
    restart_button = tk.Button(root, text="Restart", command=lambda: restart_app(None))
    restart_button.pack(padx=20, pady=20)
    quit_button = tk.Button(root, text="Quit", command=lambda: quit_app(None))
    quit_button.pack(padx=20, pady=20)
table_frame = tk.Frame(root)
stats_frame = tk.Frame(root)
launch_time = time.strftime('%l:%M:%S')
last_refreshed_text = tk.Label(root, text=f"↻ {launch_time}", font=("Arial", 10))
actions_frame = tk.Frame(root)
table = ttk.Treeview(table_frame, columns=(
    "Symbol", "Name", "Price", "Shares", "Value", "Initial Value", "Cost/Share", "Total Change $", "Total Change %",
    "Day Change $", "Day Change %"), height=len(portfolio.securities))
refresh_interval = None
root.mainloop()
