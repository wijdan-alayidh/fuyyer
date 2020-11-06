#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
from flask_wtf import Form
from forms import *
# migrate libraries 
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')

# TODO: connect to a local postgresql database
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://Wijdan@localhost:5432/fyyur'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
# migrate using flask script
migrate = Migrate(app, db)
manager = Manager(app)
manager.add_command('db', MigrateCommand)
#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Venue(db.Model):
    __tablename__ = 'Venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(), nullable=False)
    city = db.Column(db.String(120) ,nullable=False)
    state = db.Column(db.String(120), nullable=False)
    address = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # relationship
    shows = db.relationship('Shows', backref='venue', lazy=True)
    
    def __repr__(self):
      return ''' Venue {self.id} {self.name} '''

class Artist(db.Model):
    __tablename__ = 'Artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String() ,nullable=False , unique= True)
    city = db.Column(db.String(120) ,nullable=False)
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))

    # relationship
    shows = db.relationship('Shows', backref='artist', lazy=True)

    def __repr__(self):
      return ''' Artist {self.name} {self.genres} '''

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
class Shows(db.Model):
  __tablename__ = 'Show'
  id = db.Column(db.Integer, primary_key=True)
  artist_id = db.Column(db.Integer, db.ForeignKey('Artist.id'), unique= True ,nullable=False)
  venue_id = db.Column(db.Integer, db.ForeignKey('Venue.id'), unique= True ,nullable=False)
  start_time = db.Column(db.DateTime, nullable=False)

  def __repr__(self):
    return '''Show {self.id} {self.artist_id} {self.venue_id} {self.start_time}'''

db.create_all()
#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  return render_template('pages/home.html')


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.
  

  # read the data from database
  venues = Venue.query.all()
  current_time = datetime.now()
  data=[]
  # loop for venues
  for venue in venues:
    print(venue)
    upcoming_show = venue.shows.filter_by(Show.start_time > current_time).all()
    city_and_state = city_and_state.add((Venue.city , Venue.state))

    data.append({
      'city' : Venue.city ,
      'state' : Venue.state,
      "venues": [{
        "id": venues.id,
        "name": venues.name,
        "num_upcoming_shows": len(upcoming_show),
      }]
    })
  return render_template('pages/venues.html', areas=data)

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

  search_term = Venue.get('search_term')
  venues = Venue.query.filter(Venue.name.ilike('%' + search_term + '%')).all()
  venue_list = list()

  venue_list.append({
    'name' : Venue.name 
  })

  response={
    "count": len(venues),
    "data": venue_list
  }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0

  current_time = datetime.now()

  # condition to classify shows to past and upcomming shows
  for show in venue.shows:
    if show.start_time > current_time:
      upcoming_shows_count = upcoming_shows_count + 1
      upcoming_shows.append ({
        'artists_id' : show.artist_id,
        'artists_name' : show.artist.name,
        'artists_image_link' : show.artist_image_link,
        'start_time' : format_datetime(str(show.start_time))
      }) 
    elif show.start_time < current_time:
      past_shows_count = past_shows_count + 1
      past_shows.append ({
        'artists_id' : show.artist_id,
        'artists_name' : show.artist.name,
        'artists_image_link' : show.artist_image_link,
        'start_time' : format_datetime(str(show.start_time))
      }) 
  
  data ={
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "phone": venue.phone,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }
  data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=data)


