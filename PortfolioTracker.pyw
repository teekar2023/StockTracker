import tkinter as tk
from tkinter import ttk
from tkinter.messagebox import askyesno, showinfo
from tkinter.simpledialog import askstring

import pandas as pd
import yfinance as yf
import time
import os
import sys
import json
from datetime import datetime, date
import subprocess
import platform
import sv_ttk
from matplotlib import pyplot as plt


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
        stock_data = yf.download(self.symbol, period="1d", prepost=True)
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
        self.total_daily_rel_gain = round(self.total_daily_abs_gain / self.total_initial_value, 2)
        self.total_daily_abs_gain = round(self.total_daily_abs_gain, 2)
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


def update_main_window():
    global table_frame, stats_frame, actions_frame, table, refresh_interval, portfolio, last_refreshed_text, loading_label, other_loading_label
    root.geometry("1675x600")
    try:
        table_frame.destroy()
        stats_frame.destroy()
        actions_frame.destroy()
        last_refreshed_text.destroy()
        loading_label.destroy()
        other_loading_label.destroy()
        pass
    except Exception:
        pass
    for stock in portfolio.securities:
        stock.calculate_gain()
    portfolio.calculate_total_gain()
    refresh_interval = root.after(settings_json["refresh-interval"] * 1000, update_main_window)
    table_frame = ttk.LabelFrame(root, text="Holdings")
    table = ttk.Treeview(table_frame, columns=(
        "Symbol", "Name", "Price", "Shares", "Value", "Principal", "Cost/Share", "Total $", "Total %",
        "Day $", "Day %"), height=len(portfolio.securities))
    table.config(height=len(portfolio.securities))
    table.bind('<<TreeviewSelect>>', on_stock_selected)
    table.heading("Symbol", text="Symbol")
    table.heading("Name", text="Name")
    table.heading("Price", text="Price")
    table.heading("Shares", text="Shares")
    table.heading("Value", text="Value")
    table.heading("Principal", text="Principal")
    table.heading("Cost/Share", text="Cost/Share")
    table.heading("Total $", text="Total $")
    table.heading("Total %", text="Total %")
    table.heading("Day $", text="Day $")
    table.heading("Day %", text="Day %")
    for stock in portfolio.securities:
        table.insert("", tk.END, values=[stock.symbol, stock.name, round(stock.current_price, 2), stock.shares,
                                         round(stock.current_value, 2), round(stock.initial_value, 2), stock.avg_price,
                                         round(stock.absolute_gain, 2), round(stock.relative_gain, 2),
                                         round(stock.daily_abs_gain, 2), round(stock.daily_rel_gain, 2)])
    table.column("#0", width=0)
    table.column("#1", width=50)
    table.column("#2", width=230)
    table.column("#3", width=115)
    table.column("#4", width=115)
    table.column("#5", width=115)
    table.column("#6", width=115)
    table.column("#7", width=115)
    table.column("#8", width=115)
    table.column("#9", width=115)
    table.column("#10", width=115)
    table.column("#11", width=115)
    stats_frame = ttk.Frame(root)
    total_value_label = ttk.Label(stats_frame, text=f"Value: ${portfolio.total_value}", font=("Helvetica", 20))
    daily_gain_label = ttk.Label(stats_frame,
                                text=f"Daily: ${portfolio.total_daily_abs_gain} ({portfolio.total_daily_rel_gain}%)",
                                font=("Helvetica", 18))
    total_gain_label = ttk.Label(stats_frame, text=f"Total: ${portfolio.total_abs_gain} ({portfolio.total_rel_gain}%)",
                                font=("Helvetica", 18))
    total_value_label.grid(column=0, row=0, padx=5, pady=5)
    daily_gain_label.grid(column=0, row=1, padx=5, pady=5)
    total_gain_label.grid(column=0, row=2, padx=5, pady=5)
    actions_frame = ttk.Frame(root)
    refreshed_time = time.strftime('%l:%M:%S')
    last_refreshed_text = ttk.Label(root, text=f"↻ {refreshed_time}", font=("Helvetica", 15))
    log_transaction_label = ttk.Label(actions_frame, text="Portfolio", font=("Helvetica", 18))
    log_transaction_label.grid(column=0, row=1, columnspan=3, padx=5, pady=5)
    log_buy_button = ttk.Button(actions_frame, text="+ Buy", command=log_buy)
    log_buy_button.grid(column=0, row=2, padx=5, pady=5)
    log_sell_button = ttk.Button(actions_frame, text="- Sell", command=log_sell)
    log_sell_button.grid(column=1, row=2, padx=5, pady=5)
    edit_file_button = ttk.Button(actions_frame, text="✎ Edit", command=edit_holdings_file)
    edit_file_button.grid(column=2, row=2, padx=5, pady=5)
    analysis_tools_label = ttk.Label(actions_frame, text="Tools", font=("Helvetica", 18))
    analysis_tools_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
    dividend_tracker_button = ttk.Button(actions_frame, text="Dividends", command=dividend_tracker)
    dividend_tracker_button.grid(column=2, row=4, padx=5, pady=5)
    benchmark_tool_button = ttk.Button(actions_frame, text="Benchmark", command=benchmark_portfolio_performance)
    benchmark_tool_button.grid(column=1, row=4, padx=5, pady=5)
    summary_button = ttk.Button(actions_frame, text="Summary", command=portfolio_summary)
    summary_button.grid(column=0, row=4, padx=5, pady=5)
    search_button = ttk.Button(actions_frame, text="Search", command=search_stock)
    search_button.grid(padx=5, pady=5, column=0, row=5)
    settings_button = ttk.Button(actions_frame, text="Settings", command=app_settings)
    settings_button.grid(column=1, row=5, padx=5, pady=5)
    exit_button = ttk.Button(actions_frame, text="Quit", command=lambda: quit_app(None))
    exit_button.grid(column=2, row=5, padx=5, pady=5)
    stats_frame.grid(padx=10, pady=10, column=0, row=0)
    table.pack(padx=5, pady=5)
    table_frame.grid(padx=10, pady=10, column=0, row=1)
    last_refreshed_text.grid(padx=5, pady=5, column=0, row=2)
    actions_frame.grid(padx=10, pady=10, column=1, row=1)
    root.deiconify()
    root.update()
    print("Refresh complete")
    alerts_json = json.load(open("Settings/alerts.json", "r"))
    triggered_alerts = []
    for alert in alerts_json:
        stock_data = yf.download(alert["symbol"], period="1d", prepost=True)
        try:
            if alert["tresh"] == "Rises Above":
                if stock_data['Close'].iloc[-1] >= alert["target-price"]:
                    showinfo(title="Custom Alert", message=f"{alert["symbol"]} rose above {alert["target-price"]}. This alert will now be deleted")
                    triggered_alerts.append(alerts_json.index(alert))
            else:
                if stock_data['Close'].iloc[-1] <= alert["target-price"]:
                    showinfo(title="Custom Alert", message=f"{alert["symbol"]} fell below {alert["target-price"]}. This alert will now be deleted")
                    triggered_alerts.append(alerts_json.index(alert))
            pass
        except Exception:
            pass
    new_alerts = []
    for alert in alerts_json:
        if alert not in triggered_alerts:
            new_alerts.append(alert)
    alerts_object = json.dumps(new_alerts, indent=4)
    alerts_file = open("Settings/alerts.json", "w+")
    alerts_file.truncate(0)
    with alerts_file as outfile:
        outfile.write(alerts_object)
        alerts_file.close()
        pass
    print("Alert check complete")
    return


