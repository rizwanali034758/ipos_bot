import datetime
import logging
from pywinauto import Application
import psutil
import pygetwindow as gw

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
result = terminate_process(process_name="BACKOFFICE.NET.exe")
if result:
    print("Process terminated successfully.")
else:
    print("No matching process found or termination failed.")