#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  form = VenueForm()
  # data comes from form
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  image_link = form.image_link.data
  genres = form.genres.data
  website = form.website.data
  facebook_link = form.facebook_link.data.strip()
  address = form.address.data
  seeking_description = form.seeking_description.data
  seeking_talent = True if form.seeking_talent.data == 'Yes' else False
  
  
  if form.validate() == True :
    form_error = True
    flash( form.errors )
    return redirect(url_for('create_venue_submission'))

  else:
    form_error = False
    try:
      new_venue = Venue(
        name=name, 
        city=city, 
        state=state, 
        address=address, 
        phone=phone,
        seeking_talent=seeking_talent,
        seeking_description=seeking_description, 
        image_link=image_link,
        website=website,
        facebook_link=facebook_link)
      for genre in genres:
        fetch_genre = Genre.query.filter_by(name=genre).one_or_none()  
        if fetch_genre:
          new_venue.genres.append(fetch_genre)
        else:
          new_genre = Genre(name=genre)
          db.session.add(new_genre)
          new_venue.genres.append(new_genre)

      db.session.add(new_venue)
      db.session.commit()

    except Exception as e:
      form_error = True
      db.session.rollback()
    finally:
      db.session.close()
      if not form_error:
        flash('Venue ' + request.form['name'] + ' was successfully listed!')
        return redirect(url_for('index'))
      else:
        flash('An error occurred. Venue ' + name + ' could not be listed.')
        print("Error in create_venue_submission()")
        return render_template('500.html'), 500
  # on successful db insert, flash success
  flash('Venue ' + request.form['name'] + ' was successfully listed!')
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  try:
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    db.session.rollback() 
  finally:
    db.session.close()

  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # TODO: replace with real data returned from querying the database

  artists = Artist.query.filter_by(Artist.name).all()

  data = []
  for artist in artists:
    data.append({
        "id": artist.id,
        "name": artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  
  search_term = Artist.get('search_term')
  artist = Artist.query.filter(Artist.name.ilike('%' + search_term + '%')).all()
  artist_list = list()

  artist_list.append({
    'name' : Venue.name 
  })

  response={
    "count": len(artist),
    "data": artist_list
  }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  
  artist = Artist.query.get(artist_id)
  past_shows = []
  upcoming_shows = []
  past_shows_count = 0
  upcoming_shows_count = 0

  current_time = datetime.now()

  for show in artist.shows:
    if show.start_time > current_time:
      upcoming_shows_count = upcoming_shows_count + 1
      upcoming_shows.append ({
        'venue_id' : show.venue_id,
        'venue_name' : show.venue.name,
        'venue_image_link' : show.venue.artist_image_link,
        'start_time' : format_datetime(str(show.start_time))
      }) 
    elif show.start_time < current_time:
      past_shows_count = past_shows_count + 1
      past_shows.append ({
        'venue_id' : show.artist_id,
        'venue_name' : show.artist.name,
        'venue_image_link' : show.artist_image_link,
        'start_time' : format_datetime(str(show.start_time))
      }) 
  
  data ={
    "id": artist_id,
    "name": artist.name,
    "genres": genres,
    "city": artist.city,
    "state": artist.state,
    "phone": artist.phone,
    "website": artist.website,
    "facebook_link": artist.facebook_link,
    "seeking_talent": artist.seeking_talent,
    "seeking_description": artist.seeking_description,
    "image_link": artist.image_link,
    "past_shows": past_shows,
    "upcoming_shows": upcoming_shows,
    "past_shows_count": past_shows_count,
    "upcoming_shows_count": upcoming_shows_count,
  }

  data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):

  artist = Artist.query.get(artist_id)
  form = ArtistForm(obj=artist)
  genres = [ genre.name for genre in artist.genres ] 
  artist = {
      "id": artist_id,
      "name": artist.name,
      "genres": genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website": artist.website,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link
  }
  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  
  form = ArtistForm()
  
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  seeking_venue = True if form.seeking_venue.data == 'Yes' else False
  seeking_description = form.seeking_description.data.strip()
  image_link = form.image_link.data.strip()
  website = form.website.data.strip()
  facebook_link = form.facebook_link.data.strip()

  if form.validate == False:
    flash( form.errors )
    return redirect(url_for('show_artist', artist_id=artist_id))
  else:
    error_in_update = False

  try:
    artist = Artist.query.get(artist_id)
    artist.name = name
    artist.city = city
    artist.state = state
    artist.phone = phone
    artist.genres = genres
    artist.seeking_venue = seeking_venue
    artist.seeking_description = seeking_description
    artist.image_link = image_link
    artist.website = website
    artist.facebook_link = facebook_link

    db.session.commit()
  except Exception as e:
    error_in_insert = True
    db.session.rollback()
  finally:
    db.session.close()
  if error_in_insert == False:
    flash('Artist ' + request.form['name'] + ' was successfully updated!')
    return render_template('forms/edit_artist.html', form=form, artist=artist)
  else:
      flash('An error occurred. Artist ' + name + ' could not be updated.')
      return render_template('500.html'), 500
      
@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):

  venue = Venue.query.get(venue_id)

  if venue == False:
    redirect(url_for('index'))
  else:
    form = VenueForm()
    venue = Venue.query.get(venue_id)

  venue = {
    "id": venue_id,
    "name": venue.name,
    "genres": genres,
    "address": venue.address,
    "city": venue.city,
    "state": venue.state,
    "website": venue.website,
    "facebook_link": venue.facebook_link,
    "seeking_talent": venue.seeking_talent,
    "seeking_description": venue.seeking_description,
    "image_link": venue.image_link
  }

  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  form = VenueForm()

  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  image_link = form.image_link.data
  website = form.website.data
  facebook_link = form.facebook_link.data
  seeking_description = form.seeking_description.data
  seeking_venue = True if form.seeking_venue.data == 'Yes' else False


  if form.validate == False: 
    flash( form.errors )
    return redirect(edit_venue_submission, venue_id=venue_id) 
  else:
    error_in_update = False

  if not form.validate():
    flash( form.errors )
    return redirect('create_artist_submission')
  else:
    error_in_insert = False


  try:
    venue = Venue.query.get(venue_id)

    venue.name = name
    Venue.city = city
    venue.state = state
    venue.genres = genres
    venue.facebook_link = facebook_link
    venue.address = address
    venue.phone = phone
    venue.seeking_talent = seeking_talent
    venue.seeking_description = seeking_description
    venue.image_link = image_link
    venue.website = website
   
    db.session.commit()
  except Exception as e:
    error_in_insert = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error_in_insert:
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
      flash('An error occurred. Artist ' + name + ' could not be listed.')
      print("Error in create_venue_submission()")
      return render_template('500.html'), 500

  # # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # # TODO: on unsuccessful db insert, flash an error instead.
  # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return redirect(url_for('show_venue', venue_id=venue_id))
 


