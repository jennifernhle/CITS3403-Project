# CITS3403-Project

|Student ID|Student Name|GitHub Username|
|:--------:|:----------:|:-------------:|
| 24530845  | Jazmine Overend| jaz0555 |
| 24598109 | Jingbo Wang | jingboouu |
| 24502788 | Jennifer Le | jennifernhle |
| 24310849 | Tony Zhang | zhiyizhang984-ops |

## Running Tests

This project uses `pytest` for automated testing. The tests create a temporary
SQLite database, so they will not modify the local development database.

Install dependencies:

```bash
python3 -m pip install -r requirements.txt
```

Run the test suite:

```bash
python3 -m pytest
```

The current test suite covers:

- user registration, login, and logout
- movie creation and local movie search
- review creation, update, and deletion
- watchlist add/remove behaviour
- custom list creation and adding movies to lists
- private list access control
- follow/unfollow interactions
- review like/unlike interactions
