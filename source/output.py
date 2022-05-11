def write_to_file(data: list, file_path: str) -> None:
    import csv
    if not data:
        return

    keys = data[0].keys()
    with open(file_path, 'w', newline='') as output_file:
        dict_writer = csv.DictWriter(output_file, keys)
        dict_writer.writeheader()
        dict_writer.writerows(data)


def make_dir(directory):
    import os
    os.makedirs(directory, 0o777, True)
    try:
        os.chmod(directory, 0o777)
    except:
        pass


def csv_2_pdf(file_path, title=None, notes=None):
    import csv

    from fpdf import FPDF
    pdf = FPDF()
    pdf.add_page(orientation='L')
    page_width = pdf.w - 2 * pdf.l_margin

    pdf.set_font('Times', 'B', 14)
    pdf.cell(page_width, 0.0, title if title else 'Trades', align='C')
    pdf.ln(10)
    if notes:
        pdf.set_font('Times', 'B', 10)
        pdf.cell(page_width, 0.0, notes, align='L')
        pdf.ln(10)

    pdf.set_font('Courier', '', 7)
    pdf.ln(1)
    th = pdf.font_size

    cell_widths = None
    with open(file_path, newline='\n') as f:
        reader = csv.DictReader(f, delimiter=',')
        # col_width = page_width / len(reader.fieldnames)
        cell_widths = dict.fromkeys(reader.fieldnames, 0)
        for row in reader:
            for column in row.keys():
                cell_widths[column] = max(cell_widths.get(column, 0), len(str(row[column])))
    # print(cell_widths)
    with open(file_path, newline='\n') as f:
        reader = csv.reader(f, delimiter=',')
        for row in reader:
            for index, cell in enumerate(row):
                text = cell
                w = int(pdf.font_size * list(cell_widths.values())[index] * 0.75)
                if w == 0:
                    continue
                pdf.cell(w, th, text, border=1, align='R')
            pdf.ln(th)


    pdf.ln(10)

    pdf.set_font('Times', '', 10)
    pdf.cell(page_width, 0.0, '- end of report -', align='C')

    import os
    file_name, file_extension = os.path.splitext(file_path)
    pdf.output(file_name + '.pdf')


def output_to_file(result, file_path):
    output_path = 'output/kraken/' + file_path

    import os

    path = os.path.normpath(output_path)
    path_parts = path.split(os.sep)

    dir_path = ''
    for directory in path_parts[:-1]:
        dir_path += directory + os.sep
        make_dir(dir_path)

    write_to_file(result, output_path)
    # csv_2_pdf(output_path, 'Trades in Kraken.com', 'Prices are in Euros.')
    try:
        os.chmod(output_path, 0o666)
    except:
        pass
