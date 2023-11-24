#!/usr/bin/python

#Author: Kevin DEJOUR
#Reference:www.securityfriday.com/promiscuous_detection_01.pdf

#This script can detect the netword card in promiscuous mode. Moreover,
#in the case where the card is sniffing, it can guess the OS


import getopt,sys;
from scapy import Ether,ARP,IP,ICMP,srp,sr;

def usage():
	print """
USAGE: detect [OPTIONS] host

  Version 0.0.1

OPTIONS:
  -i, --iface		interface
  -h, --help		display this help message
  -v, --verbose		verbose mode
  -O			enable OS detection
	"""
	
def main():
	try:
		opts, args=getopt.getopt(sys.argv[1:],"i:hvO",["interface=","help","verbose"])
	except getopt.GetoptError, err:
		usage()
		sys.exit(2)

	#default
	interface="eth0"
	verb=0
	detection=0
	
	if len(args)!=1:
		usage()
		sys.exit(2)
	
	ipDst=args[0]
	
	for o, a in opts:
		if o in ("-i","--interface"):
			interface=a
		if o in ("-h","--help"):
			usage()
			sys.exit(2)
		if o in ("-v","--verbose"):
			verb=1;
		if o=="-O":
			detection=1
	
	verif(ipDst,interface)
	
	rep=tramARP(0,ipDst,interface,verb)
	if(rep==1):
		print ipDst, ": promiscuous mode card detected"
	else:
		print ipDst, ": promiscuous mode card non detected"
		sys.exit(2)
	
	if detection==1:
		rep=tramARP(2,ipDst,interface,verb)+2*tramARP(3,ipDst,interface,verb)
		if rep==0:
			print "probably: Windows 2k/NT4"
		elif rep==1:
			print "probably: Windows 9X/ME"
		elif rep==3:
			print "probably: Linux 2.2/2.4/2.6"


def tramARP(opt,ipDst,interface,verb):
	if opt==0:
		#Win9X/ME, Win2k/NT4, Linux2.2/2.4/2.6
		tram=Ether(dst='ff:ff:ff:ff:ff:fe')/ARP(op='who-has',pdst=ipDst);
	elif opt==1:
		#Win9X/ME, Win2k/NT4, Linux2.2/2.4/2.6
		tram=Ether(dst='ff:ff:00:00:00:00')/ARP(op='who-has',pdst=ipDst);
	elif opt==2:	
		#Win9X/ME,  Linux2.2/2.4/2.6
		tram=Ether(dst='ff:00:00:00:00:00')/ARP(op='who-has',pdst=ipDst);
	elif opt==3:	
		#Linux2.2/2.4/2.6
		tram=Ether(dst='01:00:00:00:00:00')/ARP(op='who-has',pdst=ipDst);
	elif opt==4:
		#Linux2.2/2.4/2.6
		tram=Ether(dst='01:00:5E:00:00:00')/ARP(op='who-has',pdst=ipDst);
	else:
		print "opt between 0 and 4 in tramARP"
		sys.exit(2)
	
	if verb==1:
		tram.show()

	ans,unans=srp(tram,iface=interface,verbose=verb,timeout=1);
	return len(ans)
	
	
def verif(ipDst,interface):
	ans,unans=sr(IP(dst=ipDst)/ICMP(),iface=interface,verbose=0,timeout=1)
	if len(ans)==0:
		print "ip dst=",ipDst,": down"
		sys.exit(2)
	
if __name__=="__main__":
	main()
	
