# Library
import re
import nltk

from preprocess_data import read_predata
from collections import Counter


# Helper Function
def build_inverted_index_orig_forms(documents):
    inverted_index = {}
    for no, strings in enumerate(documents):
        s = re.sub(r'([^\w\s])', '', strings)
        tokens = nltk.word_tokenize(s.lower())
        file_index = Counter(tokens)
        # update global index
        for term in file_index.keys():
            file_freq = file_index[term]
            if term not in inverted_index:
                inverted_index[term] = [file_freq, (no, file_freq)]
            else:
                inverted_index[term][0] += file_freq
                inverted_index[term].append((no, file_freq))
    return inverted_index


def generate_wildcard_options(wildcard, k, inverted_index):
    list_word = []
    for term in inverted_index.keys():
        string = wildcard.replace('*', '$')
        pad = '$' + string + '$'
        result = nltk.ngrams(pad, k)
        for i in list(result):
            tri = "".join(i)
            if re.search(tri, term):
                list_word.append(term)

    s_wildcard = wildcard.replace('*', '.+')
    return [string for string in list_word if re.match(s_wildcard, string)]


def search_wildcard(wildcard, k, index, docs):
    wildcard_options = generate_wildcard_options(wildcard, k, index)
    list_fact = []
    for term in wildcard_options:
        for line in docs:
            if re.search(term, line, flags=re.I):
                list_fact.append(line)
    return list_fact


def sent_to_words(sent):
    # splits sentence to words, filtering out non-alphabetical terms
    words = nltk.word_tokenize(sent)
    words_filtered = filter(lambda x: x.isalpha(), words)
    return words_filtered


movie_name = []
movie_dict = {}
for name, vote in zip(read_predata()['movie'], read_predata()['votes']):
    movie_name.append(name)
    movie_dict[name] = vote
index_orig_forms = build_inverted_index_orig_forms(movie_name)

vocabulary = Counter()
for name in movie_name:
    for word in sent_to_words(name.lower()):
        vocabulary[word] += 1

WORDS = vocabulary


# Norvig's spellchecker
def P(word, N=sum(WORDS.values())):
    """Probability of `word`."""
    return WORDS[word] / N


def candidates(word):
    """Generate possible spelling corrections for word."""
    return known([word]) or known(edits1(word)) or known(edits2(word)) or [word]


def known(words):
    """The subset of `words` that appear in the dictionary of WORDS."""
    return set(w for w in words if w in WORDS)


def edits1(word):
    """All edits that are one edit away from `word`."""
    letters = 'abcdefghijklmnopqrstuvwxyz'
    splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
    deletes = [L + R[1:] for L, R in splits if R]
    transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
    replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
    inserts = [L + c + R for L, R in splits for c in letters]
    return set(deletes + transposes + replaces + inserts)


def edits2(word):
    """All edits that are two edits away from `word`."""
    return (e2 for e1 in edits1(word) for e2 in edits1(e1))


def fix_typo_norvig(word) -> str:
    """Most probable spelling correction for word."""
    return max(candidates(word), key=P)


def title_suggestion(wildcard):
    top_k = 10
    new_wildcard = fix_typo_norvig(wildcard)

    def input_suggestion(wildcard, top_k):
        wildcard_results = search_wildcard(wildcard, 3, index_orig_forms, movie_name)
        input_suggest = []
        if len(wildcard_results) != 0:
            movie_result = []
            for r in wildcard_results:
                if r not in movie_result:
                    movie_result.append(r)

            movie_res = {}
            for name in movie_result:
                movie_res[name] = movie_dict[name]

            for i in sorted(movie_res.items(), key=lambda kv: (kv[1], kv[0]), reverse=True)[:top_k]:
                input_suggest.append(i[0])
                print(i[0], '- votes: ', i[1])

        return input_suggest

    result = input_suggestion(wildcard, top_k)
    result2 = input_suggestion(new_wildcard, top_k)

    if result != []:
        output = result
        print('proceed directly as a wildcard')
    elif result == [] and result2 != []:
        output = result2
        print("fixed by Norvig's spellchecker from {} to {}".format(wildcard, new_wildcard))
    else:
        output = 0
        print("Sorry, nothing to suggest! \nTry another input query!")

    return output
