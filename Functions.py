import numpy as np
import time
import pyautogui
import os
from Frame import Frame
import random
import copy


def cls():
    """
    Commented out - bootleg "clear console" for Pycharm,
    use while writing, and switch to "os.system..." line when
    packing into .exe

    for getting coordinates:
    time.sleep(2)
    print(pyautogui.position())

    launch program, and move cursor to the simulated console window,
    after 2s you'll get coordinates to put as pyautogui.click() arguments
    :return:
    """

    # time.sleep(0.1)
    pyautogui.click(x=778, y=832)
    pyautogui.hotkey('ctrl', 'l')

    # os.system('cls' if os.name == 'nt' else 'clear')


# def clean_list(mylist):
#     # newlist = []
#     # for item in mylist:
#     #     # lots of code here, possibly setting things up for calling determine
#     #     if item != 'erase':
#     #         newlist.append(item)
#     # mylist = newlist
#     # return mylist
#
#     return list(filter(lambda element: element != 'erase', mylist))




