from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt
from sqlalchemy.exc import IntegrityError

db = SQLAlchemy()

bcrypt = Bcrypt()


def connect_db(app):
    '''Connect to database.'''
    db.app = app
    db.init_app(app)


def add_to_db(object):
    '''Add the user to the database, handle errors if username already exists'''
    db.session.add(object)
    try:
        db.session.commit()
        return object
    except IntegrityError:
        db.session.rollback()
        return None


def create_user(form):
    '''Create a new user from the registration form data'''
    username = form.username.data
    password = form.password.data
    email = form.email.data
    first_name = form.first_name.data
    last_name = form.last_name.data
    new_user = User.register(username, password, email, first_name, last_name)
    
    return add_to_db(new_user)


class User(db.Model):
    '''User model'''

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True, unique=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    
    @classmethod #genereates a new instance of User
    def register(cls, username, password, email, first_name, last_name):
        '''Register user w/hashed password & return user'''

        hashed = bcrypt.generate_password_hash(password) #turns user input password into hash+salt
        hashed_utf8 = hashed.decode("utf8") #turn bytestring into normal (unicode utf8) string

        return cls(username=username, password=hashed_utf8, email=email, first_name=first_name, last_name=last_name)
        #return instance of user w/username and hashed pwd | cls (.self) same as User here in a classmethod

    @classmethod
    def authenticate(cls, username, password):
        '''Validate that user exists & password is correct | Return user if valid; else return False'''
        user = User.query.filter_by(username=username).first()

        if user and bcrypt.check_password_hash(user.password, password): #user.password is from db | password is from the user input form
            
            return user #return user instance
        else:
            return False
    
    
class Feedback(db.Model):
    
    __tablename__ = "feedback"
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    title = db.Column(db.String(100), nullable=False)
    content = db.Column(db.Text, nullable=False)
    username = db.Column(db.Text, db.ForeignKey('users.username', ondelete='CASCADE')) #CASCADE deletes associated Feedback when User is deleted
    
    user = db.relationship('User', backref=db.backref('feedback', cascade='all, delete-orphan')) #relationship with the User table