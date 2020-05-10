# Library
import pandas as pd
import nltk


# Helper Function
class Preprocessor:
    def __init__(self):
        self.stop_words = set(nltk.corpus.stopwords.words('english'))
        self.ps = nltk.stem.PorterStemmer()

    # word tokenize text using nltk lib
    def tokenize(self, text):
        return nltk.word_tokenize(text)

    # stem word using provided stemmer
    def stem(self, word, stemmer):
        return stemmer.stem(word)

    # check if word is appropriate - not a stop word and isalpha,
    # i.e consists of letters, not punctuation, numbers, dates
    def is_apt_word(self, word):
        return word not in self.stop_words and word.isalpha()

    # combines all previous methods together
    # tokenizes lowercased text and stems it, ignoring not appropriate words
    def preprocess(self, text):
        tokenized = self.tokenize(text.lower())
        return [self.stem(w, self.ps) for w in tokenized if self.is_apt_word(w)]


def short(x):
    lst = []
    for i in x:
        y = i.replace(' ', '')
        z = y.lower()
        lst.append(z)
    return lst


def read_predata():
    # Read File CSV
    file_path = 'Dataset/movie_data_5k.csv'
    movie_rating = pd.read_csv(file_path)
    movies = movie_rating

    # Preprocessing Data
    movies['director'] = movies['director'].fillna('')
    movies['stars'] = movies['stars'].fillna('')
    movies['director'].isnull().any()
    movies['stars'].isnull().any()

    movies['stars'] = movies['stars'].str.split(',')
    movies['n_stars'] = movies['stars'].apply(len)
    movies['stars_3'] = movies['stars'].apply(lambda x: x[:3] if len(x) >= 3 else x)
    movies['stars_short'] = movies['stars_3'].apply(short)

    movies['director_2'] = movies['director'].apply(lambda x: [x, x])
    movies['director_short'] = movies['director_2'].apply(short)

    movies['genre'] = movies['genre'].str.split(',')
    movies['genre_short'] = movies['genre'].apply(short)

    # movies['keywords'] = movies['description'].apply(Preprocessor().preprocess)

    # movies['bag'] = (movies['stars_short'] + movies['director_short'] + movies['genre_short'] + movies[
    #    'keywords']).apply(lambda x: [s for s in x if s])
    movies['bag'] = (movies['stars_short'] + movies['director_short'] + movies['genre_short']).apply(
        lambda x: [s for s in x if s])
    movies['bag_len'] = movies['bag'].apply(len)
    movies['list_bag'] = movies['bag'].apply(lambda x: ' '.join(x))

    return movies
