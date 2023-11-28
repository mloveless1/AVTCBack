import os
import pdfrw


class ProcessPdf:
    def __init__(self, temp_directory, output_file):
        self.temp_directory = temp_directory
        self.output_file = output_file

    def add_data_to_pdf(self, template_path, data):
        template = pdfrw.PdfReader(template_path)
        annotations = template.Root.Pages.Kids[0].Annots  # Assuming data to fill is on the first page

        for annotation in annotations:
            if annotation['/Subtype'] == '/Widget' and annotation['/T']:
                key = annotation['/T'][1:-1]  # Field name in the PDF
                if key in data:
                    if annotation['/FT'] == '/Tx':  # If it's a text field
                        annotation.update(
                            pdfrw.PdfDict(V=self.encode_pdf_string(data[key], 'string'))
                        )
                    elif annotation['/FT'] == '/Btn':  # If it's a button/check box
                        annotation.update(
                            pdfrw.PdfDict(V=self.encode_pdf_string(data[key], 'checkbox'))
                        )

        pdfrw.PdfWriter().write(os.path.join(self.temp_directory, self.output_file), template)

    def encode_pdf_string(self, value, type):
        if type == 'string':
            return pdfrw.objects.pdfstring.PdfString.encode(value)
        elif type == 'checkbox':
            return pdfrw.objects.pdfname.BasePdfName('/Yes') if value else pdfrw.objects.pdfname.BasePdfName('/Off')
        return ''
