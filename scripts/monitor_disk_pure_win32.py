import ctypes
from ctypes import wintypes
import shutil


# =========================================================
# CONFIGURATION
# =========================================================

REFRESH_MS = 5000

RIGHT_MARGIN = 270
TOP_MARGIN = -2

WIDTH = 140
HEIGHT = 16

CORNER_RADIUS = 6

# 204 / 255 = 80 %
WINDOW_ALPHA = 204

# COLORREF = 0x00BBGGRR
BG_COLOR = 0x00404040       # gris
TEXT_COLOR = 0x00FFFFFF     # blanc


# =========================================================
# DLL WINDOWS
# =========================================================

user32 = ctypes.WinDLL("user32", use_last_error=True)
gdi32 = ctypes.WinDLL("gdi32", use_last_error=True)
kernel32 = ctypes.WinDLL("kernel32", use_last_error=True)


# =========================================================
# TYPES WIN32
# =========================================================

HANDLE = ctypes.c_void_p

HWND = HANDLE
HINSTANCE = HANDLE
HICON = HANDLE
HCURSOR = HANDLE
HBRUSH = HANDLE
HGDIOBJ = HANDLE
HRGN = HANDLE
HMENU = HANDLE

LRESULT = ctypes.c_ssize_t
COLORREF = ctypes.c_uint32
UINT_PTR = ctypes.c_size_t


# =========================================================
# CONSTANTES WIN32
# =========================================================

WS_POPUP = 0x80000000

WS_EX_TOPMOST = 0x00000008
WS_EX_TOOLWINDOW = 0x00000080
WS_EX_LAYERED = 0x00080000

SW_SHOWNOACTIVATE = 4

WM_DESTROY = 0x0002
WM_PAINT = 0x000F
WM_ERASEBKGND = 0x0014
WM_TIMER = 0x0113

LWA_ALPHA = 0x00000002

TRANSPARENT = 1

DT_LEFT = 0x00000000
DT_VCENTER = 0x00000004
DT_SINGLELINE = 0x00000020
DT_NOPREFIX = 0x00000800

SM_CXSCREEN = 0


# =========================================================
# STRUCTURES
# =========================================================

class WNDCLASSW(ctypes.Structure):
    _fields_ = [
        ("style", wintypes.UINT),
        ("lpfnWndProc", ctypes.c_void_p),
        ("cbClsExtra", ctypes.c_int),
        ("cbWndExtra", ctypes.c_int),
        ("hInstance", HINSTANCE),
        ("hIcon", HICON),
        ("hCursor", HCURSOR),
        ("hbrBackground", HBRUSH),
        ("lpszMenuName", wintypes.LPCWSTR),
        ("lpszClassName", wintypes.LPCWSTR),
    ]


class POINT(ctypes.Structure):
    _fields_ = [
        ("x", wintypes.LONG),
        ("y", wintypes.LONG),
    ]


class MSG(ctypes.Structure):
    _fields_ = [
        ("hwnd", HWND),
        ("message", wintypes.UINT),
        ("wParam", wintypes.WPARAM),
        ("lParam", wintypes.LPARAM),
        ("time", wintypes.DWORD),
        ("pt", POINT),
        ("lPrivate", wintypes.DWORD),
    ]


class PAINTSTRUCT(ctypes.Structure):
    _fields_ = [
        ("hdc", HANDLE),
        ("fErase", wintypes.BOOL),
        ("rcPaint", wintypes.RECT),
        ("fRestore", wintypes.BOOL),
        ("fIncUpdate", wintypes.BOOL),
        ("rgbReserved", ctypes.c_ubyte * 32),
    ]


# =========================================================
# CALLBACK WINDOWPROC
# =========================================================

WNDPROC = ctypes.WINFUNCTYPE(
    LRESULT,
    HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM
)


# =========================================================
# USER32 - PROTOTYPES
# =========================================================

user32.DefWindowProcW.argtypes = [
    HWND,
    wintypes.UINT,
    wintypes.WPARAM,
    wintypes.LPARAM
]
user32.DefWindowProcW.restype = LRESULT


user32.RegisterClassW.argtypes = [
    ctypes.POINTER(WNDCLASSW)
]
user32.RegisterClassW.restype = wintypes.ATOM


