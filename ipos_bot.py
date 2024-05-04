import csv
import datetime
import subprocess
import pandas as pd
import pyautogui
import time
import random
import threading
import tkinter as tk
import pygetwindow as gw
from tkinter import ttk
import schedule

# Constants
ITEM_DATA_FILE = 'bot_data.xlsx'
SALES_LIMITS = {'weekday': (40000, 50000), 'weekend': (60000, 70000)}
BUSINESS_HOURS = (datetime.time(2, 0), datetime.time(23, 50))
TRANSACTION_TIMES = {'morning': (1200, 1500), 'afternoon': (900, 1380), 'evening': (600, 1200)}
MAX_BILL_TOTAL = (200, 2000)
LOG_FILE = 'log.txt'
SALES_REPORT_FILE = 'sales_report.csv'
POS_WINDOW_NAME = "IPOS.NET http://www.ipos.net.pk"
LOGIN_WINDOW_NAME = "iPOS VER: 22.112 G Pro"
SOFTWARE_WINDOW = "iPOS.NET Ver. 22.112 G Pro. Store #1001"

# Global variables
sales_records = []
total_transactions = 0
stop_clicked = False
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
""" def select_items_for_sale(item_data):
    selected_items = []
    for index, row in item_data.iterrows():
        selection_probability = row['SelectionProbability']
        if random.random() < selection_probability:
            selected_items.append({'ItemCode': row['ItemCode'], 'Quantity': row['EstimatedSale']})
    return selected_items """
# Function to select items for sale
def select_items_for_sale(item_data):
    selected_items = []
    num_selected_items = random.randint(1, 4)
    num_items_selected = 0
      # Shuffle the item_data list
    random.shuffle(item_data)
    for item in item_data:
        company = item['catcode']
        # Adjust the selection probability based on the company
        if company == 90:  # 90 for walls company
            selection_probability = 0.46
        elif company == 92:  # 92 for nestle
            selection_probability = 0.47
        elif company == 91:  # 91 for unilever
            selection_probability = 0.06
        else:
            selection_probability = 0.0

        # Generate a random number to determine if the item is selected
        if random.random() < selection_probability:
            selected_items.append(item)  # Append the complete item dictionary
            num_items_selected += 1
            if num_items_selected == num_selected_items:
                break  # Exit loop if maximum number of items reached

    return selected_items

# Function to restart POS software
def restart_pos():
    subprocess.Popen([r"C:\Program Files\iPOS.NET\BACKOFFICE.NET.exe"], creationflags=subprocess.DETACHED_PROCESS)
    time.sleep(60)  # Wait for POS software to start
    #login_to_pos()  # Log in to POS
    threading.Thread(target=login_to_pos).start()  # Restart sale simulation
def generate_window_title():
    current_date = datetime.datetime.now().strftime("%d %b %Y")
    return f"iPOS.NET Ver. 22.112 G Pro. Store #1001 - AL SIDDIQUE BAKERS (OCX) -- Server -- server-bakers- LS - POS02-PC -- 192.168.1.32 -TS- POS02-PC Date.  {current_date}  "

def cancel_bill():

    # Simulate pressing Ctrl+Z to initiate bill cancellation
    pyautogui.hotkey('ctrl', 'z')
    # Simulate typing the password (replace 'password' with your actual password)
    pyautogui.typewrite('5s')
    # Simulate pressing Enter to confirm the password
    pyautogui.press('enter')
