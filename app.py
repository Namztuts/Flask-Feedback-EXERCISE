from flask import Flask, render_template, redirect, session, flash
from flask_debugtoolbar import DebugToolbarExtension
from models import connect_db, db, User, create_user, add_to_db, Feedback
from forms import RegisterForm, LoginForm, FeedbackForm

app = Flask(__name__)

app.config["SQLALCHEMY_DATABASE_URI"] = "postgresql:///auth_db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_ECHO"] = True
app.config["SECRET_KEY"] = "SupaSecr3t"
app.config['DEBUG_TB_INTERCEPT_REDIRECTS'] = False

app.app_context().push()
connect_db(app)
db.create_all()

toolbar = DebugToolbarExtension(app)


@app.route("/")
def homepage():
    '''Redirect to user registration'''
    
    return redirect("/login")

# @app.route('/register', methods=['GET', 'POST'])
# def register_user():
    
#     form = RegisterForm()
#     if form.validate_on_submit():
#         username = form.username.data
#         password = form.password.data
#         email = form.email.data
#         first_name = form.first_name.data
#         last_name = form.last_name.data
#         new_user = User.register(username, password, email, first_name, last_name)
        
#         session ['username'] = new_user.username
        
#         db.session.add(new_user) #username already exists error handling
#         try:
#             db.session.commit()
#         except IntegrityError:
#             form.username.errors.append('Username taken. Please pick another')
#             return render_template('register.html', form=form)
        
#         flash('Welcome! Your account has been successfully created!', 'success')
#         return redirect('/')
        
#     return render_template('register.html', form=form)

@app.route('/register', methods=['GET', 'POST'])
def register_user():
    
    form = RegisterForm()
    
    if form.validate_on_submit():
        new_user = create_user(form) #method for pulling the data from the form and creating a new user | also adds to db
        
        if new_user:
            session['username'] = new_user.username
            flash('Welcome! Your account has been successfully created!', 'success')
            return redirect('/')
        else:
            form.username.errors.append('Username taken. Please pick another')

    return render_template('register.html', form=form)


@app.route('/login', methods=['GET', 'POST'])
def login_user():
    
    form = LoginForm()
    
    if form.validate_on_submit():
        username = form.username.data
        password = form.password.data
        
        auth_user = User.authenticate(username, password)
        
        if auth_user:
            flash(f'Welcome back, {auth_user.username}!', 'primary')
            session ['username'] = auth_user.username
            
            return redirect(f'/users/{auth_user.username}')
        else:
            form.username.errors = ['Invalid username/password']
    
    return render_template('login.html', form=form)


@app.route('/users/<username>')
def show_user_info(username):
    
    user = User.query.get_or_404(username)
    feedback = user.feedback
    
    if 'username' not in session:
        flash('Please login first', 'danger')
        return redirect('/login')
        
    return render_template('user_info.html', user=user, feedback=feedback)


@app.route('/users/<username>/delete')
def delete_user(username):

    user = User.query.get_or_404(username)
    
    if user.username == session['username']:
        db.session.delete(user)
        db.session.commit()
        flash('User has been deleted', 'danger')
        session.pop('username', None)
        
        return redirect('/login')
    
    else:
        flash('You do not have authorization to delete this user', 'danger')
        return redirect(f"/users/{session['username']}") #NOTE: currently i was logged in as user1 and went to users/user2/delete and it logged me in as user2 instead???
        #still gave error that i could not delete this user
        
        
@app.route('/users/<username>/feedback/add', methods=['GET', 'POST'])
def create_feedback(username):
    
    if 'username' not in session:
        flash('Please login first', 'danger')
        return redirect('/login')
    
    user = User.query.get_or_404(username)
    form = FeedbackForm()
    
    if user.username == session['username']:
        if form.validate_on_submit():
            title = form.title.data
            content = form.content.data
            username = user.username
            new_feedback = Feedback(title=title, content=content, username=username)
        
            db.session.add(new_feedback)
            db.session.commit()
            flash('New feedback created!', 'success')
        
            return redirect(f"/users/{session['username']}")
        # if form.validate_on_submit(): NOTE: giving an error | TypeError: create_feedback() takes 1 positional argument but 2 were given
        #     new_feedback = create_feedback(form, user)
            
        #     flash('New feedback created!', 'success')
        #     return redirect(f"/users/{session['username']}")
        else:
            return render_template('feedback.html', user=user, form=form)
    
    else:
        flash(f"You are not authorized to create a Feedback for that User!", 'danger')
        return redirect(f"/users/{session['username']}")
            

@app.route('/feedback/<int:id>/update', methods=['GET', 'POST'])
def edit_feedback(id):
    
    feedback = Feedback.query.get_or_404(id)
    username = feedback.user.username
    
    if username == session['username']:
            
        form = FeedbackForm(obj=feedback)
        
        if form.validate_on_submit():
            feedback.title = form.title.data
            feedback.content = form.content.data
            
            db.session.commit()
            flash('Edit has been submitted', 'success')
            
            return redirect(f"/users/{session['username']}")

        else:
            return render_template('feedback_edit.html', feedback=feedback, form=form)
    else:
        flash(f"You are not authorized to edit that Feedback!", 'danger')
        return redirect(f"/users/{session['username']}")
    
    
@app.route('/feedback/<int:id>/delete')
def delete_feedback(id):

    feedback = Feedback.query.get_or_404(id)
    username = feedback.user.username
    
    if username == session['username']:
        db.session.delete(feedback)
        db.session.commit()
        flash('Feedback has been deleted', 'danger')
        
        return redirect(f"/users/{session['username']}")
    
    else:
        flash('You are not authorized to delete that Feedback!', 'danger')
        return redirect(f"/users/{session['username']}")


@app.route('/logout', methods=['POST']) #NOTE: best practice is to make this a POST request due to 'pre-fetching' | some browsers pre fetch all get requests
def logout_user():
    
    session.pop('username', None) #second arg is the value that will be returned if it can't find username | causes a KeyError if no username is found
    flash('Successfully logged out! Adios!', 'danger')
    
    return redirect('/')

#NOTE: functionality done | play around with styles?