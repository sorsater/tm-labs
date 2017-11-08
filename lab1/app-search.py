'''
Created by micso554 and ludno249
'''

import sys
import math
sys.path.append('..')

import nltk
from nltk.corpus import stopwords
from nltk.stem.snowball import SnowballStemmer
from scraper import filter_out_description, get_page, find_all_apps
from collections import Counter
import pickle
from res.w8m8 import progressbar

SUPER_URL = 'https://play.google.com/store/apps'

class InvertedIndex(object):
    '''
    An InvertedIndex-object is initiated with a list of links
    to different apps. The apps' descriptions are then parsed
    finally resulting in a vocabulary and a vector space with
    vectors for each app.

    The InvertedIndex can then be queried. The query is also 
    converted to a vector and matched against the different
    apps. The k-most simimlar apps are returned.
    '''
    def __init__(self, apps):
        self.stemmer = SnowballStemmer('english')
        self.apps = apps
        self.idf = {}
        self.vocab = {}
        self.tf_idf_vectors = {}
        self.documents = {}

        self.build_vocab()
        self.tf_idfer()

    def build_vocab(self):
        for i, app in enumerate(self.apps):
            doc, name = filter_out_description(get_page(app))
            terms = self.process_document(doc)
            progressbar((i+1)/len(self.apps), name)
            self.documents[name] = terms
            term_set = set(terms)
            for term in term_set:
                self.vocab[term] = self.vocab.get(term, []) + [name]
        
        # Map each term in vocabulary to an index
        self.idx_map = {term: idx for idx, term in enumerate(self.vocab.keys())}

    def tf_idfer(self):
        for i, (term, docs) in enumerate(self.vocab.items()):
            progressbar((i+1)/len(self.vocab), 'idfing')
            self.idf[term] = math.log(len(self.apps) / len(docs))

        for i, (name, document) in enumerate(self.documents.items()):
            progressbar((i+1)/len(self.documents), 'tf-idfing')
            vector = self.vectorize(document)
            self.tf_idf_vectors[name] = [vector, math.sqrt(sum([v**2 for v in vector]))]
            

    def process_document(self, document):
        stems = self.stemmer.stem(document)
        tokens = nltk.word_tokenize(stems)
        filtered_words = [token for token in tokens if token not in stopwords.words('english')]
        terms = [word.encode('ascii', errors='ignore').decode() for word in filtered_words]
        return terms
    
    def vectorize(self, terms):
        vector = [-1] * len(self.vocab)
        document_counts = Counter(terms)

        max_value = max(document_counts.values())

        for term, idx in self.idx_map.items():
            if term not in terms:
                vector[idx] = 0
            else:
                vector[idx] = document_counts[term] / max_value  * self.idf[term]
        
        return vector

    def query(self, query, k):
        terms = self.process_document(query)
        q_vector = self.vectorize(terms)
        if not sum(q_vector):
            return [[-1, 'Not found']]

        q_distance = math.sqrt(sum([v**2 for v in q_vector]))
        results = []

        for i, (name, (vector, distance)) in enumerate(self.tf_idf_vectors.items()):
            progressbar((i+1)/len(self.tf_idf_vectors))
            sim = sum([q_vector[i] * vector[i] for i in range(len(vector))]) / (q_distance * distance)
            results.append([sim, name])
        
        return [(score, app) for score, app in sorted(results, reverse=True)[:k] if score]

if __name__ == '__main__':
    apps_to_parse = 10

    if len(sys.argv) > 1 and (sys.argv[1] == 'p' or sys.argv[1] == '🍆'):
        if len(sys.argv) == 3:
            apps_to_parse = int(sys.argv[2])
        print('Finding apps')        
        apps = list(find_all_apps(SUPER_URL, apps_to_parse))
        print('\033[KFound {} apps'.format(len(apps)))
        ii = InvertedIndex(apps)
        with open('dumpis.pkl', 'wb') as pkl:
            pickle.dump(ii, pkl, protocol=pickle.HIGHEST_PROTOCOL)

    else:
        try:
            with open('dumpis.pkl', 'rb') as pkl:
                ii = pickle.load(pkl)
        except FileNotFoundError:
            print('No pickle file found. Run "app-search.py p [num apps]" to download and parse apps.')
            sys.exit(1)
            
    # Query loop
    while True:
        try:
            query, k = input('>>> Enter query and k: ').rsplit(maxsplit=1)
            k = int(k)
        except KeyboardInterrupt:
            print()
            break
        except Exception:
            print('Bad input')
        else:
            results = ii.query(query, k)
            for score, app in results:
                print(app)
