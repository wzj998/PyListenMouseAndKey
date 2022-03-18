# coding=utf-8
import _thread
import time
from ctypes import *
from ctypes import wintypes
from decimal import Decimal

import win32con
import tkinter

SetWindowsHookEx = windll.user32.SetWindowsHookExA
UnhookWindowsHookEx = windll.user32.UnhookWindowsHookEx
CallNextHookEx = windll.user32.CallNextHookEx
GetMessage = windll.user32.GetMessageA
GetModuleHandle = windll.kernel32.GetModuleHandleW
# 保存键盘钩子函数句柄
keyboard_hd = None
# 保存鼠标钩子函数句柄
mouse_hd = None


class KBDLLHOOKSTRUCT(Structure):
    _fields_ = [
        ('vkCode', c_int),
        ('scanCode', c_int),
        ('flags', c_int),
        ('time', c_int),
        ('dwExtraInfo', c_uint),
        ('', c_void_p)
    ]


class POINT(Structure):
    _fields_ = [
        ('x', c_long),
        ('y', c_long)
    ]


class MSLLHOOKSTRUCT(Structure):
    _fields_ = [
        ('pt', POINT),
        ('hwnd', c_int),
        ('wHitTestCode', c_uint),
        ('dwExtraInfo', c_uint),
    ]


class MSWHEELHOOKSTRUCT(Structure):
    _fields_ = [
        ('pt', POINT),
        ('delta', c_int),
        ('wHitTestCode', c_uint),
        ('dwExtraInfo', c_uint),
    ]


def wait_for_msg():
    msg = wintypes.MSG()
    GetMessage(msg, 0, 0, 0)


def keyboard_pro(nCode, wParam, lParam):
    """
    函数功能：键盘钩子函数，当有按键按下时此函数被回调
    """
    if nCode == win32con.HC_ACTION:
        KBDLLHOOKSTRUCT_p = POINTER(KBDLLHOOKSTRUCT)
        param = cast(lParam, KBDLLHOOKSTRUCT_p)
        if 32 == param.contents.vkCode:
            global time_start, last_text
            new_str = str(param.contents.vkCode) + " " + str(param.contents.flags) + "\ntime = " + str(
                Decimal(time.time() - time_start).quantize(Decimal("0.000000")))
            last_text.set(new_str)
    return CallNextHookEx(keyboard_hd, nCode, wParam, lParam)


def start_keyboard_hook():
    """
    函数功能：启动键盘监听
    """
    HOOKPROTYPE = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    pointer = HOOKPROTYPE(keyboard_pro)
    keyboard_hd = SetWindowsHookEx(
        win32con.WH_KEYBOARD_LL,
        pointer,
        GetModuleHandle(None),
        0)
    wait_for_msg()


def stop_keyboard_hook():
    """
    函数功能：停止键盘监听
    """
    UnhookWindowsHookEx(keyboard_hd)


def mouse_pro(nCode, wParam, lParam):
    """
    函数功能：鼠标钩子函数，当有鼠标事件，此函数被回调
    """
    if nCode == win32con.HC_ACTION:
        MSLLHOOKSTRUCT_p = POINTER(MSLLHOOKSTRUCT)
        param = cast(lParam, MSLLHOOKSTRUCT_p)
        param_wheel = cast(lParam, POINTER(MSWHEELHOOKSTRUCT))
        # 鼠标左键点击
        # if wParam == win32con.WM_LBUTTONDOWN:
        #     print("左键点击，坐标：x:%d,y:%d" % (param.contents.pt.x, param.contents.pt.y))
        # elif wParam == win32con.WM_LBUTTONUP:
        #     print("左键抬起，坐标：x:%d,y:%d" % (param.contents.pt.x, param.contents.pt.y))
        # # elif wParam == win32con.WM_MOUSEMOVE:
        # #     print("鼠标移动，坐标：x:%d,y:%d" % (param.contents.pt.x, param.contents.pt.y))
        # elif wParam == win32con.WM_RBUTTONDOWN:
        #     print("右键点击，坐标：x:%d,y:%d" % (param.contents.pt.x, param.contents.pt.y))
        # elif wParam == win32con.WM_RBUTTONUP:
        #     print("右键抬起，坐标：x:%d,y:%d" % (param.contents.pt.x, param.contents.pt.y))
        if wParam == win32con.WM_MOUSEWHEEL:
            global time_start, last_text
            new_str = "鼠标滚轮 " + str(param_wheel.contents.delta) + "\ntime = " + str(
                Decimal(time.time() - time_start).quantize(Decimal("0.000000")))
            last_text.set(new_str)

    return CallNextHookEx(mouse_hd, nCode, wParam, lParam)


def start_mouse_hook():
    """
    函数功能：启动鼠标监听
    """
    HOOKPROTYPE = CFUNCTYPE(c_int, c_int, c_int, POINTER(c_void_p))
    pointer = HOOKPROTYPE(mouse_pro)
    mouse_hd = SetWindowsHookEx(
        win32con.WH_MOUSE_LL,
        pointer,
        GetModuleHandle(None),
        0)
    wait_for_msg()


def stop_mouse_hook():
    """
    函数功能：停止鼠标监听
    """
    UnhookWindowsHookEx(mouse_hd)


global time_start, last_text
if __name__ == '__main__':
    time_start = time.time()

    _thread.start_new_thread(start_mouse_hook, ())
    _thread.start_new_thread(start_keyboard_hook, ())
    # while True:
    #     time.sleep(1)

    root = tkinter.Tk()
    last_text = tkinter.StringVar()
    last_text.set('old')
    root.overrideredirect(True)
    root.attributes("-alpha", 0.5)  # 窗口透明度
    root.geometry("300x200+1620+780")

    w = tkinter.Label(root, textvariable=last_text, font=("微软雅黑", 18), wraplength=300)
    w.pack(expand=1)

    root.attributes("-topmost", True)
    root.mainloop()
