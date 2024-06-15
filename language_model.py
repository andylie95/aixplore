
### Updated Code

#### `language_model.py`

```python
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import CountVectorizer
from sklearn.naive_bayes import MultinomialNB
import pickle

MODEL_PATH = 'translation_model.pkl'
VECTORIZER_PATH = 'vectorizer.pkl'

def load_and_preprocess_data(file_path):
    data = pd.read_csv(file_path)
    X = data['indonesian']
    y = data['english']
    return X, y

def train_translation_model(X, y):
    vectorizer = CountVectorizer()
    X_vect = vectorizer.fit_transform(X)
    X_train, X_test, y_train, y_test = train_test_split(X_vect, y, test_size=0.2, random_state=42)
    model = MultinomialNB()
    model.fit(X_train, y_train)
    return model, vectorizer

def update_translation_model(model, vectorizer, X, y):
    X_vect = vectorizer.transform(X)
    model.partial_fit(X_vect, y)
    return model

def save_model(model, vectorizer, model_path=MODEL_PATH, vectorizer_path=VECTORIZER_PATH):
    with open(model_path, 'wb') as f:
        pickle.dump(model, f)
    with open(vectorizer_path, 'wb') as f:
        pickle.dump(vectorizer, f)

def load_model(model_path=MODEL_PATH, vectorizer_path=VECTORIZER_PATH):
    with open(model_path, 'rb') as f:
        model = pickle.load(f)
    with open(vectorizer_path, 'rb') as f:
        vectorizer = pickle.load(f)
    return model, vectorizer
