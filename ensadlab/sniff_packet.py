import scapy
import scapy.all
#~ a = scapy.all.sniff(count=10)
#~ a.nsummary()

ARP = scapy.all.ARP
IP = scapy.all.IP
TCP = scapy.all.TCP
UDP = scapy.all.UDP

aDns = {
    "192.168.0.46" : "mstab7",
    "216.58.214.170" : "Google",
    "78.199.86.189" : "MaFreebox",
}

def toHostname(ip):
    try:
        return aDns[ip]
    except KeyError as err:
        pass
    return ip

def monitor_callback(pkt):
    #~ return pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")
    #~ if scapy.all.ARP in pkt and pkt[scapy.all.ARP].op in (1,2): #who-has or is-at
    
    #~ print(dir(pkt))
    print("DBG: pkt: %s" % str(pkt))
    #~ print("DBG: pkt[scapy.all.ARP]: %s" % str(pkt[scapy.all.ARP]))
    if ARP in pkt:
        print("ARP")
        s = pkt.sprintf("recv: ARP: %ARP.hwsrc% %ARP.psrc% => %ARP.pdst%")
        print(s)
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
        return "" # pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")

def startPacketAnalyse():
    #~ scapy.all.sniff(prn=monitor_callback, filter="arp", store=0)
    scapy.all.sniff(prn=monitor_callback, filter="", store=0)
    
    
startPacketAnalyse()