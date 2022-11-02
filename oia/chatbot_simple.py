def clean_string(s):
    conversion_list = [ 
                ("?",""), 
                (":"," sep ")
    ]
    s = s.lower()
    for c in conversion_list:
        s = s.replace(c[0],c[1])
    return s
        
def chatbot(user_input):
    user_input = clean_string(user_input)
    if user_input in ["bonjour", "hello"]
        return "Salut Humain!"
    return "je sais pas"
        
    
def chatbot_run():
    while 1:
        s = input()
        a = chatbot(s)
        print(a)
    
def autotest():
    assert(chatbot("Salut") == "Bonjour")
    
    
autotest()
#~ chatbot_run()