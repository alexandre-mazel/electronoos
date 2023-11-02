import scapy
import scapy.all
#~ a = scapy.all.sniff(count=10)
#~ a.nsummary()

ARP = scapy.all.ARP
IP = scapy.all.IP
TCP = scapy.all.TCP
UDP = scapy.all.UDP
Raw = scapy.all.Raw
#~ A = scapy.all.A # don't exist

aDns = {
    "192.168.0.46" : "mstab7",
    "216.58.214.170" : "Google",
    "78.199.86.189" : "MaFreebox",
    "212.27.40.240" : "Free SAS",
}

"""
https://stackoverflow.com/questions/74721184/decoding-https-traffic-with-scapy

from scapy.all import *
from time import sleep
from IPython import embed
myiface = 'lo'
mycount = 30
response_time_delta = 0.0
NSS_SECRETS_LOG = "secrets.log"
SERVER_HOST = "127.0.0.1"
SERVER_PORT = 8443

def analyze_https_sniffed_traffic():
    # sniff traffic for mycount packets
    myfilter = ""
    myprn = lambda x:x.summary()
    sniff_out = sniff(filter=myfilter,prn=myprn,count=mycount,iface=myiface)

    # iterate through the sniffed packets to report on contents
    for idx,s in enumerate(sniff_out):

        print("===\npacket %d\n%s" % (idx,s.summary()))
        # if we can convert to a TLS packet, print out TLS summary
        if s.haslayer('IP') and hasattr(s,'load'):
            tls_r = TLS(s.load)
            print(tls_r.summary())
            # if this is TLS application data, do a complete show
            if tls_r.type == 23:
                print(tls_r.show())
            #embed()
    return

def send_https_request_and_analyze():
    import http.client, ssl
    # start another thread that sniffs traffic and analyzes their contents
    t = threading.Thread(target=analyze_https_sniffed_traffic)
    t.start()

    # use python requests to make a HTTPS query to a local server
    # put SSLKEYLOGFILE into the environment so I can decode captured TLS traffic
    import os; os.environ["SSLKEYLOGFILE"] = NSS_SECRETS_LOG
    time.sleep(3)
    # unverified context: using self signed cert, make requests happy
    conn = http.client.HTTPSConnection(SERVER_HOST, SERVER_PORT, context=ssl._create_unverified_context())
    conn.request('GET', '/')
    r = conn.getresponse()
    print("response: %s" % r.read())

    # wait for the sniff thread to finish up
    t.join()

load_layer("tls")
# conf commands from https://github.com/secdev/scapy/pull/3374
conf.tls_session_enable = True
conf.tls_nss_filename = NSS_SECRETS_LOG
print("scapy version: %s" % scapy.__version__)
print("conf contents:\n%s" % conf)
send_https_request_and_analyze()
"""

def toHostname(ip):
    try:
        return aDns[ip]
    except KeyError as err:
        pass
    return ip

def monitor_callback(pkt):
    bVerbose = 1
    bShowARP = 1
    
    #~ return pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")
    #~ if scapy.all.ARP in pkt and pkt[scapy.all.ARP].op in (1,2): #who-has or is-at
    
    #~ print(dir(pkt))
    if bVerbose: print("DBG: pkt: %s" % str(pkt))
    #~ print("DBG: pkt[scapy.all.ARP]: %s" % str(pkt[scapy.all.ARP]))
    if ARP in pkt:
        #~ if bShowARP: print("ARP")
        if bShowARP:  print(pkt.sprintf("recv: ARP: %ARP.hwsrc% %ARP.psrc% => %ARP.pdst%"))
            
    if IP in pkt: 
        #~ print("DBG: IP: pkt: %s" % str(pkt))
        #~ print(pkt[IP])
        #~ s = pkt.sprintf("recv: IP: %IP.src%:%IP.port% => %IP.dst%")
        #~ print(s)
        ip_src = toHostname(pkt[IP].src)
        ip_dst = toHostname(pkt[IP].dst)
        port_src = ""
        port_dst = ""
        if TCP in pkt:
            port_src = pkt[TCP].sport
            port_dst = pkt[TCP].dport
        elif UDP in pkt:
            port_src = pkt[UDP].sport
            port_dst = pkt[UDP].dport
            
        print("%s:%s > %s:%s" % (ip_src,port_src,ip_dst,port_dst))
        
        methods=[b'GET',b'POST',b'HEAD',b'PUT',b'DELETE',b'CONNECT',b'OPTIONS',b'TRACE']
        if pkt.haslayer(TCP):#Checks for TCP protocol
            if pkt.dport == 80:#Checks for http port 80
                if pkt.haslayer(Raw):#Checks if packet has payload
                    r = pkt[0][Raw].load
                    for meth in methods:#Checks if any of the http methods are present in load, if there are it prints to screen
                        #~ print("meth: %s" % str(meth))
                        #~ print("r: %s" % str(r))
                        if meth in r:
                            print("meth: %s found in\n%s" % (meth,str(r)))
                else:
                    i = 0
                    while 1:
                        layer = pkt.getlayer(i)
                        if layer == None:
                            break
                        print("layer: %d:%s" % (i,str(layer)))
                        i += 1
                    
                if 0:
                    if pkt.haslayer(A):#Checks if packet has payload
                        r = pkt[0][A].load
                        for meth in methods:#Checks if any of the http methods are present in load, if there are it prints to screen
                            #~ print("test:  meth: %s" % str(meth))
                            #~ print("test: : %s" % str(r))
                            if meth in r:
                                print("meth: %s found in\n%s" % (meth,str(r)))
        
    return "" # pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")

def startPacketAnalyse():
    #~ scapy.all.sniff(prn=monitor_callback, filter="arp", store=0)
    scapy.all.sniff(prn=monitor_callback, filter="", store=0) # filter="ip" pour avoir que ip
    
    
startPacketAnalyse()