import csv
import datetime
import os
import socket
import subprocess
import json
import sys
import pandas as pd
import pyautogui
import time
import random
import logging
import threading
import tkinter as tk
import pygetwindow as gw
from tkinter import Tk, ttk
from pynput import mouse
import schedule
import pystray
from PIL import Image, ImageTk
from tkinter import messagebox
import keyboard
import psutil
from pywinauto import Application
from pynput.mouse import Listener as MouseListener
from tkinter import Toplevel, Label, Entry, Button
#cd /d "E:\programing codes\ipos_bot"
#pyinstaller --onefile --noconsole ipos_bot.py

# Constants
ITEM_DATA_FILE = 'bot_data.xlsx'
SALES_LIMITS = {'weekday': (50000, 60000), 'weekend': (60000, 75000)}
BUSINESS_HOURS = (datetime.time(2, 0), datetime.time(23, 50))
TRANSACTION_TIMES = {'morning': (1200, 1500), 'afternoon': (900, 1380), 'evening': (600, 1200)}
MAX_BILL_TOTAL = (200, 2000)
LOG_FILE = 'log.txt'
SALES_REPORT_FILE = 'sales_report.csv'
POS_WINDOW_NAME = "IPOS.NET http://www.ipos.net.pk"
LOGIN_WINDOW_NAME = "iPOS VER: 22.112 G Pro"
SOFTWARE_WINDOW = "iPOS.NET Ver. 22.112 G Pro. Store #1001"
ERROR_WINDOW = "Microsoft .Net Framework"
DB_ERROR_WINDOW = "SQL Connection"
tray_icon = None
CONFIG_FILE = "config.json"

# Global variables
sales_records = []
total_transactions = 0
sale_stop_clicked = False
error_stop_clicked = False
login_stop_clicked = False
# Function to schedule shift closing at midnight
def load_item_codes(file_path):
    try:
        # Optimized loading with fewer columns (if known) and data types specified
        df = pd.read_excel(file_path)  # Assuming all columns are strings, adjust as needed
        log_message(f"Item codes loaded successfully from {file_path}.")
        return df.to_dict(orient='records')
    except FileNotFoundError:
        error_message = f"File not found: {file_path}"
        log_message(error_message)
    except pd.errors.EmptyDataError:
        error_message = f"No data found in the file: {file_path}"
        log_message(error_message)
    except Exception as e:
        error_message = f"Error loading item codes: {e}"
        log_message(error_message)
    
    return []

def disable_keyboard():
    for key in keyboard.all_modifiers:
        keyboard.block_key(key)
    for i in range(150):  # Typically there are around 150 key codes
        keyboard.block_key(i)
    log_message("Keyboard Disabled Keyboard input has been disabled.")
def enable_keyboard():
    for key in keyboard.all_modifiers:
        keyboard.unblock_key(key)
    for i in range(150):
        keyboard.unblock_key(i)
    log_message("Keyboard Enabled Keyboard input has been enabled.")

def log_message(message, level="INFO", gui_enabled=True):
    """
    Logs a message to the log file and optionally to the GUI.

    Args:
        message (str): The message to log.
        level (str): Log level (e.g., "INFO", "ERROR", "DEBUG"). Defaults to "INFO".
        gui_enabled (bool): Whether to display the log in the GUI. Defaults to True.
    """
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    formatted_message = f"[{timestamp}] {message}"

    # Log to the file
    if level == "INFO":
        logging.info(formatted_message)
    elif level == "ERROR":
        logging.error(formatted_message)
    elif level == "DEBUG":
        logging.debug(formatted_message)
    else:
        logging.warning(f"Unknown log level: {level}. Message: {formatted_message}")

    # Log to the GUI if enabled
    if gui_enabled and 'log_text' in globals():
        try:
            log_text.config(state=tk.NORMAL)
            log_text.insert(tk.END, f"{formatted_message}\n")
            log_text.see(tk.END)
            log_text.config(state=tk.DISABLED)
        except Exception as e:
            logging.error(f"Error updating log_text widget: {e}")

def log_messageold(message):
    # Update the log file using the logging library
    logging.info(message)
    
    # Update the GUI text widget (ensure it's thread-safe)
    try:
        log_text.config(state=tk.NORMAL)
        log_text.insert(tk.END, f"[{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {message}\n")
        log_text.see(tk.END)
        log_text.config(state=tk.DISABLED)
    except Exception as e:
        logging.error(f"Error updating log_text widget: {e}")

# Function to select items for sale
def select_items_for_sale(item_data):
    log_message("select_items_for_sale() function called.")

    selected_items = []
    num_selected_items = random.randint(1, 4)
    num_items_selected = 0
      # Shuffle the item_data list
    random.shuffle(item_data)
    for item in item_data:
        company = item['catcode']
        sale_type = item['sale_type']

        # Adjust the selection probability based on the company
        if company == 90:  # 90 for walls company
            selection_probability = 1
        """ elif company == 92:  # 92 for nestle
            if sale_type == 1:
                selection_probability = 0.2  # Adjusted probability for Nestle 3rd Schedule Goods
            elif sale_type == 2:
                selection_probability = 0.03  # Adjusted probability for Nestle general sale goods
            elif sale_type == 3:
                selection_probability = 0.2  # Adjusted probability for Nestle zero rated goods
            
        elif company == 91:  # 91 for unilever
            if sale_type == 1:
                selection_probability = 0.05  # Adjusted probability for unilever 3rd Schedule Goods
            elif sale_type == 2:
                selection_probability = 0.03  # Adjusted probability for unilever general sale goods """
            

        # Generate a random number to determine if the item is selected
        if random.random() < selection_probability:

            selected_items.append(item)  # Append the complete item dictionary
            num_items_selected += 1
            if num_items_selected == num_selected_items:
                break  # Exit loop if maximum number of items reached

    return selected_items
