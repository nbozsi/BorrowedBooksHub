from openpyxl import Workbook
import io


def to_xlsx(data):
    buffer = io.BytesIO()

    wb = Workbook()
    ws1 = wb.active
    l1 = [r for r in data.keys()]
    ws1.append(l1)

    r, c = 2, 0  # row=2 and column=0
    for row_data in data:
        d = [r for r in row_data]
        ws1.append(d)

    wb.save(buffer)
    buffer.seek(0)
    return buffer
