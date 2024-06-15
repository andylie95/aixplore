import pandas as pd
from deep_translator import GoogleTranslator
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from PyPDF2 import PdfFileReader, PdfFileWriter
import io
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from sklearn.pipeline import make_pipeline

def load_dictionaries(csv_files):
    translation_dict = {}
    for file in csv_files:
        df = pd.read_csv(file)
        for index, row in df.iterrows():
            indonesian_word = row['indonesian']
            english_word = row['english']
            translation_dict[indonesian_word] = english_word
            translation_dict[english_word] = indonesian_word
    return translation_dict

def train_translation_model(csv_files):
    data = []
    for file in csv_files:
        df = pd.read_csv(file)
        data.append(df)
    data = pd.concat(data, ignore_index=True)
    
    X = data['indonesian']
    y = data['english']
    
    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(X, y)
    return model

def translate_with_model(text, target_lang, model):
    if target_lang == 'en':
        return model.predict([text])[0]
    else:
        return "Model only supports Indonesian to English translation."

def translate_text(text, translation_dict):
    if not text:
        return text
    words = text.split()
    translated_words = [translation_dict.get(word, word) for word in words]
    return ' '.join(translated_words)

def translate_with_google(text, target_lang, translation_dict):
    text = translate_text(text, translation_dict)
    if not text.strip():
        return text
    translator = GoogleTranslator(source='auto', target=target_lang)
    translated = translator.translate(text)
    return translated

def translate_paragraph(paragraph, target_lang, translation_dict, model=None):
    for run in paragraph.runs:
        if model:
            translated_text = translate_with_model(run.text, target_lang, model)
        else:
            translated_text = translate_with_google(run.text, target_lang, translation_dict)
        run.text = translated_text if translated_text is not None else ""
    return paragraph

def translate_word(doc, target_lang, translation_dict, model=None):
    for paragraph in doc.paragraphs:
        translate_paragraph(paragraph, target_lang, translation_dict, model)
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for paragraph in cell.paragraphs:
                    translate_paragraph(paragraph, target_lang, translation_dict, model)
    return doc

def translate_excel(wb, target_lang, translation_dict, model=None):
    for sheet in wb.sheetnames:
        ws = wb[sheet]
        for row in ws.iter_rows():
            for cell in row:
                if cell.value:
                    if model:
                        cell.value = translate_with_model(cell.value, target_lang, model)
                    else:
                        cell.value = translate_with_google(cell.value, target_lang, translation_dict)
    return wb

def translate_pptx(prs, target_lang, translation_dict, model=None):
    for slide in prs.slides:
        for shape in slide.shapes:
            if shape.has_text_frame:
                for paragraph in shape.text_frame.paragraphs:
                    for run in paragraph.runs:
                        if model:
                            translated_text = translate_with_model(run.text, target_lang, model)
                        else:
                            translated_text = translate_with_google(run.text, target_lang, translation_dict)
                        run.text = translated_text if translated_text is not None else ""
    return prs

def translate_pdf(pdf_reader, target_lang, translation_dict, model=None):
    pdf_writer = PdfFileWriter()
    for page_num in range(pdf_reader.numPages):
        page = pdf_reader.getPage(page_num)
        page_content = page.extract_text()
        if model:
            translated_content = translate_with_model(page_content, target_lang, model)
        else:
            translated_content = translate_with_google(page_content, target_lang, translation_dict)
        page.merge_page(PdfFileReader(io.BytesIO(translated_content.encode('utf-8'))).getPage(0))
        pdf_writer.addPage(page)
    return pdf_writer

def save_translated_file(translated_file, file_type):
    if file_type == "docx":
        translated_file.save("translated_document.docx")
    elif file_type == "xlsx":
        translated_file.save("translated_spreadsheet.xlsx")
    elif file_type == "pptx":
        translated_file.save("translated_presentation.pptx")
    elif file_type == "pdf":
        with open("translated_document.pdf", "wb") as f:
            translated_file.write(f)
