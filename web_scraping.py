# Library
import pandas as pd
import re

from requests import get
from bs4 import BeautifulSoup
from time import time, sleep
from random import randint
from IPython.core.display import clear_output

total_movies = 5000
start = [str(i + 1) for i in range(0, total_movies, 250)]

# Declaring the lists to store data in
image_link = []
movie_name = []
movie_year = []
certificate = []
duration = []
genre = []
imdb_ratings = []
overview = []
directors = []
stars = []
votes = []

# Preparing the monitoring of the loop
start_time = time()
requests = 0
i = 0
# For every start number of movie
for st in start:
    # Make a get request for 100k movie title without filter url =
    # 'https://www.imdb.com/search/title/?moviemeter=101357&sort=num_votes,desc&count=250&start='+st+'&ref_=adv_nxt'
    # with filter: Feature Film/TV Series, Released at least 1990-01-01
    url = 'https://www.imdb.com/search/title/?title_type=feature,tv_series&release_date=1990-01-01,&sort=num_votes,' \
          'desc&count=250&start=' + st + '&ref_=adv_nxt '
    headers = {"Accept-Language": "en-US, en;q=0.5"}
    response = get(url, headers=headers)

    # Pause the loop
    sleep(randint(8, 15))

    # Monitor the requests
    requests += 1
    elapsed_time = time() - start_time
    print('Request: {}; Frequency: {} requests/s'.format(requests, requests / elapsed_time))
    clear_output(wait=True)

    # Parse the content of the request with BeautifulSoup
    page_html = BeautifulSoup(response.text, 'html.parser')

    # Select all the 250 movie containers from a single page
    mv_containers = page_html.find_all('div', class_='lister-item mode-advanced')

    # For every movie
    for container in mv_containers:
        # If the movie has Metascore, then extract:
        # if container.find('div', class_ = 'ratings-metascore') is not None:
        # Image link
        link = container.find('img')
        image_link.append(link.get('loadlate'))

        # The name of movie
        name = container.h3.a.text
        movie_name.append(name)

        # The year of movie
        year = container.h3.find('span', class_='lister-item-year').text
        movie_year.append(year)

        # Certificate
        try:
            cert = container.p.find('span', class_='certificate').text
            certificate.append(cert.replace('\n', '').strip())
        except:
            certificate.append('Not Rated')

        # Duration
        try:
            runtime = container.p.find('span', class_='runtime').text
            duration.append(runtime.replace('\n', '').strip())
        except:
            duration.append('Unknown')

        # The genre of movie
        gen = container.p.find('span', class_='genre').text
        genre.append(gen.replace('\n', '').strip())

        # The IMDB rating
        imdb = float(container.strong.text)
        imdb_ratings.append(imdb)

        # Description
        view = container.find('div', class_="lister-item-content").text
        res = view.replace('\n', '')
        if 'Metascore' in res:
            if 'Director' in res:
                result = re.search('Metascore(.*)Director', res)
            else:
                result = re.search('Metascore(.*)Star', res)
        else:
            if 'Director' in res:
                result = re.search('X(.*)Director', res)
            else:
                result = re.search('X(.*)Star', res)
        overview.append(result.group(1).strip())

        # The director of movie
        try:
            if 'Director' in res:
                direct = container.find('p', class_="").text
                movie_dir = direct.split('|')[0].rstrip()
                movie_dirs = movie_dir.split('\n')[2:]
                movie_director = [movie_dir.replace(",", "").strip() for movie_dir in movie_dirs]
                director_name = ', '.join(str(name) for name in movie_director)
                directors.append([director_name])
            else:
                directors.append('')
        except:
            directors.append('')

        # Stars
        try:
            if 'Director' in res:
                star = container.find('p', class_="").text
                m_star = star.split('|')[1].rstrip()
                movie_st = m_star.split('\n')[2:]
                movie_star = [m_star.replace(",", "").strip() for m_star in movie_st]
                star_name = ', '.join(str(name) for name in movie_star)
                stars.append([star_name])
            else:
                star = container.find('p', class_="").text
                m_star = star.split('|')[0].rstrip()
                movie_st = m_star.split('\n')[2:]
                movie_st.pop(0)
                movie_star = [m_star.replace(",", "").strip() for m_star in movie_st]
                star_name = ', '.join(str(name) for name in movie_star)
                stars.append([star_name])
        except:
            stars.append('')

        # The number of votes
        vote = container.find('span', attrs={'name': 'nv'})['data-value']
        votes.append(int(vote))

        print(i)
        clear_output(wait=True)
        i += 1

crawl_time = time() - start_time
print("total time getting data is {} ms".format(crawl_time))

# Preprocessing Data
# Reformat image link
k = 27
img_size = 'V1_SY1000_CR0,0,675,1000_AL_.jpg'
img_poster = [sub[:-k] + img_size for sub in image_link]

# Reformat year
fix_year = []
s = '-'
for year in movie_year:
    temp = re.findall(r'\d+', year)
    if len(temp) > 1:
        res = s.join(temp)
        fix_year.append(res)
    else:
        res = list(map(int, temp))
        fix_year.append(*res)

# Combine all data
movie_rating = pd.DataFrame({'movie_img': img_poster,
                             'movie': movie_name,
                             'year': fix_year,
                             'certificate': certificate,
                             'duration': duration,
                             'genre': genre,
                             'description': overview,
                             'director': directors,
                             'stars': stars,
                             'imdb': imdb_ratings,
                             'votes': votes
                            })

# Save to csv file
file_name = ''
movie_rating.to_csv('file_name')