# Function to restart POS software
def restart_pos():
    log_message("restart_pos() function called.")
    threading.Thread(target=login_to_pos).start()  # Restart sale simulation
    #'iPOS.NET Ver. 22.112 G Pro. Store #1001 - AL SIDDIQUE BAKERS (OCX) -- Server -- server-bakers- LS - POS02-PC -- 192.168.1.19 -TS- POS02-PC Date.  29 Jul 2024  '
#   return f"iPOS.NET Ver. 22.112 G Pro. Store #1001 - AL SIDDIQUE BAKERS (OCX) -- Server -- server-bakers- LS - POS02-PC -- 192.168.1.12 -TS- POS02-PC Date.  {current_date}  "
def generate_window_title():
    try:
        ip_address = get_ipv4_address()
    except Exception as e:
        log_message(f"Error retrieving IP address: {e}")
        ip_address = "Unknown IP"
    
    current_date = datetime.datetime.now().strftime("%d %b %Y")
    title = (
        f"iPOS.NET Ver. 22.112 G Pro. Store #1001 - AL SIDDIQUE BAKERS (OCX) "
        f"-- Server -- server-bakers- LS - POS02-PC -- {ip_address} -TS- POS02-PC "
        f"Date.  {current_date}  "
    )
    
    return title
def get_ipv4_address():
    try:
        # Get the hostname of the local machine
        hostname = socket.gethostname()
        # Get the IPv4 address corresponding to the hostname
        ip_address = socket.gethostbyname(hostname)
        
        # If the hostname resolves to localhost, attempt to get the actual IP
        if ip_address == "127.0.0.1":
            ip_address = socket.gethostbyname(socket.getfqdn())
        
        return ip_address
    except Exception as e:
        log_message(f"Error retrieving IP address: {e}")
        return None
def cancel_bill():
    log_message("cancel_bill() function called.")
    # Simulate pressing Ctrl+Z to initiate bill cancellation
    pyautogui.hotkey('ctrl', 'z')
    # Simulate typing the password (replace 'password' with your actual password)
    pyautogui.typewrite('5s')
    # Simulate pressing Enter to confirm the password
    pyautogui.press('enter')
# Function to handle POS errors
def handle_pos_errors():
    log_message("handle_pos_errors() function called.")
    global error_stop_clicked
    while not error_stop_clicked:
        # Get the active window
        active_window = gw.getActiveWindow()
        windows = gw.getAllTitles()

        window_title = active_window.title
       # print(f"list of window: {windows}")

        if active_window is not None:
            if windows.__contains__(POS_WINDOW_NAME):
                window_title = active_window.title
                # Check if SQL Connection error window is present
                if window_title == DB_ERROR_WINDOW:
                    log_message("SQL Connection error detected. Restarting POS software.")
                    sql_connection_error(DB_ERROR_WINDOW)
                elif window_title == ERROR_WINDOW:
                    log_message("software error detected. Restarting POS software.")
                    handle_db_error()

                elif window_title == "BACKOFFICE.NET":
                    log_message("BACKOFFICE.NET error detected.")
                    manage_quantity_error()
                    time.sleep(10)
                elif window_title == "Duplicate Bill":
                    log_message("BACKOFFICE.NET error detected.")
                    pyautogui.hotkey('alt', 'f4')
                    time.sleep(10)        
                elif not window_title == POS_WINDOW_NAME:    
                                    # Check if POS screen or item code input field has focus
                    log_message("POS window or item code input field not in focus. Bringing to front.")
                    target_window = gw.getWindowsWithTitle(POS_WINDOW_NAME)
                    if target_window:
                        focus_to_window(POS_WINDOW_NAME)    
 
            elif windows.__contains__(generate_window_title()):
                if window_title == DB_ERROR_WINDOW:
                    log_message("SQL Connection error detected. Restarting POS software.")
                    stop_sale_bot()
                    sql_connection_error(DB_ERROR_WINDOW)
                    Cashier_Login()
                    threading.Thread(target=start_sale_bot).start()
                elif window_title == ERROR_WINDOW:
                    log_message("software error detected. Restarting POS software.")
                    handle_db_error()
                
                elif not window_title == generate_window_title():    
                                    # Check if POS screen or item code input field has focus
                    log_message("SOFTWARE_WINDOW not in focus. Bringing to front.")
                    target_window = gw.getWindowsWithTitle(generate_window_title())
                    if target_window:
                        focus_to_window(generate_window_title())    
            elif windows.__contains__(LOGIN_WINDOW_NAME):
                if window_title == DB_ERROR_WINDOW:
                    log_message("SQL Connection error detected. Restarting POS software.")
                    sql_connection_error(DB_ERROR_WINDOW)
                    Main_Login()
                    Cashier_Login()
                    threading.Thread(target=start_sale_bot).start()

                elif window_title == ERROR_WINDOW:
                    log_message("software error detected. Restarting POS software.")
                    handle_db_error()
                
                elif not window_title == LOGIN_WINDOW_NAME:    
                                    # Check if POS screen or item code input field has focus
                    log_message("SOFTWARE_WINDOW not in focus. Bringing to front.")
                    target_window = gw.getWindowsWithTitle(LOGIN_WINDOW_NAME)
                    if target_window:
                        focus_to_window(LOGIN_WINDOW_NAME)
            else:
                 stop_sale_bot()
                 if window_title == DB_ERROR_WINDOW:
                     log_message("SQL Connection error detected. Restarting POS software.")
                     stop_sale_bot()
                     sql_connection_error(DB_ERROR_WINDOW)
                     Main_Login()
                     Cashier_Login()
                     threading.Thread(target=start_sale_bot).start()

                 else:
                      restart_pos()               
        time.sleep(15) 

