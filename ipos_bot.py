import csv
import datetime
import socket
import subprocess
import pandas as pd
import pyautogui
import time
import random
import threading
import tkinter as tk
import pygetwindow as gw
from tkinter import Tk, ttk
import schedule
import pystray
from PIL import Image, ImageTk
from tkinter import messagebox
import keyboard
import psutil
from pywinauto import Application

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

# Global variables
sales_records = []
total_transactions = 0
sale_stop_clicked = False
error_stop_clicked = False
login_stop_clicked = False
# Function to schedule shift closing at midnight

# Function to load item codes from Excel file
def load_item_codes(file_path):
    try:
        df = pd.read_excel(file_path)
        log_message("Item codes loaded successfully.")
        return df.to_dict(orient='records')
    except Exception as e:
        error_message = f"Error loading item codes: {e}"
        log_message(error_message)
        return []

def disable_keyboard():
    for key in keyboard.all_modifiers:
        keyboard.block_key(key)
    for i in range(150):  # Typically there are around 150 key codes
        keyboard.block_key(i)
    messagebox.showinfo("Keyboard Disabled", "Keyboard input has been disabled.")

def enable_keyboard():
    for key in keyboard.all_modifiers:
        keyboard.unblock_key(key)
    for i in range(150):
        keyboard.unblock_key(i)
    messagebox.showinfo("Keyboard Enabled", "Keyboard input has been enabled.")
# Function to log messages
def log_message(message):
    timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    log_text.config(state=tk.NORMAL)
    log_text.insert(tk.END, f"[{timestamp}] {message}\n")
    log_text.see(tk.END)
    log_text.config(state=tk.DISABLED)
 # Save message to file
    with open(LOG_FILE, 'a') as file:
        file.write(f"[{timestamp}] {message}\n")
        # Function to select items for sale based on company and selection probability

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
def generate_window_title():
    ip_address = get_ipv4_address()
    current_date = datetime.datetime.now().strftime("%d %b %Y")
    return f"iPOS.NET Ver. 22.112 G Pro. Store #1001 - AL SIDDIQUE BAKERS (OCX) -- Server -- server-bakers- LS - POS02-PC -- {ip_address} -TS- POS02-PC Date.  {current_date}  "
#   return f"iPOS.NET Ver. 22.112 G Pro. Store #1001 - AL SIDDIQUE BAKERS (OCX) -- Server -- server-bakers- LS - POS02-PC -- 192.168.1.12 -TS- POS02-PC Date.  {current_date}  "

def get_ipv4_address():
    try:
        # Get the hostname of the local machine
        hostname = socket.gethostname()
        # Get the IPv4 address corresponding to the hostname
        ip_address = socket.gethostbyname(hostname)
        return ip_address
    except Exception as e:
        print("Error:", e)
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
def handle_pos_errors_NEW():
    while not error_stop_clicked:
        active_window = gw.getActiveWindow()
        window_title = active_window.title if active_window else ""

        if POS_WINDOW_NAME in gw.getAllTitles():
            if window_title == "SQL Connection":
                log_message("SQL Connection error detected. Restarting POS software.")
                handle_db_error()
            
            elif window_title == "BACKOFFICE.NET":
                log_message("BACKOFFICE.NET error detected.")
                manage_quantity_error()
                time.sleep(10)
            elif window_title != POS_WINDOW_NAME:
                log_message("POS window or item code input field not in focus. Bringing to front.")
                focus_to_window(POS_WINDOW_NAME)
        elif LOGIN_WINDOW_NAME in gw.getAllTitles() and window_title != LOGIN_WINDOW_NAME:
            log_message("Login window not in focus. Bringing to front.")
            focus_to_window(LOGIN_WINDOW_NAME)
        time.sleep(5)
def handle_pos_errors():
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
                    handle_db_error()
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
                    handle_db_error()
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
                    handle_db_error()
                elif window_title == ERROR_WINDOW:
                    log_message("software error detected. Restarting POS software.")
                    handle_db_error()
                
                elif not window_title == LOGIN_WINDOW_NAME:    
                                    # Check if POS screen or item code input field has focus
                    log_message("SOFTWARE_WINDOW not in focus. Bringing to front.")
                    target_window = gw.getWindowsWithTitle(LOGIN_WINDOW_NAME)
                    if target_window:
                        focus_to_window(LOGIN_WINDOW_NAME)    
        time.sleep(10) 
def handle_db_error():
    log_message("handle_db_error() function called.")
    global sale_stop_clicked,error_stop_clicked,login_stop_clicked
    pyautogui.moveTo(x=787, y=495, duration=0.25)
    pyautogui.click()
    
    sale_stop_clicked = True
    error_stop_clicked = True
    login_stop_clicked = True
    close_windows_by_title(DB_ERROR_WINDOW)
    close_windows_by_title(POS_WINDOW_NAME)
    close_windows_by_title(generate_window_title())
    close_windows_by_title(LOGIN_WINDOW_NAME)
    restart_pos()
    
