from flask import (Flask,
                   render_template,
                   request,
                   redirect,
                   jsonify,
                   url_for,
                   flash,
                   session as login_session)
from sqlalchemy import create_engine, asc
from sqlalchemy.orm import sessionmaker
from database_setup import Base, Country, City, User
from helper import createUser, getUserInfo, getUserID
import random
import string
from oauth2client.client import (flow_from_clientsecrets,
                                 FlowExchangeError)
import httplib2
import json
from flask import make_response
import requests

app = Flask(__name__)


CLIENT_ID = json.loads(
    open('client_secrets.json', 'r').read())['web']['client_id']
APPLICATION_NAME = "Countries Application"


# Connect to Database and create database session
engine = create_engine('sqlite:///countries.db?check_same_thread=False')
Base.metadata.bind = engine

DBSession = sessionmaker(bind=engine)
session = DBSession()


# Create anti-forgery state token
@app.route('/login')
def showLogin():
    state = ''.join(random.choice(string.ascii_uppercase + string.digits)
                    for x in xrange(32))
    login_session['state'] = state
    # return "The current session state is %s" % login_session['state']
    return render_template('login.html', STATE=state)


@app.route('/gconnect', methods=['POST'])
def gconnect():
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
        response = make_response(
                                 json.dumps(
                                         'Current user is already connected.'),
                                 200)
        response.headers['Content-Type'] = 'application/json'
        return response

    # Store the access token in the session for later use.
    login_session['access_token'] = access_token
    login_session['gplus_id'] = gplus_id

    # Get user info
    userinfo_url = "https://www.googleapis.com/oauth2/v1/userinfo"
    params = {'access_token': credentials.access_token, 'alt': 'json'}
    answer = requests.get(userinfo_url, params=params)

    data = answer.json()

    login_session['username'] = data.get('name', '')
    login_session['picture'] = data['picture']
    login_session['email'] = data['email']
    # ADD PROVIDER TO LOGIN SESSION
    login_session['provider'] = 'google'

    # See if a user exists, if it doesn't make a new one
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
    output += ' " style = "width: 300px;'
    output += ' height: 300px;border-radius: 150px;'
    output += '-webkit-border-radius: 150px;'
    output += '-moz-border-radius: 150px;"> '
    flash("you are now logged in as %s" % login_session['username'])
    print "done!"
    return output


# DISCONNECT - Revoke a current user's token and reset their login_session
@app.route('/gdisconnect')
def gdisconnect():
    access_token = login_session.get('access_token')
    print 'In gdisconnect access token is %s', access_token
    print 'User name is: '
    print login_session['username']
    if access_token is None:
        print 'Access Token is None'
        response = make_response(json.dumps(
                                        'Current user not connected.'), 401)
        response.headers['Content-Type'] = 'application/json'
        return response
    url = ('https://accounts.google.com/o/oauth2/revoke?token=%s'
           % login_session['access_token'])
    h = httplib2.Http()
    result = h.request(url, 'GET')[0]
    print 'result is '
    print result
    if result['status'] == '200':
        response = make_response(json.dumps('Successfully disconnected.'), 200)
        response.headers['Content-Type'] = 'application/json'
        return response
    else:
        print "this is the status " + result['status']
        response = make_response(
                              json.dumps(
                                      'Failed to revoke token for given user.',
                                      400))
        response.headers['Content-Type'] = 'application/json'
        return response


# JSON APIs to view Country Information
@app.route('/country/<int:country_id>/cities/JSON')
def countryCities(country_id):
    country = session.query(Country).filter_by(id=country_id).one_or_none()
    items = session.query(City).filter_by(
        country_id=country_id).all()
    return jsonify(Cities=[i.serialize for i in items])


@app.route('/country/<int:country_id>/cities/<int:city_id>/JSON')
def cityItemJSON(country_id, city_id):
    City_Item = session.query(City).filter_by(id=city_id).one_or_none()
    return jsonify(City_Item=City_Item.serialize)


@app.route('/JSON')
def countriesJSON():
    countries = session.query(Country).all()
    return jsonify(countries=[r.serialize for r in countries])


@app.route('/')
@app.route('/country/')
def showCountries():
    countries = session.query(Country).order_by(asc(Country.name))
    if 'username' not in login_session:
        return render_template('publiccountries.html', countries=countries)
    else:
        return render_template('countries.html', countries=countries)


# Create a new country for authorized user only
@app.route('/country/new/', methods=['GET', 'POST'])
def newCountry():
    if 'username' not in login_session:
        return redirect('/login')
    if request.method == 'POST':
        newCountry = Country(
                            name=request.form['name'],
                            user_id=login_session['user_id'])
        session.add(newCountry)
        flash('New Country %s Successfully Created' % newCountry.name)
        session.commit()
        return redirect(url_for('showCountries'))
    else:
        return render_template('newCountry.html')


