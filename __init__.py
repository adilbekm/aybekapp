from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer

# Function 'urandom' is Python's cryptographically secure PRNG.
# It will be used for generating salt (for password hashing).
from os import urandom

# Imports and other code needed for Google Plus sign-in:
import random, string
#from oauth2client.client import flow_from_clientsecrets
#from oauth2client.client import FlowExchangeError
#import httplib2
import json
from flask import make_response
import requests
#CLIENT_ID = json.loads(open('/var/www/personalBudget/personalBudget/client_secrets.json', 'r').read())['web']['client_id']

# Import regular expression module (used for email validation):
import re

# 'wraps' helps a wrapped function to retain its attributes (__name__, __doc__, etc.)
from functools import wraps

# Function 'sha256' is the cryptographix hash algorithm I will use
# to hash passwords. The function produces 64-character output
# (256-bit output -> 64 characters in HEX format).
from hashlib import sha256

# Needed to perform CRUD operations with the database:
from database_setup import engine, Base, Word
from sqlalchemy.orm import sessionmaker
# Func is needed for aggregations (sum, avg, max, etc.):
from sqlalchemy.sql import func

# Import flask components:
from flask import Flask, render_template, url_for, request, redirect, flash
# jsonify is a package that allows to format data for JSON end point
from flask import jsonify
# Session is a dictionary where we can store values for the longevity of
# a user's session with our server:
from flask import session as login_session
# Create an instance of class Flask, which will be our WSGI application:
app = Flask(__name__)

# Create engine and connect to DB:
Base.metadata.bind = engine
DBSession = sessionmaker(bind=engine)
session = DBSession()

@app.route('/')
@app.route('/home/')
def home():
	return render_template('home.html')

@app.route('/newword/', methods=['GET','POST'])
def addWord():
	if request.method == 'GET':
		return render_template('newword.html')
	# Get data from POST request, stripping any leading/trailing white spaces:
	word = request.form['word'].strip()
	definition = request.form['definition'].strip()
	# Check if values are empty:
	if not word: 
		return render_template('newword.html')
	if not definition:
		return render_template('newword.html')
	# Add more validations here later. 
	newWord = Word(word=word, definition=definition)
	session.add(newWord)
	session.commit()
	return render_template('home.html')

@app.route('/allwords/')
def allWords():
	words = session.query(Word).order_by(Word.id.desc()).all()
	return render_template('allwords.html', words=words)

@app.route('/testwords/')
def testWords():
	return render_template('testwords.html')

@app.route('/allwords/<int:word_id>/edit/', methods=['GET','POST'])
def editWord(word_id):
	word_object = session.query(Word).filter_by(id=word_id).first()
	word = word_object.word
	definition = word_object.definition
	if request.method == 'GET':
		return render_template('editword.html', word_id=word_id, word=word, definition=definition)
	# Get data from POST request, stripping any leading/trailing white spaces:
	new_word = request.form['word'].strip()
	new_definition = request.form['definition'].strip()
	# Check if values are empty:
	if not new_word: 
		return render_template('newword.html')
	if not new_definition:
		return render_template('newword.html')
	# Add more validations here later. 
	word_object.word = new_word
	word_object.definition = new_definition
	session.add(word_object)
	session.commit()
	return render_template('home.html')

@app.route('/allwords/<int:word_id>/delete/')
def deleteWord(word_id):
	word_object = session.query(Word).filter_by(id=word_id).first()
	session.delete(word_object)
	session.commit()
	return redirect(url_for('allWords'))

# @app.route('/')
# @app.route('/home/')
# def showPeriods():
# 	if 'email' not in login_session:
# 		# User is not signed in.
# 		return render_template('public.html')
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	if user is None:
# 		# This is a rare case when user is deleted while still in session.
# 		output = 'The page doesn\'t exist or you are not authorized to access it.'
# 		return output
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	return render_template('home.html', items=periods, username=user.name)

# @app.route('/period/new/', methods=['GET','POST'])
# @login_required
# def newPeriod():
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	if request.method == 'GET':
# 		return render_template('period_new.html',periods=periods)
# 	# Get data from POST request, stripping any leading/trailing white spaces:
# 	period_name = request.form['period_name'].strip()
# 	# Check if value not empty:
# 	if not period_name:
# 		flash('Please enter period name')
# 		return render_template('period_new.html',periods=periods)
# 	# Check if length is reasonable (between 2 and 25 chars):
# 	if len(period_name)>25:
# 		flash('Period name appears too long - try to keep things short and sweet')
# 		return render_template('period_new.html',periods=periods)
# 	if len(period_name)<3:
# 		flash('Period name appears too short - let\'s be more serious')
# 		return render_template('period_new.html',periods=periods)
# 	# Validation passed. Add period to the database:
# 	newPeriod = Period(name=period_name, user_id=user.id) 
# 	session.add(newPeriod)
# 	session.commit()
# 	flash('New period created')
# 	return redirect(url_for('showBudget',period_id=newPeriod.id))

