import os
import nltk
import numpy as np
from nltk.corpus import stopwords
from gensim import corpora
from gensim.models import LdaModel
from sentence_transformers import SentenceTransformer
from sklearn.feature_extraction.text import TfidfVectorizer
from STOPWORDS import STOPWORDS, NARRATIVE_NOISE
from CLUES import SPEAK_WORD

# Configuration des Stopwords
try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')
stop_words = list(stopwords.words('english'))

all_stopwords = list(set(stop_words).union(set(STOPWORDS)).union(set(SPEAK_WORD)).union(set(NARRATIVE_NOISE)))

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

    # ==========================================
    # 1. PRÉPARATION COMMUNE : Découpage en 4 chunks
    # ==========================================
    chunk_size = len(text) // 4
    parts = []
    for i in range(4):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < 3 else len(text)
        parts.append(text[start:end])
    
    # Switch d'algorithme : True = Conceptuel (LDA), False = Statistique brute (TF-IDF)
    lda = False
    chunks_results = []

    # ==========================================
    # 2. BRANCHE LDA (Analyse thématique)
    # ==========================================
    if lda:
        print('### 📖 USING LDA (topics) ###')
        # Entraînement fin sur les lignes/paragraphes pour avoir de la matière
        lines = [line.strip() for line in text.split('\n') if len(line.strip()) > 15]
        processed_lines = [preprocess(line) for line in lines if len(preprocess(line)) > 0]
            
        id2word = corpora.Dictionary(processed_lines)
        corpus_training = [id2word.doc2bow(text_tokens) for text_tokens in processed_lines]

        lda_model = LdaModel(
            corpus=corpus_training, id2word=id2word, num_topics=4, random_state=100, passes=15
        )
        
        # Projection et prédiction sur nos 4 grands chunks de texte
        for i, chunk_text in enumerate(parts):
            chunk_tokens = preprocess(chunk_text)
            chunk_bow = id2word.doc2bow(chunk_tokens)
            
            # Distribution des thèmes sur ce chunk
            lda_vector = lda_model[chunk_bow]
            
            # Extraction du thème dominant
            dominant_topic = max(lda_vector, key=lambda x: x[1])[0]
            
            # 1. On récupère TOUS les mots du thème dominant (sous forme de dictionnaire {mot: probabilité})
            topic_terms = dict(lda_model.show_topic(dominant_topic, topn=len(id2word)))
            
            # 2. On score uniquement les mots RÉELLEMENT présents dans ce chunk spécifique
            chunk_word_scores = []
            for word_id, count in chunk_bow:
                word = id2word[word_id]
                prob = topic_terms.get(word, 0.0)
                # Score = Importance du mot dans le thème X sa fréquence dans ce chapitre
                chunk_word_scores.append((word, prob * count))
            
            # 3. On trie par score décroissant pour obtenir les 10 meilleurs
            chunk_word_scores.sort(key=lambda x: x[1], reverse=True)
            top_keywords = [word for word, score in chunk_word_scores[:10]]
            
            chunks_results.append({
                "chunk_index": i + 1,
                "keywords": top_keywords
            })

    # ==========================================
    # 3. BRANCHE TF-IDF (Fréquence des mots)
    # ==========================================
    else:
        print('### 📊 USING TF-IDF (statistic) ###')

        # (Optionnel) Sauvegarde des embeddings si besoin plus tard
        embedding_model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')
        embeddings = embedding_model.encode(parts).tolist()

        tfidf = TfidfVectorizer(
            stop_words=all_stopwords, 
            ngram_range=(1, 2)
        )
        tfidf_matrix = tfidf.fit_transform(parts)
        feature_names = np.array(tfidf.get_feature_names_out())

        for i in range(4):
            row = tfidf_matrix[i].toarray().squeeze()
            top_indices = row.argsort()[-10:][::-1]
            top_keywords = [feature_names[idx] for idx in top_indices if row[idx] > 0]
            
            chunks_results.append({
                "chunk_index": i + 1,
                "keywords": top_keywords
            })

    return chunks_results
