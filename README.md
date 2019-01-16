# GenderInFilm
Simple Python interface for analyzing data about gender in film. Data from Agarwal et. al (2015) and the Internet Movie Database (IMDb). Bechdel scores are from bechdeltest.com.

# Files
- bechdel_20190115.json: contains the most updated Bechdel scores from bechdeltest.com as of Jan 15, 2019.
- data_loader.py: contains DataLoader object to load information about movies from data/to memory as Movie objects.
- make_data.py: extracts metadata from IMDb and Bechdel score from json files; writes them all into text files.
- Movie.py: Object storing information about a particular movie.
- Character.py: Object storing information about a particular character.

# Data
Data is stored in the data/ folder and contains both metadata about the movie and the processed Agarwal movie script. Metadata is as follows:

- IMBD: <imdb id, str>
- Title: <title, str>
- Year: <year, int>
- Genre: <genres, list of str>
- Director <director name, str>
- Rating: <rating between 0 and 10 (inclusive), float>
- Bechdel Score: <score, int>

# Authors
Created by Kara Schechtman (kws2121@columbia.edu) and Serina Chang (sc3003@columbia.edu).

# References
Apoor Agarwal, Sriramkumar Balabsumranian, Jiehan Zheng, and Sarthak Dash. 2014. *Parsing screenplays for extracting social networks from movies.* EACL-CLFL.