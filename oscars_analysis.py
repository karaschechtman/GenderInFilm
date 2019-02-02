__author__ = 'Serina Chang <sc3003@columbia.edu>'
__date__ = 'Feb 01, 2019'

from data_loader import DataLoader
import matplotlib.pyplot as plt
import numpy as np

PATH_TO_OSCARS_CORPUS = './data/oscars/'
VALID_CATEGORIES = {'year':'Year', 'genre':'Genre', 'dir_gen':'Gender of Director', 'winner':'Oscar Best Picture Results', 'bechdel_pf':'Bechdel P/F', 'bechdel_score':'Bechdel Score'}

def counts_to_proportions(counts):
    """
    Transforms counts into proportions.
    """
    norm = np.sum(counts)
    return np.divide(np.multiply(counts, 100), norm)

def format_gender_breakdown(num_movies, female_ct, male_ct):
    """
    Formats a string for reporting movie statistics.
    """
    female_prop, male_prop = counts_to_proportions((female_ct, male_ct))
    return 'movie_ct={}, f_ct={} / {}%, m_ct={} / {}%'.format(num_movies, female_ct, round(female_prop, 2), male_ct, round(male_prop, 2))

def compute_cast_gender_breakdown(dl, category, top_billed_n=1000):
    """
    Primary function. Computes the distribution of genders in the cast, possibly
    broken down per some category, such as genre or year. The valid categories
    are listed in VALID_CATEGORIES. The total number of female and male cast
    members over the entire corpus are returned. If a category is specified,
    a dictionary is also returned; it maps category label e.g. "Comedy" to
    the total number of female and male cast members over the set of movies
    that fit this category. Note that a single movie can fit multiple categories,
    e.g. have multiple genres or have a female director and a male director.
    If a category is not specified, the return dictionary is empty.
    """
    if category:
        assert(category in VALID_CATEGORIES)
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
            elif category == 'dir_gen':
                if '(F)' in movie.director:  # has at least one female director
                    cats.append('Female Director')
                if '(M)' in movie.director:  # has at least one male director
                    cats.append('Male Director')
            elif category == 'winner':
                if movie.oscar_winner:
                    if movie.oscar_winner == True:
                        cats.append('Winner')
                    else:
                        cats.append('Non-winner')
            elif category == 'bechdel_pf':
                if movie.bechdel_score:
                    if movie.bechdel_score == 3:
                        cats.append('Pass')
                    else:
                        cats.append('Fail')
            else:  # bechdel score
                if movie.bechdel_score:
                    cats.append(movie.bechdel_score)
            for cat in cats:
                if cat not in per_category:
                    per_category[cat] = [0, 0, 0]
                per_category[cat][0] += 1  # number of movies
                per_category[cat][1] += female_ct  # number of female cast members
                per_category[cat][2] += male_ct  # number of male cast members
    return total_female_ct, total_male_ct, per_category

def compute_director_gender_breakdown(dl):
    """
    Computes the distribution of genders over all directors in
    the corpus.
    """
    female_ct = 0
    male_ct = 0
    for movie_id in dl.movies:
        movie = dl.get_movie(movie_id)
        directors = movie.director
        for dir in directors.split(', '):
            if '(F)' in dir:
                female_ct += 1
            elif '(M)' in dir:
                male_ct += 1
    return female_ct, male_ct

def make_gender_breakdown_bar_viz(global_f_ct, global_m_ct, per_category, cat_name, min_count=7):
    """
    Creates a bar graph of the per-category findings. Each category displays two bars,
    one for the percentage of cast members who are female and one for the percentage of
    cast members who are male (over all cast members in movies who fit the category).
    """
    sorted_cat_items = sorted(per_category.items(), key=lambda x:x[0])
    female_props = []
    male_props = []
    labels = []
    for cat, (num_movies, f_ct, m_ct) in sorted_cat_items:
        if num_movies >= min_count:
            labels.append('{}\n(n={})'.format(cat, num_movies))
            f_prop, m_prop = counts_to_proportions((f_ct, m_ct))
            female_props.append(f_prop)
            male_props.append(m_prop)
    bar_width = 0.4
    offset = bar_width/2
    x = np.arange(len(labels))
    plt.ylabel('Percentage of cast')
    plt.bar(x-offset, height=female_props, width=bar_width, color='#599190')
    plt.bar(x, height=female_props, width=0, tick_label=labels)
    plt.bar(x+offset, height=male_props, width=bar_width, color='#bb751b')
    global_f_prop, global_m_prop = counts_to_proportions((global_f_ct, global_m_ct))
    step = .2 if len(labels) > 5 else .1
    x_line = np.arange(0-bar_width, len(labels)-bar_width, step=step)
    plt.plot(x_line, [global_f_prop]*len(x_line), color='#599190', marker='.')
    plt.plot(x_line, [global_m_prop]*len(x_line), color='#bb751b', marker='.')
    plt.title('Distribution of Genders in Cast\nPer ' + VALID_CATEGORIES[cat_name], fontdict={'family':'serif', 'size':14})
    plt.show()

def make_gender_breakdown_pie_viz(group, female_ct, male_ct):
    """
    Creates a pie chart comparing the female count to male count for some group, e.g.
    directors.
    """
    plt.title('Distribution of Genders ' + group, fontdict={'family':'serif', 'size':16})
    plt.axis('equal')
    labels = ['Female', 'Male']
    sizes = [female_ct, male_ct]
    colors = ['#599190', '#bb751b']
    explode = (0, 0.01)
    patches, texts, autotexts = plt.pie(sizes, explode=explode, labels=labels, colors=colors, autopct='%1.1f%%')
    for text in texts:
        text.set_fontsize(12)
        text.set_family('serif')
    plt.show()

if __name__ == "__main__":
    dl = DataLoader(PATH_TO_OSCARS_CORPUS, verbose=False)
    corpus_size = len(dl.movies)

    category = 'winner'
    female_ct, male_ct, per_cat = compute_cast_gender_breakdown(dl, category=category)
    print('GLOBAL STATS:', format_gender_breakdown(corpus_size, female_ct, male_ct))
    sorted_cat_items = sorted(per_cat.items(), key=lambda x:x[0])
    for cat, (num_movies, f_ct, m_ct) in sorted_cat_items:
        print('{}: {}'.format(cat, format_gender_breakdown(num_movies, f_ct, m_ct)))
    make_gender_breakdown_bar_viz(female_ct, male_ct, per_cat, cat_name=category)

    # f_ct, m_ct = compute_director_gender_breakdown(dl)
    # print('Director stats:', format_gender_breakdown(corpus_size, f_ct, m_ct))
    # make_gender_breakdown_pie_viz('for Directors', f_ct, m_ct)

    # f_ct, m_ct, _ = compute_cast_gender_breakdown(dl, category=None)
    # print('Global stats:', format_gender_breakdown(corpus_size, f_ct, m_ct))
    # make_gender_breakdown_pie_viz('in Cast', f_ct, m_ct)
