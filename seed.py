from app import app
from models import db, User, Feedback

db.drop_all()
db.create_all()

user1 = User.register(
    username = 'Username100',
    password = 'mommymilkers',
    email = 'email1@email.com',
    first_name = 'User100',
    last_name = 'Name100',
)

user2 = User.register(
    username = 'Username200',
    password = 'mommymilkers',
    email = 'email2@email.com',
    first_name = 'User200',
    last_name = 'Name200',
)

feedback1 = Feedback(
    title = 'Title1',
    content = 'This is not content',
    username = 'Username100'
)

feedback2 = Feedback(
    title = 'Title2',
    content = 'Now THIS is content',
    username = 'Username100'
)

db.session.add_all([user1, user2])
db.session.add_all([feedback1, feedback2])
db.session.commit()