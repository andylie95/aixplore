import streamlit as st
from translate_codebase import (
    load_dictionaries, translate_with_google, translate_word, 
    translate_excel, translate_pptx, translate_pdf, save_translated_file
)
from language_model import (
    load_and_preprocess_data, train_translation_model, 
    update_translation_model, save_model, load_model
)
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from PyPDF2 import PdfFileReader
import io
import base64

MODEL_PATH = 'translation_model.pkl'
VECTORIZER_PATH = 'vectorizer.pkl'

def get_download_link(file_path, file_name, file_label):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{file_name}">{file_label}</a>'

st.title("AI XPLORE")

uploaded_csv_files = st.file_uploader("Upload CSV files to train/update model", type="csv", accept_multiple_files=True)
if uploaded_csv_files:
    model, vectorizer = None, None
    try:
        model, vectorizer = load_model(MODEL_PATH, VECTORIZER_PATH)
    except FileNotFoundError:
        st.warning("No existing model found. A new model will be trained.")
    
    for csv_file in uploaded_csv_files:
        X, y = load_and_preprocess_data(csv_file)
        if model is None or vectorizer is None:
            model, vectorizer = train_translation_model(X, y)
        else:
            model = update_translation_model(model, vectorizer, X, y)
    
    save_model(model, vectorizer, MODEL_PATH, VECTORIZER_PATH)
    st.success("Model trained/updated and saved successfully.")

try:
    model, vectorizer = load_model(MODEL_PATH, VECTORIZER_PATH)
except FileNotFoundError:
    st.error("No trained model found. Please upload CSV files to train the model first.")

text_to_translate = st.text_area("Enter text to translate")
target_language = st.selectbox("Select target language", ["en", "id"])

if st.button("Translate Text"):
    if text_to_translate:
        translated_text = translate_with_google(text_to_translate, target_language, {})
        st.write("Translated Text:")
        st.write(translated_text)
    else:
        st.error("Please enter text to translate.")

uploaded_file = st.file_uploader("Upload a document", type=["docx", "xlsx", "pptx", "pdf"])
if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]
    file_name = f"translated_document.{file_type}"
    if file_type == "docx":
        doc = Document(uploaded_file)
        translated_doc = translate_word(doc, target_language, {})
        translated_doc.save(file_name)
        st.success(f"Translated Word document saved as '{file_name}'")
    elif file_type == "xlsx":
        wb = load_workbook(uploaded_file)
        translated_wb = translate_excel(wb, target_language, {})
        translated_wb.save(file_name)
        st.success(f"Translated Excel spreadsheet saved as '{file_name}'")
    elif file_type == "pptx":
        prs = Presentation(uploaded_file)
        translated_prs = translate_pptx(prs, target_language, {})
        translated_prs.save(file_name)
        st.success(f"Translated PowerPoint presentation saved as '{file_name}'")
    elif file_type == "pdf":
        pdf_reader = PdfFileReader(uploaded_file)
        translated_pdf_writer = translate_pdf(pdf_reader, target_language, {})
        with open(file_name, "wb") as f:
            translated_pdf_writer.write(f)
        st.success(f"Translated PDF saved as '{file_name}'")

    download_link = get_download_link(file_name, file_name, 'Download Translated Document')
    st.markdown(download_link, unsafe_allow_html=True)
