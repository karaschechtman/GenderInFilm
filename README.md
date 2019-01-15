# GenderInFilm
Simple Python interface for analyzing data about gender in film. Data from Agarwal et. al (2015) and the Internet Movie Database (IMDB). Bechdel scores were computed by Serina Chang and Navie Narula.

# Files
- DataLoader.py: Object to load information about movies from data/ to memory as Movie Python objects.
- Movie.py: Object storing information about a particular movie.
- Character.py: Object storing information about a particular character.

# Data
Data is stored in the data/ folder and contains both metadata about the movie and the processed Agarwal movie script. Metadata is as follows:

- IMBD: <imdb id, str>
- Title: <title, str>
- Year: <year, str>
- Genre: <genres, list of str>
- Director <director name, str>
- Rating: <rating between 0 and 10, float>
- Bechdel Score: <score, int>

# Authors
Created by Kara Schechtman (kws2121@columbia.edu) and Serina Chang (sc3003@columbia.edu).

# References
Apoor Agarwal, Sriramkumar Balabsumranian, Jiehan Zheng, and Sarthak Dash. 2014. *Parsing screenplays for extracting social networks from movies.* EACL-CLFL.
