__author__ = 'Serina Chang <sc3003@columbia.edu>'
__date__ = 'Jan 20, 2019'

from bs4 import BeautifulSoup
import json
import os
import pickle
import requests

'''Parsing from screenplay'''
def extract_sp_title_and_char_names(lines):
    """
    Extracts the title and character names in the screenplay lines.
    """
    title, char_names = None, set()
    for line in lines:
        line = line.strip()
        if title is None:
            potential_title = line.strip('M|').strip().strip('\"').lower()
            if len(potential_title) > 0:
                title = potential_title
        if line.startswith('C|'):
            char_names.add(line.strip('C|').strip().lower())
    return title, char_names

'''Parsing from imdb'''
IMDB_DOMAIN = 'https://www.imdb.com'
FEMALE_PRONOUNS = {'she', 'her', 'hers', 'herself'}
MALE_PRONOUNS = {'he', 'him', 'his', 'himself'}

def find_imdb_match(s_title, s_char_names, top_n=5):
    """
    Finds the IMDb search result that has the highest number of character matches with
    the character names from the screenplay.
    """
    title_toks = s_title.split()
    search_url = 'https://www.imdb.com/find?q={}&s=tt'.format('+'.join(title_toks))
    r = requests.get(search_url)
    soup = BeautifulSoup(r.content, 'html.parser')
    top_results = soup.find_all('tr', attrs={'class':'findResult'})
    if len(top_results) > top_n:
        top_results = top_results[:top_n]
    best_char_match = 0
    best_soup = None
    for r in top_results:
        result_url = IMDB_DOMAIN + r.find('a')['href']
        r = requests.get(result_url)
        soup = BeautifulSoup(r.content, 'html.parser')
        i_char_names = extract_imdb_char_names(soup)
        char_match = compute_char_match(s_char_names, i_char_names)
        if char_match > best_char_match:
            best_char_match = char_match
            best_soup = soup
    return best_soup

def extract_imdb_char_names(main_page):
    """
    Extracts character names from the main IMDb page for the movie.
    """
    characters = main_page.find_all('td', attrs={'class':'character'})
    char_names = set()
    for item in characters:
        c = clean_char_name_text(item.text)
        if len(c) > 0:
            char_names.add(c)
    return char_names

def clean_char_name_text(text):
    """
    Cleans a character name extracted from the main IMDb page for the movie.
    """
    text = text.replace(',', '')  # strip commas
    char_names = text.split('/')  # sometimes a row lists multiple character names
    cleaned_names = []
    for cn in char_names:
        cleaned_names.append(cn.split('(')[0].strip())
    return '/'.join(cleaned_names)

def compute_char_match(s_char_names, i_char_names):
    """
    Computes the number of matches between the extracted screenplay character names
    and the extracted IMDb names.
    """
    num_matched = 0
    for icn in i_char_names:
        sub_icns = icn.split('/')
        for sub_icn in sub_icns:
            if sub_icn.lower() in s_char_names:  # s_char_names are all lowercased
                num_matched += 1
    return num_matched

def extract_imdb_id(main_page):
    """
    Extracts the IMDb ID from the main IMDb page for the movie.
    """
    id_wrapper = main_page.find('meta', attrs={'property':'pageId'})
    if id_wrapper is not None:
        return id_wrapper['content'].strip('tt')
    return None

def extract_imdb_headings(main_page):
    """
    Extracts the movie title, year, and list of genres from the main
    IMDb page for the movie.
    """
    title, year, genres = None, None, set()
    wrapper = main_page.find('div', attrs={'class':'title_wrapper'})
    if wrapper is not None:
        heading = wrapper.find('h1')
        if heading is not None:
            title = heading.text.replace('\xa0', ' ').rsplit('(', 1)[0].strip()
            year_wrap = heading.find('span', attrs={'id':'titleYear'})
            if year_wrap is not None:
                year = year_wrap.text.strip('(').strip(')')
        subtext = wrapper.find('div', attrs={'class':'subtext'})
        if subtext is not None:
            links = subtext.find_all('a')
            for l in links:
                if 'genres=' in l['href']:
                    genres.add(l.text)
    return title, year, genres

def extract_imdb_rating(main_page):
    """
    Extracts the IMDb rating from the main IMDb page for the movie.
    """
    rating_wrap = main_page.find('span', attrs={'itemprop':'ratingValue'})
    if rating_wrap is not None:
        return float(rating_wrap.text)
    return None

