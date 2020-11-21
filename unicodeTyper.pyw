from win32clipboard import OpenClipboard, EmptyClipboard, CloseClipboard,SetClipboardText
from win32con import KEYEVENTF_KEYUP
from win32api import GetKeyState, keybd_event
import win32gui
import time
import sys
from functools import partial
import threading
from threading import Thread

from tkinter import *
from tkinter import font as tkFont
import tkinter.ttk as ttk

import inspect
import ctypes
import csv

def _async_raise(tid, exctype):
    """raises the exception, performs cleanup if needed"""
    tid = ctypes.c_long(tid)
    if not inspect.isclass(exctype):
        exctype = type(exctype)
    res = ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, ctypes.py_object(exctype))
    if res == 0:
        raise ValueError("invalid thread id")
    elif res != 1:
        # """if it returns a number greater than one, you're in trouble,
        # and you should call it again with exc=NULL to revert the effect"""
        ctypes.pythonapi.PyThreadState_SetAsyncExc(tid, None)
        raise SystemError("PyThreadState_SetAsyncExc failed")

top_two_wins = [0,10]
def monitor_window():
    state_left = GetKeyState(0x01)  # Left button down = 0 or 1. 
    while True:
        a = GetKeyState(0x01)
        if a != state_left:  # Button state changed
            state_left = a
            if a < 0:
                continue
            else:
                top_win = win32gui.GetForegroundWindow()
                tktop="TkTopLevel"
                if top_win and win32gui.GetClassName(top_win) != tktop:
                    top_two_wins[1] = top_win
        time.sleep(0.001)
   
def clipboard_operate(seq=u'empty \u00f8'):
    global top_two_wins
    win32gui.SetForegroundWindow(top_two_wins[1])
    #add unicode to clipboard
    OpenClipboard()
    EmptyClipboard()
    SetClipboardText(seq,13)
    CloseClipboard()
    # ctrl+v
    keybd_event(0x11, 0, 0, 0)
    keybd_event(0x56, 0, 0, 0)
    keybd_event(0x56, 0, KEYEVENTF_KEYUP, 0)
    keybd_event(0x11, 0, KEYEVENTF_KEYUP, 0)

class uniKeyboard:
    def __init__(self,top, value):
        self.b = Button(top)
        self.v = value

class TyperLocater:
    def __init__(self, top=None):
        #super(TyperLocater,self).__init__()
        _bgcolor = '#d9d9d9'  # X11 color: 'gray85'
        _fgcolor = '#000000'  # X11 color: 'black'
        _compcolor = '#b2c9f4' # Closest X11 color: 'SlateGray2'
        _ana1color = '#eaf4b2' # Closest X11 color: '{pale goldenrod}'
        _ana2color = '#f4bcb2' # Closest X11 color: 'RosyBrown2'

        self.top = top
        top.geometry("-9+100")
        top.title("STyper")
        top.configure(highlightbackground="#f5deb3")
        top.configure(highlightcolor="black")
        
        menubar = Menu(top)
        menubar.add_command(label="file", command=self.entry_csv_file)
        menubar.add_command(label="-", command=self.zoom_out)
        menubar.add_command(label="+", command=self.zoom_in)
        self.top.config(menu=menubar)
        
        self.helv36 = tkFont.Font(family='Helvetica', size=18, weight='bold')
        self.keyboard = []
        self.uni_list = [[u'\u00B9',u'\u00B2',u'\u00B3',u'\u2122',u'\u2229'],[u'\u2074',u'\u2075',u'\u2076',u'\u2070',u'\u222A'],[u'\u2077',u'\u2078',u'\u2079',u'\u306E',u'\uFFE5']]
        
        self.create_keyboard()
        
    def redraw_keyboard(self):
        for uk in self.keyboard:
            uk.b.grid_forget()
        #self.uni_list = [[u'\u0045',u'\u004d',u'\u0050',u'\u0054',u'\u2122']]
        self.create_keyboard()
        
    def zoom_out(self):
        org_size = self.helv36["size"]
        if org_size>10:
            self.helv36.configure(size=org_size-1)
        
    def zoom_in(self):
        org_size = self.helv36["size"]
        if org_size<38:
            self.helv36.configure(size=org_size+1)
        
    def create_keyboard(self):
        m = len(self.uni_list)
        n = len(self.uni_list[0])
        for i in range(m):
            for j in range(n):
                uk =uniKeyboard(self.top, self.uni_list[i][j])
                self.keyboard.append(uk)
                uk.b.configure(activebackground="#d9d9d9")
                uk.b.configure(disabledforeground="#b8a786")
                uk.b.configure(highlightbackground="#f5deb3")
                uk.b.configure(text=uk.v)
                uk.b.configure(command=partial(clipboard_operate,uk.v))
                uk.b.configure(font=self.helv36)
                uk.b.grid(row=i,column=j)

    def read_unicode_csv(self,v,entry_win):
        try:
            filename = v.get()
            with open(filename,"rb") as f:
                self.uni_list = []
                for line in f.readlines():
                    s = [i for i in line.decode("utf-8").strip().split(',')]
                    self.uni_list.append(s)
                self.redraw_keyboard()
        except:
            tkinter.messagebox.showinfo('csv error','only utf-8 .csv file')
        
    def entry_csv_file(self):
        entry_win = Toplevel()
        entry_win.geometry("-90+10")
        entry_win.title("input a csv file")
        v1 = StringVar()
        e1=Entry(entry_win,textvariable=v1,width=50)
        e1.grid(row=1,column=0)
        Button(entry_win,text="OK",command=partial(self.read_unicode_csv,v1,entry_win)).grid(row=3,column=0)
        
root = Tk()
root.wm_attributes('-topmost',1)
top = TyperLocater (root)
monitor = threading.Thread(target=monitor_window)
monitor.start()

def stop_thread():
    _async_raise(monitor.ident, SystemExit)
    sys.exit(0)
    
root.protocol("WM_DELETE_WINDOW", stop_thread)
root.mainloop()