# ---- This is old code. Keep it here for reference ----

# # I am renaming this function from 'login_app' to 'login' in order to make it
# # the default login method (bypassing Google Plus sign in).
# @app.route('/login/', methods=['GET','POST'])
# def login():
# 	if request.method == 'GET':
# 		return render_template('login_app.html')
# 	else:
# 		# The request is POST. Get form data from the POST request,
# 		# stripping any leading and trailing whitespaces (and converting all characters
# 		# in the email to lowercase), and then validate all data:
# 		email = request.form['email'].strip().lower()
# 		password = request.form['password'].strip()
# 		# Check if all fields are non-empty; flash an error otherwise:
# 		if not email or not password:
# 			 flash('Please enter all fields')
# 			 return render_template('login_app.html')
# 		# Lookup the user by email and verify the password:
# 		user = session.query(User).filter_by(email=email).first()
# 		if user == None:
# 			flash('Invalid user name or password')
# 			return render_template('login_app.html')
# 		if not user.check_password(password):
# 			flash('Invalid user name or password')
# 			return render_template('login_app.html')
# 		# Validation passed. Log the user into session.
# 		login_session['username'] = user.name
# 		login_session['email'] = user.email
# 		# Redirect to the 'periods' page:
# 		flash('You are now logged in as %s' % user.name)
# 		return redirect(url_for('showPeriods'))
# 		# return 'email:%s,session:%s' % (login_session['email'], login_session['state'])

# @app.route('/logout/', methods=['GET'])
# def logout():
# 	# Check if currently logged in user used the Google Plus login
# 	# by looking for 'access_token' in the session.
# 	access_token = login_session.get('access_token')
# 	if access_token is not None:
# 		# Access token is in session, so revoke it on the server.
# 		url = 'https://accounts.google.com/o/oauth2/revoke?token=%s' % access_token
# 		h = httplib2.Http()
# 		result = h.request(url, 'GET')[0]
# 		if result['status'] == '200':
# 			# Reset the user's session.
# 			del login_session['access_token']
# 			del login_session['gplus_id']
# 			del login_session['username']
# 			del login_session['email']
# 			flash('Successfully logged out and revoked Google Plus token')
# 			return redirect(url_for('login'))
# 		else:
# 			try:
# 				del login_session['access_token']
# 				del login_session['gplus_id']
# 				del login_session['username']
# 				del login_session['email']
# 				# For whatever reason, the given token was invalid.
# 				flash('Successfully logged out but failed to revoke Goole Plus token')
# 				return redirect(url_for('login'))
# 			except:
# 				flash('Logout did not succeed for unknown reason')
# 				return redirect(url_for('login'))
# 	else:
# 		# Access token is None. Check for local user in session.
# 		email = login_session.get('email')
# 		if email is not None:
# 			# Local user is in session, so log the user out.
# 			del login_session['username']
# 			del login_session['email']
# 			flash('Successfully logged out')
# 			return redirect(url_for('login'))
# 		else:
# 			flash('Already logged out')
# 			return redirect(url_for('login'))