#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  form = ArtistForm()
  name = form.name.data
  city = form.city.data
  state = form.state.data
  phone = form.phone.data
  genres = form.genres.data
  seeking_venue = True if form.seeking_venue.data == 'Yes' else False
  seeking_description = form.seeking_description.data
  image_link = form.image_link.data
  website = form.website.data
  facebook_link = form.facebook_link.data

  if not form.validate():
    flash( form.errors )
    return redirect(create_artist_submission)
  else:
    error_in_insert = False
  try:
    new_artist = Artist(name=name, 
                        city=city, 
                        state=state, 
                        phone=phone,
                        genres=genres,
                        seeking_venue=seeking_venue, 
                        seeking_description=seeking_description, 
                        image_link=image_link,
                        website=website, 
                        facebook_link=facebook_link)

    db.session.add(new_artist)
    db.session.commit()
  except Exception as e:
    error_in_insert = True
    db.session.rollback()
  finally:
    db.session.close()
  if not error_in_insert:
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
    return render_template('pages/home.html')
  else:
      flash('An error occurred. Artist ' + name + ' could not be listed.')
      print("Error in create_artist_submission()")
      return render_template('500.html'), 500

  # # on successful db insert, flash success
  flash('Artist ' + request.form['name'] + ' was successfully listed!')
  # # TODO: on unsuccessful db insert, flash an error instead.
  # # e.g., flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.
  #       num_shows should be aggregated based on number of upcoming shows per venue.

  data = []
  shows = Show.query.all()
  
  for show in shows:
    data.append({
        "venue_id": show.venue.id,
        "venue_name": show.venue.name,
        "artist_id": show.artist.id,
        "artist_name": show.artist.name,
        "artist_image_link": show.artist.image_link,
        "start_time": format_datetime(str(show.start_time))
    })

  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead
  form = ShowForm()

  artist_id = form.artist_id.data
  venue_id = form.venue_id.data
  start_time = form.start_time.data

  form_error = False

  try:
    new_show = Show(start_time=start_time, artist_id=artist_id, venue_id=venue_id)
    db.session.add(new_show)
    db.session.commit()
  except Exception as e:
    form_error = True
    print( ''' Exception "{e}" in create_show_submission() ''')
    db.session.rollback()
  finally:
    db.session.close()

  if form_error:
    flash('An error occurred. Venue  could not be listed.')
    return redirect(url_for('index'))
  else:
    flash('Show was successfully listed!')
  # on successful db insert, flash success
  
  # TODO: on unsuccessful db insert, flash an error instead.
  # e.g., flash('An error occurred. Show could not be listed.')
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()
    # migrate running 
    manager.run()
# # Or specify port manually:
# '''
# if __name__ == '__main__':
#     port = int(os.environ.get('PORT', 5000))
#     app.run(host='0.0.0.0', port=port)
# '''