def handle_pos_errors():
    while not stop_clicked:
        # Get the active window
        active_window = gw.getActiveWindow()
        windows = gw.getAllTitles()
        window_title = active_window.title

        if active_window is not None:
            if windows.__contains__(POS_WINDOW_NAME):
                window_title = active_window.title
                # Check if SQL Connection error window is present
                if window_title == "SQL Connection":
                    log_message("SQL Connection error detected. Restarting POS software.")
                    restart_pos()
                # Check if BACKOFFICE.NET error window is present
                elif window_title == "BACKOFFICE.NET":
                    log_message("BACKOFFICE.NET error detected.")
                    manage_quantity_error()
                    """ error_text = active_window.text.lower()
                    if "itemcode does not exist" in error_text:
                        log_message("Item code not found. Handling the error.")
                        pyautogui.press('enter')
                        # Call function to handle item not found error
                    elif "please enter quantity" in error_text:
                        log_message("Quantity error. Handling the error.")
                        manage_quantity_error()
                        # Call function to handle quantity error
                    elif "msgbox please enter correct payment," in error_text:
                        log_message("Payment error. Handling the error.")
                        pyautogui.press('enter')
                        cancel_bill()
                        # Call function to handle payment error
                    else:
                        log_message("Unknown error detected.") """
                    time.sleep(10)  # Wait for the error window to close
                elif not window_title == POS_WINDOW_NAME:    
                                    # Check if POS screen or item code input field has focus
                    log_message("POS window or item code input field not in focus. Bringing to front.")
                    target_window = gw.getWindowsWithTitle(POS_WINDOW_NAME)
                    if target_window:
                        focus_to_window(POS_WINDOW_NAME)    
                #else:
                    #log_message("")
            elif windows.__contains__(generate_window_title()):
                if window_title == "SQL Connection":
                    log_message("SQL Connection error detected. Restarting POS software.")
                    restart_pos()
                elif not window_title == generate_window_title():    
                                    # Check if POS screen or item code input field has focus
                    log_message("SOFTWARE_WINDOW not in focus. Bringing to front.")
                    target_window = gw.getWindowsWithTitle(generate_window_title())
                    if target_window:
                        focus_to_window(generate_window_title())    
            elif windows.__contains__(LOGIN_WINDOW_NAME):
                if window_title == "SQL Connection":
                    log_message("SQL Connection error detected. Restarting POS software.")
                    restart_pos()
                elif not window_title == LOGIN_WINDOW_NAME:    
                                    # Check if POS screen or item code input field has focus
                    log_message("SOFTWARE_WINDOW not in focus. Bringing to front.")
                    target_window = gw.getWindowsWithTitle(LOGIN_WINDOW_NAME)
                    if target_window:
                        focus_to_window(LOGIN_WINDOW_NAME)    
        time.sleep(5) 

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
    pyautogui.press('enter')
    pyautogui.press('enter')
    for _ in range(7):
        pyautogui.press('backspace')
    pyautogui.press('enter')
    pyautogui.press('enter')
    cancel_bill() # Check every 5 seconds
def shift_closing():
    # Activate the POS window
    focus_to_window(POS_WINDOW_NAME)
    # Simulate pressing Ctrl+Alt+S to initiate shift closing
    pyautogui.hotkey('ctrl', 'alt', 's')
    # Simulate pressing Enter 14 times
    for _ in range(14):
        pyautogui.press('enter')
    # Move the mouse cursor to the bottom center of the screen
    pyautogui.moveTo(x=906, y=324, duration=0.25)
    # Simulate a mouse click to confirm shift closing
    pyautogui.click()
   # Simulate pressing Enter 3 times
    time.sleep(5)  # Wait for 2 seconds for the POS software to load
    for _ in range(3):
        time.sleep(2)  # Wait for 2 seconds for the POS software to load
        pyautogui.press('enter')
    pyautogui.moveTo(x=49, y=35, duration=0.25)
    pyautogui.click()
    pyautogui.press('enter')
    # Simulate pressing Alt+F4 2 times to close the Shift Closing window
    for _ in range(2):
        time.sleep(2)  # Wait for 2 seconds for the POS software to load
        pyautogui.hotkey('alt', 'f4')
    # Wait for the software to close
    time.sleep(10)
    # Restart POS
    login_to_pos()
def schedule_shift_closing():
    schedule.every().day.at("00:00").do(shift_closing)

# Start the scheduling thread
schedule_shift_closing()

