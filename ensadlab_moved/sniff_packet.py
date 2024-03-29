import scapy
import scapy.all
import base64
#~ from scapy_http import http
#~ import scapy_http.http
from scapy.layers import http

import sys
sys.path.append("../alex_pytools")
import nettools

bDeactivateToHostname = 1
bDeactivateToHostname = 0



#~ a = scapy.all.sniff(count=10)
#~ a.nsummary()

ARP = scapy.all.ARP
IP = scapy.all.IP
IPV6 = scapy.all.IPv6
TCP = scapy.all.TCP
UDP = scapy.all.UDP
DNS = scapy.all.DNS
Raw = scapy.all.Raw
#~ A = scapy.all.A # don't exist

aDns = {
    "192.168.0.46" : "mstab7",
    "216.58.214.170" : "Google",
    "78.199.86.189" : "MaFreebox",
    "212.27.40.240" : "Free SAS",
}



def cacheDns():
    preloadCacheDns()
    ip = nettools.getLocalIP()
    aDns[ip] = "Me"
    ip6 = nettools.getLocalIP6()
    aDns[ip6] = "Me6"
    printCacheDns()

        
def printCacheDns():
    print("")
    print("DBG: cacheDns: aDns: ")
    for k,v in sorted(aDns.items()):
        print("%s => %s" % (k,v))    

    
def addToCacheDns(s):
    """
    add an ip or a domain to CacheDns
    """
    print( "DBG: addToCacheDns: site: %s" % s )
    ips = nettools.getIPx(s)
    if ips != False and ips[0] != s: # ip => [ip]
        print( "DBG:    addToCacheDns: ips: %s (len:%d)" % ( ips, len(ips) ) )
        for ip in ips:
            aDns[ip] = s
        # add ipv6 version
        ipv6 = nettools.getIPV6Sub(s)
        for ip in ipv6:
            aDns[ip] = s
    else: # (1)
        domain = nettools.getHost(s)
        if domain != False:
            print( "DBG:    addToCacheDns: domain: %s" % domain )
            s = nettools.reduceIPV6ToDomainSubPart(s)
            domain = nettools.reduceDomainToMasterDomain(domain)
            aDns[s] = domain
                
        """
        (1):
            # si on ne met pas le else, il y a une piste, interessante: savoir quel site sont sur les memes reseau
            google.com => par21s22-in-x0e.1e100.net
            obo-world.com => cap33-1_migr-78-199-86-189.fbx.proxad.net
            youtube.com => par21s20-in-x0e.1e100.net
        """    

def preloadCacheDns():
    sites = [
                    "youtube.com",
                    "google.com",
                    "obo-world.com",
                    "stackoverflow.com",
                    
                    #~ "2a00:1450:4007:80a::200a",
                    #~ "2a00:1450:4007:810::200a",
                    #~ "2a00:1450:4007:81a::200a",
                    #~ "2a00:1450:4007:80c::200a",
                    #~ "2a00:1450:4007:80d::200a",
                    "2a02:26f0:2b00:12::5f64",
                    "2a02:26f0:2b00:12::5f64:5545",
                    "2a01:e34:ec75:6bd0:f8ff:fa45:f8ae:4086",
                    "2a02:26f0:2b00",
                    "2620:11a:a01f::1b",
            ]
    for s in sites:
        addToCacheDns(s)


def outputAllFields(o,bLimitToInteresting=1):
    out = ""
    fields = dir(o)
    for field in fields:
        try:
            f = getattr(o,field)
            if callable( f ):
                #~ v = f()
                if not bLimitToInteresting: out += "field %s type: function\n" % field
            else:
                v = f
                if not bLimitToInteresting or v != None:
                    out += "field %s (type:%s): %s\n" % (field, type(v),str(v) )
        except AttributeError:
            out += "field %s attribute error\n"% field
    return out
        

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

"""
import scapy.all as scapy
from scapy_http import http

def sniff(interface):
    scapy.sniff(iface=interface, store=False, prn=process_packets)

def process_packets(packet):
    if packet.haslayer(http.HTTPRequest):
        url = packet[http.HTTPRequest].Host + packet[http.HTTPRequest].Path
        print('URL: ' + url.decode())
        if packet.haslayer(scapy.Raw):
            load = packet[scapy.Raw].load
            for i in words:
                if i in str(load):
                    print('Load: ' + load.decode())
                    break



words = ["password", "user", "username", "login", "pass", "Username", "Password", "User", "Email"]
sniff("WiFi 2")
"""

def http_header(packet):
        http_packet=str(packet)
        if http_packet.find('GET'):
                return GET_print(packet)

def GET_print(packet1):
    ret = "***************************************GET PACKET****************************************************\n"
    ret += "\n".join(packet1.sprintf("{Raw:%Raw.load%}\n").split(r"\r\n"))
    ret += "*****************************************************************************************************\n"
    return ret
    