def load_app():
    global root, loading_label, portfolio, stats_frame, table_frame, actions_frame, table, refresh_interval, last_refreshed_text, other_loading_label, yet_another_loading_label
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
    yet_another_loading_label.destroy()
    table.config(height=len(portfolio.securities))
    table.bind('<<TreeviewSelect>>', on_stock_selected)
    table.heading("Symbol", text="Symbol")
    table.heading("Name", text="Name")
    table.heading("Price", text="Price")
    table.heading("Shares", text="Shares")
    table.heading("Value", text="Value")
    table.heading("Principal", text="Principal")
    table.heading("Cost/Share", text="Cost/Share")
    table.heading("Total $", text="Total $")
    table.heading("Total %", text="Total %")
    table.heading("Day $", text="Day $")
    table.heading("Day %", text="Day %")
    for stock in portfolio.securities:
        table.insert("", tk.END, values=[stock.symbol, stock.name, round(stock.current_price, 2), stock.shares,
                                         round(stock.current_value, 2), round(stock.initial_value, 2), stock.avg_price,
                                         round(stock.absolute_gain, 2), round(stock.relative_gain, 2),
                                         round(stock.daily_abs_gain, 2), round(stock.daily_rel_gain, 2)])
    table.column("#0", width=0)
    table.column("#1", width=50)
    table.column("#2", width=230)
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
    total_value_label = ttk.Label(stats_frame, text=f"Value: ${portfolio.total_value}", font=("Helvetica", 20))
    daily_gain_label = ttk.Label(stats_frame,
                                text=f"Daily: ${portfolio.total_daily_abs_gain} ({portfolio.total_daily_rel_gain}%)",
                                font=("Helvetica", 18))
    total_gain_label = ttk.Label(stats_frame, text=f"Total: ${portfolio.total_abs_gain} ({portfolio.total_rel_gain}%)",
                                font=("Helvetica", 18))
    total_value_label.grid(column=0, row=0, padx=5, pady=5)
    daily_gain_label.grid(column=0, row=1, padx=5, pady=5)
    total_gain_label.grid(column=0, row=2, padx=5, pady=5)
    log_transaction_label = ttk.Label(actions_frame, text="Portfolio", font=("Helvetica", 18))
    log_transaction_label.grid(column=0, row=1, columnspan=3, padx=5, pady=5)
    log_buy_button = ttk.Button(actions_frame, text="+ Buy", command=log_buy)
    log_buy_button.grid(column=0, row=2, padx=5, pady=5)
    log_sell_button = ttk.Button(actions_frame, text="- Sell", command=log_sell)
    log_sell_button.grid(column=1, row=2, padx=5, pady=5)
    edit_file_button = ttk.Button(actions_frame, text="✎ Edit", command=edit_holdings_file)
    edit_file_button.grid(column=2, row=2, padx=5, pady=5)
    analysis_tools_label = ttk.Label(actions_frame, text="Tools", font=("Helvetica", 18))
    analysis_tools_label.grid(row=3, column=0, columnspan=3, padx=5, pady=5)
    dividend_tracker_button = ttk.Button(actions_frame, text="Dividends", command=dividend_tracker)
    dividend_tracker_button.grid(column=2, row=4, padx=5, pady=5)
    benchmark_tool_button = ttk.Button(actions_frame, text="Benchmark", command=benchmark_portfolio_performance)
    benchmark_tool_button.grid(column=1, row=4, padx=5, pady=5)
    summary_button = ttk.Button(actions_frame, text="Summary", command=portfolio_summary)
    summary_button.grid(column=0, row=4, padx=5, pady=5)
    search_button = ttk.Button(actions_frame, text="Search", command=search_stock)
    search_button.grid(padx=5, pady=5, column=0, row=5)
    settings_button = ttk.Button(actions_frame, text="Settings", command=app_settings)
    settings_button.grid(column=1, row=5, padx=5, pady=5)
    exit_button = ttk.Button(actions_frame, text="Quit", command=lambda: quit_app(None))
    exit_button.grid(column=2, row=5, padx=5, pady=5)
    stats_frame.grid(padx=10, pady=10, column=0, row=0)
    table.pack(padx=5, pady=5)
    table_frame.grid(padx=10, pady=10, column=0, row=1)
    last_refreshed_text.grid(padx=5, pady=5, column=0, row=2)
    actions_frame.grid(padx=10, pady=10, column=1, row=1)
    root.deiconify()
    root.update()
    refresh_interval = root.after(settings_json["refresh-interval"] * 1000, update_main_window)
    print("Loading complete")
    return