def close_windows_by_title(target_title):
    # Retrieve all window titles
    window_titles = gw.getAllTitles()
    target_windows = [win for win in gw.getWindowsWithTitle(target_title) if win.title == target_title]

    if not target_windows:
        log_message(f"No windows found with title '{target_title}'")
        return

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
    windows = gw.getAllTitles()
    target_window = gw.getWindowsWithTitle(window_title)

    if windows.__contains__(window_title):    
        target_window = gw.getWindowsWithTitle(window_title)
                # If the window is found, activate it
        if target_window:
           target_window[0].activate()
           print(f"Switched to window: {window_title}")
        else:
            print(f"Unable to find window: {window_title}")
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
    global total_transactions
    pyautogui.FAILSAFE = False
    time.sleep(15)  # Wait for 2 seconds for the POS software to load
    focus_to_window(POS_WINDOW_NAME)
    #x, y = 200, 100
    
    #pyautogui.click(x, y)
    global total_transactions,sale_stop_clicked
    log_message("Bot started.")
    total_sales_today = 0
    total_sales_limit = get_total_sales_limit()
    log_message(f"Total sales limit for the day: {total_sales_limit}")
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

def get_remaining_time_until_business_hours_old():
    now = datetime.datetime.now()
    opening_time, closing_time = BUSINESS_HOURS

    # Calculate target time based on the current day if current time is after 12 AM
    if now.hour < 2:
        target_time = datetime.datetime(now.year, now.month, now.day, 2, 0)
    else:
        next_day = now + datetime.timedelta(days=1)
        target_time = datetime.datetime(next_day.year, next_day.month, next_day.day, 2, 0)

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
    threading.Thread(target=handle_pos_errors).start()
    threading.Thread(target=login_to_pos).start()
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
keyboard.add_hotkey('ctrl+shift+0', toggle_window_visibility)

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
#Function to open the settings window
def open_settings_window():
    # Create a new window for settings
    settings_window = Toplevel(root)
    settings_window.title("Settings")

    # Function to save the settings
    def save_settings():
        # Retrieve the values entered by the user and update the constants
        SALES_LIMITS['weekday'] = (int(weekday_lower_limit_entry.get()), int(weekday_upper_limit_entry.get()))
        SALES_LIMITS['weekend'] = (int(weekend_lower_limit_entry.get()), int(weekend_upper_limit_entry.get()))
        BUSINESS_HOURS = (datetime.time(int(business_hours_start_entry.get()), 0),
                          datetime.time(int(business_hours_end_entry.get()), 0))
        TRANSACTION_TIMES['morning'] = (int(morning_start_entry.get()), int(morning_end_entry.get()))
        TRANSACTION_TIMES['afternoon'] = (int(afternoon_start_entry.get()), int(afternoon_end_entry.get()))
        TRANSACTION_TIMES['evening'] = (int(evening_start_entry.get()), int(evening_end_entry.get()))
        MAX_BILL_TOTAL = (int(max_bill_total_min_entry.get()), int(max_bill_total_max_entry.get()))
        settings_window.destroy()