def make_full_credits_url(imdb_id):
    """
    Makes the URL for the IMDb full credits page of the movie, given its
    IMDb ID.
    """
    return '{}/title/tt{}/fullcredits'.format(IMDB_DOMAIN, imdb_id)

def extract_credits(credits_page):
    """
    Extracts the full list of director and cast credits from the
    IMDb full credits page of the movie.
    director tuples: < director name, director gender >
    cast tuples: < character name, actor name, actor gender >
    """
    dir_tuples = []
    char_tuples = []
    headers = credits_page.find_all('h4', attrs={'class':'dataHeaderWithBorder'})
    tables = credits_page.find_all('table', attrs={'class':'simpleTable simpleCreditsTable'})
    for h, t in zip(headers, tables):
        if 'Directed by' in h.text:
            for name_item in t.find_all('td', attrs={'class':'name'}):
                name = name_item.text.strip()
                bio_url = IMDB_DOMAIN + name_item.find('a')['href']
                bio_soup = BeautifulSoup(requests.get(bio_url).content, 'html.parser')
                gender = predict_gender_from_bio(bio_soup)
                dir_tuples.append((name, gender))
            break
    cast_table = credits_page.find('table', attrs={'class':'cast_list'})
    if cast_table is not None:
        for row in cast_table.find_all('tr'):
            if row.has_attr('class') and row['class'] != 'classlist_label':
                act_name, char_name = row.text.split('...')
                act_name = act_name.strip()
                char_name = clean_char_name_text(char_name)
                gender = None
                photo = row.find('td', attrs={'class':'primary_photo'})
                if photo is not None:
                    link = photo.find('a')
                    if link is not None:
                        bio_url = IMDB_DOMAIN + link['href']
                        bio_soup = BeautifulSoup(requests.get(bio_url).content, 'html.parser')
                        gender = predict_gender_from_bio(bio_soup)
                char_tuples.append((char_name, act_name, gender))
    return dir_tuples, char_tuples

def predict_gender_from_bio(bio_page):
    """
    Predicts the gender from the IMDb bio page for a (real) person, e.g.
    a director or an actor.
    """
    jobs = bio_page.find('div', attrs={'id':'name-job-categories'})
    if jobs is not None:
        text = jobs.text
        # Actress / Actor are gendered on IMDb; others, like Producer, are not
        if 'Actress' in text:
            return 'F'
        elif 'Actor' in text:
            return 'M'
    bio = bio_page.find('div', attrs={'id':'name-bio-text'})
    if bio is not None:
        text = bio.text.lower()
        fcount = 0
        mcount = 0
        for tok in text.split():
            if tok in FEMALE_PRONOUNS:
                fcount += 1
            elif tok in MALE_PRONOUNS:
                mcount += 1
        if fcount > mcount:
            return 'F'
        if mcount > fcount:
            return 'M'
    return None

'''Bechdel functions'''
PATH_TO_BECHDEL = '../data/bechdel/bechdel_20190124.json'

def make_bechdel_dict():
    """
    Makes a dictionary of IMDb ID mapped to Bechdel rating.
    """
    bechdel_json = json.load(open(PATH_TO_BECHDEL, 'r'))
    bechdel_dict = {}
    for entry in bechdel_json:
        bechdel_dict[str(entry['imdbid'])] = str(entry['rating'])
    return bechdel_dict

'''Write to file'''
PATH_TO_SCREENPLAYS = './data/agarwal_screenplays/'
PATH_TO_SKIPPED = './data/skipped.pkl'
PATH_TO_DATA = './data/data_with_screenplays/'

