# Library
from preprocess_data import read_predata
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity, linear_kernel

# count = CountVectorizer(analyzer='word', stop_words='english')
score = TfidfVectorizer(analyzer='word', stop_words='english')
# movies_matrix = count.fit_transform(read_predata()['list_bag'])
movies_matrix = score.fit_transform(read_predata()['list_bag'])

# cosine_sim = cosine_similarity(movies_matrix)
cosine_sim = linear_kernel(movies_matrix, movies_matrix)


def get_title_from_index(index):
    return read_predata()[read_predata()['Unnamed: 0'] == index]["movie"].values[0]


def get_index_from_title(title):
    return read_predata()[read_predata()["movie"] == title]["Unnamed: 0"].values[0]


def recommendations(movie_user_likes):
    movie_index = get_index_from_title(movie_user_likes)
    similar_movies = list(enumerate(cosine_sim[movie_index]))

    sorted_similar_movies = sorted(similar_movies, key=lambda x: x[1], reverse=True)[0:6]
    movie_rec_id = []
    i = 0
    # print("Top k similar movies to " + movie_user_likes + " are:\n")
    for element in sorted_similar_movies:
        movie_rec_id.append(element[0])
        # print(get_title_from_index(element[0]), 'similarity: ', element[1])
        i = i + 1
        if i > 5:
            break

    return movie_rec_id

# movie_user_likes = "Parasite"
# recommendations(movie_user_likes)