"""
should print sth like (but not for me):

***************************************GET PACKET****************************************************
'GET /projects/scapy/doc/usage.html HTTP/1.1
Host: www.secdev.org
Connection: keep-alive
Cache-Control: max-age=0
Accept: text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8
User-Agent: Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.65 Safari/537.36
Referer: https://www.google.co.uk/
Accept-Encoding: gzip, deflate, sdch
Accept-Language: en-GB,en;q=0.8,en-US;q=0.6
If-None-Match: "28c84-48498d5654df67640-gzip"
If-Modified-Since: Mon, 19 Apr 2010 15:44:17 GMT

'
*
"""

def arp_display(pkt):
    if pkt[ARP].op == 1: #who-has (request)
        return f"Request: {pkt[ARP].psrc} is asking about {pkt[ARP].pdst}"
    if pkt[ARP].op == 2: #is-at (response)
        return f"*Response: {pkt[ARP].hwsrc} has address {pkt[ARP].psrc}"

#~ sniff(iface='eth0', prn=http_header, filter="tcp port 80")

def toHostname(ip):
    if bDeactivateToHostname: return ip
    try:
        return aDns[nettools.reduceIPV6ToDomainSubPart(ip)]
    except KeyError as err:
        print("WRN: toHostname: ip '%s' not found, adding to the cache..." % ip)
        addToCacheDns(ip)
        printCacheDns()
        try:
            return aDns[nettools.reduceIPV6ToDomainSubPart(ip)]
        except KeyError as err:
            print("WRN: toHostname: ip '%s' is an unknown domain ip (reduced: %s)." % (ip,nettools.reduceIPV6ToDomainSubPart(ip)) )
            aDns[nettools.reduceIPV6ToDomainSubPart(ip)] = nettools.reduceIPV6ToDomainSubPart(ip) # to gain time next time, we add them to the cache
    return ip


