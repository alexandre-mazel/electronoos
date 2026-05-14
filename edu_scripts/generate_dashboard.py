from odf.opendocument import OpenDocumentText
from odf.style import PageLayout, PageLayoutProperties, MasterPage, Style, TableColumnProperties, TableCellProperties, TextProperties, ParagraphProperties
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

import os
import copy

def generate_odt_dashboard( filename = "dash", columns = [], headers = [], legends = [] ):
    
    # Create a text document
    doc = OpenDocumentText()
    

    # nothing works to succeed in putting in lanscape mode!
    """
    page_layout = PageLayout(name="LandscapeLayout")
    page_layout.addElement(PageLayoutProperties(
        margintop="2cm", marginbottom="2cm",
        marginleft="2cm", marginright="2cm",
        pagewidth="29.7cm", pageheight="21cm",
        printorientation="landscape"
    ))
    doc.automaticstyles.addElement(page_layout)

    # attach to MasterPage
    master_page = MasterPage(name="LandscapeMaster", pagelayoutname=page_layout)
    doc.masterstyles.addElement(master_page)
    """

    # Define page layout in landscape mode
    page_layout = PageLayout(name="landscape")
    
    margin = 1
    
    plp = PageLayoutProperties(
        margin="%dcm" % margin,
        pagewidth="29.7cm",   # A4 width in landscape
        pageheight="21cm",    # A4 height in landscape
        printorientation="landscape",
        marginleft="0cm", marginright="0cm", # margin doesn't work
        margintop="0cm", marginbottom="0cm"
    )
    #~ plp.setPrintOrientation(PrintOrientation.LANDSCAPE);
    
    page_layout.addElement(plp)
    doc.automaticstyles.addElement(page_layout)
    
   # Attach the page layout to a master page (this makes it active!)
    master_page = MasterPage(name="LandscapeMaster", pagelayoutname=page_layout)
    #~ master_page = MasterPage(name="LandscapeMaster", pagelayoutname="LandscapeLayout")
    doc.masterstyles.addElement(master_page)

    
    width = 29.7
    nbr_columns = 32
    
    nbr_wide = 2
    nbr_normal = 4
    nbr_small = nbr_columns-nbr_wide-nbr_normal

    # Available width (after margins)
    available_width_cm = 29.7 - (2 * margin)  # 29.7cm - left and right margins (2cm each)

    # Weighting: first column = 2 parts, other 9 columns = 1 part each
    total_parts = nbr_wide*2+nbr_normal+nbr_small/3
    part_width = available_width_cm / total_parts
    col1_width = part_width * 2
    other_col_width = part_width
    col_width_mini = part_width/3

    # Define column styles
    col_wide = Style(name="WideColumn", family="table-column")
    col_wide.addElement(TableColumnProperties(columnwidth=f"{col1_width:.2f}cm"))
    doc.automaticstyles.addElement(col_wide)

    col_normal = Style(name="NormalColumn", family="table-column")
    col_normal.addElement(TableColumnProperties(columnwidth=f"{other_col_width:.2f}cm"))
    doc.automaticstyles.addElement(col_normal)
    
    col_small = Style(name="SmallColumn", family="table-column")
    col_small.addElement(TableColumnProperties(columnwidth=f"{col_width_mini:.2f}cm"))
    doc.automaticstyles.addElement(col_small)

    # Define header cell style
    header_style = Style(name="HeaderCell", family="table-cell")
    header_style.addElement(TableCellProperties(backgroundcolor="#CCCCFF"))
    header_style.addElement(TextProperties(fontsize= "8pt",fontweight="bold"))
    header_style.addElement(ParagraphProperties(textalign="center"))
    doc.automaticstyles.addElement(header_style)
    
    header_style_lefted = copy.deepcopy(header_style)
    header_style_lefted.name = "HeaderCell2" # usefull? working ?
    header_style_lefted.addElement(ParagraphProperties(textalign="left"))
    doc.automaticstyles.addElement(header_style_lefted)
    
    # doing again a deep copy doesn't work...
    header_style_small = Style(name="HeaderCellSmall", family="table-cell")
    header_style_small.addElement(TableCellProperties(backgroundcolor="#DDDDFF"))
    header_style_small.addElement(TextProperties(fontsize= "6pt",fontweight="normal"))
    header_style_small.addElement(ParagraphProperties(textalign="center"))
    doc.automaticstyles.addElement(header_style_small)

    # Create the table
    table = Table(name="MyTable")

    # Add columns
    for _ in range(nbr_wide):
        table.addElement(TableColumn(stylename=col_wide))
    for _ in range(nbr_normal):
        table.addElement(TableColumn(stylename=col_normal))
    for _ in range(nbr_small):
        table.addElement(TableColumn(stylename=col_small))
        
    # Header row
    header_row = TableRow()
    #~ for i in range(10):
        #~ cell = TableCell(stylename=header_style)
        #~ cell.addElement(P(text=f"Column {i+1}"))
        #~ header_row.addElement(cell)
    for i,h in enumerate(headers):
        if i == 0:
            cell = TableCell(stylename=header_style_lefted)
        elif i < nbr_wide+nbr_normal:
            cell = TableCell(stylename=header_style)
        else:
            cell = TableCell(stylename=header_style_small)
        cell.addElement(P(text=h))
        header_row.addElement(cell)
    table.addElement(header_row)

    # Example data rows (5 rows)
    #~ for row_idx in range(5):
        #~ row = TableRow()
        #~ for col_idx in range(10):
            #~ cell = TableCell()
            #~ cell.addElement(P(text=f"R{row_idx+1}C{col_idx+1}"))
            #~ row.addElement(cell)
        #~ table.addElement(row)
    
    for j in range(len(columns[0])):
        row = TableRow()
        for i in range(len(columns)):
            cell = TableCell()
            cell.addElement(P(text=columns[i][j]))
            row.addElement(cell)
        while i < nbr_columns:
            cell = TableCell()
            cell.addElement(P(text=" "))
            row.addElement(cell)
            i += 1
        table.addElement(row)

    # Add table to the document (simple)
    if 1:
        doc.text.addElement(table)
    
    # Add table to the document (no spacing) (not working)
    else:
        # Define a "tight" paragraph style (fonctionne pas)
        tight_para = Style(name="TightParagraph", family="paragraph")
        tight_para.addElement(ParagraphProperties(margintop="0cm", marginbottom="0cm"))
        doc.automaticstyles.addElement(tight_para)

        # Add an empty "tight" paragraph before the table
        doc.text.addElement(P(stylename=tight_para, text=""))

        # Add the table itself (directly under text, valid ODF)
        doc.text.addElement(table)

        # Add another "tight" paragraph after the table
        doc.text.addElement(P(stylename=tight_para, text=""))
    
    if len(legends) > 0:
        # --- Create a paragraph style with bottom border ---
        #~ line_style = Style(name="LineBelowTable", family="paragraph")
        #~ line_style.addElement(ParagraphProperties(borderbottom="0.5pt solid #000000"))
        line_style = Style(name="LineAbove", family="paragraph")
        line_style.addElement(ParagraphProperties(bordertop="0.2pt solid #000000"))
        line_style.addElement(TextProperties(fontsize= "6pt",fontweight="normal"))
        doc.automaticstyles.addElement(line_style)

        # --- Add the paragraph below the table ---
        line_para = P(stylename=line_style, text=legends[0])
        doc.text.addElement(line_para)

    # Save the file
    doc.save(filename, True)
    print(f"Document generated: {filename}.odt")