def sql_connection_error(window_title):
    """
    Function to click a checkbox and then click the Connect button in the SQL connection window.
    
    :param window_title: The title (or partial title) of the SQL connection window.
    """
    # Relative coordinates of the checkbox and "Connect" button within the window
    checkbox_relative_coords = (387, 249)   # (Relative X, Relative Y) for the checkbox
    connect_button_relative_coords = (256, 309)  # (Relative X, Relative Y) for the Connect button

    # Get the SQL connection window by title
    try:
        windows = gw.getWindowsWithTitle(window_title)
        if not windows:
            raise Exception("SQL connection window not found.")
        window = windows[0]  # Use the first window matching the title
    except Exception as e:
        print(f"Error: {e}")
        return

    # Bring the window to the foreground and give time to activate
    window.activate()
    time.sleep(1)

    # Get the top-left corner of the window
    window_x, window_y = window.topleft

    # Calculate the absolute position of the checkbox and the Connect button based on the window's position
    checkbox_x = window_x + checkbox_relative_coords[0]
    checkbox_y = window_y + checkbox_relative_coords[1]
    connect_button_x = window_x + connect_button_relative_coords[0]
    connect_button_y = window_y + connect_button_relative_coords[1]

    # Step 1: Click on the checkbox with slow movement
    print(f"Clicking on checkbox at absolute position: ({checkbox_x}, {checkbox_y})")
    pyautogui.moveTo(checkbox_x, checkbox_y, duration=2.0)  # Slow movement with duration of 2 seconds
    pyautogui.click()
    print("Checkbox clicked.")

    # Small delay before moving to the Connect button
    time.sleep(1)

    # Step 2: Click on the Connect button with slow movement
    print(f"Clicking on Connect button at absolute position: ({connect_button_x}, {connect_button_y})")
    pyautogui.moveTo(connect_button_x, connect_button_y, duration=2.0)  # Slow movement with duration of 2 seconds
    pyautogui.click()
    print("Connect button clicked.")

def handle_db_error():
    stop_sale_bot()
    log_message("handle_db_error() function called.")
    #pyautogui.moveTo(x=787, y=495, duration=0.25)
    #pyautogui.click()
    result = terminate_process(process_name="BACKOFFICE.NET.exe")
    if result:
        log_message("Process terminated successfully.")
    else:
        log_message("No matching process found or termination failed.")  
    
    log_message("Attempting to restart POS software...")
    restart_pos()

def terminate_process(process_name=None, window_title=None):
    """
    Terminate a process either by its name or by the title of its window.

    Args:
        process_name (str, optional): Name of the process to terminate.
        window_title (str, optional): Title of the window associated with the process to terminate.

    Returns:
        bool: True if at least one process was terminated, False otherwise.
    """
    terminated = False

    # Stop by process name
    if process_name:
        try:
            for proc in psutil.process_iter(['pid', 'name']):
                if proc.info['name'].lower() == process_name.lower():
                    log_message(f"Found process to terminate: {proc.info['name']} (PID: {proc.info['pid']})")
                    proc.terminate()
                    proc.wait(timeout=10)
                    log_message(f"Successfully terminated process: {proc.info['name']} (PID: {proc.info['pid']})")
                    terminated = True
        except psutil.NoSuchProcess:
            log_message(f"Process {process_name} does not exist.", level="WARNING")
        except psutil.AccessDenied:
            log_message(f"Access denied while trying to terminate process: {process_name}.", level="ERROR")
        except Exception as e:
            log_message(f"Unexpected error while stopping process {process_name}: {e}", level="ERROR")

    # Stop by window title
    if window_title:
        try:
            windows = gw.getWindowsWithTitle(window_title)
            if not windows:
                log_message(f"No windows found with title '{window_title}'")
                return terminated
            
            for window in windows:
                hwnd = window._hWnd
                app = Application().connect(handle=hwnd)
                pid = app.process
                proc = psutil.Process(pid)
                proc.terminate()
                proc.wait()
                log_message(f"Terminated process: {proc.name()} (PID: {pid}) for window '{window_title}'")
                terminated = True
        except Exception as e:
            log_message(f"Failed to terminate process for window '{window_title}': {e}", level="ERROR")

    if not terminated:
        log_message(f"No processes were terminated for process_name='{process_name}' or window_title='{window_title}'")
    return terminated
    
def close_windows_by_title(target_title):
    # Retrieve all window titles
    window_titles = gw.getAllTitles()
    target_windows = [win for win in gw.getWindowsWithTitle(target_title) if win.title == target_title]
    if not target_windows:
        log_message(f"No windows found with title '{target_title}'")
        return
    process_found = False
    for window in target_windows:
        hwnd = window._hWnd
        try:
            # Use pywinauto to connect to the window and get the process ID
            app = Application().connect(handle=hwnd)
            pid = app.process
            # Find and terminate the process using psutil
            proc = psutil.Process(pid)
            proc.terminate()
            proc.wait()  # Ensure the process has terminated
            log_message(f"Terminated process: {proc.name()} (PID: {pid})")
        except Exception as e:
            log_message(f"Failed to terminate process for window '{target_title}': {e}")

