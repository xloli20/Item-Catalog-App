# Main Reference : https://github.com/udacity/ud330/tree/master/Lesson4/step2
# https://www.tutorialspoint.com/flask
from flask import Flask, request, make_response
from flask import jsonify, url_for, redirect, render_template, flash
from flask import session as login_session
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker, scoped_session
from database_setup import Base, Genre, Item, User
import random
import string
import datetime
from oauth2client.client import flow_from_clientsecrets
from oauth2client.client import FlowExchangeError
import httplib2
import json
import requests

# Flask constructor takes the name of current module (__name__) as argument.
app = Flask(__name__)

# Client ID for Google oauth2, extracted form client_secrets.json
# that was downaloaded from Google API Console
CLIENT_ID = json.loads(open('client_secrets.json',
                            'r').read())['web']['client_id']
APPLICATION_NAME = "catalog List Application"


# Connect to itemcatalog database
# add check_same_thread flage to prevent having multiple connections
# to a SQLite database that only exists in memory
# https://stackoverflow.com/questions/34009296/using-sqlalchemy-session-from-flask-raises-sqlite-objects-created-in-a-thread-c/34010159#34010159
engine = create_engine('sqlite:///itemcatalog.db?check_same_thread=False')
Base.metadata.bind = engine

# The sessionmaker will generate newly-configured Session classes.
# sessionmaker allow us to talk to the database in a controlled environment
DBSession = sessionmaker(bind=engine)
# define instance of the class DBSession
session = DBSession()


# Start login routing section
@app.route('/login')
def showLogin():
    # Create anti-forgery state token
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in range(32))
    login_session['state'] = state
    return render_template('login.html', STATE=state)


