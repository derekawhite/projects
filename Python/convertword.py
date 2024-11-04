#python -m pip install --trusted-host pypi.python.org --trusted-host pypi.org --trusted-host files.pythonhosted.org Spire.Doc

import aspose.words as aw

from spire.doc import *
from spire.doc.common import *


import convertapi
convertapi.api_secret = '3TaEJs0ah6R8EIIG'

convertapi.convert('jpg', {
    'File': 'c:\\temp\\test.docx'
}, from_format = 'docx').save_files('c:\\temp\\output')


exit(0)
# Create a Document object
document = Document()

# Load a doc or docx file
document.LoadFromFile("test.docx")

for i in range(document.GetPageCount()):

    # Convert a specific page to bitmap image
    imageStream = document.SaveImageToStreams(i, ImageType.Bitmap)

    # Save the bitmap to a PNG file
    with open('Output/ToImage-{0}.png'.format(i),'wb') as imageFile:
        imageFile.write(imageStream.ToArray())

document.Close()

                      

# load document
doc = aw.Document("test.docx")

# set output image format
options = aw.saving.ImageSaveOptions(aw.SaveFormat.PNG)

# loop through pages and convert them to PNG images
for pageNumber in range(doc.page_count):
    options.page_set = aw.saving.PageSet(pageNumber)
    doc.save(str(pageNumber+1)+"_page.png", options)