# @app.route('/register/', methods=['GET','POST'])
# def register():
# 	if request.method == 'GET':
# 		return render_template('register.html')
# 	# The request is POST. Get form data from the POST request,
# 	# stripping any leading and trailing whitespaces (and converting all characters
# 	# in the email to lowercase), and then validate all data:
# 	name = request.form['name'].strip()
# 	email = request.form['email'].strip().lower()
# 	password = request.form['password'].strip()
# 	pwdconfirm = request.form['pwdconfirm'].strip()
# 	invite_code = request.form['invite_code'].strip()
# 	# Check if all fields are non-empty; flash an error otherwise:
# 	if not name or not email or not password or not pwdconfirm or not invite_code: 
# 		 flash('Please enter all fields')
# 		 return render_template('register.html')
# 	# Check if lengths are reasonable (between 2 and 250 chars):
# 	if len(name)>250 or len(email)>250 or len(password)>250 or len(pwdconfirm)>250:
# 		flash('Some values appear too long - try to keep things short and sweet')
# 		return render_template('register.html')
# 	if len(name)<3 or len(email)<3 or len(password)<3 or len(pwdconfirm)<3:
# 		flash('Some values appear too short - let\'s be more serious')
# 		return render_template('register.html')
# 	# Check if the two password entries match:
# 	if not password == pwdconfirm:
# 		flash('Password and confirmation don\'t match')
# 		return render_template('register.html')
# 	# Check if email is a valid email address (it has @ and . in that order):
# 	if not re.match('[^@]+@[^@]+\.[^@]+',email):
# 		flash('Invalid email address')
# 		return render_template('register.html')
# 	if not invite_code == '747':
# 		flash('Invalid invitation code')
# 		return render_template('register.html')
# 	# Check if email already exists:
# 	user = session.query(User).filter_by(email=email).first()
# 	if user:
# 		flash('This email address is already registered')
# 		return render_template('register.html')
# 	# Validations passed.
# 	# Hash the password:
# 	# Create 32-byte (256-bit) long salt and convert to ASCII format.
# 	# In ASCII, the salt will always be 45 characters long.
# 	salt = urandom(32).encode('base64')
# 	# Prepend salt to password:
# 	salted_password = salt + password
# 	# Hash the resulting string:
# 	hashed_password = sha256(salted_password).hexdigest()
# 	#
# 	# Add user to database:
# 	newUser = User(name=name, email=email, password=hashed_password, salt=salt)
# 	session.add(newUser)
# 	session.commit()
# 	#
# 	# Enter user's information into session
# 	login_session['username'] = newUser.name
# 	login_session['email'] = newUser.email
# 	# Redirect to the 'periods' page:
# 	flash('Thank you for registering! You are now logged in as %s' % newUser.name)
# 	return redirect(url_for('showPeriods'))

# def login_required(f):
# 	'''This decorator function checks if the user is logged in and has authorization
# 	   to accesss the requested resource. It assumes the function it wraps has up to
# 	   two keyword arguments: period_id and budget_id. If those are passed, each
# 	   is checked for validity. period_id is additionally checked to see if the user
# 	   associated with the period is the same as the user requesting access to it.'''
# 	@wraps(f)
# 	def wrapper_function(**kwargs):
# 		output = 'The page doesn\'t exist or you are not authorized to access it.'
# 		if 'email' not in login_session:
# 			# User is not signed in.
# 			return output
# 		user = session.query(User).filter_by(email=login_session['email']).first()
# 		if user is None:
# 			# A rare case when user is deleted while still in session.
# 			return output
# 		if 'period_id' in kwargs.keys():
# 			period_id = kwargs['period_id']
# 			period = session.query(Period).filter_by(id=period_id).first()
# 			if period is None or user.id != period.user_id:
# 				# The period doesn't exist or the user isn't allowed to access it.
# 				return output
# 		if 'budget_id' in kwargs.keys():
# 			budget_id = kwargs['budget_id']
# 			budget = session.query(Budget).filter_by(id=budget_id).first()
# 			if budget is None:
# 				# The budget doesn't exist.
# 				return output
# 		return f(**kwargs)
# 	return wrapper_function

# @app.route('/')
# @app.route('/home/')
# def showPeriods():
# 	if 'email' not in login_session:
# 		# User is not signed in.
# 		return render_template('public.html')
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	if user is None:
# 		# This is a rare case when user is deleted while still in session.
# 		output = 'The page doesn\'t exist or you are not authorized to access it.'
# 		return output
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	return render_template('home.html', items=periods, username=user.name)

# @app.route('/period/new/', methods=['GET','POST'])
# @login_required
# def newPeriod():
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	if request.method == 'GET':
# 		return render_template('period_new.html',periods=periods)
# 	# Get data from POST request, stripping any leading/trailing white spaces:
# 	period_name = request.form['period_name'].strip()
# 	# Check if value not empty:
# 	if not period_name:
# 		flash('Please enter period name')
# 		return render_template('period_new.html',periods=periods)
# 	# Check if length is reasonable (between 2 and 25 chars):
# 	if len(period_name)>25:
# 		flash('Period name appears too long - try to keep things short and sweet')
# 		return render_template('period_new.html',periods=periods)
# 	if len(period_name)<3:
# 		flash('Period name appears too short - let\'s be more serious')
# 		return render_template('period_new.html',periods=periods)
# 	# Validation passed. Add period to the database:
# 	newPeriod = Period(name=period_name, user_id=user.id) 
# 	session.add(newPeriod)
# 	session.commit()
# 	flash('New period created')
# 	return redirect(url_for('showBudget',period_id=newPeriod.id))

