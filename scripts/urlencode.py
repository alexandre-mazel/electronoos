import urllib.parse
import sys

s = sys.argv[1]
safe_string = urllib.parse.quote_plus(s)
print( s )
print( "is urlencoded as:" )
print( safe_string ) 