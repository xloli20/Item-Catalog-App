from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from database_setup import Base, Genre, Item, User
import datetime

engine = create_engine('sqlite:///itemcatalog.db')
# Bind the engine to the metadata of the Base class so that the
# declaratives can be accessed through a DBSession instance
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
# A DBSession() instance establishes all conversations with the database
# and represents a "staging zone" for all the objects loaded into the
# database session object. Any change made against the objects in the
# session won't be persisted into the database until you call
# session.commit(). If you're not happy about the changes, you can
# revert all of them back to the last commit by calling
# session.rollback()
session = DBSession()

# user Alaa which is me haha! 
User1 = User(name="Alaa", email="alaa.alzahrani88@gmail.com",
             picture='https://lh6.googleusercontent.com/-wYCHEphHC-0/AAAAAAAAAAI/AAAAAAAAABI/PfwT4K7mIOk/photo.jpg')
session.add(User1)
session.commit()


# genre for Food
Genre1 = Genre(user_id=1, name="Food")
session.add(Genre1)
session.commit()


Item1 = Item(title="French Fries", description="with garlic and parmesan",
                     genre=Genre1, user_id=1)

session.add(Item1)
session.commit()



Item2 = Item(title="Chicken Burger", description="Juicy grilled chicken patty with tomato mayo and lettuce",
                     genre=Genre1, user_id=1)

session.add(Item2)
session.commit()

# genre for Games
Genre2 = Genre(user_id=1, name="Games")
session.add(Genre2)
session.commit()

item1 = Item(title="OverWatch",
                      description="Overwatch is a team-based multiplayer first-person shooter video game developed and published by Blizzard Entertainment, which released on May 24, 2016 for PlayStation 4, Xbox One, and Windows.",
                      user_id=1,
                      genre=Genre2)

session.add(item1)
session.commit()


item2 = Item(title="Call of duty",
                      description="Call of Duty is a first-person shooter video game franchise. The series began on Microsoft Windows, and expanded to consoles and handhelds. Several spin-off games have been released. ",
                      user_id=1,
                      genre=Genre2)

session.add(item2)
session.commit()

item3 = Item(title="Horizon Zero Dawn",
                      description="Horizon Zero Dawn is an action role-playing video game developed by Guerrilla Games and published by Sony Interactive Entertainment. It was released for the PlayStation 4 in early 2017.",
                      user_id=1,
                      genre=Genre2)

session.add(item3)
session.commit()


# genre for Movies
Genre3 = Genre(user_id=1, name="Movies")
session.add(Genre3)
session.commit()

item1 = Item(title="Inception",
                      description="Dom Cobb (Leonardo DiCaprio) is a thief with the rare ability to enter people's dreams and steal their secrets from their subconscious. His skill has made him a hot commodity in the world of corporate espionage but has also cost him everything he loves.",
                      user_id=1,
                      genre=Genre3)

session.add(item1)
session.commit()

item2 = Item(title="The lord of the rings",
                      description="The Lord of the Rings is a film series consisting of three epic fantasy adventure films directed by Peter Jackson. They are based on the novel The Lord of the Rings by J. R. R. Tolkien. The films are subtitled The Fellowship of the Ring, The Two Towers and The Return of the King.",
                      user_id=1,
                      genre=Genre3)

session.add(item2)
session.commit()


# genre for Books
Genre4 = Genre(user_id=1, name="Books")
session.add(Genre4)
session.commit()

item1 = Item(title="Awaken the giant within",
                      description="Awaken The Giant Within: How to Take Immediate Control of Your Mental, Emotional, Physical and Financial Destiny! By Tony Robbins | Book Summary | Readtrepreneur ",
                      user_id=1,
                      genre=Genre4)

session.add(item1)
session.commit()

item2 = Item(title="Think like a freak",
                      description="Think Like a Freak: The Authors of Freakonomics Offer to Retrain Your Brain is the third non-fiction book by University of Chicago economist Steven Levitt and New York Times journalist Stephen J. Dubner. The book was published on May 12, 2014 by William Morrow.",
                      user_id=1,
                      genre=Genre4)

session.add(item2)
session.commit()

item3 = Item(title="A brief history of time",
                      description="A Brief History of Time: From the Big Bang to Black Holes is a popular-science book on cosmology by British physicist Stephen Hawking. It was first published in 1988. Hawking wrote the book for nonspecialist readers with no prior knowledge of scientific theories. ",
                      user_id=1,
                      genre=Genre4)

session.add(item3)
session.commit()


# genre for Languages
Genre5 = Genre(user_id=1, name="Languages")
session.add(Genre5)
session.commit()

item1 = Item(title="English",
                      description="English is a West Germanic language that was first spoken in early medieval England and eventually became a global lingua franca.",
                      user_id=1,
                      genre=Genre5)

session.add(item1)
session.commit()

item2 = Item(title="Arabic",
                      description="Arabic al-arabiyyah or arabi or is a Central Semitic language that first emerged in Iron Age northwestern Arabia and is now the lingua franca of the Arab world.",
                      user_id=1,
                      genre=Genre5)

session.add(item2)
session.commit()

item3 = Item(title="Spanish",
                      description="Spanish or Castilian, is a Western Romance language that originated in the Castile region of Spain and today has hundreds of millions of native speakers in the Americas and Spain. It is usually considered a global language and the world's second-most spoken native language, after Mandarin Chinese. ",
                      user_id=1,
                      genre=Genre5)

session.add(item3)
session.commit()


print "added items!"