# Login via Goolge oauth2 section
@app.route('/gconnect', methods=['POST'])
def gconnect():
    '''
    using post method to login using google
    gconnect(): to connect and validate the token
    '''
    # Validate state token
    if request.args.get('state') != login_session['state']:
        response = make_response(json.dumps('Invalid state parameter.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    # Obtain authorization code
    code = request.data

    try:
        # Upgrade the authorization code into a credentials object
        oauth_flow = flow_from_clientsecrets('client_secrets.json', scope='')
        oauth_flow.redirect_uri = 'postmessage'
        credentials = oauth_flow.step2_exchange(code)
    except FlowExchangeError:
        response = make_response(
            json.dumps('Failed to upgrade the authorization code.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Check that the access token is valid.
    access_token = credentials.access_token
    url = ('https://www.googleapis.com/oauth2/v1/tokeninfo?access_token=%s'
           % access_token)
    h = httplib2.Http()
    result = json.loads(h.request(url, 'GET')[1])
    # If there was an error in the access token info, abort.
    if result.get('error') is not None:
        response = make_response(json.dumps(result.get('error')), 500)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is used for the intended user.
    gplus_id = credentials.id_token['sub']
    if result['user_id'] != gplus_id:
        response = make_response(
            json.dumps("Token's user ID doesn't match given user ID."), 401)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Verify that the access token is valid for this app.
    if result['issued_to'] != CLIENT_ID:
        response = make_response(
            json.dumps("Token's client ID does not match app's."), 401)
        print "Token's client ID does not match app's."
        response.headers['Content-Type'] = 'application/json'
        return response

    stored_access_token = login_session.get('access_token')
    stored_gplus_id = login_session.get('gplus_id')
    if stored_access_token is not None and gplus_id == stored_gplus_id:
        response = make_response(json.dumps('''Current user
        is already connected.'''),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = credentials.access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data['name']
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']

    # create User Id
    user_id = getUserID(login_session['email'])
    if not user_id:
        user_id = createUser(login_session)
    login_session['user_id'] = user_id

    output = ''
    output += '<h1>Welcome, '
    output += login_session['username']
    output += '!</h1>'
    output += '<img src="'
    output += login_session['picture']
    output += ''' " style = "width: 200px; height: 200px;border-radius:
    120px;-webkit-border-radius: 120px;-moz-border-radius: 120px;"> '''
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


@app.route('/gdisconnect')
def gdisconnect():
    # Check if user is connected, disconnect it.
    # DISCONNECT will reset the user's login_session
    # and revoke the user's token.
    access_token = login_session.get('access_token')
    if access_token is None:
        response = make_response(
            json.dumps('Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        flash("You have successfully logged out")
        login_session.clear()
        return redirect(url_for('showCatalog'))
    else:
        response = make_response(json.dumps(
            'Failed to revoke token for given user.', 400))
        response.headers['Content-Type'] = 'application/json'
        return response


# User Helper Function, create user in database
def createUser(login_session):
    newUser = User(name=login_session['username'], email=login_session[
                  'email'], picture=login_session['picture'])
    session.add(newUser)
    session.commit()
    user = session.query(User).filter_by(email=login_session['email']).one()
    return user.id


# User Helper Functions, return user info by passing user's Id
def getUserInfo(user_id):
    user = session.query(User).filter_by(id=user_id).one()
    return user


# User Helper Functions, return user_id by passing his/her email
def getUserID(email):
    try:
        user = session.query(User).filter_by(email=email).one()
        return user.id
    except Exception:
        return None

# End login routing section


# Start JSON endpoint implemintation section
@app.route('/genres/<int:genre_id>/item/<int:item_id>/JSON')
def GenreItemJSON(genre_id, item_id):
    Items = session.query(Item).filter_by(genre_id=genre_id, id=item_id).one()
    return jsonify(Items=Items.serialize)


@app.route('/genres/<int:genre_id>/item/JSON')
def CatalogItemJSON(genre_id):
    Genres = session.query(Genre).filter_by(id=genre_id).one()
    items = session.query(Item).filter_by(genre_id=genre_id).all()
    return jsonify(Item=[i.serialize for i in items])


@app.route('/genres/JSON')
def catalogJSON():
    genres = session.query(Genre).all()
    return jsonify(genres=[g.serialize for g in genres])
# End JSON endpoint implemintation section


# Show catalog
@app.route('/')
@app.route('/genres/')
def showCatalog():
    genres = session.query(Genre).all()
    # Show recent items
    recentItems = session.query(Item).order_by(Item.id.desc()).limit(7)
    if 'username' not in login_session:
        print('public catalog')
        # if user is not logged in show him a screen without add new item
        return render_template('publicCatalog.html',
                               genres=genres, items=recentItems)
    else:
        # if user is logged in show him a screen
        # with the option of adding new item
        return render_template('privateCatalog.html',
                               genres=genres, items=recentItems)


# Create a new genre by providing genre name
@app.route('/genres/new/', methods=['GET', 'POST'])
def newGenre():
    # Implement local permission , by checking
    # if the user is autherized to add a genre or no
    if 'username' not in login_session:
        return redirect('/login')

    if request.method == 'POST':
        genre = Genre(name=request.form['name'],
                      user_id=login_session['user_id'])
        session.add(genre)
        flash('New genre %s Successfully Created!' % genre.name)
        session.commit()
        return redirect(url_for('showCatalog'))
    else:
        return render_template('newGenre.html')


# Edit a genre
@app.route('/genres/<int:genre_id>/edit/', methods=['GET', 'POST'])
def editGenre(genre_id):
    print('edit genre')
    genreToEdit = session.query(
                                Genre).filter_by(id=genre_id).one()
    # Implement local permission , by checking if the
    # user is autherized to edit the genre or no
    if 'username' not in login_session:
        return redirect('/login')
    if genreToEdit.user_id != login_session['user_id']:
        flash('You are not authorized to edit this genre Please'
              'create your own genre in order to edit.')
        return redirect(url_for('showCatalog',
                                genre_id=genre_id))
    if request.method == 'POST':
        if request.form['name']:
            genreToEdit.name = request.form['name']
            flash('Genre Successfully Edited %s' % genreToEdit.name)
            return redirect(url_for('showCatalog'))
    else:
        return render_template('editGenre.html', genre=genreToEdit)


# Delete a genre
@app.route('/genres/<int:genre_id>/delete/', methods=['GET', 'POST'])
def deleteGenre(genre_id):
    genreToDelete = session.query(
                                  Genre).filter_by(id=genre_id).one()
    # Implement local permission , by checking if the user
    # is autherized to delete the genre or no
    if 'username' not in login_session:
        return redirect('/login')
    if genreToDelete.user_id != login_session['user_id']:
        flash('You are not authorized to delete this genre Please'
              'create your own genre in order to delete.')
        return redirect(url_for('showCatalog',
                                genre_id=genre_id))
    if request.method == 'POST':
        session.delete(genreToDelete)
        flash('%s Successfully Deleted' % genreToDelete.name)
        session.commit()
        return redirect(url_for('showCatalog', genre_id=genre_id))
    else:
        return render_template('deleteGenre.html', genre=genreToDelete)


# Show a specific genre item
@app.route('/genres/<int:genre_id>/')
@app.route('/genres/<int:genre_id>/item/')
def showGenre(genre_id):
    genre = session.query(
                          Genre).filter_by(id=genre_id).one()
    creator = getUserInfo(genre.user_id)
    items = session.query(Item).filter_by(
                                         genre_id=genre_id).all()

    if ('username' not in login_session or
       creator.id != login_session['user_id']):
        return render_template('publicGenre.html', items=items,
                               genre=genre, creator=creator)
    else:
        return render_template('privateGenre.html', items=items,
                               genre=genre, creator=creator)


# Show a specific genre item
@app.route('/genres/<int:genre_id>/<int:item_id>')
def showitem(genre_id, item_id):
    item = session.query(Item).filter_by(
                                         id=item_id).first()

    if 'username' not in login_session:
        return render_template('publicitem.html', item=item)
    else:
        return render_template('privateitem.html', genre_id=genre_id,
                               item=item)


# Create a new genre item
@app.route('/genres/<int:genre_id>/item/new/', methods=['GET', 'POST'])
def newitem(genre_id):
    # Implement local permission , by checking if the user is autherized to
    # create new item or no
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    if request.method == 'POST':
        newItem = Item(title=request.form['title'],
                       description=request.form['description'],
                       genre_id=genre_id,
                       user_id=login_session['user_id'])
        session.add(newItem)
        session.commit()
        flash('A new item has been added')
        return redirect(url_for('showGenre', genre_id=genre_id))
    else:
        return render_template('newitem.html', genre_id=genre_id)


# Edit a item
@app.route(
           '/genres/<int:genre_id>/item/<int:item_id>/edit',
           methods=[
                    'GET',
                    'POST'])
def edititem(genre_id, item_id):
    print('here')
    if 'username' not in login_session:
        print('not')
        return redirect('/login')
    itemToEdit = session.query(Item).filter_by(id=item_id).one()
    genre = session.query(Genre).filter_by(id=genre_id).one()
    print('before')
    print(login_session['user_id'])
    print(itemToEdit.user_id)
    if login_session['user_id'] != itemToEdit.user_id:
        flash('You are not authorized to edit this item Please'
              'create your own item in order to edit.')
        return redirect(url_for('showCatalog',
                                genre_id=genre_id))
    if request.method == 'POST':
        if request.form['name']:
            itemToEdit.name = request.form['name']
        if request.form['description']:
            itemToEdit.description = request.form['description']
        session.add(itemToEdit)
        session.commit()
        print('item successfully edieted')
        return redirect(url_for('showGenre', genre_id=genre_id))
    else:
        print('render_template')
        genres = session.query(Genre).all()
        return render_template('edititem.html',
                               genre_id=genre_id, item_id=item_id,
                               item=itemToEdit, genres=genres)


# Delete a item
@app.route(
           '/genres/<int:genre_id>/item/<int:item_id>/delete',
           methods=[
                    'GET',
                    'POST'])
def deleteitem(genre_id, item_id):
    if 'username' not in login_session:
        return redirect('/login')
    genre = session.query(Genre).filter_by(id=genre_id).one()
    itemToDelete = session.query(Item).filter_by(id=item_id).one()
    if login_session['user_id'] != itemToDelete.user_id:
        flash('You are not authorized to delete this item Please'
              'create your own item in order to delete.')
    return redirect(url_for('showCatalog',
                            genre_id=genre_id))
    if request.method == 'POST':
        session.delete(itemToDelete)
        session.commit()
        flash('Menu Item Successfully Deleted')
        return redirect(url_for('showGenre', genre_id=genre_id))
    else:
        return render_template('deleteitem.html', item=itemToDelete)


# Run the server
if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)

