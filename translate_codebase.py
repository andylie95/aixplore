import pandas as pd
import pickle
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
from deep_translator import GoogleTranslator
from docx import Document
from openpyxl import load_workbook
from pptx import Presentation
from PyPDF2 import PdfFileReader, PdfFileWriter
import io

def load_dictionaries(csv_files):
    translation_dict = {}
    all_texts = []
    all_labels = []
    for file in csv_files:
        df = pd.read_csv(file)
        for index, row in df.iterrows():
            indonesian_word = row['indonesian']
            english_word = row['english']
            translation_dict[indonesian_word] = english_word
            translation_dict[english_word] = indonesian_word
            all_texts.extend([indonesian_word, english_word])
            all_labels.extend(['indonesian', 'english'])
    
    vectorizer = CountVectorizer()
    X = vectorizer.fit_transform(all_texts)
    model = MultinomialNB()
    model.fit(X, all_labels)
    
    save_model(model, vectorizer)
    
    return translation_dict

def save_model(model, vectorizer):
    with open('language_model.pkl', 'wb') as f:
        pickle.dump((model, vectorizer), f)

def load_model():
    with open('language_model.pkl', 'rb') as f:
        model, vectorizer = pickle.load(f)
    return model, vectorizer

def translate_with_ml(text):
    model, vectorizer = load_model()
    X = vectorizer.transform([text])
    predicted_language = model.predict(X)[0]
    return predicted_language

def translate_with_google(text, target_lang, translation_dict):
    translator = GoogleTranslator(source='auto', target=target_lang)
    translated = translator.translate(text)
    return translated