user32.CreateWindowExW.argtypes = [
    wintypes.DWORD,
    wintypes.LPCWSTR,
    wintypes.LPCWSTR,
    wintypes.DWORD,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    HWND,
    HMENU,
    HINSTANCE,
    HANDLE
]
user32.CreateWindowExW.restype = HWND


user32.ShowWindow.argtypes = [
    HWND,
    ctypes.c_int
]
user32.ShowWindow.restype = wintypes.BOOL


user32.UpdateWindow.argtypes = [
    HWND
]
user32.UpdateWindow.restype = wintypes.BOOL


user32.GetSystemMetrics.argtypes = [
    ctypes.c_int
]
user32.GetSystemMetrics.restype = ctypes.c_int


user32.SetLayeredWindowAttributes.argtypes = [
    HWND,
    COLORREF,
    wintypes.BYTE,
    wintypes.DWORD
]
user32.SetLayeredWindowAttributes.restype = wintypes.BOOL


user32.SetWindowRgn.argtypes = [
    HWND,
    HRGN,
    wintypes.BOOL
]
user32.SetWindowRgn.restype = ctypes.c_int


user32.SetTimer.argtypes = [
    HWND,
    UINT_PTR,
    wintypes.UINT,
    HANDLE
]
user32.SetTimer.restype = UINT_PTR


user32.KillTimer.argtypes = [
    HWND,
    UINT_PTR
]
user32.KillTimer.restype = wintypes.BOOL


user32.InvalidateRect.argtypes = [
    HWND,
    ctypes.POINTER(wintypes.RECT),
    wintypes.BOOL
]
user32.InvalidateRect.restype = wintypes.BOOL


user32.GetClientRect.argtypes = [
    HWND,
    ctypes.POINTER(wintypes.RECT)
]
user32.GetClientRect.restype = wintypes.BOOL


user32.BeginPaint.argtypes = [
    HWND,
    ctypes.POINTER(PAINTSTRUCT)
]
user32.BeginPaint.restype = HANDLE


user32.EndPaint.argtypes = [
    HWND,
    ctypes.POINTER(PAINTSTRUCT)
]
user32.EndPaint.restype = wintypes.BOOL


user32.FillRect.argtypes = [
    HANDLE,
    ctypes.POINTER(wintypes.RECT),
    HBRUSH
]
user32.FillRect.restype = ctypes.c_int


user32.DrawTextW.argtypes = [
    HANDLE,
    wintypes.LPCWSTR,
    ctypes.c_int,
    ctypes.POINTER(wintypes.RECT),
    wintypes.UINT
]
user32.DrawTextW.restype = ctypes.c_int


user32.PostQuitMessage.argtypes = [
    ctypes.c_int
]


user32.GetMessageW.argtypes = [
    ctypes.POINTER(MSG),
    HWND,
    wintypes.UINT,
    wintypes.UINT
]
user32.GetMessageW.restype = wintypes.BOOL


user32.TranslateMessage.argtypes = [
    ctypes.POINTER(MSG)
]


user32.DispatchMessageW.argtypes = [
    ctypes.POINTER(MSG)
]


# =========================================================
# GDI32 - PROTOTYPES
# =========================================================

gdi32.CreateRoundRectRgn.argtypes = [
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int,
    ctypes.c_int
]
gdi32.CreateRoundRectRgn.restype = HRGN


gdi32.CreateSolidBrush.argtypes = [
    COLORREF
]
gdi32.CreateSolidBrush.restype = HBRUSH


gdi32.CreateFontW.argtypes = [
    ctypes.c_int,       # height
    ctypes.c_int,       # width
    ctypes.c_int,       # escapement
    ctypes.c_int,       # orientation
    ctypes.c_int,       # weight
    wintypes.BOOL,      # italic
    wintypes.BOOL,      # underline
    wintypes.BOOL,      # strikeout
    wintypes.UINT,      # charset
    wintypes.UINT,      # out precision
    wintypes.UINT,      # clip precision
    wintypes.UINT,      # quality
    wintypes.UINT,      # pitch/family
    wintypes.LPCWSTR    # face
]
gdi32.CreateFontW.restype = HGDIOBJ


gdi32.SelectObject.argtypes = [
    HANDLE,
    HGDIOBJ
]
gdi32.SelectObject.restype = HGDIOBJ


gdi32.SetTextColor.argtypes = [
    HANDLE,
    COLORREF
]
gdi32.SetTextColor.restype = COLORREF


