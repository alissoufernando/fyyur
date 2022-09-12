#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_migrate import Migrate
import logging
from logging import Formatter, FileHandler, error, exception
from flask_wtf import Form
from forms import *
from models import *
import collections
collections.Callable = collections.abc.Callable
import pickle

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
db.init_app(app)
migrate = Migrate(app, db)


# TODO: connect to a local postgresql database


#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="EE MM, dd, y h:mma"
  return babel.dates.format_datetime(date, format, locale='en')

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
# ----------------------------- implementation for displaying all venue -----------------------------

def venues():
  # TODO: replace with real venues data.
  #       num_upcoming_shows should be aggregated based on number of upcoming shows per venue.
  data=[]
  results = Venue.query.distinct(Venue.city, Venue.state).all()
  for result in results:
    local = {
      'city': result.city,
      'state': result.state,
    }
    venues = Venue.query.filter_by(city=result.city, state=result.state).all()
    formatted_venues = []
    for venue in venues:
      formatted_venues.append({
        "id": venue.id,
        "name": venue.name,
        #"num_upcoming_shows": len(list(filter(lambda x: x.start_time > datetime.now() )))
      })
    local["venues"] = formatted_venues
    data.append(local)
  
  return render_template('pages/venues.html', areas=data);

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for Hop should return "The Musical Hop".
  # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"
  data = Venue.query.filter(Venue.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  response = {"count": len(data), "data": data }
  return render_template('pages/search_venues.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  venue = Venue.query.get(venue_id)

  upcoming_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows = []
  for show in upcoming_shows_query:
    upcoming_shows.append({
     "artist_id": show.artist_id,
      "artist_name": show.artist_name,
      "artist_image_link": show.artist_image_link,
      "start_time": show.start_time.strftime('%m%/%d/%Y, %H:%M:%S')
    })
  past_shows_query = db.session.query(Show).join(Artist).filter(Show.venue_id==venue_id).filter(Show.start_time < datetime.now()).all()
  past_shows = []

  for show in past_shows_query:
    past_shows.append({
     "artist_id": show.artist_id,
      "artist_image_link":  Artist.query.with_entities(Artist.image_link).filter_by(id = show.artist_id).first(),
      "artist_name": Artist.query.with_entities(Artist.name).filter_by(id = show.artist_id).first(),
      "start_time": str(show.start_time)
    })
  data = {
      "id": venue.id,
      "name": venue.name,
      "genres": venue.genres,
      "address": venue.address,
      "city": venue.city,
      "state": venue.state,
      "phone": venue.phone,
      "website_link": venue.website_link,
      "facebook_link": venue.facebook_link,
      "seeking_talent": venue.seeking_talent,
      "seeking_description": venue.seeking_description,
      "image_link": venue.image_link,
      "past_shows": past_shows,
      "upcoming_shows": upcoming_shows,
      "past_shows_count": len(past_shows),
      "upcoming_shows_count": len(upcoming_shows),
    }

  return render_template('pages/show_venue.html', venue=data)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
# ----------------------------------------- implementation for creating a venue -----------------------------------------
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  form = VenueForm(request.form)

  try:
    n_venue = Venue(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      address=form.address.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      seeking_talent=form.seeking_talent.data,
      website_link=form.website_link.data,
      seeking_description=form.seeking_description.data,
    )
    db.session.add(n_venue)
    db.session.commit()
    flash('Venue ' + request.form['name'] + ' was successfully listed!')
  except Exception:
    flash('An error occurred. Venue ' + data.name + ' could not be listed.')
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion

  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.
  # see: http://flask.pocoo.org/docs/1.0/patterns/flashing/
  return render_template('pages/home.html')

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):

  try:
    venue = Venue.query.filter(id=venue_id).first_or_404()
    db.session.delete(venue)
    db.session.commit()
    flash('Venue delete')
    return render_template('pages/home.html')
  except ValueError:
    flash('Erros deleting')
    db.session.rollback()
  finally:
    db.session.close()

  return None
  # TODO: Complete this endpoint for taking a venue_id, and using
  # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

  # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
# ----------------------------- implementation for displaying all artists  -----------------------------

def artists():
  # TODO: replace with real data returned from querying the database
  data= Artist.query.all()

  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
# ----------------------------- implementation pour la recherche d'un artist -----------------------------
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  data = Artist.query.filter(Artist.name.ilike('%{}%'.format(request.form.get('search_term', '')))).all()
  response = {"count": len(data), "data": data }
  return render_template('pages/search_artists.html', results=response, search_term=request.form.get('search_term', ''))

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the artist page with the given artist_id
  # TODO: replace with real artist data from the artist table, using artist_id
  artist = Artist.query.get(artist_id)
 
  all_post_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
  past_shows_list = []

  for past_show in all_post_shows:
    past_shows_list.append({
      "venue_id": past_show.venue_id,
      "venue_name": past_show.venue_name,
      "venue_image_link": past_show.venue_image_link,
      "start_time": format_datetime(str(past_show.start_time)),
    })
 
  all_upcoming_shows = db.session.query(Show).join(Venue).filter(Show.artist_id == artist_id).filter(Show.start_time > datetime.now()).all()
  upcoming_shows_list = []

  for upcoming_show in all_upcoming_shows:
    upcoming_shows_list.append({
      "venue_id": upcoming_show.venue_id,
      "venue_name": upcoming_show.venue_name,
      "venue_image_link": upcoming_show.venue_image_link,
      "start_time": format_datetime(str(upcoming_show.start_time)),
    })
  data = {
      "id": artist.id,
      "name": artist.name,
      "genres": artist.genres,
      "city": artist.city,
      "state": artist.state,
      "phone": artist.phone,
      "website_link": artist.website_link,
      "facebook_link": artist.facebook_link,
      "seeking_venue": artist.seeking_venue,
      "seeking_description": artist.seeking_description,
      "image_link": artist.image_link,
      "past_shows": past_shows_list,
      "upcoming_shows": upcoming_shows_list,
      "past_shows_count": len(past_shows_list),
      "upcoming_shows_count": len(upcoming_shows_list),
    }

  return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist = Artist.query.get(artist_id)
  if artist:
    form.name.data = artist.name
    form.city.data = artist.city
    form.state.data = artist.state
    form.phone.data = artist.phone
    form.genres.data = artist.genres
    form.facebook_link.data = artist.facebook_link
    form.image_link.data = artist.image_link
    form.website_link.data = artist.website_link
    form.seeking_venue.data = artist.seeking_venue
    form.seeking_description.data = artist.seeking_description


  # TODO: populate form with fields from artist with ID <artist_id>
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
# ----------------------------- implementation for modifying an Artist -----------------------------

  form = ArtistForm(request.form)  
  try:
    artist = Artist.query.filter_by(id = artist_id).first()
    artist.name = form.name.data
    artist.city=form.city.data
    artist.state=form.state.data
    artist.phone=form.phone.data
    artist.genres=form.genres.data
    artist.image_link=form.image_link.data
    artist.facebook_link=form.facebook_link.data
    artist.seeking_venue=form.seeking_venue.data
    artist.website_link=form.website_link.data
    artist.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('la modification a été prise en charge')
  except:
    db.rollback()
    flash('La modification a echoué')
 

  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes

  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  venue= Venue.query.get(venue_id)
  if venue:
    form.name.data = venue.name
    form.city.data = venue.city
    form.state.data = venue.state
    form.phone.data = venue.phone
    form.address.data = venue.address
    form.genres.data = venue.genres
    form.facebook_link.data = venue.facebook_link
    form.image_link.data = venue.image_link
    form.website_link.data = venue.website_link
    form.seeking_talent.data = venue.seeking_talent
    form.seeking_description.data = venue.seeking_description
   
  return render_template('forms/edit_venue.html', form=form, venue=venue)
  # TODO: populate form with values from venue with ID <venue_id>

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
# ----------------------------- implementation for modifying an Venue -----------------------------
def edit_venue_submission(venue_id):
  form = VenueForm(request.form)
  try:
    venue = Venue.query.filter_by(id = venue_id).first()
    venue.name=form.name.data
    venue.city=form.city.data
    venue.state=form.state.data
    venue.address=form.address.data
    venue.phone=form.phone.data
    venue.genres=form.genres.data
    venue.image_link=form.image_link.data
    venue.facebook_link=form.facebook_link.data
    venue.seeking_talent= form.seeking_talent.data
    venue.website_link=form.website_link.data
    venue.seeking_description=form.seeking_description.data
    db.session.commit()
    flash('la modification a été prise en charge')

  except:
    db.session.rollback()
    flash('La modification a echoué')
  finally:
    db.session.close()


  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
# ----------------------------- implementation for creating a artist -----------------------------
  form = ArtistForm(request.form)
  try:
    n_artist = Artist(
      name=form.name.data,
      city=form.city.data,
      state=form.state.data,
      phone=form.phone.data,
      genres=form.genres.data,
      image_link=form.image_link.data,
      facebook_link=form.facebook_link.data,
      seeking_venue=form.seeking_venue.data,
      website_link=form.website_link.data,
      seeking_description=form.seeking_description.data,
    )
    db.session.add(n_artist)
    db.session.commit()
    flash('Artist ' + request.form['name'] + ' was successfully listed!')
  except Exception:
    flash('An error occurred. Artist ' + data.name + ' could not be listed.')
  return render_template('pages/home.html')

  # called upon submitting the new artist listing form
  # TODO: insert form data as a new Venue record in the db, instead
  # TODO: modify data to be the data object returned from db insertion
  # on successful db insert, flash success
  # TODO: on unsuccessful db insert, flash an error instead.

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  # TODO: replace with real venues data.

# ----------------------------- implementation of requests to display the real data of show -----------------------------

  shows = Show.query.all()
  data= []
  for show in shows:
    x = {
      "venue_id": show.venue_id,
      "venu_name": Venue.query.with_entities(Venue.name).filter_by(id = show.venue_id).first(),
      "artist_id": show.artist_id,
      "artist_name": Artist.query.with_entities(Artist.name).filter_by(id = show.artist_id).first(),
      "artist_image_link": Artist.query.with_entities(Artist.image_link).filter_by(id = show.artist_id).first(),
      "start_time": str(show.start_time)
    }
    data.append(x)
    print(data)
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
# ----------------------------- implementation for creating a show -----------------------------

  form = ShowForm(request.form)
  if form.validate():
    venue_id = form.venue_id.data,
    artist_id = form.artist_id.data,
    venue = db.session.query(Venue).filter_by(id=venue_id).first()
    artist = db.session.query(Artist).filter_by(id=artist_id).first()
    
    try:
      n_show = Show()
      form.populate_obj(n_show)
      db.session.add(n_show)
      db.session.commit()
      flash('Show was successfully listed!')
    except Exception:
      flash('An error occurred. Show could not be listed.')
    
  # called to create new shows in the db, upon submitting new show listing form
  # TODO: insert form data as a new Show record in the db, instead

  # on successful db insert, flash success

  # TODO: on unsuccessful db insert, flash an error instead.
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

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
