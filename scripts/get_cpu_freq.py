# -*- coding: iso-8859-1 -*-

"""
import psutil
retVal = psutil.cpu_freq()
print(retVal)
    
class SYSTEM_POWER_INFORMATION(Structure):
    _fields_ = [
            ("MaxIdlenessAllowed", c_ulong),
            ("Idleness", c_ulong),
            ("TimeRemaining", c_ulong),
            ("CoolingMode", c_ubyte)
            ]

call_nt_power_information = windll.powrprof.CallNtPowerInformation
call_nt_power_information.restype = c_uint

def get_idle_timer():
    # Get the time remaining before idle
    info = SYSTEM_POWER_INFORMATION()
    r = call_nt_power_information(SystemPowerInformation, None, 0, pointer(info), sizeof(SYSTEM_POWER_INFORMATION))
    if r != 0:
        raise Exception("Call to CallNtPowerInformation failed with code " + r)

    return info.TimeRemaining
    """
import ctypes

powprooflib = ctypes.cdll.LoadLibrary("powrprof")

SystemBatteryState = 5  # POWER_INFORMATION_LEVEL enum

class SYSTEM_BATTERY_STATE(ctypes.Structure):
    _fields_ = [
                ("AcOnLine", ctypes.c_bool),
                ("BatteryPresent", ctypes.c_bool),
                ("Charging", ctypes.c_bool),
                ("Discharging", ctypes.c_bool),
                ("Spare1", ctypes.c_bool * 4),
                ("MaxCapacity", ctypes.c_long),
                ("RemainingCapacity", ctypes.c_long),
                ("Rate", ctypes.c_long),
                ("EstimatedTime", ctypes.c_long),
                ("DefaultAlert1", ctypes.c_long),
                ("DefaultAlert2", ctypes.c_long),
                ]


sb = SYSTEM_BATTERY_STATE(0)
addr = ctypes.addressof(sb)
size = ctypes.sizeof(sb)
print("addr: 0x%x, size: %d" % (addr,size) )
#~ retval = powprooflib.CallNtPowerInformation(SystemBatteryState, None, 0, addr, size)
#~ powprooflib.CallNtPowerInformation.argtypes = [int,int]
retval = powprooflib.CallNtPowerInformation(SystemBatteryState, None, 0, addr, size)
assert retval == 0  # debe devolver 0 si no hay error
print( "AcOnLine:", sb.AcOnLine )
print( "Charging:", sb.Charging )
print( "Discharging:", sb.Discharging )
print( "Capacity:", sb.MaxCapacity, "mWh max", sb.RemainingCapacity, "mWh remaining", )
print( sb.RemainingCapacity*100/sb.MaxCapacity, "%" )
print( "Rate:", sb.Rate / 1000.0, "W" )
print( "Estimated Time:", sb.EstimatedTime / 3600, "h", sb.EstimatedTime / 60 % 60, "min" )