# Add input fields for all constant values
    Label(settings_window, text="Sales Limits:").grid(row=0, column=0, columnspan=2)
    Label(settings_window, text="Weekday Lower Limit:").grid(row=1, column=0)
    weekday_lower_limit_entry = Entry(settings_window)
    weekday_lower_limit_entry.insert(0, str(SALES_LIMITS['weekday'][0]))  # Display current value
    weekday_lower_limit_entry.grid(row=1, column=1)

    Label(settings_window, text="Weekday Upper Limit:").grid(row=2, column=0)
    weekday_upper_limit_entry = Entry(settings_window)
    weekday_upper_limit_entry.insert(0, str(SALES_LIMITS['weekday'][1]))  # Display current value
    weekday_upper_limit_entry.grid(row=2, column=1)

    Label(settings_window, text="Weekend Lower Limit:").grid(row=3, column=0)
    weekend_lower_limit_entry = Entry(settings_window)
    weekend_lower_limit_entry.insert(0, str(SALES_LIMITS['weekend'][0]))  # Display current value
    weekend_lower_limit_entry.grid(row=3, column=1)

    Label(settings_window, text="Weekend Upper Limit:").grid(row=4, column=0)
    weekend_upper_limit_entry = Entry(settings_window)
    weekend_upper_limit_entry.insert(0, str(SALES_LIMITS['weekend'][1]))  # Display current value
    weekend_upper_limit_entry.grid(row=4, column=1)

    Label(settings_window, text="Business Hours:").grid(row=5, column=0, columnspan=2)
    Label(settings_window, text="Start Time (hour):").grid(row=6, column=0)
    business_hours_start_entry = Entry(settings_window)
    business_hours_start_entry.insert(0, str(BUSINESS_HOURS[0].hour))  # Display current value
    business_hours_start_entry.grid(row=6, column=1)

    Label(settings_window, text="End Time (hour):").grid(row=7, column=0)
    business_hours_end_entry = Entry(settings_window)
    business_hours_end_entry.insert(0, str(BUSINESS_HOURS[1].hour))  # Display current value
    business_hours_end_entry.grid(row=7, column=1)

    Label(settings_window, text="Transaction Times:").grid(row=8, column=0, columnspan=2)
    Label(settings_window, text="Morning Start Time:").grid(row=9, column=0)
    morning_start_entry = Entry(settings_window)
    morning_start_entry.insert(0, str(TRANSACTION_TIMES['morning'][0]))  # Display current value
    morning_start_entry.grid(row=9, column=1)

    Label(settings_window, text="Morning End Time:").grid(row=10, column=0)
    morning_end_entry = Entry(settings_window)
    morning_end_entry.insert(0, str(TRANSACTION_TIMES['morning'][1]))  # Display current value
    morning_end_entry.grid(row=10, column=1)

    Label(settings_window, text="Afternoon Start Time:").grid(row=11, column=0)
    afternoon_start_entry = Entry(settings_window)
    afternoon_start_entry.insert(0, str(TRANSACTION_TIMES['afternoon'][0]))  # Display current value
    afternoon_start_entry.grid(row=11, column=1)

    Label(settings_window, text="Afternoon End Time:").grid(row=12, column=0)
    afternoon_end_entry = Entry(settings_window)
    afternoon_end_entry.insert(0, str(TRANSACTION_TIMES['afternoon'][1]))  # Display current value
    afternoon_end_entry.grid(row=12, column=1)

    Label(settings_window, text="Evening Start Time:").grid(row=13, column=0)
    evening_start_entry = Entry(settings_window)
    evening_start_entry.insert(0, str(TRANSACTION_TIMES['evening'][0]))  # Display current value
    evening_start_entry.grid(row=13, column=1)

    Label(settings_window, text="Evening End Time:").grid(row=14, column=0)
    evening_end_entry = Entry(settings_window)
    evening_end_entry.insert(0, str(TRANSACTION_TIMES['evening'][1]))  # Display current value
    evening_end_entry.grid(row=14, column=1)

    Label(settings_window, text="Max Bill Total:").grid(row=15, column=0, columnspan=2)
    Label(settings_window, text="Min Value:").grid(row=16, column=0)
    max_bill_total_min_entry = Entry(settings_window)
    max_bill_total_min_entry.insert(0, str(MAX_BILL_TOTAL[0]))  # Display current value
    max_bill_total_min_entry.grid(row=16, column=1)

    Label(settings_window, text="Max Value:").grid(row=17, column=0)
    max_bill_total_max_entry = Entry(settings_window)
    max_bill_total_max_entry.insert(0, str(MAX_BILL_TOTAL[1]))  # Display current value
    max_bill_total_max_entry.grid(row=17, column=1)

    # Add a button to save settings
    save_button = Button(settings_window, text="Save", command=save_settings)
    save_button.grid(row=18, column=0, columnspan=2)

# Menu for the system tray icon
# Create Tkinter window
root = tk.Tk()
root.title("POS Bot")
root.geometry("600x600")

# Style for buttons
style = ttk.Style()
style.configure('TButton', font=('Arial', 12), padding=5)

# Frame to contain buttons
button_frame = ttk.Frame(root)
button_frame.pack(pady=20)

# Buttons
login_button = ttk.Button(button_frame, text="Bot Login & Sale", command=start_login_bot)
login_button.grid(row=0, column=0, padx=10, pady=5)

start_button = ttk.Button(button_frame, text="Bot Sale", command=start_sale_bot)
start_button.grid(row=1, column=0, padx=10, pady=5)

stop_button = ttk.Button(button_frame, text="Stop Bot", command=stop_sale_bot)
stop_button.grid(row=2, column=0, padx=10, pady=5)

generate_report_button = ttk.Button(button_frame, text="Generate Report", command=generate_report)
generate_report_button.grid(row=3, column=0, padx=10, pady=5)
special_button = ttk.Button(button_frame, text="shift close POS", command=shift_closing)
special_button.grid(row=0, column=1, padx=10, pady=5)
special_button = ttk.Button(button_frame, text="Run POS", command=run_pos_thread)
special_button.grid(row=1, column=1, padx=10, pady=5)
hide_button = ttk.Button(button_frame, text="Main Login", command=Main_Login)
hide_button.grid(row=2, column=1, padx=10, pady=5)

show_button = ttk.Button(button_frame, text="Cashier Login", command=Cashier_Login)
show_button.grid(row=3, column=1, padx=10, pady=5)
# Add a button named "Hide" to the GUI to trigger the hide_gui function
hide_button = tk.Button(root, text="Hide", command=toggle_window_visibility)
hide_button.pack()
# Add a button named "Settings" to the GUI to trigger the open_settings_window function
settings_button = Button(root, text="Settings", command=open_settings_window)
settings_button.pack()
disable = Button(root, text="disable", command=disable_keyboard)
disable.pack()
enable = Button(root, text="enable", command=enable_keyboard)
enable.pack()
# Create a Text widget to display log messages
log_text = tk.Text(root, height=20, width=70)
log_text.pack(pady=20, padx=10) 
# Start the Tkinter event loop

# Start the scheduler thread
threading.Thread(target=run_scheduler, daemon=True).start()

# Schedule the shift closing
schedule_shift_closing()

# Start the login bot by default
#start_login_bot()
root.mainloop()