import os
from popcorn_journal_app import create_app, db
from popcorn_journal_app.models import User, Movie, Review, List
from popcorn_journal_app.config import Config

app = create_app(Config)

def seed_database():
    print("🎬 Seeding database...")
    
    db.create_all()
    print("Clearing existing data...")
    try:
        Review.query.delete()
        List.query.delete()
        Movie.query.delete()
        User.query.delete()
        db.session.commit()
    except Exception as e:
        print(f"Note: Error during cleanup: {e}")
        db.session.rollback()

    # Creating users
    def add_user(username, email, password, first=None, last=None, bio=None):
        u = User(
            username=username, 
            email=email, 
            first_name=first, 
            last_name=last, 
            bio=bio,
            profile_pic='user.png'
        )
        u.set_password(password)
        db.session.add(u)
        # Flush to get ID for relationships
        db.session.flush()
        return u

    print("Creating users...")
    ron = add_user('RonReviews', 'ron@gmail.com', 'ronreviews123', 'Ron', 'Smith', 'Avid movie watcher and critic.')
    felicia = add_user('FeliciaFrames', 'felicia@gmail.com', 'feliciaframes123', 'Felicia', 'Brown', 'Film fanatic.')
    zoe = add_user('ZoeZone', 'zoe@gmail.com', 'zoezone123', 'Zoe', 'Taylor', 'Student who enjoys films in all forms.')

    # Movie catalog data
    movie_data = [
        ('Grave of the Fireflies', 'Isao Takahata', 1988, 'Animation', 'A young boy and his little sister struggle to survive in Japan during World War II.'),
        ('Inception', 'Christopher Nolan', 2010, 'Sci-Fi', 'A thief who steals corporate secrets through the use of dream-sharing technology is given the inverse task of planting an idea into the mind of a CEO, but his tragic past may doom the project and his team to disaster.'),
        ('Fight Club', 'David Fincher', 1999, 'Thriller', 'An insomniac office worker and a devil-may-care soap maker form an underground fight club that evolves into much more.'),
        ('Pulp Fiction', 'Quentin Tarantino', 1994, 'Crime', 'The lives of two mob hitmen, a boxer, a gangster and his wife, and a pair of diner bandits intertwine in four tales of violence and redemption.'),
        ('Life of Pi', 'Ang Lee', 2012, 'Adventure', 'A young man who survives a disaster at sea is hurtled into an epic journey of adventure and discovery. While cast away, he forms an unexpected connection with another survivor: a fearsome Bengal tiger.'),
        ('Spirited Away', 'Hayao Miyazaki', 2001, 'Animation', 'Ten-year-old Chihiro and her parents end up at an abandoned amusement park inhabited by supernatural beings. Soon, she learns that she must work to free her parents who have been turned into pigs.'),
        ('Parasite', 'Bong Joon-ho', 2019, 'Thriller', 'The struggling Kim family sees an opportunity when the son starts working for the wealthy Park family. Soon, all of them find a way to work within the same household and start living a parasitic life.'),
        ('Interstellar', 'Christopher Nolan', 2014, 'Sci-Fi', 'When Earth becomes uninhabitable in the future, a farmer and ex-NASA pilot, Joseph Cooper, is tasked to pilot a spacecraft, along with a team of researchers, to find a new planet for humans.'),
        ('The Matrix', 'Lana Wachowski', 1999, 'Action', 'Neo, a computer programmer and hacker, has always questioned the reality of the world around him. His suspicions are confirmed when Morpheus, a rebel leader, contacts him and reveals the truth to him.'),
        ('Amy', 'Asif Kapadia', 2015, 'Documentary', 'Filmmaker Asif Kapadia sheds light on the life, career and struggles of Amy Winehouse, a popular British singer-songwriter, through archived footage and testimonies from friends, family and peers.'),
        ('Bugonia', 'Yorgos Lanthimos', 2025, 'Comedy', 'Two conspiracy-obsessed men kidnap the CEO of a major company when they become convinced that she is an alien who wants to destroy Earth.'),
        ('In the Mood for Love', 'Wong Kar-wai', 2001, 'Romance', 'Two neighbors form a strong bond after both suspect extramarital activities of their spouses. However, they agree to keep their bond platonic so as not to commit similar wrongs.'),
        ('Portrait of a Lady on Fire', 'Celine Sciamma', 2019, 'Romance', 'Marianne, a female painter, is commissioned to paint a portrait of Heloise, an aristocratic woman, in a wedding dress. They soon fall in love with each other but cannot unite.'),
        ('Get Out', 'Jordan Peele', 2017, 'Horror', 'Chris, an African-American man, decides to visit his Caucasian girlfriend\'s parents during a weekend getaway. Although they seem normal at first, he is not prepared to experience the horrors ahead.'),
        ('Remember the Titans', 'Boaz Yakin', 2001, 'Sports', 'Herman Boone, an African-American, is appointed as the new coach of a high school team. The team is playing as a racially-integrated team for the first time.'),
        ('Crouching Tiger, Hidden Dragon', 'Ang Lee', 2001, 'Action', 'Master Li Mu Bai, a warrior, is about to retire and gives his sword to his lover Yu Shu Lien to keep it safe. However, the sword is stolen and now an embittered Li embarks on a mission to find it.'),
        ('Aftersun', 'Charlotte Wells', 2022, 'Drama', 'Sophie reflects on the shared joy and private melancholy of a holiday she took with her father twenty years earlier. Memories real and imagined fill the gaps between as she tries to reconcile the father she knew with the man she didn\'t.'),
        ('Sinners', 'Ryan Coogler', 2025, 'Horror', 'Trying to leave their troubled lives behind, twin brothers return to their Mississippi hometown to start again, only to discover that an even greater evil is waiting to welcome them back.'),
        ('The Handmaiden', 'Park Chan-wook', 2016, 'Thriller', 'A Korean con-man conjures up an elaborate plan to seduce a woman and swindle her of all her wealth. Along the way, he seeks the help of an orphan to ensure that he succeeds.'),
        ('Past Lives', 'Celine Song', 2023, 'Drama', 'Nora and Hae Sung, two deeply connected childhood friends, are torn apart after Nora\'s family emigrates from South Korea. Decades later, they are reunited for one fateful week as they confront destiny, love and the choices that make a life.')
    ]

    print(f"Populating {len(movie_data)} movies...")
    movies = []
    for title, director, year, genre, synop in movie_data:
        m = Movie(
            title=title,
            director=director,
            release_year=year,
            genre=genre,
            synopsis=synop,
            creator_id=ron.id
        )
        db.session.add(m)
        movies.append(m)
    db.session.flush()

    # Seed reviews
    print("Seeding reviews...")
    review_data = [
        (felicia, movies[5], 10, "A dazzling, enchanting, and gorgeously drawn fairy tale. What a wonderful story with great animation and a beautiful score."),
        (ron, movies[5], 8, "Spirited Away is no secondhand fairytale retread; it's a fully imagined universe, populated by wondrous beings and haunting landscapes."),
        (zoe, movies[6], 10, "Parasite is both darkly hilarious and delightfully shocking, setting a new sky-high standard for black comedy - the style of Bong Joon-ho."),
        (felicia, movies[19], 9, "A first love is a precious thing. And despite the inherent irrationality, it can be hard to let go of the golden sheen that covers a fond memory. But that is precisely what Song guides her characters to achieve in her film."),
        (zoe, movies[19], 6, "The characters are empty enough for me to imagine my own heartache in its own stead, but hazy characterisations and intriguing concepts aren't enough to sustain a movie."),
        (ron, movies[2], 5, "Fight Club promises a lot and delivers quite a bit less. In between, there are scenes of raw brutality, some funny dialogue, and a premise that's so old, it feels like a guest that has overstayed its welcome. In short, it's a mess."),
        (zoe, movies[18], 9, "While its a feat of technical brilliance and visual genius, its the way Park uses his story to force his audience to question their assumptions that made me speechless the first time I saw it."),
        (ron, movies[0], 9, "One of the most startling and moving animated films ever.")
    ]
    
    for author, movie, rating, content in review_data:
        r = Review(author=author, movie=movie, rating=rating, content=content)
        db.session.add(r)

    # Social interactions (followers)
    print("Seeding social network...")
    ron.follow(felicia)
    felicia.follow(ron)
    zoe.follow(ron)
    zoe.follow(felicia)

    # Public and private lists
    print("Seeding lists...")
    #Public
    tearjerkers = List(name="Tear jerkers", description="A curated collection of films that don't just make you cry, but leave a lasting ache. For when you need to feel everything at once. Keep tissues close.", owner=ron, public_status=True)
    tearjerkers.movies.extend([movies[0], movies[16], movies[19]])

    # Private list visible only to Zoe
    zoe_secret = List(name="My Guilty Pleasures", description="Movies I like but don't want to admit to.", owner=zoe, public_status=False)
    zoe_secret.movies.extend([movies[2], movies[18]])

    animation_gems = List(name="Animation Gems", description="The best animated films from across the globe.", owner=felicia, public_status=True)
    animation_gems.movies.extend([movies[0], movies[5]])
    db.session.add_all([tearjerkers, zoe_secret, animation_gems])

    # Watchlists
    print("Seeding watchlists...")
    felicia.watchlist.append(movies[18])
    zoe.watchlist.extend([movies[7], movies[8], movies[9]])

    db.session.commit()
    print("Database seeding complete. Run 'flask run' to see the results.")

if __name__ == '__main__':
    with app.app_context():
        seed_database()