# generate_odt_dashboard - end

def cut_names_first( fullname ):
    """
    look for the  first filename not uppercased
    """
    splitted = fullname.split()
    for i in range( len(splitted) ):
        if splitted[i] != splitted[i].upper():
            names = " ".join( splitted[:i] )
            firsts = " ".join( splitted[i:] )
            break
    return names, firsts

print( cut_names_first("MAZEL CARVLALHO Corto Truc") )

def load_names( afn ):
    print( "INF: load_names: processing '%s'" % afn )
    import csv
    names = []
    with open(afn, mode ='r')as file:
        csvFile = csv.reader(file,delimiter=';')
        for i, lines in enumerate(csvFile):
            if len(lines) < 1:
                continue
            print(lines)
            if i == 0:
                header = lines
            else:
                names.append(lines[0])
                
    return header, names

#~ generate_odt_dashboard("my_table")

list_class = ["202", "204", "205", "206"]
#~ list_class = ["202"]
for classname in list_class:
    afn = r"C:\Users\alexa\perso\docs_nextcloud_edu\2025_Bernard\SNT/" + "liste_" + classname + ".csv"
    header, names = load_names( afn )
    print( "INF: names:\n%s" % names )
    last_names = []
    first_names = []
    for n in names:
        l,f = cut_names_first( n )
        last_names.append(l)
        first_names.append(f)
    
    tps = ["TP%d G%d" % (j+1,i+1) for j in range(14) for i in range(2)]
    head = [classname, "", "Comments", "Part1", "Part2", "Part3"]
    #~ head.extend(["ev1","ev2"])
    head.extend(tps)
    
    fn = "dash_" + classname
    legends = ["(B: bavardage, A: Attitude, T: Toilette, I: Infirmerie, R: Retard)"]
    generate_odt_dashboard( fn, [last_names, first_names], head, legends)
    os.system("start " + fn + ".odt" )


