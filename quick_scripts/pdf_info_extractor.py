import PyPDF2

def getInfo(path):
    with open(path, 'rb') as f:
        pdf = PyPDF2.PdfFileReader(f)
        info = pdf.getDocumentInfo()
        number_of_pages = pdf.getNumPages()
        print(info)
        author = info.author
        creator = info.creator
        producer = info.producer
        subject = info.subject
        title = info.title
        print("Title: %s" % title )
        
        print("Page number: %s" % pdf.getNumPages() )
        
        page = pdf.getPage(0)
        print(page)
        print('Page type: {}'.format(str(type(page))))
        text = page.extractText()
        print("text1: '%s'" % text)
        text = page.getContents()
        print("text2: '%s'" % text)
        
def getInfo2(strPath):
    import textract
    text = textract.process(strPath, method='pdfminer')
    
strPath = "D:/hri_only_paper/p202.pdf"
getInfo( strPath )