def log_buy():
    buy_window = tk.Toplevel(root)
    buy_window.geometry("200x300")
    buy_window.title("Log Buy")
    buy_window_title = ttk.Label(buy_window, text="Add Buy to Portfolio")
    buy_window_title.pack(padx=5, pady=5)
    symbol_label = ttk.Label(buy_window, text="Stock Symbol")
    symbol_label.pack(padx=5, pady=5)
    symbol_var = tk.StringVar()
    symbol_entry = ttk.Entry(buy_window, textvariable=symbol_var, width=10)
    symbol_entry.pack(padx=5, pady=5)
    shares_label = ttk.Label(buy_window, text="# of Shares")
    shares_label.pack(padx=5, pady=5)
    shares_var = tk.StringVar()
    shares_entry = ttk.Entry(buy_window, textvariable=shares_var, width=10)
    shares_entry.pack(padx=5, pady=5)
    buy_price_label = tk.Label(buy_window, text="Cost/Share")
    buy_price_label.pack(padx=5, pady=5)
    buy_price_var = tk.StringVar()
    buy_price_entry = ttk.Entry(buy_window, textvariable=buy_price_var, width=10)
    buy_price_entry.pack(padx=5, pady=5)
    submit_wait_var = tk.IntVar()
    submit_wait_var.set(0)
    submit_button = ttk.Button(buy_window, text="Confirm", command=lambda: submit_wait_var.set(1))
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
    stock_label = ttk.Label(sell_window, text="Select Stock")
    stock_label.pack(padx=5, pady=5)
    stock_options = []
    for stock in portfolio.securities:
        stock_options.append(stock.symbol)
    selected_stock = tk.StringVar(sell_window)
    selected_stock.set(stock_options[0])
    stock_dropdown = ttk.Combobox(sell_window, textvariable=selected_stock, values=stock_options, state="readonly")
    stock_dropdown.pack()
    shares_label = ttk.Label(sell_window, text="# of Shares")
    shares_label.pack(padx=5, pady=5)
    shares_var = tk.StringVar()
    shares_entry = ttk.Entry(sell_window, textvariable=shares_var, width=10)
    shares_entry.pack(padx=5, pady=5)
    submit_wait_var = tk.IntVar()
    submit_wait_var.set(0)
    submit_button = ttk.Button(sell_window, text="Confirm", command=lambda: submit_wait_var.set(1))
    submit_button.pack(padx=5, pady=5)
    sell_all_shares_button = ttk.Button(sell_window, text="Sell All Shares", command=lambda: sell_all_shares(sell_window,
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
    global table_frame, stats_frame, actions_frame, table, refresh_interval, portfolio, last_refreshed_text, loading_label, other_loading_label
    root.after_cancel(refresh_interval)
    selected_item = table.selection()[0]
    item_values = table.item(selected_item)['values']
    symbol = item_values[0]
    table_frame.destroy()
    stats_frame.destroy()
    actions_frame.destroy()
    last_refreshed_text.destroy()
    root.geometry("1030x885")
    stock: Stock = portfolio.get_security_by_symbol(symbol)
    stock_title_label = ttk.Label(root, text=f"{stock.name}\n{stock.symbol}", font=("Helvetica", 30))
    stock_title_label.grid(padx=5, pady=5, column=0, row=0)
    tinfo = yf.Ticker(stock.symbol).info
    for i in tinfo:
        print(i)
    info_frame = ttk.LabelFrame(root, text="Information")
    try:
        ttk.Label(info_frame,
                 text=f"{tinfo['website']}\n{tinfo['longBusinessSummary']}\n\n{tinfo['industry']} - {tinfo['sector']}",
                 wraplength=520, width=60).pack(padx=5, pady=5)
        pass
    except Exception:
        ttk.Label(info_frame,
                 text=f"ETF\n\n{tinfo['longBusinessSummary']}\n\nCategory: {tinfo['category']}\n\n",
                 wraplength=520, width=60).pack(padx=5, pady=5)
        pass
    info_frame.grid(padx=5, pady=5, column=0, row=1)
    price_info_frame = ttk.LabelFrame(root, text="Market Data")
    ttk.Label(price_info_frame,
             text=f"-----Metrics-----\nCurrent Price: {stock.current_price}\nClose: {tinfo['previousClose']}\nOpen: "
                  f"{tinfo['open']}\nDay Low: {tinfo['dayLow']}\nDay High: {tinfo['dayHigh']}\n52-day Low: "
                  f"{tinfo['fiftyTwoWeekLow']}\n52-Week High: {tinfo['fiftyTwoWeekHigh']}\nVolume: "
                  f"{tinfo['volume']}\n\n\n-----Holdings-----\nShares: {stock.shares}\nAvg. Price/Share: {stock.avg_price}\n"
                  f"Value: {stock.current_value}\nInitial Value: {stock.initial_value}\n"
                  f"Total Change: {stock.absolute_gain} ({stock.relative_gain}%)\n"
                  f"Daily Change: {stock.daily_abs_gain} ({stock.daily_rel_gain}%)", wraplength=520, width=50).pack(padx=5, pady=5)
    price_info_frame.grid(padx=5, pady=5, column=1, row=1)
    dividend_frame = ttk.LabelFrame(root, text="Dividends")
    if "dividendYield" in tinfo:
        ttk.Label(dividend_frame,
                 text=f"Rate: {tinfo['dividendRate']}\n\nYield: {tinfo['dividendYield']}\n\n5y Avg. Yield: {tinfo['fiveYearAvgDividendYield']}\n\n"
                      f"Ex-Div. Date: {datetime.fromtimestamp(int(tinfo['exDividendDate'])).strftime("%Y-%m-%d %H:%M:%S")}\n\nPayout Ratio: {tinfo['payoutRatio']}\n\n"
                      f"Last Div. Value: {tinfo['lastDividendValue']}\n\nLast Div. Date: {datetime.fromtimestamp(int(tinfo['lastDividendDate'])).strftime("%Y-%m-%d %H:%M:%S")}",
                 wraplength=520, width=60).pack(padx=5, pady=5)
        pass
    else:
        ttk.Label(dividend_frame,
                 text=f"No Dividend Data",
                 wraplength=520, width=60).pack(padx=5, pady=5)
        pass
    dividend_frame.grid(padx=5, pady=5, column=0, row=2)
    tool_frame = ttk.LabelFrame(root, text="More Tools")
    graphs_button = ttk.Button(tool_frame, text="Graphs", command=lambda: stock_graphs(stock))
    graphs_button.grid(padx=5, pady=5, column=0, row=0)
    news_button = ttk.Button(tool_frame, text="News", command=lambda: stock_news(stock))
    news_button.grid(padx=5, pady=5, column=1, row=0)
    earnings_button = ttk.Button(tool_frame, text="Earnings", command=lambda: stock_earnings(stock))
    earnings_button.grid(padx=5, pady=5, column=0, row=1)
    back_button_wait_var = tk.IntVar(root, 0)
    back_button = ttk.Button(tool_frame, text="Back", command=lambda: back_button_wait_var.set(1))
    back_button.grid(padx=5, pady=5, column=1, row=1)
    tool_frame.grid(padx=5, pady=5, column=1, row=2)
    root.deiconify()
    root.update()
    root.focus_set()
    root.wait_variable(back_button_wait_var)
    stock_title_label.destroy()
    info_frame.destroy()
    price_info_frame.destroy()
    dividend_frame.destroy()
    tool_frame.destroy()
    loading_label = ttk.Label(root, text="Loading...", font=("Helvetica", 30))
    loading_label.pack(pady=150)
    other_loading_label = ttk.Label(root, text="Download might take a couple seconds...", font=("Helvetica", 15))
    other_loading_label.pack()
    root.deiconify()
    root.update()
    root.focus_set()
    update_main_window()
    return


def search_stock():
    global table_frame, stats_frame, actions_frame, table, refresh_interval, portfolio, last_refreshed_text, loading_label, other_loading_label
    symbol = askstring(title="Stock Search", prompt="Enter symbol to view stock information").upper()
    if symbol is None or symbol == "" or symbol.isspace():
        return
    root.after_cancel(refresh_interval)
    table_frame.destroy()
    stats_frame.destroy()
    actions_frame.destroy()
    last_refreshed_text.destroy()
    root.geometry("1030x885")
    tinfo = yf.Ticker(symbol).info
    stock_data = yf.download(symbol, period="1d", prepost=True)
    stock_title_label = ttk.Label(root, text=f"{tinfo["shortName"]}\n{symbol}", font=("Helvetica", 30))
    stock_title_label.grid(padx=5, pady=5, column=0, row=0)
    info_frame = ttk.LabelFrame(root, text="Information")
    try:
        ttk.Label(info_frame,
                  text=f"{tinfo['website']}\n{tinfo['longBusinessSummary']}\n\n{tinfo['industry']} - {tinfo['sector']}",
                  wraplength=520, width=60).pack(padx=5, pady=5)
        pass
    except Exception:
        ttk.Label(info_frame,
                  text=f"ETF\n\n{tinfo['longBusinessSummary']}\n\nCategory: {tinfo['category']}\n\n",
                  wraplength=520, width=60).pack(padx=5, pady=5)
        pass
    info_frame.grid(padx=5, pady=5, column=0, row=1)
    price_info_frame = ttk.LabelFrame(root, text="Market Data")
    try:
        stock = portfolio.get_security_by_symbol(symbol)
        ttk.Label(price_info_frame,
                  text=f"-----Metrics-----\nCurrent Price: {stock.current_price}\nClose: {tinfo['previousClose']}\nOpen: "
                       f"{tinfo['open']}\nDay Low: {tinfo['dayLow']}\nDay High: {tinfo['dayHigh']}\n52-day Low: "
                       f"{tinfo['fiftyTwoWeekLow']}\n52-Week High: {tinfo['fiftyTwoWeekHigh']}\nVolume: "
                       f"{tinfo['volume']}\n\n\n-----Holdings-----\nShares: {stock.shares}\nAvg. Price/Share: {stock.avg_price}\n"
                       f"Value: {stock.current_value}\nInitial Value: {stock.initial_value}\n"
                       f"Total Change: {stock.absolute_gain} ({stock.relative_gain}%)\n"
                       f"Daily Change: {stock.daily_abs_gain} ({stock.daily_rel_gain}%)", wraplength=520,
                  width=50).pack(
            padx=5, pady=5)
    except Exception:
        ttk.Label(price_info_frame,
                text=f"-----Metrics-----\nCurrent Price: {stock_data['Close'].iloc[-1]}\nClose: {tinfo['previousClose']}\nOpen: "
                    f"{tinfo['open']}\nDay Low: {tinfo['dayLow']}\nDay High: {tinfo['dayHigh']}\n52-day Low: "
                    f"{tinfo['fiftyTwoWeekLow']}\n52-Week High: {tinfo['fiftyTwoWeekHigh']}\nVolume: "
                    f"{tinfo['volume']}", wraplength=520, width=50).pack(
            padx=5, pady=5)
    price_info_frame.grid(padx=5, pady=5, column=1, row=1)
    dividend_frame = ttk.LabelFrame(root, text="Dividends")
    if "dividendYield" in tinfo:
        ttk.Label(dividend_frame,
                  text=f"Rate: {tinfo['dividendRate']}\n\nYield: {tinfo['dividendYield']}\n\n5y Avg. Yield: {tinfo['fiveYearAvgDividendYield']}\n\n"
                       f"Ex-Div. Date: {datetime.fromtimestamp(int(tinfo['exDividendDate'])).strftime("%Y-%m-%d %H:%M:%S")}\n\nPayout Ratio: {tinfo['payoutRatio']}\n\n"
                       f"Last Div. Value: {tinfo['lastDividendValue']}\n\nLast Div. Date: {datetime.fromtimestamp(int(tinfo['lastDividendDate'])).strftime("%Y-%m-%d %H:%M:%S")}",
                  wraplength=520, width=60).pack(padx=5, pady=5)
        pass
    else:
        ttk.Label(dividend_frame,
                  text=f"No Dividend Data",
                  wraplength=520, width=60).pack(padx=5, pady=5)
        pass
    dividend_frame.grid(padx=5, pady=5, column=0, row=2)
    tool_frame = ttk.LabelFrame(root, text="More Tools")
    graphs_button = ttk.Button(tool_frame, text="Graphs", command=lambda: stock_graphs(stock))
    graphs_button.grid(padx=5, pady=5, column=0, row=0)
    news_button = ttk.Button(tool_frame, text="News", command=lambda: stock_news(stock))
    news_button.grid(padx=5, pady=5, column=1, row=0)
    earnings_button = ttk.Button(tool_frame, text="Earnings", command=lambda: stock_earnings(stock))
    earnings_button.grid(padx=5, pady=5, column=0, row=1)
    back_button_wait_var = tk.IntVar(root, 0)
    back_button = ttk.Button(tool_frame, text="Back", command=lambda: back_button_wait_var.set(1))
    back_button.grid(padx=5, pady=5, column=1, row=1)
    tool_frame.grid(padx=5, pady=5, column=1, row=2)
    root.deiconify()
    root.update()
    root.focus_set()
    root.wait_variable(back_button_wait_var)
    stock_title_label.destroy()
    info_frame.destroy()
    price_info_frame.destroy()
    dividend_frame.destroy()
    tool_frame.destroy()
    loading_label = ttk.Label(root, text="Loading...", font=("Helvetica", 30))
    loading_label.pack(pady=150)
    other_loading_label = ttk.Label(root, text="Download might take a couple seconds...", font=("Helvetica", 15))
    other_loading_label.pack()
    root.deiconify()
    root.update()
    root.focus_set()
    update_main_window()
    return


def stock_graphs(stock: Stock):
    return  # TODO


def stock_news(stock: Stock):
    return  # TODO


def stock_earnings(stock: Stock):
    return  # TODO


def dividend_tracker():
    global table_frame, stats_frame, actions_frame, table, refresh_interval, portfolio, last_refreshed_text, loading_label, other_loading_label
    dividend_stock_list = []
    for security in portfolio.securities:
        tinfo = yf.Ticker(security.symbol).info
        if "dividendYield" in tinfo:
            dividend_stock_list.append(security)
    root.after_cancel(refresh_interval)
    table_frame.destroy()
    stats_frame.destroy()
    actions_frame.destroy()
    last_refreshed_text.destroy()
    root.geometry("600x460")
    dividend_tracker_title = ttk.Label(root, text="Dividend Tracker", font=("Helvetica", 30))
    dividend_tracker_title.grid(padx=5, pady=5, column=0, row=0, columnspan=2)
    dividend_stock_list_text = "-----Positions-----\n"
    weight_list = []
    yield_list = []
    for security in portfolio.securities:
        tinfo = yf.Ticker(security.symbol).info
        weight = security.current_value / portfolio.total_value
        if "dividendYield" in tinfo:
            weight_list.append(weight)
            yield_list.append(tinfo['dividendYield'])
        else:
            weight_list.append(weight)
            yield_list.append(0.0)
    total_div_yield = 0.0
    for i in range(len(weight_list)):
        div_yield = yield_list[i]
        weight = weight_list[i]
        weighted_yield = div_yield * weight
        total_div_yield += weighted_yield
    total_div_yield *= 100
    dividend_stock_list_text += f"Total Dividend Yield: {round(total_div_yield, 2)}%\n\n"
    for stock in dividend_stock_list:
        dividend_stock_list_text += f"{stock.name} - {yf.Ticker(stock.symbol).info["dividendYield"] * 100}%\n\n"
    list_of_dividend_stocks = ttk.Label(root, text=f"{dividend_stock_list_text}")
    list_of_dividend_stocks.grid(padx=5, pady=5, column=0, row=1)
    upcoming_dividends_string = "-----Forecasted-----\n"
    today = date.today()
    previous_dividends = []
    for stock in dividend_stock_list:
        expected_date = datetime.fromtimestamp(
            int(yf.Ticker(stock.symbol).info['exDividendDate'])).date()
        days_until = (expected_date - today).days
        if days_until == 0:
            upcoming_dividends_string += f"{stock.symbol} - TODAY: {yf.Ticker(stock.symbol).info["dividendYield"] * 100}%\n"
        elif days_until > 0:
            upcoming_dividends_string += f"{stock.symbol} - {expected_date}: {yf.Ticker(stock.symbol).info["dividendYield"] * 100}%\n"
        else:
            previous_dividends.append(stock)
            pass
    if len(previous_dividends) == 0:
        pass
    else:
        upcoming_dividends_string += "\n\n-----Recent-----\n"
        for stock in previous_dividends:
            expected_date = datetime.fromtimestamp(
                int(yf.Ticker(stock.symbol).info['lastDividendDate'])).date()
            days_until = (expected_date - today).days
            upcoming_dividends_string += f"{stock.symbol} - {str(days_until).replace("-", "")} days: {yf.Ticker(stock.symbol).info["dividendYield"] * 100}% | ${round(yf.Ticker(stock.symbol).info["lastDividendValue"] * stock.shares, 2)}\n"
    upcoming_dividends_text = ttk.Label(root, text=upcoming_dividends_string)
    upcoming_dividends_text.grid(padx=5, pady=5, column=1, row=1)
    back_button_wait_var = tk.IntVar(root, 0)
    back_button = ttk.Button(root, text="Back", command=lambda: back_button_wait_var.set(1))
    back_button.grid(padx=5, pady=5, column=0, row=2, columnspan=2)
    root.deiconify()
    root.update()
    root.focus_set()
    root.wait_variable(back_button_wait_var)
    dividend_tracker_title.destroy()
    list_of_dividend_stocks.destroy()
    upcoming_dividends_text.destroy()
    back_button.destroy()
    loading_label = ttk.Label(root, text="Loading...", font=("Helvetica", 30))
    loading_label.pack(pady=150)
    other_loading_label = ttk.Label(root, text="Download might take a couple seconds...", font=("Helvetica", 15))
    other_loading_label.pack()
    root.deiconify()
    root.update()
    root.focus_set()
    update_main_window()
    return


def benchmark_portfolio_performance():
    return  # TODO allow user to select benchmark from dropdown and show both graphs on top of each other


def app_settings():
    global table_frame, stats_frame, actions_frame, table, refresh_interval, portfolio, last_refreshed_text, loading_label, other_loading_label
    root.after_cancel(refresh_interval)
    table_frame.destroy()
    stats_frame.destroy()
    actions_frame.destroy()
    last_refreshed_text.destroy()
    root.geometry("660x350")
    settings_window_title = ttk.Label(root, text="Settings", font=("Helvetica", 30))
    settings_window_title.grid(padx=5, pady=5, column=0, row=0, columnspan=3)
    customization_frame = ttk.LabelFrame(root, text="Customization")
    dark_mode_var = tk.IntVar()
    dark_mode_checkbutton = ttk.Checkbutton(customization_frame, text="Dark Mode", variable=dark_mode_var, onvalue=1,
                                            offvalue=0)
    dark_mode_checkbutton.pack(padx=5, pady=5)
    customization_frame.grid(padx=5, pady=5, column=0, row=1)
    other_frame = ttk.LabelFrame(root, text="Other")
    refresh_interval_label = ttk.Label(other_frame, text="Refresh Interval (Seconds)")
    refresh_interval_label.pack(padx=5, pady=5)
    refresh_interval_entry = ttk.Entry(other_frame, width=5)
    refresh_interval_entry.pack(padx=5, pady=5)
    other_frame.grid(padx=5, pady=5, column=1, row=1)
    settings_json = json.load(open("Settings/settings.json", "r"))
    if settings_json["dark-mode"] == 1:
        dark_mode_var.set(1)
    refresh_interval_entry.insert(tk.END, settings_json["refresh-interval"])
    alerts_frame = ttk.LabelFrame(root, text="Alerts")
    list_of_alerts_string = "-----Current Alerts-----\n"
    alerts_json = json.load(open("Settings/alerts.json", "r"))
    for alert in alerts_json:
        if alert["tresh"] == "Rises Above":
            list_of_alerts_string += f"{alert["symbol"]} | >${alert["target-price"]}\n"
        else:
            list_of_alerts_string += f"{alert["symbol"]} | <${alert["target-price"]}\n"
    list_of_alerts_text = ttk.Label(alerts_frame, text=list_of_alerts_string)
    list_of_alerts_text.grid(padx=5, pady=5, column=0, row=0)
    add_alert_button = ttk.Button(alerts_frame, text="Create", command=create_alert)
    add_alert_button.grid(padx=5, pady=5, column=1, row=0)
    remove_alert_button = ttk.Button(alerts_frame, text="Remove", command=remove_alert)
    remove_alert_button.grid(padx=5, pady=5, column=2, row=0)
    alerts_frame.grid(padx=5, pady=5, row=1, column=2)
    settings_wait_var = tk.IntVar(root, 0)
    save_button = ttk.Button(root, text="Save", command=lambda: settings_wait_var.set(1), style="Accent.TButton")
    save_button.grid(row=2, column=1, padx=5, pady=5)
    back_button = ttk.Button(root, text="Back", command=lambda: restart_app(None))
    back_button.grid(padx=5, pady=5, row=2, column=0)
    root.deiconify()
    root.update()
    root.focus_set()
    root.wait_variable(settings_wait_var)
    settings = {
        "refresh-interval": int(refresh_interval_entry.get()),
        "dark-mode": dark_mode_var.get()
    }
    settings_window_title.destroy()
    customization_frame.destroy()
    other_frame.destroy()
    alerts_frame.destroy()
    back_button.destroy()
    save_button.destroy()
    settings_object = json.dumps(settings, indent=4)
    settings_file = open("Settings/settings.json", "w+")
    settings_file.truncate(0)
    with settings_file as outfile:
        outfile.write(settings_object)
        settings_file.close()
        pass
    restart_app(None)
    return


def create_alert():
    create_alert_window = tk.Toplevel(root)
    create_alert_window.title("Create Alert")
    create_alert_window.geometry("200x300")
    create_alert_title = ttk.Label(create_alert_window, text="Create Alert", font=("Helvetica", 30))
    create_alert_title.pack(padx=5, pady=5)
    symbol_entry_label = ttk.Label(create_alert_window, text="Symbol")
    symbol_entry_label.pack(padx=5, pady=5)
    symbol_entry = ttk.Entry(create_alert_window, width=6)
    symbol_entry.pack(padx=5, pady=5)
    price_entry_label = ttk.Label(create_alert_window, text="Price")
    price_entry_label.pack(padx=5, pady=5)
    price_entry = ttk.Entry(create_alert_window, width=6)
    price_entry.pack(padx=5, pady=5)
    tresh_dropdown_label = ttk.Label(create_alert_window, text="Type")
    tresh_dropdown_label.pack(padx=5, pady=5)
    tresh_dropdown = ttk.Combobox(create_alert_window, width=25, state="readonly", values=["Rises Above", "Falls Below"])
    tresh_dropdown.pack(padx=5, pady=5)
    create_alert_wait_var = tk.IntVar()
    create_button = ttk.Button(create_alert_window, text="Create Alert", style="Accent.TButton", command=lambda: create_alert_wait_var.set(1))
    create_button.pack(padx=5, pady=5)
    create_alert_window.wait_variable(create_alert_wait_var)
    alerts_json = json.load(open("Settings/alerts.json", "r"))
    alerts = []
    for alert in alerts_json:
        alerts.append(alert)
    new_alert = {
        "symbol": symbol_entry.get(),
        "target-price": price_entry.get(),
        "tresh": tresh_dropdown.get()
    }
    alerts.append(new_alert)
    alerts_object = json.dumps(alerts, indent=4)
    alerts_file = open("Settings/alerts.json", "w+")
    alerts_file.truncate(0)
    with alerts_file as outfile:
        outfile.write(alerts_object)
        alerts_file.close()
        pass
    create_alert_window.destroy()
    root.iconify()
    showinfo(title="Create Alert", message=f"New alert created for when {new_alert["symbol"]} {new_alert["tresh"]} {new_alert["target-price"]}")
    restart_app(None)


def remove_alert():
    remove_alert_window = tk.Toplevel(root)
    remove_alert_window.title("Remove Alert")
    remove_alert_window.geometry("200x180")
    remove_alert_title = ttk.Label(remove_alert_window, text="Remove Alert", font=("Helvetica", 30))
    remove_alert_title.pack(padx=5, pady=5)
    current_alerts = []
    alerts = json.load(open("Settings/alerts.json", "r"))
    for alert in alerts:
        if alert["tresh"] == "Rises Above":
            current_alerts.append(f"{alert["symbol"]} | >${alert["target-price"]}")
        else:
            current_alerts.append(f"{alert["symbol"]} | <${alert["target-price"]}")
    alerts_selection_label = ttk.Label(remove_alert_window, text="Select One")
    alerts_selection_label.pack(padx=5, pady=5)
    alerts_dropdown = ttk.Combobox(remove_alert_window, state="readonly", values=current_alerts, width=25)
    alerts_dropdown.pack(padx=5, pady=5)
    remove_alert_wait_var = tk.IntVar()
    remove_button = ttk.Button(remove_alert_window, text="Remove Alert", command=lambda: remove_alert_wait_var.set(1), style="Accent.TButton")
    remove_button.pack(padx=5, pady=5)
    remove_alert_window.wait_variable(remove_alert_wait_var)
    selected_alert = alerts_dropdown.get()
    remove_alert_window.destroy()
    new_alerts = []
    for alert in alerts:
        if alert["tresh"] == "Rises Above":
            search_alert = f"{alert["symbol"]} | >${alert["target-price"]}"
        else:
            search_alert = f"{alert["symbol"]} | <${alert["target-price"]}"
        if search_alert != selected_alert:
            new_alerts.append(alert)
    alerts_object = json.dumps(new_alerts, indent=4)
    alerts_file = open("Settings/alerts.json", "w+")
    alerts_file.truncate(0)
    with alerts_file as outfile:
        outfile.write(alerts_object)
        alerts_file.close()
        pass
    root.iconify()
    showinfo(title="Create Alert",
             message=f"Deleted alert: {selected_alert}")
    restart_app(None)


def edit_holdings_file():
    showinfo(title="Edit Holdings", message="Holdings file will be opened in another app")
    if platform.system() == 'Darwin':
        subprocess.call(('open', "portfolio-holdings.csv"))
    elif platform.system() == 'Windows':
        os.startfile("portfolio-holdings.csv")
    else:
        subprocess.call(('xdg-open', "portfolio-holdings.csv"))
    return


def portfolio_summary():
    global table_frame, stats_frame, actions_frame, table, refresh_interval, portfolio, last_refreshed_text, loading_label, other_loading_label
    root.after_cancel(refresh_interval)
    table_frame.destroy()
    stats_frame.destroy()
    actions_frame.destroy()
    last_refreshed_text.destroy()
    root.geometry("1100x500")
    summary_window_title = ttk.Label(root, text="Portfolio Summary", font=("Helvetica", 30))
    summary_window_title.grid(row=0, column=1, padx=5, pady=5)
    holdings_summary_text = ttk.Label(root, text=f"Current Value: ${portfolio.total_value}\n"
                                                          f"Invested Capital: ${round(portfolio.total_initial_value, 2)}\n"
                                                          f"Total Change: ${portfolio.total_abs_gain} ({portfolio.total_rel_gain}%)\n"
                                                          f"Daily Change: ${portfolio.total_daily_abs_gain} ({portfolio.total_daily_rel_gain}%)", font=("Helvetica", 15))
    holdings_summary_text.grid(row=1, column=1, padx=5, pady=5)
    history_frame = ttk.Frame(root)
    history_frame.grid(row=0, column=1, padx=5, pady=5)
    # TODO add history graph
    allocation_frame = ttk.LabelFrame(root, text="Allocation")
    stock_count = 0
    etf_count = 0
    for security in portfolio.securities:
        tinfo = yf.Ticker(security.symbol).info
        if "industry" in tinfo:
            stock_count += 1
        else:
            etf_count += 1
    total_count = stock_count + etf_count
    type_allocation_text = ttk.Label(allocation_frame, text=f"Positions: {total_count}\n\n"
                                                            f"Stocks: {stock_count} ({round((stock_count / total_count) * 100, 2)}%)\n"
                                                            f"ETFs: {etf_count} ({round((etf_count / total_count) * 100, 2)}%)")
    type_allocation_text.grid(padx=5, pady=5, column=0, row=0)
    sector_allocation_button = ttk.Button(allocation_frame, text="Sectors", command=portfolio_sector_allocation)
    sector_allocation_button.grid(padx=5, pady=5, column=0, row=1)
    country_allocation_button = ttk.Button(allocation_frame, text="Countries", command=portfolio_country_allocation)
    country_allocation_button.grid(padx=5, pady=5, column=1, row=1)
    pos_allocation_text = "Symbol - Percent | Shares\n"
    for position in portfolio.securities:
        pos_allocation_text += f"{position.symbol} - {round((position.current_value / portfolio.total_value) * 100, 2)}% | {round(position.shares, 4)}\n"
    position_allocation_label = ttk.Label(allocation_frame, text=pos_allocation_text)
    position_allocation_label.grid(padx=5, pady=5, column=1, row=0)
    allocation_frame.grid(column=0, row=2, padx=5, pady=5)
    insights_frame = ttk.LabelFrame(root, text="Insights")
    presorted_list = []
    for security in portfolio.securities:
        presorted_list.append(security.absolute_gain)
    gain_sorted_list = sorted(presorted_list, reverse=True)
    loss_sorted_list = sorted(presorted_list)
    gain_sorted_stocks = []
    loss_sorted_stocks = []
    for i in range(5):
        gain_sorted_stocks.append(portfolio.securities[presorted_list.index(gain_sorted_list[i])])
        loss_sorted_stocks.append(portfolio.securities[presorted_list.index(loss_sorted_list[i])])
    top_gainers_text = "-----Top Gainers-----\n"
    top_losers_text = "-----Top Losers-----\n"
    for stock in gain_sorted_stocks:
        top_gainers_text += f"{stock.symbol} - ${round(stock.absolute_gain, 2)} | {round(stock.relative_gain, 2)}%\n"
    for stock in loss_sorted_stocks:
        top_losers_text += f"{stock.symbol} - ${round(stock.absolute_gain, 2)} | {round(stock.relative_gain, 2)}%\n"
    top_gainers_list = ttk.Label(insights_frame, text=top_gainers_text)
    absolute_sort_label = ttk.Label(insights_frame, text="By Absolute Change:")
    absolute_sort_label.grid(column=0, row=0)
    top_gainers_list.grid(padx=5, pady=5, column=1, row=0)
    top_losers_list = ttk.Label(insights_frame, text=top_losers_text)
    top_losers_list.grid(padx=5, pady=5, column=2, row=0)
    presorted_rel_list = []
    for pos in portfolio.securities:
        presorted_rel_list.append(pos.relative_gain)
    gain_sorted_rel_list = sorted(presorted_rel_list, reverse=True)
    loss_sorted_rel_list = sorted(presorted_rel_list)
    gain_sorted_rel_stocks = []
    loss_sorted_rel_stocks = []
    for i in range(5):
        gain_sorted_rel_stocks.append(portfolio.securities[presorted_rel_list.index(gain_sorted_rel_list[i])])
        loss_sorted_rel_stocks.append(portfolio.securities[presorted_rel_list.index(loss_sorted_rel_list[i])])
    top_gainers_rel_text = "-----Top Gainers-----\n"
    top_losers_rel_text = "-----Top Losers-----\n"
    for stock in gain_sorted_rel_stocks:
        top_gainers_rel_text += f"{stock.symbol} - ${round(stock.absolute_gain, 2)} | {round(stock.relative_gain, 2)}%\n"
    for stock in loss_sorted_rel_stocks:
        top_losers_rel_text += f"{stock.symbol} - ${round(stock.absolute_gain, 2)} | {round(stock.relative_gain, 2)}%\n"
    relative_sort_label = ttk.Label(insights_frame, text="By Relative Change:")
    relative_sort_label.grid(row=1, column=0)
    top_gainers_rel_list = ttk.Label(insights_frame, text=top_gainers_rel_text)
    top_gainers_rel_list.grid(padx=5, pady=5, column=1, row=1)
    top_losers_rel_list = ttk.Label(insights_frame, text=top_losers_rel_text)
    top_losers_rel_list.grid(padx=5, pady=5, column=2, row=1)
    insights_frame.grid(column=1, row=2, padx=5, pady=5)
    summary_wait_var = tk.IntVar(root, 0)
    back_button = ttk.Button(root, text="Back", command=lambda: summary_wait_var.set(1))
    back_button.grid(row=3, column=0, padx=5, pady=5)
    save_button = ttk.Button(root, text="Save to file", command=save_portfolio_summary)
    save_button.grid(row=3, column=1, padx=5, pady=5)
    root.wait_variable(summary_wait_var)
    summary_window_title.destroy()
    holdings_summary_text.destroy()
    history_frame.destroy()
    back_button.destroy()
    allocation_frame.destroy()
    insights_frame.destroy()
    save_button.destroy()
    loading_label = ttk.Label(root, text="Loading...", font=("Helvetica", 30))
    loading_label.pack(pady=150)
    other_loading_label = ttk.Label(root, text="Download might take a couple seconds...", font=("Helvetica", 15))
    other_loading_label.pack()
    root.deiconify()
    root.update()
    root.focus_set()
    update_main_window()
    return


def save_portfolio_summary():
    return  # TODO compile portfolio summary and write to selected file


def portfolio_sector_allocation():
    list_of_sectors = {}
    for stock in portfolio.securities:
        tinfo = yf.Ticker(stock.symbol).info
        try:
            sector = tinfo['sector']
            pass
        except Exception:
            sector = "ETFs"
            pass
        if sector not in list_of_sectors.keys():
            list_of_sectors[f'{sector}'] = 1
        else:
            for key, value in list_of_sectors.items():
                if key == sector:
                    list_of_sectors[f'{sector}'] = value + 1
    category_labels = list(list_of_sectors.keys())
    category_values = list(list_of_sectors.values())
    fig, ax = plt.subplots()
    plt.pie(category_values, labels=category_labels, autopct="%1.1f%%")
    plt.title("Sectors")
    plt.show()
    plt.close()
    return


def portfolio_country_allocation():
    list_of_countries = {}
    for stock in portfolio.securities:
        tinfo = yf.Ticker(stock.symbol).info
        try:
            country = tinfo['country']
            pass
        except Exception:
            continue
        if country not in list_of_countries.keys():
            list_of_countries[f'{country}'] = 1
        else:
            for key, value in list_of_countries.items():
                if key == country:
                    list_of_countries[f'{country}'] = value + 1
    cat_labels = list(list_of_countries.keys())
    cat_values = list(list_of_countries.values())
    fig, ax = plt.subplots()
    plt.pie(cat_values, labels=cat_labels, autopct="%1.1f%%")
    plt.title("Countries")
    plt.show()
    plt.close()
    return


def restart_app(event):
    print("Restarting")
    os.execv(sys.executable, [sys.executable] + sys.argv)


def quit_app(event):
    print("Quitting")
    root.destroy()
    sys.exit(0)


portfolio = Portfolio()
root = tk.Tk()
root.title("Stonks 📈")
settings_json = json.load(open("Settings/settings.json", "r"))
if settings_json["dark-mode"] == 1:
    sv_ttk.set_theme("dark")
else:
    sv_ttk.set_theme("light")
root.geometry("1675x600")
root.protocol("WM_DELETE_WINDOW", lambda: quit_app(None))
root.bind("<r>", restart_app)
root.bind("<Escape>", quit_app)
if os.path.exists("portfolio-holdings.csv"):
    loading_label = ttk.Label(root, text="Stonks 📈", font=("Helvetica", 30))
    loading_label.pack(pady=150)
    other_loading_label = ttk.Label(root, text="By Sreekar Palla", font=("Helvetica", 15))
    other_loading_label.pack()
    yet_another_loading_label = ttk.Label(root, text="Loading might take a couple seconds...", font=("Helvetica", 15))
    yet_another_loading_label.pack(pady=115)
    root.after(100, load_app)
else:
    error_label = ttk.Label(root, text=f"Error: Portfolio data not found\nPlace portfolio-holdings.csv in {os.getcwd()}",
                           font=("Helvetica", 30))
    error_label.pack(pady=150)
    restart_button = ttk.Button(root, text="Restart", command=lambda: restart_app(None))
    restart_button.pack(padx=20, pady=20)
    quit_button = ttk.Button(root, text="Quit", command=lambda: quit_app(None))
    quit_button.pack(padx=20, pady=20)
table_frame = ttk.LabelFrame(root, text="Holdings")
stats_frame = ttk.Frame(root)
launch_time = time.strftime('%l:%M:%S')
last_refreshed_text = ttk.Label(root, text=f"↻ {launch_time}", font=("Helvetica", 15))
actions_frame = ttk.Frame(root)
table = ttk.Treeview(table_frame, columns=(
    "Symbol", "Name", "Price", "Shares", "Value", "Principal", "Cost/Share", "Total $", "Total %",
    "Day $", "Day %"), height=len(portfolio.securities))
refresh_interval = "None"
root.mainloop()
