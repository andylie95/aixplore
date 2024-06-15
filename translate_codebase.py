import pandas as pd
from deep_translator import GoogleTranslator
from langdetect import detect
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
            source_word = row['source']
            target_word = row['target']
            translation_dict[source_word] = target_word
            translation_dict[target_word] = source_word
    return translation_dict

def train_translation_model(csv_files):
    data = []
    for file in csv_files:
        df = pd.read_csv(file)
        data.append(df)
    data = pd.concat(data, ignore_index=True)
    
    X = data['source']
    y = data['target']
    
    model = make_pipeline(CountVectorizer(), MultinomialNB())
    model.fit(X, y)
    return model

def detect_language(text):
    return detect(text)

def translate_with_model(text, source_lang, target_lang, model):
    if source_lang in ['id', 'ms', 'th'] and target_lang == 'en':
        return model.predict([text])[0]
    elif source_lang == 'en' and target_lang in ['id', 'ms', 'th']:
        return model.predict([text])[0]
    else:
        return "Model only supports translations between English, Indonesian, Malaysian, and Thai."

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
            detected_lang = detect_language(run.text)
            translated_text = translate_with_model(run.text, detected_lang, target_lang, model)
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
                        detected_lang = detect_language(cell.value)
                        cell.value = translate_with_model(cell.value, detected_lang, target_lang, model)
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
                            detected_lang = detect_language(run.text)
                            translated_text = translate_with_model(run.text, detected_lang, target_lang, model)
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
            detected_lang = detect_language(page_content)
            translated_content = translate_with_model(page_content, detected_lang, target_lang, model)
        else:
            translated_content = translate_with_google(page_content, target_lang, translation_dict)
        translated_page = PdfFileReader(io.BytesIO(translated_content.encode('utf-8')))
        pdf_writer.add_page(translated_page.getPage(0))
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
