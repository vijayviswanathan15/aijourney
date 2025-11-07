import pyautogui
import time
import webbrowser

webbrowser.open("https://web.whatsapp.com")
time.sleep(20)

pyautogui.click(1596, 175)
time.sleep(2)

pyautogui.write("SE - AI-B3 - 1")
time.sleep(3)

pyautogui.press('enter')
time.sleep(2)

pyautogui.write("pyautogui demo whatsapp task completed")
time.sleep(1)

pyautogui.press('enter')

print("Task Completed")
