import win32com.client, time, os

WIA_COM = "WIA.CommonDialog"

WIA_DEVICE_UNSPECIFIED = 0
WIA_DEVICE_CAMERA = 2

WIA_INTENT_UNSPECIFIED = 0

WIA_BIAS_MIN_SIZE = 65536
WIA_BIAS_MAX_QUALITY = 65536

WIA_IMG_FORMAT_PNG = "{B96B3CAF-0728-11D3-9D7B-0000F81EF32E}"

WIA_COMMAND_TAKE_PICTURE="{AF933CAC-ACAD-11D2-A093-00C04F72DC3C}"

def acquire_image_wia():
    wia = win32com.client.Dispatch(WIA_COM) # wia is a CommonDialog object
    dev = wia.ShowSelectDevice()
    for command in dev.Commands:
        if command.CommandID==WIA_COMMAND_TAKE_PICTURE:
            foo=dev.ExecuteCommand(WIA_COMMAND_TAKE_PICTURE)

    item = dev.Items[0]
    for p in item.Properties:
        if not p.IsReadOnly:
            print( "%s: %s" % (p.Name,  p.Value) )
            # all those are working !
            #~ if p.Name == "Vertical Extent":
                #~ p.value = 2000 #change len to scan
            if p.Name == "Bits Per Pixel":
                p.value = 8 #gray
            if p.Name == "Bits Per Pixel":
                p.value = 24 #RGB
            #~ if p.Name == "Horizontal Resolution":
                #~ p.value = 600
            #~ if p.Name == "Vertical Resolution":
                #~ p.value = 600
    #~ i=1
    #~ for item in dev.Items:
        #~ if i==dev.Items.Count:
            #~ image=item.Transfer(WIA_IMG_FORMAT_PNG)
            #~ break
        #~ i=i+1
        
    image=item.Transfer(WIA_IMG_FORMAT_PNG)

    fname = 'wia-test.png'
    if os.path.exists(fname):
        os.remove(fname)
    image.SaveFile(fname)

os.chdir("c:/tmp")
while 1:
    try:
        acquire_image_wia()
        break
    except BaseException as err:
        print("err: %s" % err)