# @app.route('/period/<int:period_id>/budget/', methods=['GET'])
# @login_required
# def showBudget(period_id):
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	period = session.query(Period).filter_by(id=period_id).first()
# 	periods = session.query(Period).filter_by(user_id=user.id).\
# 		order_by(Period.id.desc()).all()
# 	budgets = session.query(Budget).filter_by(period_id=period_id).order_by(Budget.id).all()
# 	total_budget = session.query(func.sum(Budget.budget_amount)).\
# 		filter_by(period_id=period_id)
# 	total_actual = session.query(func.sum(Budget.actual_amount)).\
# 		filter_by(period_id=period_id)
# 	return render_template('budget.html',periods=periods,budgets=budgets,period_id=period_id,\
# 		total_budget=(0 if total_budget[0][0] is None else total_budget[0][0]),\
# 		total_actual=(0 if total_actual[0][0] is None else total_actual[0][0]),\
# 		period=period)
		
# @app.route('/period/<int:period_id>/edit/', methods=['GET','POST'])
# @login_required
# def editPeriod(period_id):
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	period = session.query(Period).filter_by(id=period_id).first()
# 	period_name = period.name
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	if request.method == 'GET':
# 		return render_template('period_edit.html',periods=periods,period_id=period_id,\
# 			period_name=period_name)
# 	# Get data from POST request, stripping any leading/trailing white spaces:
# 	new_name = request.form['period_name'].strip()
# 	# Check if value not empty:
# 	if not new_name:
# 		flash('Period name cannot be empty')
# 		return render_template('period_edit.html',periods=periods,period_id=period_id,\
# 			period_name=period_name)
# 	# Check if length is reasonable (between 2 and 25 chars):
# 	if len(new_name)>25:
# 		flash('Period name appears too long - try to keep things short and sweet')
# 		return render_template('period_edit.html',periods=periods,period_id=period_id,\
# 			period_name=period_name)
# 	if len(new_name)<3:
# 		flash('Period name appears too short - let\'s be more serious')
# 		return render_template('period_edit.html',periods=periods,period_id=period_id,\
# 			period_name=period_name)
# 	# Validation passed. Update period name in the database:
# 	period.name = new_name
# 	session.add(period)
# 	session.commit()
# 	flash('Period name was updated')
# 	return redirect(url_for('showBudget',period_id=period_id))

# @app.route('/period/<int:period_id>/delete/', methods=['GET','POST'])
# @login_required
# def deletePeriod(period_id):
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	period = session.query(Period).filter_by(id=period_id).first()
# 	period_name = period.name
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	if request.method == 'GET':
# 		return render_template('period_delete.html',periods=periods,period_id=period_id,\
# 			period_name=period_name)
# 	# Process the POST request.
# 	# Delete the period. Note that the associated budget items will be deleted
# 	# automatically thanks to 'cascade' option we set up in database_setup.py file:
# 	session.delete(period)
# 	session.commit()
# 	flash('Period "%s" was deleted' % period_name)
# 	return redirect(url_for('showPeriods',period_id=period_id))

# @app.route('/period/<int:period_id>/new/', methods=['GET','POST'])
# @login_required
# def newBudget(period_id):
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	period = session.query(Period).filter_by(id=period_id).first()
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	if request.method == 'GET':
# 		return render_template('budget_new.html',periods=periods,period_id=period_id)
# 	# Get data from the POST request:
# 	budget_name = request.form['budget_name'].strip()
# 	budget_amount = request.form['budget_amount']
# 	actual_amount = request.form['actual_amount']
# 	# Check if budget name is non-empty:
# 	if not budget_name:
# 		flash('Please enter the budget category name')
# 		return render_template('budget_new.html',periods=periods,period_id=period_id)
# 	# Check if length is reasonable (between 2 and 25 chars):
# 	if len(budget_name)>25:
# 		flash('Category name appears too long - try to keep things short and sweet')
# 		return render_template('budget_new.html',periods=periods,period_id=period_id)
# 	if len(budget_name)<3:
# 		flash('Category name appears too short - let\'s be more serious')
# 		return render_template('budget_new.html',periods=periods,period_id=period_id)
# 	# If amounts are null or empty string, set to zero:
# 	if budget_amount == '' or budget_amount is None:
# 		budget_amount = 0
# 	if actual_amount == '' or actual_amount is None:
# 		actual_amount = 0
# 	# Convert amounts to type integer or flash the error:
# 	try:
# 		budget_amount = int(budget_amount)
# 		actual_amount = int(actual_amount)
# 	except:
# 		flash('Amounts must be whole numbers, not text or decimals')
# 		return render_template('budget_new.html',periods=periods,period_id=period_id)
# 	# Check if amounts are between 0 and 1,000,000:
# 	if budget_amount<0 or actual_amount<0:
# 		flash('Amounts cannot be negative')
# 		return render_template('budget_new.html',periods=periods,period_id=period_id)
# 	if budget_amount>1000000 or actual_amount>1000000:
# 		flash('Amount greater than 1,000,000 - are you serious?')
# 		return render_template('budget_new.html',periods=periods,period_id=period_id)
# 	# Validation passed. Add budget to the database:
# 	newBudget = Budget(period_id=period_id,name=budget_name,budget_amount=budget_amount,\
# 		actual_amount=actual_amount)
# 	session.add(newBudget)
# 	session.commit()
# 	flash('New budget category was added')
# 	return redirect(url_for('showBudget',period_id=period_id))

