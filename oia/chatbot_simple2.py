def clean_string(s):
    conversion_list = [ 
                ("?",""), 
                (":"," sep ")
    ]
    s = s.lower()
    for c in conversion_list:
        s = s.replace(c[0],c[1])
    return s
        
tableau_questions_reponses = [
[ ["bonjour", "hello", "salut"], "Salut Humain!"],
[ ["comment ca va", "ca boume", "tu va bien"], "moi ca va!"],
[ ["au revoir", "bye"], "a+"],
]
def chatbot(user_input):
    user_input = clean_string(user_input)
    for qr in tableau_questions_reponses:
        qs,r = qr
        if user_input in qs:
            return r
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