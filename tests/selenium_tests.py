import threading
import time
import unittest
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from popcorn_journal_app import create_app, db
from popcorn_journal_app.config import TestingConfig

RON_USER = {
    'username': 'RonReviews',
    'email': 'ron@gmail.com',
    'password': 'Ronreviews123!'
}

FELICIA_USER = {
    'username': 'FeliciaFrames',
    'email': 'felicia@gmail.com',
    'password': 'Feliciaframes123!'
}

class SeleniumTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = create_app(TestingConfig)
        cls.app_context = cls.app.app_context()
        cls.app_context.push()

        db.create_all()

        port = 5000
        cls.base_url = f'http://127.0.0.1:{port}'

        def run_app():
            cls.app.run(host='127.0.0.1', port=port, use_reloader=False, debug=False)

        cls.server_thread = threading.Thread(target=run_app, daemon=True)
        cls.server_thread.start()
        time.sleep(2)

        # Launch headless Chrome
        options = Options()
        options.add_argument("--headless=new")
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')

        cls.driver = webdriver.Chrome(options=options)
        cls.driver.implicitly_wait(10)

    @classmethod
    def tearDownClass(cls):
        if hasattr(cls, 'driver'):
            cls.driver.quit()
        if cls.app_context:
            db.session.remove()
            db.drop_all()
            cls.app_context.pop()

    def setUp(self):
        for table in reversed(db.metadata.sorted_tables):
            db.session.execute(table.delete())
        db.session.commit()
        self.driver.delete_all_cookies()

    def register_user(self, user_data):
        self.driver.get(f'{self.base_url}/register')
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.element_to_be_clickable((By.ID, 'username'))).send_keys(user_data['username'])
        self.driver.find_element(By.ID, 'login-email').send_keys(user_data['email'])
        self.driver.find_element(By.ID, 'login-password').send_keys(user_data['password'])
        self.driver.find_element(By.ID, 'confirm-password').send_keys(user_data['password'])
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, 'submitbtn')))
        self.click_element(submit_btn)
        time.sleep(1)

    def login_user(self, user_data):
        self.driver.get(f'{self.base_url}/login')
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'login-email'))).send_keys(user_data['email'])
        self.driver.find_element(By.ID, 'login-password').send_keys(user_data['password'])
        submit_btn = wait.until(EC.element_to_be_clickable((By.ID, 'submitbtn')))
        self.click_element(submit_btn)
        time.sleep(1)

    def logout_user(self):
        self.driver.get(self.base_url)
        wait = WebDriverWait(self.driver, 10)
        try:
            toggle = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-bs-toggle="dropdown"]')))
            toggle.click()
            time.sleep(0.5)
            logout_btn = wait.until(EC.element_to_be_clickable((By.LINK_TEXT, 'Logout')))
            logout_btn.click()
            time.sleep(1)
        except Exception:
            pass

    def scroll_to_element(self, element):
        self.driver.execute_script('arguments[0].scrollIntoView({behavior: "smooth", block: "center"});', element)
        time.sleep(0.5)

    def click_element(self, element):
        self.scroll_to_element(element)
        self.driver.execute_script('arguments[0].click();', element)

    def add_movie(self, title, director, year, genre, synopsis=None):
        self.driver.get(f'{self.base_url}/add-movie')
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.NAME, 'title'))).send_keys(title)
        self.driver.find_element(By.NAME, 'director').send_keys(director)
        self.driver.find_element(By.NAME, 'release_year').send_keys(str(year))
        self.driver.find_element(By.NAME, 'genre').send_keys(genre)
        if synopsis is not None:
            self.driver.find_element(By.NAME, 'synopsis').send_keys(synopsis)
        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        self.click_element(submit_btn)
        time.sleep(1)

    def get_user_id(self, username):
        from popcorn_journal_app.models import User
        user = User.query.filter_by(username=username).first()
        return user.id if user else None

    def test_register_login_logout(self):
        self.register_user(RON_USER)
        self.login_user(RON_USER)
        self.assertNotIn('/login', self.driver.current_url.lower())

        self.logout_user()
        time.sleep(1)
        self.assertIn(self.base_url, self.driver.current_url)

    def test_invalid_login_shows_error(self):
        self.driver.get(f'{self.base_url}/login')
        wait = WebDriverWait(self.driver, 10)
        wait.until(EC.presence_of_element_located((By.ID, 'login-email'))).send_keys('invalid@example.com')
        self.driver.find_element(By.ID, 'login-password').send_keys('wrongpassword')
        self.driver.find_element(By.ID, 'submitbtn').click()
        time.sleep(1)

        self.assertIn('/login', self.driver.current_url.lower())
        self.assertIn('invalid', self.driver.page_source.lower())

    def test_protected_pages_require_login(self):
        for path in ['/profile', '/watchlist', '/lists', '/add-movie']:
            self.driver.get(f'{self.base_url}{path}')
            time.sleep(1)
            self.assertIn('/login', self.driver.current_url.lower())

    def test_add_movie_and_search(self):
        self.register_user(RON_USER)
        self.login_user(RON_USER)
        self.add_movie('Inception', 'Christopher Nolan', 2010, 'Sci-Fi', synopsis='A mind-bending thriller.')

        self.driver.get(f'{self.base_url}/search')
        wait = WebDriverWait(self.driver, 10)
        search_input = wait.until(EC.presence_of_element_located((By.NAME, 'query')))
        search_input.send_keys('Inception')
        search_input.send_keys(Keys.RETURN)
        time.sleep(2)

        self.assertIn('inception', self.driver.page_source.lower())

        result_link = wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//h5[contains(text(), 'Inception')]/ancestor::div[contains(@class, 'card-body')]//a[normalize-space(text())='View']")
            )
        )
        self.click_element(result_link)
        time.sleep(1)
        self.assertIn('inception', self.driver.page_source.lower())

    def test_watchlist_add_and_remove_from_movie_page(self):
        self.register_user(RON_USER)
        self.login_user(RON_USER)
        self.add_movie('Inception', 'Christopher Nolan', 2010, 'Sci-Fi')

        self.driver.get(f'{self.base_url}/movie/1')
        wait = WebDriverWait(self.driver, 10)
        watch_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.watchlist-toggle-btn[data-movie-id="1"]'))
        )
        self.click_element(watch_btn)
        time.sleep(1)

        self.driver.get(f'{self.base_url}/watchlist')
        time.sleep(1)
        self.assertIn('inception', self.driver.page_source.lower())

        remove_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '.watchlist-toggle-btn[data-movie-id="1"]'))
        )
        self.click_element(remove_btn)
        time.sleep(1)
        self.assertIn('your watchlist is currently empty', self.driver.page_source.lower())

    def test_watchlist_toggle_from_search_results(self):
        self.register_user(RON_USER)
        self.login_user(RON_USER)
        self.add_movie('Inception', 'Christopher Nolan', 2010, 'Sci-Fi')

        self.driver.get(f'{self.base_url}/search')
        wait = WebDriverWait(self.driver, 10)
        search_input = wait.until(EC.presence_of_element_located((By.NAME, 'query')))
        search_input.send_keys('Inception')
        search_input.send_keys(Keys.RETURN)
        wait.until(EC.text_to_be_present_in_element((By.TAG_NAME, "body"), "Inception"))
        time.sleep(1)

        def click_watchlist_btn():
            btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '.watchlist-toggle-btn')))
            self.click_element(btn)

        click_watchlist_btn()
        time.sleep(1)

        self.driver.get(f'{self.base_url}/watchlist')
        wait.until(EC.presence_of_element_located((By.TAG_NAME, "body")))
        self.assertIn('inception', self.driver.page_source.lower())

    def test_create_public_list(self):
        self.register_user(RON_USER)
        self.login_user(RON_USER)

        self.driver.get(f'{self.base_url}/lists')
        wait = WebDriverWait(self.driver, 10)
        create_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '[data-bs-target="#createListModal"]')))
        self.click_element(create_btn)
        time.sleep(1)

        wait.until(EC.presence_of_element_located((By.NAME, 'name'))).send_keys('Best Sci-Fi')
        self.driver.find_element(By.NAME, 'description').send_keys('My favorite sci-fi movies.')
        public_checkbox = self.driver.find_element(By.NAME, 'public_status')
        if not public_checkbox.is_selected():
            self.click_element(public_checkbox)

        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'button[type="submit"]')))
        self.click_element(submit_btn)
        time.sleep(1)

        self.assertIn('best sci-fi', self.driver.page_source.lower())

    def test_follow_user(self):
        self.register_user(RON_USER)
        self.login_user(RON_USER)
        self.logout_user()

        self.register_user(FELICIA_USER)
        self.login_user(FELICIA_USER)

        ron_id = self.get_user_id(RON_USER['username'])
        self.driver.get(f'{self.base_url}/user/{ron_id}')
        wait = WebDriverWait(self.driver, 10)
        follow_btn = wait.until(EC.element_to_be_clickable((By.ID, 'follow-button')))
        self.click_element(follow_btn)
        time.sleep(1)

        self.assertIn('unfollow', follow_btn.text.lower())

    def test_like_review(self):
        self.register_user(RON_USER)
        self.login_user(RON_USER)

        from popcorn_journal_app.models import Movie, Review
        movie = Movie(
            title='Dune',
            director='Denis Villeneuve',
            release_year=2021,
            genre='Sci-Fi',
            creator_id=1,
        )
        db.session.add(movie)
        db.session.commit()

        review = Review(rating=10, content='Great movie.', movie_id=movie.id, user_id=1)
        db.session.add(review)
        db.session.commit()

        self.logout_user()
        self.register_user(FELICIA_USER)
        self.login_user(FELICIA_USER)

        self.driver.get(f'{self.base_url}/movie/{movie.id}')
        wait = WebDriverWait(self.driver, 10)
        like_btn = wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, f'button.heart-btn[data-review-id="{review.id}"]'))
        )
        self.click_element(like_btn)
        time.sleep(1)

        self.assertTrue('1' in like_btn.text or 'liked' in like_btn.text.lower())

    def test_edit_profile(self):
        self.register_user(RON_USER)
        self.login_user(RON_USER)

        self.driver.get(f'{self.base_url}/edit_profile')
        wait = WebDriverWait(self.driver, 10)
        bio_field = wait.until(EC.presence_of_element_located((By.NAME, 'bio')))
        bio_field.clear()
        bio_field.send_keys('I love movies and reviews.')

        submit_btn = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'input[type="submit"], button[type="submit"]')))
        self.click_element(submit_btn)
        time.sleep(1)

        self.assertIn('your profile has been updated', self.driver.page_source.lower())

if __name__ == '__main__':
    unittest.main(verbosity=2)