# @app.route('/period/<int:period_id>/budget/<int:budget_id>/edit', methods=['GET','POST'])
# @login_required
# def editBudget(period_id, budget_id):
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	period = session.query(Period).filter_by(id=period_id).first()
# 	budget = session.query(Budget).filter_by(id=budget_id).first()
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	if request.method == 'GET':
# 		return render_template('budget_edit.html',periods=periods,period_id=period_id,budget=budget)
# 	# Get data from the POST request:
# 	budget_name = request.form['budget_name'].strip()
# 	budget_amount = request.form['budget_amount']
# 	actual_amount = request.form['actual_amount']
# 	# Check if budget name is non-empty:
# 	if not budget_name:
# 		flash('Please enter the budget category name')
# 		return render_template('budget_edit.html',periods=periods,period_id=period_id,budget=budget)
# 	# Check if length is reasonable (between 2 and 25 chars):
# 	if len(budget_name)>25:
# 		flash('Category name appears too long - try to keep things short and sweet')
# 		return render_template('budget_edit.html',periods=periods,period_id=period_id,budget=budget)
# 	if len(budget_name)<3:
# 		flash('Category name appears too short - let\'s be more serious')
# 		return render_template('budget_edit.html',periods=periods,period_id=period_id,budget=budget)
# 	# If amounts are null or empty string, set to zero:
# 	if budget_amount == '' or budget_amount is None:
# 		budget_amount = 0
# 	if actual_amount == '' or actual_amount is None:
# 		actual_amount = 0
# 	# Convert amounts to type integer or flash the error:
# 	try:
# 		budget_amount = int(budget_amount)
# 		actual_amount = int(actual_amount)
# 	except:
# 		flash('Amounts must be whole numbers, not text or decimals')
# 		return render_template('budget_edit.html',periods=periods,period_id=period_id,budget=budget)
# 	# Check if amounts are between 0 and 1,000,000:
# 	if budget_amount<0 or actual_amount<0:
# 		flash('Amounts cannot be negative')
# 		return render_template('budget_edit.html',periods=periods,period_id=period_id,budget=budget)
# 	if budget_amount>1000000 or actual_amount>1000000:
# 		flash('Amount greater than 1,000,000 - are you serious?')
# 		return render_template('budget_edit.html',periods=periods,period_id=period_id,budget=budget)
# 	# Validation passed. Update budget in the database:
# 	budget.name = budget_name
# 	budget.budget_amount = budget_amount
# 	budget.actual_amount = actual_amount
# 	session.add(budget)
# 	session.commit()
# 	flash('Budget category was updated')
# 	return redirect(url_for('showBudget',period_id=period_id))

# @app.route('/period/<int:period_id>/budget/<int:budget_id>/delete', methods=['GET','POST'])
# @login_required
# def deleteBudget(period_id, budget_id):
# 	user = session.query(User).filter_by(email=login_session['email']).first()
# 	period = session.query(Period).filter_by(id=period_id).first()
# 	budget = session.query(Budget).filter_by(id=budget_id).first()
# 	periods = session.query(Period).filter_by(user_id=user.id).order_by(Period.id.desc())
# 	budget_name = budget.name
# 	if request.method == 'GET':
# 		return render_template('budget_delete.html',periods=periods,period_id=period_id,\
# 			budget_id=budget_id,budget_name=budget_name)
# 	# Process the POST request:
# 	session.delete(budget)
# 	session.commit()
# 	flash('Category "%s" was deleted' % budget_name)
# 	return redirect(url_for('showBudget',period_id=period_id))

# # Making an API Endpoint (GET Request)
# @app.route('/JSON')
# def budgetItems():
# 	items = session.query(Budget).all()
# 	return jsonify(BudgetItems=[i.serialize for i in items])

if __name__ == '__main__':
	app.secret_key = 'super_secret_key'
	# secret_key above is for session management
	app.debug = True
	# debug mode allows server to reload automatically after code change
	app.run(host = '0.0.0.0', port = 8000)
	# listening on all public IP, port 8000