# Edit a country name by the creator only
@app.route('/country/<int:country_id>/edit/', methods=['GET', 'POST'])
def editCountry(country_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCountry = session.query(
        Country).filter_by(id=country_id).one()
    if editedCountry.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not" +
                " authorized.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['name']:
            editedCountry.name = request.form['name']
            flash('Country Successfully Edited %s' % editedCountry.name)
            return redirect(url_for('showCountries'))
    else:
        return render_template('editCountry.html', country=editedCountry)


# Delete a country by the creator only
@app.route('/country/<int:country_id>/delete/', methods=['GET', 'POST'])
def deleteCountry(country_id):
    if 'username' not in login_session:
        return redirect('/login')
    countryToDelete = session.query(
        Country).filter_by(id=country_id).one()
    if countryToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not" +
                " authorized.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(countryToDelete)
        flash('%s Successfully Deleted' % countryToDelete.name)
        session.commit()
        return redirect(url_for('showCountries', country_id=country_id))
    else:
        return render_template('deleteCountry.html', country=countryToDelete)


# Show a cities of a country
@app.route('/country/<int:country_id>/')
@app.route('/country/<int:country_id>/cities/')
def showCities(country_id):
    country = session.query(Country).filter_by(id=country_id).one_or_none()
    items = session.query(City).filter_by(country_id=country_id).all()
    creator = getUserInfo(country.user_id)
    if (('username' not in login_session or
         creator.id != login_session['user_id'])):

        return render_template(
                             'publicCities.html',
                             items=items,
                             country=country,
                             creator=creator)
    else:
        return render_template(
                             'cities.html',
                             items=items,
                             country=country,
                             creator=creator)


# Create a new city for logged in user only
@app.route('/country/<int:country_id>/cities/new/', methods=['GET', 'POST'])
def newCity(country_id):
    if 'username' not in login_session:
        return redirect('/login')
    country = session.query(Country).filter_by(id=country_id).one()
    if request.method == 'POST':
        newCity = City(
                    city=request.form['city'],
                    description=request.form['description'],
                    country_id=country_id,
                    user_id=country.user_id)
        session.add(newCity)
        session.commit()
        flash('New City %s  Successfully Added' % (newCity.city))
        return redirect(url_for('showCities', country_id=country_id))
    else:
        return render_template('newcity.html', country_id=country_id)


# Edit a city by the creator only
@app.route(
        '/country/<int:country_id>/cities/<int:city_id>/edit',
        methods=['GET', 'POST'])
def editCity(country_id, city_id):
    if 'username' not in login_session:
        return redirect('/login')
    editedCity = session.query(City).filter_by(id=city_id).one()
    country = session.query(Country).filter_by(id=country_id).one()
    if editedCity.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not" +
                " the creator.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        if request.form['city']:
            editedCity.city = request.form['city']
        if request.form['description']:
            editedCity.description = request.form['description']
        session.add(editedCity)
        session.commit()
        flash('City  Successfully Edited')
        return redirect(url_for('showCities', country_id=country_id))
    else:
        return render_template(
                            'editCity.html',
                            country_id=country_id,
                            city_id=city_id,
                            item=editedCity)


# Delete a city by the creator only
@app.route('/country/<int:country_id>/cities/<int:city_id>/delete',
           methods=['GET', 'POST'])
def deleteCity(country_id, city_id):
    if 'username' not in login_session:
        return redirect('/login')
    country = session.query(Country).filter_by(id=country_id).one()
    cityToDelete = session.query(City).filter_by(id=city_id).one()
    if cityToDelete.user_id != login_session['user_id']:
        return ("<script>function myFunction() {alert('You are not" +
                " the creator.');}</script><body onload='myFunction()'>")
    if request.method == 'POST':
        session.delete(cityToDelete)
        session.commit()
        flash('City Successfully Deleted')
        return redirect(url_for('showCities', country_id=country_id))
    else:
        return render_template('deleteCity.html', item=cityToDelete)


# Disconnect based on provider
@app.route('/disconnect')
def disconnect():
    if 'provider' in login_session:
        if login_session['provider'] == 'google':
            gdisconnect()
            del login_session['gplus_id']
            del login_session['username']
            del login_session['user_id']
            del login_session['provider']
        flash("You have successfully been logged out.")
        return redirect(url_for('showCountries'))
    else:
        flash("You were not logged in")
        return redirect(url_for('showCountries'))


if __name__ == '__main__':
    app.secret_key = 'super_secret_key'
    app.debug = True
    app.run(host='0.0.0.0', port=5000)
