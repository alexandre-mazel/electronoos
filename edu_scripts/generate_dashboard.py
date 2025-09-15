from odf.opendocument import OpenDocumentText
from odf.style import PageLayout, PageLayoutProperties, MasterPage, Style, TableColumnProperties, TableCellProperties, TextProperties
from odf.text import P
from odf.table import Table, TableColumn, TableRow, TableCell

def generate_odt_dashboard( filename = "dash.odt" ):
    
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
    
    plp = PageLayoutProperties(
        margin="2cm",
        pagewidth="29.7cm",   # A4 width in landscape
        pageheight="21cm",    # A4 height in landscape
        printorientation="landscape"
    )
    #~ plp.setPrintOrientation(PrintOrientation.LANDSCAPE);
    
    page_layout.addElement(plp)
    doc.automaticstyles.addElement(page_layout)
    
   # Attach the page layout to a master page (this makes it active!)
    master_page = MasterPage(name="LandscapeMaster", pagelayoutname=page_layout)
    #~ master_page = MasterPage(name="LandscapeMaster", pagelayoutname="LandscapeLayout")
    doc.masterstyles.addElement(master_page)
    
    width = 29.7
    margin = 2

    # Available width (after margins)
    available_width_cm = 29.7 - (2 * margin)  # 29.7cm - left and right margins (2cm each)

    # Weighting: first column = 2 parts, other 9 columns = 1 part each
    total_parts = 2 + 9
    part_width = available_width_cm / total_parts
    col1_width = part_width * 2
    other_col_width = part_width

    # Define column styles
    col_wide = Style(name="WideColumn", family="table-column")
    col_wide.addElement(TableColumnProperties(columnwidth=f"{col1_width:.2f}cm"))
    doc.automaticstyles.addElement(col_wide)

    col_normal = Style(name="NormalColumn", family="table-column")
    col_normal.addElement(TableColumnProperties(columnwidth=f"{other_col_width:.2f}cm"))
    doc.automaticstyles.addElement(col_normal)

    # Define header cell style
    header_style = Style(name="HeaderCell", family="table-cell")
    header_style.addElement(TableCellProperties(backgroundcolor="#CCCCCC"))
    header_style.addElement(TextProperties(fontweight="bold"))
    doc.automaticstyles.addElement(header_style)

    # Create the table
    table = Table(name="MyTable")

    # Add columns: 1 wide + 9 normal
    table.addElement(TableColumn(stylename=col_wide))
    for _ in range(9):
        table.addElement(TableColumn(stylename=col_normal))

    # Header row
    header_row = TableRow()
    for i in range(10):
        cell = TableCell(stylename=header_style)
        cell.addElement(P(text=f"Column {i+1}"))
        header_row.addElement(cell)
    table.addElement(header_row)

    # Example data rows (5 rows)
    for row_idx in range(5):
        row = TableRow()
        for col_idx in range(10):
            cell = TableCell()
            cell.addElement(P(text=f"R{row_idx+1}C{col_idx+1}"))
            row.addElement(cell)
        table.addElement(row)

    # Add table to the document
    doc.text.addElement(table)

    # Save the file
    doc.save(filename, True)
    print(f"Document generated: {filename}.odt")

# generate_odt_dashboard - end

generate_odt_dashboard("my_table")
