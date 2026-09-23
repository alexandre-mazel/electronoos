import bcrypt
import sys

if len(sys.argv)<2:
    print("Generate a hashed password\nsyntax: %s password" % sys.argv[0] )
    exit(-1)


password = sys.argv[1]

print( "\nUn bon hash pour '%s':" % password )
hashed = bcrypt.hashpw( password.encode("utf-8"), bcrypt.gensalt());
print(hashed)