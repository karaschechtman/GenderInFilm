from data_loader import DataLoader
import matplotlib.pyplot as plt
import numpy as np

PATH_TO_SCRIPTS_CORPUS = './data/movies/'
PATH_TO_OSCARS_CORPUS = './data/oscars/'

VALID_MODES = {'year':'Year', 'genre':'Genre', 'dir_gen':'Gender of Director'}

def gender_breakdown(dl, category=None, top_billed_n=1000):
    if category:
        assert(category in VALID_MODES)
    total_female_ct = 0
    total_male_ct = 0
    per_category = {}  # category mapped to (num_movies, num_females, num_males)
    for movie_id in dl.movies:
        movie = dl.get_movie(movie_id)
        female_ct = 0
        male_ct = 0
        billing_idx = 0
        for char_name in movie.imdb_cast:
            actor, gender = movie.imdb_cast[char_name]
            if gender == 'F':
                female_ct += 1
            elif gender == 'M':
                male_ct +=1
            billing_idx += 1
            if billing_idx == top_billed_n:
                break
        total_female_ct += female_ct
        total_male_ct += male_ct
        if category:
            cats = []
            if category == 'year':
                cats.append(movie.year)
            elif category == 'genre':
                for genre in movie.genre:
                    cats.append(genre)
            else:
                if '(F)' in movie.director:
                    cats.append('Female Director')
                if '(M)' in movie.director:
                    cats.append('Male Director')
            for cat in cats:
                if cat not in per_category:
                    per_category[cat] = [0, 0, 0]
                per_category[cat][0] += 1  # number of movies
                per_category[cat][1] += female_ct  # number of female characters
                per_category[cat][2] += male_ct  # number of male characters
    return total_female_ct, total_male_ct, per_category

def get_proportions(female_ct, male_ct):
    char_ct = female_ct + male_ct
    female_prop = female_ct * 100 / char_ct
    male_prop = male_ct * 100 / char_ct
    return female_prop, male_prop

def format_stats(num_movies, female_ct, male_ct):
    female_prop, male_prop = get_proportions(female_ct, male_ct)
    return 'movie_ct={}, f_ct={} / {}%, m_ct={} / {}%'.format(num_movies, female_ct, round(female_prop, 3), male_ct, round(male_prop, 3))

def viz(global_f_ct, global_m_ct, per_category, title, min_count=7):
    sorted_cat_items = sorted(per_category.items(), key=lambda x:x[0])
    female_props = []
    male_props = []
    labels = []
    for cat, (num_movies, f_ct, m_ct) in sorted_cat_items:
        if num_movies >= min_count:
            labels.append('{}\n(n={})'.format(cat, num_movies))
            f_prop, m_prop = get_proportions(f_ct, m_ct)
            female_props.append(f_prop)
            male_props.append(m_prop)
    bar_width = 0.4
    offset = bar_width/2
    x = np.arange(len(labels))
    plt.bar(x-offset, height=female_props, width=bar_width, color='pink')
    plt.bar(x, height=female_props, width=0, tick_label=labels)
    plt.bar(x+offset, height=male_props, width=bar_width, color='lightblue')
    global_f_prop, global_m_prop = get_proportions(global_f_ct, global_m_ct)
    x_line = np.arange(0-bar_width, len(labels)-bar_width, step=.2)
    plt.plot(x_line, [global_f_prop]*len(x_line), 'r.')
    plt.plot(x_line, [global_m_prop]*len(x_line), 'b.')
    plt.title(title)
    plt.show()

if __name__ == "__main__":
    dl = DataLoader(PATH_TO_OSCARS_CORPUS, verbose=False)
    category= 'year'
    corpus_size = len(dl.movies)
    female_ct, male_ct, per_cat = gender_breakdown(dl, category=category)
    print('GLOBAL STATS: ' + format_stats(corpus_size, female_ct, male_ct))
    sorted_cat_items = sorted(per_cat.items(), key=lambda x:x[0])
    for cat, (num_movies, f_ct, m_ct) in sorted_cat_items:
        print('{}: {}'.format(cat, format_stats(num_movies, f_ct, m_ct)))
    viz(female_ct, male_ct, per_cat, 'Distribution of Genders in Cast\nPer ' + VALID_MODES[category])