gdi32.SetBkMode.argtypes = [
    HANDLE,
    ctypes.c_int
]
gdi32.SetBkMode.restype = ctypes.c_int


gdi32.DeleteObject.argtypes = [
    HGDIOBJ
]
gdi32.DeleteObject.restype = wintypes.BOOL


# =========================================================
# VARIABLES GLOBALES
# =========================================================

current_text = "C: ?    D: ?"

font = None


# =========================================================
# DISQUE
# =========================================================

def get_free_space(drive):

    try:
        free = shutil.disk_usage(drive).free

        return free / (1024 ** 3)

    except Exception:
        return None


def update_text():

    global current_text

    c = get_free_space("C:\\")
    d = get_free_space("D:\\")

    if c is not None:
        c_text = f"C: {c:.1f} Go"
    else:
        c_text = "C: ?"

    if d is not None:
        d_text = f"D: {d:.1f} Go"
    else:
        d_text = "D: ?"

    current_text = f"    {c_text}    {d_text}"


# =========================================================
# COINS ARRONDIS
# =========================================================

def make_rounded(hwnd, width, height, radius=10):

    region = gdi32.CreateRoundRectRgn(
        0,
        0,
        width + 1,
        height + 1,
        radius * 2,
        radius * 2
    )

    if not region:
        raise ctypes.WinError(
            ctypes.get_last_error()
        )

    result = user32.SetWindowRgn(
        hwnd,
        region,
        True
    )

    if not result:

        # Si SetWindowRgn échoue,
        # on doit libérer la région.
        gdi32.DeleteObject(region)

        raise ctypes.WinError(
            ctypes.get_last_error()
        )

    # IMPORTANT :
    # Si SetWindowRgn réussit, Windows prend
    # possession de la région.
    #
    # Ne PAS faire DeleteObject(region) ici.


# =========================================================
# WINDOW PROCEDURE
# =========================================================

@WNDPROC
def wnd_proc(hwnd, msg, wparam, lparam):

    global font

    # -----------------------------------------------------
    # PAINT
    # -----------------------------------------------------

    if msg == WM_PAINT:

        ps = PAINTSTRUCT()

        hdc = user32.BeginPaint(
            hwnd,
            ctypes.byref(ps)
        )

        rect = wintypes.RECT()

        user32.GetClientRect(
            hwnd,
            ctypes.byref(rect)
        )

        # -------------------------------------------------
        # Fond gris
        # -------------------------------------------------

        brush = gdi32.CreateSolidBrush(
            BG_COLOR
        )

        user32.FillRect(
            hdc,
            ctypes.byref(rect),
            brush
        )

        gdi32.DeleteObject(brush)

        # -------------------------------------------------
        # Police
        # -------------------------------------------------

        if not font:

            font = gdi32.CreateFontW(
                -11,           # hauteur
                0,             # largeur
                0,             # angle
                0,             # orientation
                400,           # poids
                False,         # italic
                False,         # underline
                False,         # strikeout
                1,             # DEFAULT_CHARSET
                0,             # OUT_DEFAULT_PRECIS
                0,             # CLIP_DEFAULT_PRECIS
                5,             # CLEARTYPE_QUALITY
                0,             # DEFAULT_PITCH
                "Segoe UI"
            )

        old_font = gdi32.SelectObject(
            hdc,
            font
        )

        # -------------------------------------------------
        # Texte
        # -------------------------------------------------

        gdi32.SetTextColor(
            hdc,
            TEXT_COLOR
        )

        gdi32.SetBkMode(
            hdc,
            TRANSPARENT
        )

        text_rect = wintypes.RECT(
            5,
            0,
            rect.right - 5,
            rect.bottom
        )

        user32.DrawTextW(
            hdc,
            current_text,
            -1,
            ctypes.byref(text_rect),
            DT_LEFT |
            DT_VCENTER |
            DT_SINGLELINE |
            DT_NOPREFIX
        )

        # -------------------------------------------------
        # Restaurer ancienne police
        # -------------------------------------------------

        gdi32.SelectObject(
            hdc,
            old_font
        )

        user32.EndPaint(
            hwnd,
            ctypes.byref(ps)
        )

        return 0

    # -----------------------------------------------------
    # TIMER
    # -----------------------------------------------------

    if msg == WM_TIMER:

        update_text()

        user32.InvalidateRect(
            hwnd,
            None,
            True
        )

        return 0

    # -----------------------------------------------------
    # Pas d'effacement du fond
    # -----------------------------------------------------

    if msg == WM_ERASEBKGND:
        return 1

    # -----------------------------------------------------
    # DESTROY
    # -----------------------------------------------------

    if msg == WM_DESTROY:

        user32.KillTimer(
            hwnd,
            1
        )

        if font:

            gdi32.DeleteObject(
                font
            )

            font = None

        user32.PostQuitMessage(0)

        return 0

    return user32.DefWindowProcW(
        hwnd,
        msg,
        wparam,
        lparam
    )