def convert_screenplays_to_dl_files(continue_work=True, max_files=None):
    """
    For each screenplay in the original Agarwal dataset, this function tries to create
    a new text file that includes metadata pulled from IMDb and bechdeltest.com,
    followed by the original screenplay. From IMDb, the metadata consists of: ID, title,
    year, genres, director(s)/gender(s), movie rating, and characters/actors/genders,
    and from bechdeltest.com, we find the Bechdel score if applicable.
    The creation of the new file fails if:
    (1) no title or character name can be extracted from the original screenplay;
    (2) no IMDb match is found for the screenplay's extracted title + character names;
    (3) some ValueError occurs while making requests and parsing IMDb pages.
    """
    screenplay_files = os.listdir(PATH_TO_SCREENPLAYS)
    if continue_work:
        skipped = pickle.load(open(PATH_TO_SKIPPED, 'rb'))
        processed_before = len(os.listdir(PATH_TO_DATA)) + len(skipped)
        print('Processed {} screenplays before'.format(processed_before))
        screenplay_files = screenplay_files[processed_before:]
    else:
        skipped = set()
    if max_files is not None and len(screenplay_files) > max_files:
        screenplay_files = screenplay_files[:max_files]
    print('Processing {} screenplays...'.format(len(screenplay_files)))
    bechdel_dict = make_bechdel_dict()
    for s_fn in screenplay_files:
        with open(PATH_TO_SCREENPLAYS + s_fn, 'r') as s_file:
            try:
                s_lines = s_file.readlines()
                s_title, s_char_names = extract_sp_title_and_char_names(s_lines)
                if len(s_title) == 0:
                    print('Missing title for', s_fn)
                    skipped.add(s_fn)
                elif len(s_char_names) == 0:
                    print('Missing character names for', s_title.upper())
                    skipped.add(s_fn)
                else:
                    soup = find_imdb_match(s_title, s_char_names)
                    if soup is None:
                        print('Could not find IMDb match for', s_title.upper())
                        skipped.add(s_fn)
                    else:
                        print('Success: making DataLoader file for', s_title.upper())
                        ID = extract_imdb_id(soup)
                        title, year, genres = extract_imdb_headings(soup)
                        rating = extract_imdb_rating(soup)
                        credits_url = make_full_credits_url(ID)
                        credits_page = BeautifulSoup(requests.get(credits_url).content, 'html.parser')
                        dir_tuples, char_tuples = extract_credits(credits_page)
                        bechdel_score = bechdel_dict.get(ID)
                        metadata = format_metadata(ID, title, year, genres, rating, dir_tuples, char_tuples, bechdel_score)
                        new_fn = PATH_TO_DATA + '{}___{}.txt'.format('_'.join(title.split()), year)
                        with open(new_fn, 'w') as new_f:
                            new_f.write(metadata)
                            new_f.write('\n')
                            for line in s_lines:
                                new_f.write(line)
            except ValueError:
                print('ValueError:', s_fn)
                skipped.add(s_fn)
            pickle.dump(skipped, open(PATH_TO_SKIPPED, 'wb'))
    print('Progress: {} successful, {} skipped'.format(len(os.listdir(PATH_TO_DATA)), len(skipped)))

def format_metadata(ID, title, year, genres, rating, dir_tuples, char_tuples, bechdel_score):
    """
    Formats metadata into a string.
    """
    genres = ', '.join(sorted(list(genres)))  # sort alphabetically
    tuples_as_strings = []
    for d, g in dir_tuples:
        if g is None:
            g = '?'
        tuples_as_strings.append('{} ({})'.format(d, g))
    dir_str = ', '.join(tuples_as_strings)
    if bechdel_score is None:
        bechdel_score = 'N/A'
    tuples_as_strings = []
    for c, a, g in char_tuples:
        if g is None:
            g = '?'
        tuples_as_strings.append('{} | {} ({})'.format(c, a, g))
    char_str = ', '.join(tuples_as_strings)
    return 'IMDB: {}\nTitle: {}\nYear: {}\nGenre: {}\nDirector: {}\nRating: {}\nBechdel score: {}\nIMDB Cast: {}\n'.format(
        ID, title, year, genres, dir_str, rating, bechdel_score, char_str)

def demo(imdb_movie_url, bechdel_dict):
    """
    Retrieves the metadata for some movie and prints the formatted metadata string.
    """
    main_page = BeautifulSoup(requests.get(imdb_movie_url).content, 'html.parser')
    ID = extract_imdb_id(main_page)
    title, year, genres = extract_imdb_headings(main_page)
    rating = extract_imdb_rating(main_page)
    credits_url = make_full_credits_url(ID)
    print(credits_url)
    credits_page = BeautifulSoup(requests.get(credits_url).content, 'html.parser')
    dir_tuples, char_tuples = extract_credits(credits_page)
    bechdel_score = bechdel_dict.get(ID)
    metadata = format_metadata(ID, title, year, genres, rating, dir_tuples, char_tuples, bechdel_score)
    print(metadata)

if __name__ == "__main__":
    # bechdel_dict = make_bechdel_dict()
    # carol_url = 'https://www.imdb.com/title/tt2402927/'
    # bob_url = 'https://www.imdb.com/title/tt0103241/'  # has multiname characters
    # thelma_and_louise_url = 'https://www.imdb.com/title/tt0103074/'  # has commas in char names
    # four_rooms_url = 'https://www.imdb.com/title/tt0113101/'  # has multiple directors
    # demo(carol_url, bechdel_dict)
    convert_screenplays_to_dl_files(continue_work=True)
