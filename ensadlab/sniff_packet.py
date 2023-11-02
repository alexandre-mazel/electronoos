import scapy
import scapy.all
#~ a = scapy.all.sniff(count=10)
#~ a.nsummary()

def monitor_callback(pkt):
    #~ return pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")
    #~ if scapy.all.ARP in pkt and pkt[scapy.all.ARP].op in (1,2): #who-has or is-at
    
    if scapy.all.ARP in pkt and pkt[scapy.all.ARP].op in (1,2): #who-has or is-at
        s = pkt.sprintf("recv: %ARP.hwsrc% %ARP.psrc%")
        print(s)
        return "" # pkt.sprintf("%ARP.hwsrc% %ARP.psrc%")

def startPacketAnalyse():
    #~ scapy.all.sniff(prn=monitor_callback, filter="arp", store=0)
    scapy.all.sniff(prn=monitor_callback, filter="", store=0)
    
    
startPacketAnalyse()