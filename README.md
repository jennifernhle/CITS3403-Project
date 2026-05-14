# Popcorn Journal

Popcorn Journal is a web application for movie enthusiasts to track their movie watching habits, create reviews, manage watchlists, and share lists with the community. Users can log movies they've watched, rate and review them, follow other users and see their reviews and lists, and discover new movies through community lists.

| Student ID | Student Name    | GitHub Username   |
| ---------- | --------------- | ----------------- |
| 24530845   | Jazmine Overend | jaz0555           |
| 24598109   | Jingbo Wang     | jingboouu         |
| 24502788   | Jennifer Le     | jennifernhle      |
| 24310849   | Tony Zhang      | zhiyizhang984-ops |

## Design

### Features

- User authentication (registration, login, logout)
- Movie database that users can gradually add to, with option for TMDB integration for movie importing
- Personal watchlists
- Movie reviews and ratings
- Custom lists (public and private)
- Social features (follow users, like reviews)
- Search functionality for movies
- Responsive design with Bootstrap

### Structure and Workflow

- **Home Page**
  Users can see community reviews, reviews of people they follow, profile statistics, and public lists
  - Tabs to toggle between community reviews and reviews of people the user follows
  - Profile statistics including number of movies in watchlist, and number of reviews, lists, and followers
  - A list of the custom lists that are public to the community

- **Add Movies Page**
  Users can add movies to the local database
  - Input the title, director, release year, synopsis, and upload the movie poster to add a movie to the local database

- **Search Movies Page**
  Users can search the local database, or optionally choose to import movies from TheMovieDatabase (TMDB) for movies to the local database to view, add to their watchlist, or add to their custom lists
  - Tabs to toggle between local database and TMDB discovery (depending on initial setup)
  - Users can filter by title, genre, or release year of the film
  - From the local database, users can search for a movie to either view its details or add to watchlist directly
  - If using TMDB, users can search movies by title, genre or release year and import to the local database rather than manually adding movies

- **Movie Overview Page**
  Users can see the details and user reviews of the film, as well as having options to add to a custom list, or to a personal watchlist
  - Users can create, edit, or delete their reviews
  - Users can add the movie to their custom lists or watchlist
  - Custom lists can be created directly from this page and be set to private or public
  - Users can see other reviews, where they can like a review or click the reviewer's name and be redirected to their profile

- **Watchlist Page**
  Users that add movies to their personal watchlist, will see these films on this page, and are able to view the details of those films or remove them from their watchlist
  - If blank, there is an option to redirect to search for films for the user to add

- **Lists Page**
  Users can create private or public lists
  - Creating, viewing, updating, and removal of lists
  - Involves a title, description, and toggle to alter a personal list from private to public, vice versa

- **Personal and Other User Profile Pages**
  Users can view their own profile and other users' profiles
  - Personal:
    - Profile statistics including number of movies in watchlist, and number of reviews, lists, and followers
    - Recent reviews
    - Followers and following lists
    - Quick actions to allow for one-click access to manage lists, manage watchlists, search and import movies, or profile settings
  - Other users:
    - Recent reviews
    - Followers and following lists
    - Public lists

## Deployment instructions

1. Clone the repository:

   ```bash
   git clone https://github.com/jennifernhle/CITS3403-Project.git
   cd CITS3403-Project
   ```

2. Create a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Set up environment variables (create a `.env` file):

   ```
   # Delete .example from .env.example file name and then add the following
   SECRET_KEY=your-secret-key-here
   TMDB_API_KEY=your-tmdb-api-key-here  # Optional, for TMDB integration
   USE_TMDB_API=True  # Set to False if no TMDB key
   ```

   **TMDB API Key Setup (Optional):**

   To enable TMDB movie data integration:
   1. Visit [TMDB API](https://www.themoviedb.org/settings/api)
   2. Create a free account if you don't have one
   3. Request an API key
   4. Copy your API key to the `TMDB_API_KEY` environment variable
   5. Set `USE_TMDB_API=True` to enable TMDB features

   If you don't set up TMDB, the app will still work but won't fetch movie data from TMDB.

5. Initialise the database:

   ```bash
   flask db upgrade
   ```

6. Seed the database (optional):

   ```bash
   python seed.py
   ```

   This will create a couple demo users, reviews, and lists. You can log in as any demo user, and use the general functionalities of this web app as that user.

7. Run the application:

   ```bash
   flask run
   ```

8. Open your browser and navigate to `http://127.0.0.1:5000`

   **Note:** If you encounter a port conflict, the app will use the next available port. Check the terminal output for the exact URL.

## Running Tests

The project includes unit tests and Selenium tests organised as follows:

### Unit Tests

Run all unit tests:

```bash
# Run all unit tests
python -m pytest tests/test_auth.py tests/test_movies_reviews.py tests/test_lists_watchlist_social.py tests/test_models.py tests/test_forms.py -v
```

### Selenium Tests

Run Selenium tests:

```bash
# Option 1: Run Selenium tests with pytest
python -m pytest tests/selenium_tests.py -v

# Option 2: Run with unittest
python -m unittest tests.selenium_tests -v

# To watch the browser while tests run:
# In `tests/selenium_tests.py`, find this line and uncomment it:
# options.add_argument("--headless=new")  # Uncomment to see browser (currently hidden)

```

## Project Structure

```
popcorn_journal_app/
├── __init__.py
├── models.py
├── routes.py
├── forms.py
├── config.py
├── templates/
│   ├── about_us.html
│   ├── add_movie.html
│   ├── base.html
│   ├── home.html
│   ├── index.html
│   ├── list_detail.html
│   ├── lists.html
│   ├── login.html
│   ├── movie_overview.html
│   ├── profile.html
│   ├── register.html
│   ├── search.html
│   ├── settings.html
│   ├── user.html
│   ├── watchlist.html
│   └── ...
├── static/
│   ├── css/
│   │   └── styles.css
│   ├── js/
│   │   ├── auth.js
│   │   ├── like.js
│   │   ├── lists.js
│   │   ├── search.js
│   │   ├── settings.js
│   │   ├── user-interaction.js
│   │   └── watchlist.js
│   ├── img/
│   │   ├── landing-feature-showcase-1.png
│   │   ├── landing-feature-showcase-2.png
│   │   ├── landing-feature-showcase-3.png
│   │   ├── logo.png
│   │   └── user.png
│   └── posters/
└── ...
tests/
├── conftest.py
├── selenium_tests.py
├── test_auth.py
├── test_forms.py
├── test_lists_watchlist_social.py
├── test_models.py
└── test_movies_reviews.py
instance/
└── popcorn_journal.sqlite
migrations/
Root Files:
├── .env.example
├── .gitignore
├── app.py
├── README.md
├── requirements.txt
└── seed.py

```

### Authors: Jazmine Overend, Jingbo Wang, Jennifer Le, Tony Zhang
