import streamlit as st
from translate_codebase import (load_dictionaries, train_translation_model, translate_with_model,
                                translate_with_google, translate_word, translate_excel, 
                                translate_pptx, translate_srt, save_translated_file)
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
import io
import base64

def get_download_link(file_path, file_label):
    with open(file_path, "rb") as f:
        bytes_data = f.read()
    b64 = base64.b64encode(bytes_data).decode()
    return f'<a href="data:file/txt;base64,{b64}" download="{file_path}">{file_label}</a>'

translation_dict = {}
models = None

st.title("XPLORE Translation")

uploaded_csv_files = st.file_uploader("Upload CSV files for contextualized translation", type="csv", accept_multiple_files=True)
if uploaded_csv_files:
    if st.button("Load AI Model"):
        translation_dict = load_dictionaries(uploaded_csv_files)
        st.write("AI Model loaded successfully.")
    elif st.button("Train your AI model"):
        models = train_translation_model(uploaded_csv_files)
        st.write("Your AI model was trained successfully.")

st.markdown("---")

text_to_translate = st.text_area("Enter text to translate")
target_language = st.selectbox("Translate to", ["english", "indonesian", "malay", "hindi"])

if st.button("Translate Text"):
    if text_to_translate:
        if models:
            translated_text = translate_with_model(text_to_translate, 'auto', target_language, models)
        else:
            translated_text = translate_with_google(text_to_translate, target_language, translation_dict)
        st.write("Translated Text:")
        st.write(translated_text)
    else:
        st.error("Please enter text to translate.")

st.markdown("---")

uploaded_file = st.file_uploader("Upload a document", type=["docx", "xlsx", "pptx", "srt"])
if uploaded_file:
    file_type = uploaded_file.name.split('.')[-1]
    initial_name = uploaded_file.name.split('.')[0]
    if file_type == "docx":
        doc = Document(uploaded_file)
        translated_doc = translate_word(doc, target_language, translation_dict, models)
        file_name = save_translated_file(translated_doc, file_type, initial_name, target_language)
        st.success(f"Translated Word document saved as '{file_name}'")
    elif file_type == "xlsx":
        wb = load_workbook(uploaded_file)
        translated_wb = translate_excel(wb, target_language, translation_dict, models)
        file_name = save_translated_file(translated_wb, file_type, initial_name, target_language)
        st.success(f"Translated Excel spreadsheet saved as '{file_name}'")
    elif file_type == "pptx":
        prs = Presentation(uploaded_file)
        translated_prs = translate_pptx(prs, target_language, translation_dict, models)
        file_name = save_translated_file(translated_prs, file_type, initial_name, target_language)
        st.success(f"Translated PowerPoint presentation saved as '{file_name}'")
    elif file_type == "srt":
        srt_content = uploaded_file.read().decode("utf-8")
        translated_srt = translate_srt(srt_content, target_language, translation_dict, models)
        file_name = save_translated_file(translated_srt, file_type, initial_name, target_language)
        st.success(f"Translated SRT file saved as '{file_name}'")

    download_link = get_download_link(file_name, 'Download Translated Document')
    st.markdown(download_link, unsafe_allow_html=True)

st.markdown("---")

accuracy_rating = st.selectbox("Rate the translation accuracy", [1, 2, 3, 4, 5], index=4)
st.write(f"Translation Accuracy Rating: {accuracy_rating}")