# =========================================================
# MAIN
# =========================================================

def main():

    # -----------------------------------------------------
    # Instance du programme
    # -----------------------------------------------------

    hinstance = kernel32.GetModuleHandleW(
        None
    )

    class_name = "DiskSpaceMonitorWin32"


    # -----------------------------------------------------
    # Classe fenêtre
    # -----------------------------------------------------

    wc = WNDCLASSW()

    wc.style = 0

    wc.lpfnWndProc = ctypes.cast(
        wnd_proc,
        ctypes.c_void_p
    )

    wc.cbClsExtra = 0
    wc.cbWndExtra = 0

    wc.hInstance = hinstance

    wc.hIcon = None
    wc.hCursor = None
    wc.hbrBackground = None

    wc.lpszMenuName = None
    wc.lpszClassName = class_name


    # -----------------------------------------------------
    # Enregistrer classe
    # -----------------------------------------------------

    atom = user32.RegisterClassW(
        ctypes.byref(wc)
    )

    if not atom:

        error = ctypes.get_last_error()

        # ERROR_CLASS_ALREADY_EXISTS
        if error != 1410:

            raise ctypes.WinError(
                error
            )


    # -----------------------------------------------------
    # Position haut-droite
    # -----------------------------------------------------

    screen_width = user32.GetSystemMetrics(
        SM_CXSCREEN
    )

    x = (
        screen_width
        - WIDTH
        - RIGHT_MARGIN
    )

    y = TOP_MARGIN


    # -----------------------------------------------------
    # Création fenêtre
    # -----------------------------------------------------

    hwnd = user32.CreateWindowExW(

        WS_EX_TOPMOST |
        WS_EX_TOOLWINDOW |
        WS_EX_LAYERED,

        class_name,

        "Disk Space",

        WS_POPUP,

        x,
        y,

        WIDTH,
        HEIGHT,

        None,
        None,

        hinstance,

        None
    )

    if not hwnd:

        raise ctypes.WinError(
            ctypes.get_last_error()
        )


    # -----------------------------------------------------
    # Transparence
    # -----------------------------------------------------

    result = user32.SetLayeredWindowAttributes(
        hwnd,
        0,
        WINDOW_ALPHA,
        LWA_ALPHA
    )

    if not result:

        raise ctypes.WinError(
            ctypes.get_last_error()
        )


    # -----------------------------------------------------
    # Coins arrondis
    # -----------------------------------------------------

    make_rounded(
        hwnd,
        WIDTH,
        HEIGHT,
        CORNER_RADIUS
    )


    # -----------------------------------------------------
    # Première lecture
    # -----------------------------------------------------

    update_text()


    # -----------------------------------------------------
    # Timer 5 secondes
    # -----------------------------------------------------

    timer = user32.SetTimer(
        hwnd,
        1,
        REFRESH_MS,
        None
    )

    if not timer:

        raise ctypes.WinError(
            ctypes.get_last_error()
        )


    # -----------------------------------------------------
    # Afficher
    # -----------------------------------------------------

    user32.ShowWindow(
        hwnd,
        SW_SHOWNOACTIVATE
    )

    user32.UpdateWindow(
        hwnd
    )


    # -----------------------------------------------------
    # Message loop
    # -----------------------------------------------------

    msg = MSG()

    while user32.GetMessageW(
        ctypes.byref(msg),
        None,
        0,
        0
    ) > 0:

        user32.TranslateMessage(
            ctypes.byref(msg)
        )

        user32.DispatchMessageW(
            ctypes.byref(msg)
        )


# =========================================================
# START
# =========================================================

if __name__ == "__main__":
    main()
