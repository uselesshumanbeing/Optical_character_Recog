import docx

def texttodoc(path,content):
    doc=docx.Document()
    doc.add_paragraph(content)
    doc.save(path+'sample.docx')