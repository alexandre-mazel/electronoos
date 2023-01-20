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
    if user_input in ["bonjour", "hello", "salut"]:
        return "Salut Humain!"
    if user_input in ["comment ca va", "ca boume", "tu va bien"]:
        return "moi ca va!"
    if user_input in ["au revoir", "bye"]:
        return "a+"
    return "je sais pas"
        
    
def chatbot_run():
    while 1:
        s = input()
        a = chatbot(s)
        print(a)
        if a.lower() in ["a+","bye"]: break
    
def autotest():
    assert(chatbot("Salut") == "Salut Humain!")
    assert(chatbot("Ca boume?") == "moi ca va!")
    assert(chatbot("bye") == "a+")
    assert(chatbot("pipi") == "je sais pas")
    
    
autotest()
chatbot_run()