def focus_to_window(window_title):
    """
    Bring a window with the specified title to the foreground.

    Args:
        window_title (str): The title of the window to focus.

    Returns:
        bool: True if the window was successfully focused, False otherwise.
    """
    try:
        target_windows = gw.getWindowsWithTitle(window_title)
        
        if not target_windows:
            log_message(f"No windows found with title: {window_title}")
            return False

        # Activate the first matching window
        target_windows[0].activate()
        log_message(f"Switched to window: {window_title}")
        return True

    except Exception as e:
        log_message(f"Error focusing on window '{window_title}': {e}", level="ERROR")
        return False
def manage_quantity_error():
    log_message("manage_quantity_error() function called.")
  
    pyautogui.press('enter')
    pyautogui.press('enter')
    for _ in range(7):
        pyautogui.press('backspace')
    pyautogui.press('enter')
    pyautogui.press('enter')
    cancel_bill() # Check every 5 seconds
def shift_closing():
    stop_sale_bot()
    # Activate the POS window
    focus_to_window(POS_WINDOW_NAME)
    # Simulate pressing Ctrl+Alt+S to initiate shift closing
    pyautogui.hotkey('ctrl', 'alt', 's')
    # Simulate pressing Enter 14 times
    for _ in range(14):
        time.sleep(1)  # Wait for 2 seconds for the POS software to load
        pyautogui.press('enter')
    # Move the mouse cursor to the bottom center of the screen
    pyautogui.moveTo(x=906, y=324, duration=0.25)
    # Simulate a mouse click to confirm shift closing
    pyautogui.click()
   # Simulate pressing Enter 3 times
    time.sleep(5)  # Wait for 2 seconds for the POS software to load
    for _ in range(3):
        time.sleep(3)  # Wait for 2 seconds for the POS software to load
        pyautogui.press('enter')
    pyautogui.moveTo(x=49, y=35, duration=0.25)
    pyautogui.click()
    for _ in range(3):
        time.sleep(3)  # Wait for 2 seconds for the POS software to load
        pyautogui.press('enter')    # Simulate pressing Alt+F4 2 times to close the Shift Closing window
    for _ in range(3):
        time.sleep(3)  # Wait for 2 seconds for the POS software to load
        pyautogui.hotkey('alt', 'f4')
    # Wait for the software to close
    time.sleep(10)
    # Restart POS
    threading.Thread(target=login_to_pos).start()  # Restart sale simulation

def schedule_shift_closing():
    schedule.every().day.at("00:00").do(shift_closing)
    log_message("Scheduled shift closing at 00:00")

# Start the scheduling thread
def run_scheduler():
    while True:
        schedule.run_pending()
        time.sleep(1)
