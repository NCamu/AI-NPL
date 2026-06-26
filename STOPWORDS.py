STOPWORDS = {
    "had", "to", "that", "very", "few", "were", "a", "an", "the", "in", "on", "of", "and", "or", "is", "was",
    "o","i","ii","iii","iv","v","vi","vii","viii","ix","x","xi","xii","xiii","xiv","xv","xvi","xvii","xviii","xix","xx",
    "oh", "ah", "alas", "hurrah", "eh", "well", "yes", "no", "hello", "please",
    "this", "these", "those", "each", "every", "all", "any", "both", "some", "such", "no", "nor", "not", "other", "another",
    "i", "me", "my", "myself", "we", "our", "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves",
    "he", "him", "his", "himself", "she", "her", "hers", "herself", "it", "its", "itself", "they", "them",
    "their", "theirs", "themselves", "what", "which", "who", "whom", "whose",
    "about", "above", "after", "against", "along", "among", "around", "at", "before", "behind", "below",
    "beneath", "beside", "between", "beyond", "by", "down", "during", "except", "for", "from", "inside",
    "into", "near", "off", "out", "outside", "over", "past", "through", "throughout", "till", "toward",
    "towards", "under", "underneath", "until", "up", "upon", "with", "within", "without", "but", "because",
    "as", "while", "again", "further", "then", "once", "so", "than",
    "am", "are", "be", "been", "being", "have", "has", "having", "do", "does", "did", "doing", "can",
    "could", "will", "would", "shall", "should", "may", "might", "must",
    "only", "too", "just", "now", "here", "there", "when", "where", "why", "how", "own", "same",
    "don't", "can't", "won't", "isn't", "aren't", "wasn't", "weren't", "haven't", "hasn't", "hadn't",
    "doesn't", "didn't", "shouldn't", "couldn't", "wouldn't", "mustn't", "shan't", "it's", "i'm",
    "you're", "he's", "she's", "we're", "they're", "i've", "you've", "we've", "they've", "i'd",
    "you'd", "he'd", "she'd", "we'd", "they'd", "i'll", "you'll", "he'll", "she'll", "we'll", "they'll",
    's', 't', 'll', 'd', 'm', 've', 're',
    "dont", "cant", "wont", "isnt", "arent", "wasnt", "werent", "havent", "hasnt", "hadnt",
    "doesnt", "didnt", "shouldnt", "couldnt", "wouldnt", "mustnt", "shant", "its", "im",
    "youre", "hes", "shes", "were", "theyre", "ive", "youve", "weve", "theyve", "id",
    "youd", "hed", "shed", "wed", "theyd", "ill", "youll", "hell", "shell", "well", "theyll",
    "monsieur", "madame", "mme", "mille", "mlle", "lord", "lady", "count", "comte", "marquis", "duchesse", "abbé", "monseigneur", "sir",
    "chapter"
}

SPE_EXCLU = {
        "nobody", "anybody", "somebody", "someone", "everyone", "anyone",
        "something", "anything", "everything", "nothing",
        "lewis carroll", "shakespeare", "tell", "said", "asked", "replied", 
        "spoke", "voice", "miss", "tarts", "tart", "soup", "wine", "tea", "bread", 
        "butter", "herald", "preface"
    }

NARRATIVE_NOISE = [
    # Verbes courants et leurs formes au passé / participe
    'get', 'got', 'getting', 'make', 'made', 'making', 'go', 'went', 'going', 
    'come', 'came', 'coming', 'take', 'took', 'taking', 'find', 'found', 'finding', 
    'seem', 'seemed', 'seeming', 'try', 'tried', 'trying', 'begin', 'began', 'begun', 
    'know', 'knew', 'known', 'see', 'saw', 'seen', 'look', 'looked', 'looking', 
    'think', 'thought', 'thinking', 'tell', 'told', 'ask', 'asked', 'hear', 'heard', 
    'put', 'give', 'gave', 'given', 'sit', 'sat', 'sitting', 'turn', 'turned', 
    'feel', 'felt', 'keep', 'kept', 'bring', 'brought', 'leave', 'left', 'call', 'called',
    
    # Noms abstraits, contenants ou parties du corps ultra-fréquents
    'thing', 'things', 'time', 'times', 'way', 'ways', 'day', 'days', 'word', 'words', 
    'place', 'places', 'part', 'parts', 'sort', 'sorts', 'kind', 'kinds', 'bit', 'bits', 
    'nothing', 'something', 'anything', 'everything', 'matter', 'head', 'hand', 'hands', 
    'eye', 'eyes', 'face', 'side', 'end', 'voice',
    
    # Adjectifs et adverbes de remplissage / transition
    'little', 'one', 'ones', 'two', 'three', 'like', 'good', 'long', 'great', 'old', 
    'young', 'small', 'big', 'large', 'first', 'last', 'next', 'much', 'many', 'whole', 
    'quite', 'rather', 'very', 'just', 'almost', 'back', 'away', 'upon', 'down', 'up', 
    'out', 'never', 'ever', 'always', 'soon', 'suddenly', 'well', 'oh', 'ah', 'yet', 
    'though', 'although', 'even', 'still', 'again', 'either', 'neither', 'too', 'also',
    'shook', 'cried', 'replied', # Ajout de verbes d'action/dialogue fréquents chez Carroll
    'said', 'says', 'say', 'go', 'went'
]