# Function to simulate sale transaction
def simulate_sale():
    global total_transactions, stop_clicked
    pyautogui.FAILSAFE = False
    time.sleep(15)  # Wait for 2 seconds for the POS software to load
    focus_to_window(POS_WINDOW_NAME)
    #x, y = 200, 100
    
    #pyautogui.click(x, y)
    global total_transactions
    log_message("Bot started.")
    total_sales_today = 0
    total_sales_limit = get_total_sales_limit()
    log_message(f"Total sales limit for the day: {total_sales_limit}")
    item_data = load_item_codes(ITEM_DATA_FILE)
    if not item_data:
        log_message("No item codes loaded. Exiting.")
        return

    while not stop_clicked:
        if total_sales_today >= total_sales_limit:
            log_message("Total sales limit for the day reached. Waiting for tomorrow.")
            total_sales_today = 0
            total_sales_limit = get_total_sales_limit()
            remaining_time = get_remaining_time_until_business_hours()
            log_message(f"Bussiness is closed now. Bot will resume at 2.00 AM till 23.50 PM. Wait: {remaining_time}")
            time.sleep(remaining_time)
            continue

       
        selected_items = select_items_for_sale(item_data)
        #total_price = sum(item['slprice'] for item in selected_items)
        
        #if not MAX_BILL_TOTAL[0] <= total_price <= MAX_BILL_TOTAL[1]:
         #   log_message("Total price of selected items exceeds bill limit. Completing transaction.")
          #  continue
        

        total_price = 0
        #bill_total_limit = random.randint(*MAX_BILL_TOTAL)
        #log_message(f"Maximum bill total allowed: {bill_total_limit}")

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
# Function to analyze sales without performing transactions
def analyze_sales():
    log_message("Starting sales analysis.")
# Get current time in seconds
    current_time = datetime.datetime.now()
    current_time_seconds = current_time.hour * 3600 + current_time.minute * 60 + current_time.second

# Calculate remaining time until end of day in seconds
    end_of_day = datetime.datetime.combine(current_time.date(), datetime.time(23, 50))
    end_of_day_seconds = (end_of_day - current_time).total_seconds()

# Initialize timer
    timer = current_time_seconds

# In each iteration of the loop
    while timer < end_of_day_seconds:
    # Generate random transaction frequency in seconds
        transaction_frequency = random.randint(1, 600)  # Example range, adjust as needed

    # Add transaction frequency to timer
        timer += transaction_frequency

    # Check if timer exceeds end of day
        if timer >= end_of_day_seconds:
            break

    item_data = load_item_codes(ITEM_DATA_FILE)
    if not item_data:
        log_message("No item codes loaded. Exiting.")

    total_sales_today = 0
    total_sales_limit = get_total_sales_limit()
    log_message(f"Total sales limit for the day: {total_sales_limit}")

    # Initialize timer variables
    current_time = datetime.datetime.now()
    end_time = datetime.datetime(current_time.year, current_time.month, current_time.day, 23, 50)
    timer = 0

    while not stop_clicked:
        if total_sales_today >= total_sales_limit:
            log_message("Total sales limit for the day reached. Waiting for tomorrow.")
            total_sales_today = 0
            total_sales_limit = get_total_sales_limit()
            remaining_time = get_remaining_time_until_business_hours()
            log_message(
                f"Bussiness is closed now. Bot will resume at 6.00 AM till 23.50 PM. Wait: {remaining_time}")
            time.sleep(remaining_time)
            continue

        selected_items = select_items_for_sale(item_data)

        total_price = 0

        for item in selected_items:
            item_code, item_name, item_price = item['ItemCode'], item['Description'], item['Slprice']
            if item['Slprice'] > 1000:
                quantity = 1
            else:
                quantity = random.randint(1, 3)
            item_total_price = quantity * item_price
            log_message(
                f"Selected Item code: {item_code} Item name: {item_name} Price: {item_price} Quantity: {quantity} item_total_price={item_total_price}")
            if not MAX_BILL_TOTAL[0] <= total_price + item_total_price <= MAX_BILL_TOTAL[1]:
                log_message("Maximum bill total reached. Completing transaction.")
                continue

            total_price += item_total_price
            log_message(f"bill total so far ={total_price}")

        total_sales_today += total_price
        log_message(
            f"Total sales for the day so far: {total_sales_today} target sale: {total_sales_limit}  target remaining: {total_sales_limit - total_sales_today}")

        # Increment the timer by the time elapsed since the last iteration
        current_time = datetime.datetime.now()
        time_difference = current_time - end_time
        timer += time_difference.total_seconds()

        if current_time >= end_time:
            log_message("End time reached. Analyzing completed.")
            break

        if is_business_hours():
            transaction_frequency = get_transaction_frequency()
            log_message(f"Waiting for {transaction_frequency} seconds before next transaction.")
            # No sleep here, just keep track of time
            current_time = datetime.datetime.now()
            time_difference = current_time - end_time
            timer += time_difference.total_seconds()
        else:
            total_sales_today = 0
            total_sales_limit = get_total_sales_limit()
            remaining_time = get_remaining_time_until_business_hours()
            hours = remaining_time // 3600
            minutes = (remaining_time % 3600) // 60
            seconds = remaining_time % 60
            log_message(
                f"Bussiness is closed now. Bot will resume at 6.00 AM till 23.50 PM. Wait: {int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}")
            # No sleep here, just keep track of time
            current_time = datetime.datetime.now()
            time_difference = current_time - end_time
            timer += time_difference.total_seconds()
            log_message(f"Total sales limit for the day: {total_sales_limit}")

    return timer