# Function to simulate sale transaction
def simulate_sale():
    pyautogui.FAILSAFE = False
    time.sleep(15)  # Wait for 2 seconds for the POS software to load
    focus_to_window(POS_WINDOW_NAME)
    pyautogui.moveTo(x=222, y=99, duration=0.25)
    pyautogui.click()
    global total_transactions,sale_stop_clicked
    log_message("Bot started.")
    total_sales_today = 0
    total_sales_limit = get_total_sales_limit()
    log_message(f"Total sales limit for the day AT START: {total_sales_limit}")
    item_data = load_item_codes(ITEM_DATA_FILE)
    if not item_data:
        log_message("No item codes loaded. Exiting.")
        return

    while not sale_stop_clicked:
        if total_sales_today >= total_sales_limit:
            log_message("Total sales limit for the day reached. Waiting for tomorrow.")
            total_sales_today = 0
            total_sales_limit = get_total_sales_limit()
            remaining_time = get_remaining_time_until_business_hours()
            log_message(f"Bussiness is closed now. Bot will resume at 2.00 AM till 23.50 PM. Wait: {remaining_time}")
            time.sleep(remaining_time)
            continue
        selected_items = select_items_for_sale(item_data)
        total_price = 0
        for item in selected_items:
            item_code, item_name, item_price = item['ItemCode'], item['Description'], item['Slprice']
            if item['Slprice'] >1000:
                quantity=1
            else:    
                quantity = random.randint(1, 3)
            item_total_price = quantity * item_price
            log_message(f"Selected Item code: {item_code} Item name: {item_name} Price: {item_price} Quantity: {quantity} item_total_price={item_total_price}")
            if not MAX_BILL_TOTAL[0] <= total_price + item_total_price <= MAX_BILL_TOTAL[1]:
                log_message("Maximum bill total reached. Completing transaction.")
                continue
            sales_records.append({'ItemCode': item_code, 'ItemName': item_name, 'Quantity': quantity, 'TotalPrice': item_total_price})
            for _ in range(quantity):
                pyautogui.typewrite(str(item_code))
                pyautogui.press('enter')
                time.sleep(12)  
            total_price += item_total_price
            log_message(f"bill total so far ={total_price}")
        pyautogui.press('enter')        
        pyautogui.press('f1')
        total_transactions += 1
        total_sales_today += total_price
        log_message(f"Total sales for the day so far: {total_sales_today} target sale: {total_sales_limit}  target remaining: {total_sales_limit-total_sales_today}")

        if is_business_hours():
            transaction_frequency = get_transaction_frequency()
            log_message(f"Waiting for {transaction_frequency} seconds before next transaction.")
            time.sleep(transaction_frequency)
        else:
            total_sales_today = 0
            total_sales_limit = get_total_sales_limit()
            remaining_time = get_remaining_time_until_business_hours()
            hours = remaining_time // 3600
            minutes = (remaining_time % 3600) // 60
            seconds = remaining_time % 60
            log_message(f"Bussiness is closed now. Bot will resume at 6.00 AM till 23.50 PM. Wait: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
            #log_message(f"Bussiness is closed now. Bot will resume at 6.00 AM till 23.50 PM. Wait: {remaining_time}")
            time.sleep(remaining_time)
            log_message(f"Total sales limit for the day: {total_sales_limit}")
# Function to get total sales limit based on the day of the week
def get_total_sales_limit():
    today = datetime.datetime.today()
    weekday = today.weekday()
    limit_range = SALES_LIMITS['weekday'] if weekday < 4 else SALES_LIMITS['weekend']
    total_sales_limit = random.randint(*limit_range)
    log_message(f"Selected sale limit for the day: {total_sales_limit}")
    return total_sales_limit

# Function to check if current time is within business hours
def is_business_hours():
    now = datetime.datetime.now().time()
    return BUSINESS_HOURS[0] <= now <= BUSINESS_HOURS[1]
def get_remaining_time_until_business_hours():
    now = datetime.datetime.now()
    opening_time, closing_time = BUSINESS_HOURS
    # If current time is before opening time, calculate remaining time until opening
    if now.time() < opening_time:
        target_time = datetime.datetime.combine(now.date(), opening_time)
    # If current time is after opening time but before closing time, calculate remaining time until closing
    elif now.time() < closing_time:
        target_time = datetime.datetime.combine(now.date(), closing_time)
    # If current time is after closing time, calculate remaining time until next day's opening
    else:
        next_day = now + datetime.timedelta(days=1)
        target_time = datetime.datetime.combine(next_day.date(), opening_time)
    remaining_time = (target_time - now).total_seconds()
    log_message(f"Remaining time until business hours: in hours:{remaining_time/3600}  in minutes: {remaining_time/60} in seconds: {remaining_time} ")
    return remaining_time
# Function to get transaction frequency based on the current time of day
def get_transaction_frequency():
    now = datetime.datetime.now().hour
    if now < 12:
        return random.randint(*TRANSACTION_TIMES['morning'])
    elif now < 17:
        return random.randint(*TRANSACTION_TIMES['afternoon'])
    else:
        return random.randint(*TRANSACTION_TIMES['evening'])

def run_pos():
    log_message("Starting run_pos function.")
    pos_path = r"C:\Program Files\iPOS.NET\BACKOFFICE.NET.exe"
    subprocess.Popen([pos_path], creationflags=subprocess.DETACHED_PROCESS)
    time.sleep(60)  
    log_message("Starting pos software.")
# Function to login to POS and cashier screens
# Function to login to POS

def login_to_pos():
    log_message("Starting login_to_pos function.")
    pyautogui.FAILSAFE = False
    stop_sale_bot()
    run_pos()
    time.sleep(60)  
    Main_Login()
    time.sleep(30)  # Adjust as needed
    Cashier_Login()
    time.sleep(30)
    pyautogui.hotkey('ctrl', 'alt', 'c')
    threading.Thread(target=start_sale_bot).start()
def Cashier_Login():
    focus_to_window(generate_window_title())
    pyautogui.press('enter')
    log_message("Starting cashier login details.")
    pyautogui.typewrite("POS2")
    pyautogui.press('enter')
    pyautogui.typewrite("POS2")
    pyautogui.press('enter')
    pyautogui.press('enter')
    pyautogui.press('enter')
    
def Main_Login():
    focus_to_window(LOGIN_WINDOW_NAME)
    pyautogui.FAILSAFE = False
    log_message("Starting pos software.")    # Wait for the POS application to start (adjust the delay as needed)
    #time.sleep(60)  
    log_message("Starting login details.")
    pyautogui.typewrite("DEO")
    pyautogui.press('enter')
    pyautogui.typewrite("DEO098")
    pyautogui.press('enter')
    pyautogui.press('enter')
# Function to handle start button click
def generate_report():
    log_message("Starting generate reports")

    item_report = {}
    total_sale = 0
    for record in sales_records:
        item_code, item_name, quantity, total_price = record['ItemCode'], record['ItemName'], record['Quantity'], record['TotalPrice']
        if item_code in item_report:
            item_report[item_code]['Quantity'] += quantity
            item_report[item_code]['Total'] += total_price
        else:
            item_report[item_code] = {'ItemName': item_name, 'Quantity': quantity, 'Total': total_price}
        total_sale += total_price

    with open(SALES_REPORT_FILE, 'w', newline='') as file:
        fieldnames = ['ItemCode', 'ItemName', 'Quantity', 'Total', 'Total Sale Value', 'Total Transactions']
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for item_code, data in item_report.items():
            writer.writerow({'ItemCode': item_code, 'ItemName': data['ItemName'], 'Quantity': data['Quantity'], 'Total': data['Total']})
        writer.writerow({'Total Sale Value': total_sale, 'Total Transactions': total_transactions})

    # Display sales report in GUI
    root = tk.Tk()
    root.title("Sales Report")
    tree = ttk.Treeview(root, columns=('Item Code', 'Item Name', 'Quantity Sold', 'Total'))
    tree.heading('#0', text='Item Code')
    tree.heading('#1', text='Item Name')
    tree.heading('#2', text='Quantity Sold')
    tree.heading('#3', text='Total')

    for item_code, data in item_report.items():
        tree.insert('', 'end', text=item_code, values=(data['ItemName'], data['Quantity'], data['Total']))

    tree.pack(expand=True, fill='both')

    total_label = tk.Label(root, text=f'Total Sale Value: {total_sale}')
    total_label.pack()

    transactions_label = tk.Label(root, text=f'Total Transactions: {total_transactions}')
    transactions_label.pack()
    root.mainloop()

def start_login_bot():
    global sale_stop_clicked,login_stop_clicked,error_stop_clicked
    sale_stop_clicked = False
    login_stop_clicked= False
    error_stop_clicked=False
    disable_keyboard()
    #threading.Thread(target=login_to_pos).start()
    threading.Thread(target=handle_pos_errors).start()
# Function to handle start button click
def start_sale_bot():
    global sale_stop_clicked,login_stop_clicked,error_stop_clicked
    sale_stop_clicked = False
    login_stop_clicked= False
    error_stop_clicked=False
    threading.Thread(target=handle_pos_errors).start()
    threading.Thread(target=simulate_sale).start()

def run_pos_thread():
    threading.Thread(target=run_pos).start()                                                                                                 
def stop_sale_bot():
    global sale_stop_clicked,login_stop_clicked,error_stop_clicked
    sale_stop_clicked = True
    login_stop_clicked= True
    error_stop_clicked= True
    log_message(f"Stoping sale bot")
def stop_error_bot():
    global sale_stop_clicked,login_stop_clicked,error_stop_clicked
    sale_stop_clicked = True
    login_stop_clicked= True
    error_stop_clicked= True
    log_message(f"Stoping stop_error_bot")    
    # Function to handle stop button click
def stop_login_bot():
    global sale_stop_clicked,login_stop_clicked,error_stop_clicked
    sale_stop_clicked = True
    login_stop_clicked= True
    error_stop_clicked= True
    log_message(f"Stoping stop_login_bot ")

# Function to handle the global hotkey event and show the window
def show_window_hotkey():
    root.after(0, root.deiconify)

# Register the hotkey to show the window when it's hidden

def hide_window():
    root.withdraw()  # Hide the window

def show_window():
    root.deiconify()  # Show the window

def toggle_window_visibility():
    global window_hidden
    if window_hidden:
        show_window()
        window_hidden = False
    else:
        hide_window()
        window_hidden = True
# Set initial window state
window_hidden = False
keyboard.add_hotkey('ctrl+0', toggle_window_visibility)
# Variables to track left and right mouse button states
left_pressed = False
right_pressed = False
last_right_click_time = 0

# Mouse listener to detect both buttons pressed
def on_click(x, y, button, pressed):
    global left_pressed, right_pressed, last_right_click_time

    # Check if left or right buttons are pressed/released
    if button == button.left:
        left_pressed = pressed
    if button == button.right:
        right_pressed = pressed
    
    # Toggle window visibility when both left and right buttons are pressed
    if left_pressed and right_pressed:
        toggle_window_visibility()
    
    # Detect right double-click
    if button == button.right and pressed:
        current_time = time.time()
        if current_time - last_right_click_time < 0.3:  # 0.3 seconds threshold for double-click
            print("Right button double-clicked. Exiting the program.")
            mouse_listener.stop()  # Stop the listener
            stop_sale_bot()
            os._exit(0)  # Exit the program on right double-click
        last_right_click_time = current_time# Start mouse listener to detect both button clicks
mouse_listener = MouseListener(on_click=on_click)
mouse_listener.start()
# Function to hide the window and show a system tray icon
def hide_window1():
    root.withdraw()
    icon_image = Image.open("icon.ico")  # Use your own icon image here
    icon = pystray.Icon("POS Bot", icon_image, "POS Bot", menu)
    icon.run()

# Function to show the window and stop the system tray icon
def show_window1(icon, item):
    icon.stop()
    root.after(0, root.deiconify)

# Function to quit the application
def quit_app(icon, item):
    icon.stop()
    root.after(0, root.destroy)

# Menu for the system tray icon
menu = (pystray.MenuItem('Show', toggle_window_visibility), pystray.MenuItem('Quit', quit_app))


def load_config():
    """
    Load configuration from a JSON file and assign values to global variables.
    """
    global SALES_LIMITS, BUSINESS_HOURS, TRANSACTION_TIMES, MAX_BILL_TOTAL, LOG_FILE, SALES_REPORT_FILE

    if not os.path.exists(CONFIG_FILE):
        log_message(f"{CONFIG_FILE} not found. Using default settings.")
        #return

    try:
        with open(CONFIG_FILE, 'r') as file:
            config = json.load(file)

            SALES_LIMITS = config.get('SALES_LIMITS', SALES_LIMITS)
            BUSINESS_HOURS = tuple(datetime.time.fromisoformat(t) for t in config.get('BUSINESS_HOURS', BUSINESS_HOURS))
            TRANSACTION_TIMES = config.get('TRANSACTION_TIMES', TRANSACTION_TIMES)
            MAX_BILL_TOTAL = config.get('MAX_BILL_TOTAL', MAX_BILL_TOTAL)
            LOG_FILE = config.get('LOG_FILE', LOG_FILE)
            SALES_REPORT_FILE = config.get('SALES_REPORT_FILE', SALES_REPORT_FILE)

        log_message(f"Configuration loaded successfully from {CONFIG_FILE}.")
    except Exception as e:
        log_message(f"Error loading configuration: {e}. Using default settings.")

def save_config():
    """
    Save current global variable values to the JSON config file.
    """
    config = {
        "SALES_LIMITS": SALES_LIMITS,
        "BUSINESS_HOURS": [t.strftime("%H:%M:%S") for t in BUSINESS_HOURS],
        "TRANSACTION_TIMES": TRANSACTION_TIMES,
        "MAX_BILL_TOTAL": MAX_BILL_TOTAL,
        "LOG_FILE": LOG_FILE,
        "SALES_REPORT_FILE": SALES_REPORT_FILE
    }

    try:
        with open(CONFIG_FILE, 'w') as file:
            json.dump(config, file, indent=4)
        print(f"Configuration saved to {CONFIG_FILE}.")
    except Exception as e:
        print(f"Error saving configuration: {e}")
#Function to open the settings window
def open_settings_window():
    """
    Open a settings window for editing global variables.
    """
    settings_window = Toplevel(root)
    settings_window.title("Settings")
    settings_window.geometry("600x700")
    settings_window.resizable(False, False)

    def save_settings():
        """
        Save the user-modified values back to the global variables and config file.
        """
        global SALES_LIMITS, BUSINESS_HOURS, TRANSACTION_TIMES, MAX_BILL_TOTAL

        try:
            SALES_LIMITS['weekday'] = [int(weekday_lower_limit.get()), int(weekday_upper_limit.get())]
            SALES_LIMITS['weekend'] = [int(weekend_lower_limit.get()), int(weekend_upper_limit.get())]
            BUSINESS_HOURS = (
                datetime.time.fromisoformat(business_start.get()),
                datetime.time.fromisoformat(business_end.get())
            )
            TRANSACTION_TIMES['morning'] = [int(morning_start.get()), int(morning_end.get())]
            TRANSACTION_TIMES['afternoon'] = [int(afternoon_start.get()), int(afternoon_end.get())]
            TRANSACTION_TIMES['evening'] = [int(evening_start.get()), int(evening_end.get())]
            MAX_BILL_TOTAL = [int(max_bill_min.get()), int(max_bill_max.get())]

            save_config()  # Save to config file
            load_config()
            settings_window.destroy()
        except ValueError:
            messagebox.showerror("Invalid Input", "Please enter valid numeric values.")

    # Create a styled frame for better UI
    frame = ttk.Frame(settings_window, padding=20)
    frame.pack(fill="both", expand=True)

    # Sales Limits
    Label(frame, text="Sales Limits", font=("Arial", 14, "bold")).grid(row=0, column=0, columnspan=2, pady=10)
    Label(frame, text="Weekday Lower:").grid(row=1, column=0, sticky="w")
    weekday_lower_limit = Entry(frame)
    weekday_lower_limit.insert(0, SALES_LIMITS['weekday'][0])
    weekday_lower_limit.grid(row=1, column=1, pady=5)

    Label(frame, text="Weekday Upper:").grid(row=2, column=0, sticky="w")
    weekday_upper_limit = Entry(frame)
    weekday_upper_limit.insert(0, SALES_LIMITS['weekday'][1])
    weekday_upper_limit.grid(row=2, column=1, pady=5)

    Label(frame, text="Weekend Lower:").grid(row=3, column=0, sticky="w")
    weekend_lower_limit = Entry(frame)
    weekend_lower_limit.insert(0, SALES_LIMITS['weekend'][0])
    weekend_lower_limit.grid(row=3, column=1, pady=5)

    Label(frame, text="Weekend Upper:").grid(row=4, column=0, sticky="w")
    weekend_upper_limit = Entry(frame)
    weekend_upper_limit.insert(0, SALES_LIMITS['weekend'][1])
    weekend_upper_limit.grid(row=4, column=1, pady=5)

    # Business Hours
    Label(frame, text="Business Hours", font=("Arial", 14, "bold")).grid(row=5, column=0, columnspan=2, pady=10)
    Label(frame, text="Start Time (HH:MM:SS):").grid(row=6, column=0, sticky="w")
    business_start = Entry(frame)
    business_start.insert(0, BUSINESS_HOURS[0].strftime("%H:%M:%S"))
    business_start.grid(row=6, column=1, pady=5)

    Label(frame, text="End Time (HH:MM:SS):").grid(row=7, column=0, sticky="w")
    business_end = Entry(frame)
    business_end.insert(0, BUSINESS_HOURS[1].strftime("%H:%M:%S"))
    business_end.grid(row=7, column=1, pady=5)

    # Transaction Times
    Label(frame, text="Transaction Times", font=("Arial", 14, "bold")).grid(row=8, column=0, columnspan=2, pady=10)
    Label(frame, text="Morning Start:").grid(row=9, column=0, sticky="w")
    morning_start = Entry(frame)
    morning_start.insert(0, TRANSACTION_TIMES['morning'][0])
    morning_start.grid(row=9, column=1, pady=5)

    Label(frame, text="Morning End:").grid(row=10, column=0, sticky="w")
    morning_end = Entry(frame)
    morning_end.insert(0, TRANSACTION_TIMES['morning'][1])
    morning_end.grid(row=10, column=1, pady=5)

    Label(frame, text="Afternoon Start:").grid(row=11, column=0, sticky="w")
    afternoon_start = Entry(frame)
    afternoon_start.insert(0, TRANSACTION_TIMES['afternoon'][0])
    afternoon_start.grid(row=11, column=1, pady=5)

    Label(frame, text="Afternoon End:").grid(row=12, column=0, sticky="w")
    afternoon_end = Entry(frame)
    afternoon_end.insert(0, TRANSACTION_TIMES['afternoon'][1])
    afternoon_end.grid(row=12, column=1, pady=5)

    Label(frame, text="Evening Start:").grid(row=13, column=0, sticky="w")
    evening_start = Entry(frame)
    evening_start.insert(0, TRANSACTION_TIMES['evening'][0])
    evening_start.grid(row=13, column=1, pady=5)

    Label(frame, text="Evening End:").grid(row=14, column=0, sticky="w")
    evening_end = Entry(frame)
    evening_end.insert(0, TRANSACTION_TIMES['evening'][1])
    evening_end.grid(row=14, column=1, pady=5)

    # Max Bill Total
    Label(frame, text="Max Bill Total", font=("Arial", 14, "bold")).grid(row=15, column=0, columnspan=2, pady=10)
    Label(frame, text="Min:").grid(row=16, column=0, sticky="w")
    max_bill_min = Entry(frame)
    max_bill_min.insert(0, MAX_BILL_TOTAL[0])
    max_bill_min.grid(row=16, column=1, pady=5)

    Label(frame, text="Max:").grid(row=17, column=0, sticky="w")
    max_bill_max = Entry(frame)
    max_bill_max.insert(0, MAX_BILL_TOTAL[1])
    max_bill_max.grid(row=17, column=1, pady=5)

    # Save Button
    Button(frame, text="Save Settings", command=save_settings).grid(row=18, column=0, columnspan=2, pady=20)

# Create the Tkinter window
root = tk.Tk()
root.title("POS Bot")
root.withdraw()
# Set a professional window size and center it on the screen
window_width, window_height = 650, 600
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
position_top = int(screen_height / 2 - window_height / 2)
position_right = int(screen_width / 2 - window_width / 2)
root.geometry(f"{window_width}x{window_height}+{position_right}+{position_top}")

# Apply a background color or image
root.config(bg="#f0f4f7")  # Light gray-blue background

# Style for ttk widgets
style = ttk.Style()
style.theme_use("clam")  # A modern, clean theme
style.configure("TButton", font=("Arial", 12), padding=10, relief="flat", background="#2b5797", foreground="white")
style.map("TButton", background=[("active", "#1d3d6e")], foreground=[("active", "white")])

# Create a main frame to contain all widgets
main_frame = ttk.Frame(root, padding=(20, 10), style="TFrame")
main_frame.pack(expand=True, fill="both")

# Create a label for the title
title_label = ttk.Label(main_frame, text="POS Bot Control Panel", font=("Arial", 18, "bold"), background="#f0f4f7")
title_label.pack(pady=10)

# Frame to contain buttons
button_frame = ttk.Frame(main_frame)
button_frame.pack(pady=20)

# Define button padding and layout
button_padding = {'padx': 10, 'pady': 5}

# Buttons
login_button = ttk.Button(button_frame, text="Bot Login & Sale", command=start_login_bot)
login_button.grid(row=0, column=0, **button_padding)

start_button = ttk.Button(button_frame, text="Bot Sale", command=start_sale_bot)
start_button.grid(row=1, column=0, **button_padding)

stop_button = ttk.Button(button_frame, text="Stop Bot", command=stop_sale_bot)
stop_button.grid(row=2, column=0, **button_padding)

generate_report_button = ttk.Button(button_frame, text="Generate Report", command=generate_report)
generate_report_button.grid(row=3, column=0, **button_padding)

special_button = ttk.Button(button_frame, text="Shift Close POS", command=shift_closing)
special_button.grid(row=0, column=1, **button_padding)

pos_button = ttk.Button(button_frame, text="Run POS", command=run_pos_thread)
pos_button.grid(row=1, column=1, **button_padding)

main_login_button = ttk.Button(button_frame, text="Main Login", command=Main_Login)
main_login_button.grid(row=2, column=1, **button_padding)

cashier_login_button = ttk.Button(button_frame, text="Cashier Login", command=Cashier_Login)
cashier_login_button.grid(row=3, column=1, **button_padding)

# Add control buttons to the bottom
control_frame = ttk.Frame(main_frame)
control_frame.pack(pady=10)

hide_button = ttk.Button(control_frame, text="Hide", command=toggle_window_visibility)
hide_button.grid(row=0, column=0, **button_padding)

settings_button = ttk.Button(control_frame, text="Settings", command=open_settings_window)
settings_button.grid(row=0, column=1, **button_padding)

disable_button = ttk.Button(control_frame, text="Disable Keyboard", command=disable_keyboard)
disable_button.grid(row=1, column=0, **button_padding)

enable_button = ttk.Button(control_frame, text="Enable Keyboard", command=enable_keyboard)
enable_button.grid(row=1, column=1, **button_padding)

# Add a Text widget to display log messages with a scrollbar
log_frame = ttk.Frame(main_frame)
log_frame.pack(pady=10, fill="x")

log_text = tk.Text(log_frame, height=12, width=70, wrap="word", padx=10, pady=10)
log_text.pack(side="left", fill="both", expand=True)

scrollbar = ttk.Scrollbar(log_frame, command=log_text.yview)
scrollbar.pack(side="right", fill="y")
log_text.config(yscrollcommand=scrollbar.set)

# Add bottom padding
ttk.Label(main_frame, text="© 2024 POS Bot", font=("Arial", 10), background="#f0f4f7").pack(side="bottom", pady=10)

# Start the Tkinter event loop
#start_login_bot()
load_config()
root.mainloop()
