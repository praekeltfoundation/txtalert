import xlrd

def read_cd4_document(filename):
    # load the book
    book = xlrd.open_workbook(filename)
    # only using first sheet
    sheet = book.sheet_by_index(0)
    # assume the column names are the first row
    column_names = sheet.row_values(0)
    return [zip(column_names, sheet.row_values(row_index))
            for row_index in range(1, sheet.nrows)] 
    