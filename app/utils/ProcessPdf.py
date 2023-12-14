import os
import pdfrw
from PIL import Image


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

    def embed_image_to_pdf(self, image_path, pdf_path, x, y, width, height, page_number=0):
        """
        Embeds an image into the PDF at the specified location.
        x, y: Coordinates for the image's lower-left corner
        width, height: Dimensions of the image
        page_number: Page number to add the image to
        """
        # Create a stamp PDF with the image
        stamp = self.create_stamp_pdf(image_path, width, height)

        # Merge the stamp with the form PDF
        self.merge_pdfs(stamp, pdf_path, page_number, x, y)

    def create_stamp_pdf(self, image_path, width, height):
        """
        Creates a stamp PDF with the image.
        """
        # Load and resize the image
        image = Image.open(image_path)
        image = image.resize((width, height))

        # Save the image as a PDF
        stamp_path = os.path.join(self.temp_directory, 'stamp.pdf')
        image.save(stamp_path, 'PDF', resolution=100.0)

        return stamp_path

    @staticmethod
    def merge_pdfs(stamp_pdf_path, pdf_path, page_number, x, y):
        """
        Merges the stamp PDF with the form PDF at specific coordinates.
        """
        form_pdf_path = pdf_path
        form_pdf = pdfrw.PdfReader(form_pdf_path)
        stamp_pdf = pdfrw.PdfReader(stamp_pdf_path)

        # Get the page where the signature will be placed
        form_page = form_pdf.pages[page_number]

        # Create a PageMerge object for the form page
        merger = pdfrw.PageMerge(form_page)

        # Get the stamp page
        stamp_page = stamp_pdf.pages[0]

        # Adjust the stamp page dimensions and position
        stamp_page_obj = pdfrw.PageMerge().add(stamp_page)[0]
        stamp_page_obj.x, stamp_page_obj.y = x, y

        # Add the stamp page to the merger and render it
        merger.add(stamp_page_obj)
        merger.render()

        # Save the merged PDF
        pdfrw.PdfWriter(form_pdf_path, trailer=form_pdf).write()