def monitor_callback(pkt):
    bVerbose = 1
    bShowARP = 1
    bShowDNS = 1
    
    #~ return pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")
    #~ if scapy.all.ARP in pkt and pkt[scapy.all.ARP].op in (1,2): #who-has or is-at
    
    #~ print(dir(pkt))
    print("*"*40)
    if bVerbose: print("DBG: pkt: '%s' len: %s time: %.2f" % (str(pkt),len(pkt),pkt.time))
    #~ print("DBG: pkt[scapy.all.ARP]: %s" % str(pkt[scapy.all.ARP]))
    if ARP in pkt:
        #~ if bShowARP: print("ARP")
        if bShowARP:  print(pkt.sprintf("recv: ARP: %ARP.hwsrc% %ARP.psrc% => %ARP.pdst%"))
        stats.addVolArp(len(pkt))
        
    if DNS in pkt:
        if bShowDNS: print("DNS")
        #~ if bShowDNS:  print(pkt.sprintf("recv: ARP: %ARP.hwsrc% %ARP.psrc% => %ARP.pdst%"))
        #~ decoded_data = base64.b64decode(str(pkt[DNS].an.rdata)) 
        #~ print(decoded_data)
        
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
            
        print("INF: IP: %s:%s > %s:%s" % (ip_src,port_src,ip_dst,port_dst))
        
        stats.addSrc(ip_src,len(pkt))
        stats.addDst(ip_dst,len(pkt))
        
        methods=[b'GET',b'POST',b'HEAD',b'PUT',b'DELETE',b'CONNECT',b'OPTIONS',b'TRACE']
        words = ["password", "user", "username", "login", "pass", "Username", "Password", "User", "Email"]
        if pkt.haslayer(TCP): #Checks for TCP protocol
            print("DBG: tcp time (at senders): " + str(pkt[TCP].options))
            print("DBG: tcp time (at senders): " + str(pkt[TCP].sent_time))
            print("DBG: tcp time (at senders): " + str(dir(pkt[TCP])))
            print("DBG: tcp time (at senders): " + outputAllFields(pkt[TCP]))
            print("DBG: tcp time (at senders): %.4f (diff to send:%.4f)" % (pkt[TCP].time,pkt.time-pkt[TCP].time))
            #~ print("DBG: tcp time (at senders): " + str(pkt[TCP].keys()))
            if port_src == 80 or port_dst == 80: #Checks for http port 80
                stats.addVolHttp(len(pkt))
                if pkt.haslayer(http.HTTPRequest):
                    http_layer = pkt.getlayer(http.HTTPRequest)
                    print("DBG: keys: " + str(http_layer.fields.keys()))
                    print("DBG: " + str(http_layer.fields))

                    url = http_layer.fields['Host'] + http_layer.fields['Path']
                    print("HTTP url: %s" % url)
                if pkt.haslayer(Raw):#Checks if packet has payload
                    print("DBG: raw")
                    r = pkt[0][Raw].load
                    print("DBG: raw load: %s" % str(r)) #r.decode()
                    #~ decoded_data = base64.b64decode(r)
                    #~ print(decoded_data)
                    for meth in methods:#Checks if any of the http methods are present in load, if there are it prints to screen
                        #~ print("meth: %s" % str(meth))
                        #~ print("r: %s" % str(r))
                        if meth in r:
                            print("meth: %s found in\n%s" % (meth,str(r)))
                        #~ s = http_header(pkt)
                        #~ print(ascii(s
                    scapy.all.hexdump(pkt)
                else:
                    print("DBG: no raw")
                    i = 0
                    while 1:
                        layer = pkt.getlayer(i)
                        if layer == None:
                            break
                        print("layer %d: %s" % (i,str(layer)))
                        i += 1
                    #~ print(str(pkt)[:(pkt[IP].ihl * 4)])
                    print(pkt.show(dump=True))
                    print(dir(pkt[TCP]))
                    #~ decoded_data = base64.b64decode(str(pkt[TCP].original)) 
                    scapy.all.hexdump(pkt)
                    
                if 0:
                    if pkt.haslayer(A):#Checks if packet has payload
                        r = pkt[0][A].load
                        for meth in methods:#Checks if any of the http methods are present in load, if there are it prints to screen
                            #~ print("test:  meth: %s" % str(meth))
                            #~ print("test: : %s" % str(r))
                            if meth in r:
                                print("meth: %s found in\n%s" % (meth,str(r)))
            # if port_src == 80 - end
            if port_src == 443 or port_dst == 443:
                print("https!")
                stats.addVolHttps(len(pkt))
                if pkt.haslayer(http.HTTPRequest):
                    http_layer = pkt.getlayer(http.HTTPRequest)
                    print("DBG: keys: " + str(http_layer.fields.keys()))
                    print("DBG: " + str(http_layer.fields))

                    url = http_layer.fields['Host'] + http_layer.fields['Path']
                    print("HTTP url: %s" % url)
        # layer tcp - end
        
        if pkt.haslayer(UDP):
            stats.addVolUdp(len(pkt))
        # layer udp - end
        
    # ip in pkt
    
    if IPV6 in pkt: 
        print("DBG: IPV6: pkt: %s" % str(pkt))
        ip_src = toHostname(pkt[IPV6].src)
        ip_dst = toHostname(pkt[IPV6].dst)
        print("DBG: IPv6: %s > %s" % (ip_src,ip_dst))
        
        stats.addSrc(ip_src,len(pkt))
        stats.addDst(ip_dst,len(pkt))

        #~ stats.addVolArp(len(pkt))
        if TCP in pkt:
            port_src = pkt[TCP].sport
            port_dst = pkt[TCP].dport
        elif UDP in pkt:
            port_src = pkt[UDP].sport
            port_dst = pkt[UDP].dport
        else:
            print("no port?")
            port_src = -1
            port_dst = -1
        if port_src == 443 or port_dst == 443:
            print("https!")
            stats.addVolHttps(len(pkt))
            if pkt.haslayer(http.HTTPRequest):
                http_layer = pkt.getlayer(http.HTTPRequest)
                print("DBG: keys: " + str(http_layer.fields.keys()))
                print("DBG: " + str(http_layer.fields))

                url = http_layer.fields['Host'] + http_layer.fields['Path']
                print("HTTP url: %s" % url)
            
    # ipv6 in pkt
        
    return "" # pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")

def startPacketAnalyse():
    #~ scapy.all.sniff(prn=monitor_callback, filter="arp", store=0)
    scapy.all.sniff(prn=monitor_callback, filter="", store=0) # filter="ip" pour avoir que ip # iface='eth0' pour interface
    """
    count: number of packets to capture. 0 means infinity
      store: wether to store sniffed packets or discard them
        prn: function to apply to each packet. If something is returned,
             it is displayed. Ex:
             ex: prn = lambda x: x.summary()
    lfilter: python function applied to each packet to determine
             if further action may be done
             ex: lfilter = lambda x: x.haslayer(Padding)
    offline: pcap file to read packets from, instead of sniffing them
    timeout: stop sniffing after a given time (default: None)
    L2socket: use the provided L2socket
    """

cacheDns()
toHostname("fe80::20c4:b6f:84d5:565c")
toHostname("ff02::1:3")
toHostname("13.248.212.111")
printCacheDns()
#~ exit(1)
import stater
stats = stater.Stater(1)
stats.sendLabels()
stats.startUpdateLoopInTheBackground()
startPacketAnalyse()