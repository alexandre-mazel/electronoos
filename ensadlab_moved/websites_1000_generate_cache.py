import sys
sys.path.append("../alex_pytools")
import csv_loader
import nettools

# en fait, impossible de trouver une base de données ou service ip => name (car ca permettrait de faire un mega spammer)
# donc on peut generer un cache en partant des sites les plus visitées => ip


def generateCacheDns(filename):
    datas = csv_loader.load_csv(filename,sepa=',')
    for record in datas:
        n,site,rank = record
        #site = "signal.org"
        print("\n"+site)
        ips = nettools.getIPx(site)
        print(ips)
        ips = nettools.getIPV6x(site)
        print(ips)
        ips = nettools.getIPV6Sub(site)
        print(ips)
        if n>20:
            break
    
    
filename = "websites_1000.csv"
generateCacheDns(filename)