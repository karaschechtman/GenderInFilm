from bs4 import BeautifulSoup
import json
import os
import requests

'''Parsing from screenplay'''
# Extract the title and character names from the screenplay
def extract_sp_title_and_char_names(lines):
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

# Find IMDb search result that has the highest number of character matches with the
# character names extracted from the screenplay
def find_imdb_match(s_title, s_char_names, top_n=5):
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

def extract_imdb_char_names(soup):
    characters = soup.find_all('td', attrs={'class':'character'})
    char_names = set()
    for item in characters:
        c = clean_char_name_text(item.text)
        if len(c) > 0:
            char_names.add(c)
    return char_names

def clean_char_name_text(text):
    char_names = text.split('/')  # sometimes a row lists multiple character names
    cleaned_names = []
    for cn in char_names:
        cleaned_names.append(cn.split('(')[0].strip())
    return '/'.join(cleaned_names)

def compute_char_match(s_char_names, i_char_names):
    num_matched = 0
    for icn in i_char_names:
        sub_icns = icn.split('/')
        for sub_icn in sub_icns:
            if sub_icn.lower() in s_char_names:  # s_char_names are all lowercased
                num_matched += 1
    return num_matched

def extract_imdb_id(soup):
    id_wrapper = soup.find('meta', attrs={'property':'pageId'})
    if id_wrapper is not None:
        return id_wrapper['content'].strip('tt')
    return None

def extract_imdb_headings(soup):
    title, year, genres = None, None, set()
    wrapper = soup.find('div', attrs={'class':'title_wrapper'})
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

def extract_imdb_rating(soup):
    rating_wrap = soup.find('span', attrs={'itemprop':'ratingValue'})
    if rating_wrap is not None:
        return float(rating_wrap.text)
    return None

def extract_imdb_director_and_gender(soup):
    crew_list = soup.find_all('div', attrs={'class':'credit_summary_item'})
    for item in crew_list:
        text = item.text
        if 'Director' in text:
            name = text.split(':')[1].strip()
            gender = None
            link = item.find('a')
            if link is not None:
                bio_url = IMDB_DOMAIN + link['href']
                bio_soup = BeautifulSoup(requests.get(bio_url).content, 'html.parser')
                gender = predict_gender_from_bio(bio_soup)
            return name, gender
    return None, None

# returns list of tuples: < character name, actor name, actor gender >
def extract_imdb_char_tuples(soup):
    tuples = []
    table = soup.find('table', attrs={'class':'cast_list'})
    for row in table.find_all('tr'):
        if row.has_attr('class') and row['class'] != 'classlist_label':  # first row
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
            tuples.append((char_name, act_name, gender))
    return tuples

def predict_gender_from_bio(soup):
    jobs = soup.find('div', attrs={'id':'name-job-categories'})
    if jobs is not None:
        text = jobs.text
        # Actress / Actor are gendered on IMDb; others, like Producer, are not
        if 'Actress' in text:
            return 'F'
        elif 'Actor' in text:
            return 'M'
    bio = soup.find('div', attrs={'id':'name-bio-text'})
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
PATH_TO_BECHDEL = 'bechdel_20190115.json'

def make_bechdel_dict():
    bechdel_json = json.load(open(PATH_TO_BECHDEL, 'r'))
    bechdel_dict = {}
    for entry in bechdel_json:
        bechdel_dict[str(entry['imdbid'])] = str(entry['rating'])
    return bechdel_dict

'''Write to file'''
PATH_TO_SCREENPLAYS = './data/agarwal_screenplays/'
PATH_TO_DATA = './data/data_loader_txt/'

def convert_screenplays_to_dl_files(continue_work=True, max_files=None):
    screenplay_files = os.listdir(PATH_TO_SCREENPLAYS)
    if continue_work:
        already_done = len(os.listdir(PATH_TO_DATA))
        print('Already finished {} screenplays'.format(already_done))
        screenplay_files = screenplay_files[already_done:]
    if max_files is not None and len(screenplay_files) > max_files:
        screenplay_files = screenplay_files[:max_files]
    print('Processing {} screenplays...'.format(len(screenplay_files)))
    bechdel_dict = make_bechdel_dict()
    for fn in screenplay_files:
        with open(PATH_TO_SCREENPLAYS + fn, 'r') as s_file:
            try:
                s_lines = s_file.readlines()
                s_title, s_char_names = extract_sp_title_and_char_names(s_lines)
                if len(s_title) > 0 and len(s_char_names) > 0:
                    soup = find_imdb_match(s_title, s_char_names)
                    if soup is not None:
                        print('Making DataLoader file for {}...'.format(s_title.upper()))
                        ID = extract_imdb_id(soup)
                        title, year, genres = extract_imdb_headings(soup)
                        rating = extract_imdb_rating(soup)
                        dir_name, dir_gender = extract_imdb_director_and_gender(soup)
                        char_tuples = extract_imdb_char_tuples(soup)  # character name, actor name, actor gender
                        bechdel_score = bechdel_dict.get(ID)
                        metadata = format_metadata(ID, title, year, genres, rating, dir_name, dir_gender, char_tuples, bechdel_score)
                        new_fn = PATH_TO_DATA + '{}___{}.txt'.format('_'.join(title.split()), year)
                        with open(new_fn, 'w') as new_f:
                            new_f.write(metadata)
                            new_f.write('\n')
                            for line in s_lines:
                                new_f.write(line)
            except ValueError:
                print(fn)

def format_metadata(ID, title, year, genres, rating, dir_name, dir_gender, char_tuples, bechdel_score):
    if dir_gender is None:
        dir_gender = '?'
    if bechdel_score is None:
        bechdel_score = 'N/A'
    genres = ', '.join(sorted(list(genres)))  # sort alphabetically
    string = 'IMDB: {}\nTitle: {}\nYear: {}\nGenre: {}\nDirector: {} ({})\nRating: {}\nBechdel score: {}\nIMDB Cast: '.format(
        ID, title, year, genres, dir_name, dir_gender, rating, bechdel_score)
    tuples_as_strings = []
    for c, a, g in char_tuples:
        if g is None:
            g = '?'
        tuples_as_strings.append('{} | {} ({})'.format(c, a, g))
    string += ', '.join(tuples_as_strings) + '\n'
    return string

def demo(imdb_movie_url, bechdel_dict):
    soup = BeautifulSoup(requests.get(imdb_movie_url).content, 'html.parser')
    ID = extract_imdb_id(soup)
    title, year, genres = extract_imdb_headings(soup)
    rating = extract_imdb_rating(soup)
    dir_name, dir_gender = extract_imdb_director_and_gender(soup)
    char_tuples = extract_imdb_char_tuples(soup)
    bechdel_score = bechdel_dict.get(ID)
    metadata = format_metadata(ID, title, year, genres, rating, dir_name, dir_gender, char_tuples, bechdel_score)
    print(metadata)

if __name__ == "__main__":
    bechdel_dict = make_bechdel_dict()
    carol_url = 'https://www.imdb.com/title/tt2402927/'
    pitch_perfect_url = 'https://www.imdb.com/title/tt1981677/'
    has_multiname_characters = 'https://www.imdb.com/title/tt0103241/'
    # demo(carol_url, bechdel_dict)
    convert_screenplays_to_dl_files(continue_work=True)