def run_pos():
    log_message("Starting run_pos function.")
    pos_path = r"C:\Program Files\iPOS.NET\BACKOFFICE.NET.exe"
    subprocess.Popen([pos_path], creationflags=subprocess.DETACHED_PROCESS)
    time.sleep(60)  
    log_message("Starting pos software.")

    # Wait for the POS application to start (adjust the delay as needed)
  

# Function to login to POS and cashier screens
def login_to_pos():
    run_pos()
    time.sleep(60)  
    Main_Login()

    time.sleep(30)  # Adjust as needed
    Cashier_Login()
    time.sleep(30)
    pyautogui.hotkey('ctrl', 'alt', 'c')
    threading.Thread(target=simulate_sale).start()
    threading.Thread(target=simulate_sale)

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

    
    log_message("Starting pos software.")    # Wait for the POS application to start (adjust the delay as needed)
    #time.sleep(60)  
    log_message("Starting login details.")
    pyautogui.typewrite("DEO")
    pyautogui.press('enter')
    pyautogui.typewrite("DEO098")
    pyautogui.press('enter')
    pyautogui.press('enter')
# Function to handle start button click
def login_bot():
    global stop_clicked
    stop_clicked = False
    threading.Thread(target=handle_pos_errors).start()
    threading.Thread(target=login_to_pos).start()


# Function to handle start button click
def start_bot():
    global stop_clicked
    stop_clicked = False
    threading.Thread(target=handle_pos_errors).start()
    threading.Thread(target=simulate_sale).start()

# Function to generate report and display in GUI
def generate_report_old():
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
        writer = csv.DictWriter(file, fieldnames=['ItemCode', 'ItemName', 'Quantity', 'Total'])
        writer.writeheader()
        for item_code, data in item_report.items():
            writer.writerow({'ItemCode': item_code, 'ItemName': data['ItemName'], 'Quantity': data['Quantity'], 'Total': data['Total']})
        writer.writerow({'Total Sale Value:': total_sale, 'Total Transactions': total_transactions})
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
def run_pos_thread():
    threading.Thread(target=run_pos).start()
# Function to handle stop button click
def stop_bot():
    global stop_clicked
    stop_clicked = True
    log_message(f"Stoping sale bot")
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

    # Calculate target time based on the current day if current time is after 12 AM
    if now.hour < 2:
        target_time = datetime.datetime(now.year, now.month, now.day, 2, 0)
    else:
        next_day = now + datetime.timedelta(days=1)
        target_time = datetime.datetime(next_day.year, next_day.month, next_day.day, 6, 0)

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
login_button = ttk.Button(button_frame, text="Bot Login & Sale", command=login_bot)
login_button.grid(row=0, column=0, padx=10, pady=5)

start_button = ttk.Button(button_frame, text="Bot Sale", command=start_bot)
start_button.grid(row=1, column=0, padx=10, pady=5)

stop_button = ttk.Button(button_frame, text="Stop Sale", command=stop_bot)
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



# Create a Text widget to display log messages
log_text = tk.Text(root, height=20, width=70)
log_text.pack(pady=20, padx=10)

# Start the Tkinter event loop
root.mainloop()