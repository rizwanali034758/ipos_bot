import pyautogui

# Get the current position of the mouse cursor
current_position = pyautogui.position()
pyautogui.moveTo(x=416, y=33, duration=0.25)
pyautogui.click()
pyautogui.moveTo(x=454, y=76, duration=0.25)

# Print the coordinates
print("Current mouse position:", current_position)
