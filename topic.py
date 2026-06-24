import os
import nltk
import numpy as np
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import LdaModel
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from STOPWORDS import STOPWORDS

# Configuration des Stopwords
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
stop_words = list(stopwords.words('english'))  # scikit-learn attend une liste

all_stopwords = list(set(stop_words).union(set(STOPWORDS)))

def preprocess(text):
    """Nettoie le texte pour le LDA."""
    tokens = text.lower().split()
    return [token for token in tokens if token.isalpha() and token not in all_stopwords]


def topic(doc_id: int) -> dict:
    file_path = f"{doc_id}_sent_tok.txt"
    
    if not os.path.exists(file_path):
        raise FileNotFoundError(f"Le fichier {file_path} est introuvable.")

    with open(file_path, "r", encoding="utf-8") as f:
        text = f.read()

    # 1. Découpage en 4 chunks
    chunk_size = len(text) // 4
    parts = []
    for i in range(4):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < 3 else len(text)
        parts.append(text[start:end])
    
    # 2. Vectorisation dense (Embeddings)
    embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
    embeddings = embedding_model.encode(parts).tolist()

    # 3. Préparation LDA
    processed_chunks = [preprocess(chunk) for chunk in parts]
    id2word = corpora.Dictionary(processed_chunks)
    corpus = [id2word.doc2bow(text_tokens) for text_tokens in processed_chunks]

    lda_model = LdaModel(
        corpus=corpus, id2word=id2word, num_topics=2, random_state=100, passes=10
    )

    # 4. Extraction des 10 mots-clés par chunk via TF-IDF
    # On applique les stopwords directement dans le vectoriseur
    tfidf = TfidfVectorizer(stop_words=all_stopwords)
    tfidf_matrix = tfidf.fit_transform(parts)
    feature_names = np.array(tfidf.get_feature_names_out())

    # 5. Construction du résultat par chunk
    chunks_results = []
    for i, chunk_corpus in enumerate(corpus):
        # Distribution LDA
        lda_vector = lda_model[chunk_corpus]
        
        # Extraction des top 10 mots TF-IDF pour ce chunk spécifique
        row = tfidf_matrix[i].toarray().squeeze()
        # On récupère les indices des 10 plus grands scores TF-IDF
        # (Si le chunk a moins de 10 mots uniques, il prendra le max possible)
        top_indices = row.argsort()[-10:][::-1]
        top_keywords = [feature_names[idx] for idx in top_indices if row[idx] > 0]
        
        chunks_results.append({
            "chunk_index": i+1,
           # "text": parts[i],
           # "embedding": embeddings[i],
           # "lda_topics": lda_vector,
            "keywords": top_keywords  # Vos 10 mots-clés sont ici
        })

    return chunks_results
         
    