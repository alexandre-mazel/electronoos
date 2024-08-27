"""
helpfull tools to automatise navigation

NB: Currently only for windows computers
"""


def showStartOfPage(strPartOfWindowName):
    focusOnWindow(strPartOfWindowName)
    keyboard.press(['ctrl', "origine"])
    keyboard.press(['ctrl', "home"])
    keyboard.release("ctrl") # clean ctrl key
    
    
def showContextualMenu(x,y):
    setCursorPos(x,y)
    time.sleep(0.4)
    # right button contextual windows, work well but fail if click on a bad point
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTDOWN,x,y,0,0)
    time.sleep(0.3) # time for system to register
    win32api.mouse_event(win32con.MOUSEEVENTF_RIGHTUP,x,y,0,0)
    time.sleep(1.)
    
def getClipboardText():
    """
    return text present in the clipboard or None if not text
    """
    
    """
    # not working:
    import ctypes

    CF_TEXT = 1

    kernel32 = ctypes.windll.kernel32
    kernel32.GlobalLock.argtypes = [ctypes.c_void_p]
    kernel32.GlobalLock.restype = ctypes.c_void_p
    kernel32.GlobalUnlock.argtypes = [ctypes.c_void_p]
    user32 = ctypes.windll.user32
    user32.GetClipboardData.restype = ctypes.c_void_p

    def get_clipboard_text():
        user32.OpenClipboard(0)
        try:
            if user32.IsClipboardFormatAvailable(CF_TEXT):
                data = user32.GetClipboardData(CF_TEXT)
                data_locked = kernel32.GlobalLock(data)
                text = ctypes.c_char_p(data_locked)
                value = text.value
                kernel32.GlobalUnlock(data_locked)
                return value
        finally:
            user32.CloseClipboard()
    """

    import win32clipboard

    # get clipboard data
    win32clipboard.OpenClipboard()
    try:
        data = win32clipboard.GetClipboardData()
        #~ data = win32clipboard.GetClipboardData(win32clipboard.CF_UNICODETEXT)
    except TypeError:
        data = None
    win32clipboard.CloseClipboard()
    if 0:
        # look for eol mark when from html => none
        for d in data:
            print("%s, 0x%d" % (d,ord(d)) )
    return data
# getClipboardText - end

def setClipboardText( txt ):
    # set txt in clipboard
    import win32clipboard
    win32clipboard.OpenClipboard()
    win32clipboard.EmptyClipboard()
    win32clipboard.SetClipboardText(txt) # also try: win32clipboard.SetClipboardData(win32clipboard.CF_TEXT, data).
    win32clipboard.CloseClipboard()
# setClipboardText - end


if __name__ == "__main__":
    #~ setClipboardText("coucou\nles") # copying from web page, remove \n
    txt = getClipboardText()
    print("getClipboardText: '%s'" % txt )