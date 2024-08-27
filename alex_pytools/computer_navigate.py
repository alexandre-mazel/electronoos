"""
helpfull tools to automatise navigation
"""


def showStartOfPage(strPartOfWindowName):
    focusOnWindow(strPartOfWindowName)
    keyboard.press(['ctrl', "origine"])
    keyboard.press(['ctrl', "home"])
    keyboard.release("ctrl") # clean ctrl key