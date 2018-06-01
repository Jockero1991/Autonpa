from openpyxl import load_workbook as lw
from openpyxl import Workbook
from openpyxl.compat import range
from openpyxl.utils import get_column_letter
import csv

def pyxl(p, sh):
    d_file = 'data\\17_05_18 Предварительный отчет по задачам релиза 2 Sprint 1-2.xlsx'
    report_book = lw(d_file)
    current_sheet = report_book[sh]
    
    reading_txt=[]
    with open(p, "r") as csv_file:
        reader = csv.DictReader(csv_file, delimiter=';')
        #print(reader[2])
        for line in reader:
            reading_txt.append(line["№ в Jira|Тип задачи|Статус|Приоритет|Тема|Исполнитель|Тестировщик|Sprint"])
    #print(len(reading_txt))
    for row in range(3, (len(reading_txt)+3)):
        _ = current_sheet.cell(column = 2, row=row, value="{0}".format(reading_txt[row-3]))
    report_book.save(filename=d_file)
    

# def example_pyxl():
#     wb = Workbook()
#     dest_filename = 'empty_book.xlsx'
 
#     ws1 = wb.active
#     ws1.title = "range names"

#     for row in range(1, 40):
#         ws1.append(range(600))

#     ws2 = wb.create_sheet(title="Pi")

#     ws2['F5'] = 3.14

#     ws3 = wb.create_sheet(title="Data")
#     for row in range(10, 20):
#         for col in range(27, 54):
#             _ = ws3.cell(column=col, row=row, value="{0}".format(get_column_letter(col)))
#     print(ws3['AA10'].value)

#     wb.save(filename = dest_filename)
# example_pyxl()
#test_pyxl('в_тестировании.csv', 'В тестировании')