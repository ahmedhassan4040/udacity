#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#
import sys
import json
import dateutil.parser
import babel
from flask import(
    Flask,
    render_template,
    request,
    Response,
    flash,
    redirect,
    url_for
)

from flask_moment import Moment
import logging
from logging import Formatter, FileHandler
# from flask_wtf import Form
from forms import *
from sqlalchemy import func
from model import *

#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
db =db_setup(app)

dateTimeFormat = "YYYY-MM-DD hh:mm:ss"
dateTimeFormat_sql = "%m/%d/%Y, %H:%M"



#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#


def format_datetime(value, format='medium'):
    date = dateutil.parser.parse(value)
    if format == 'full':
        format = "EEEE MMMM, d, y 'at' h:mma"
    elif format == 'medium':
        format = "EE MM, dd, y h:mma"
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
    all_cities = Venue.query.distinct(Venue.city, Venue.state).all()
    data = []
    all_venues = Venue.query.all()

    for cityObj in all_cities:
        data.append({
            'city': cityObj.city,
            'state': cityObj.state,
            'venues': [{
                "id": ven.id,
                "name": ven.name
            } for ven in all_venues if ven.city == cityObj.city and ven.state == cityObj.state]
        })
    return render_template('pages/venues.html', areas=data)


@app.route('/venues/search', methods=['POST'])
def search_venues():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for Hop should return "The Musical Hop".
    # search for "Music" should return "The Musical Hop" and "Park Square Live Music & Coffee"

    # Filter Now In Venues
    search_term = request.form.get('search_term', '')

    search_result = db.session.query(Venue.id, Venue.name, func.count('*').label('num_upcoming_shows')).filter(Venue.name.like(
        f'%{search_term}%')).join(Show, Show.start_time > datetime.now(), isouter=True).group_by(Venue.id, Venue.name).all()
    response = {
        "count": len(search_result),
        "data": search_result
    }
    return render_template('pages/search_venues.html', results=response, search_term=search_term)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    venue_target = db.session.query(Venue).get(venue_id)

    if not venue_target:
        return render_template('errors/404.html')

    # Get Upcomig Show To Venue Target  
    upcoming_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
            Show.venue_id == venue_id,
            Show.artist_id == Artist.id,
            Show.start_time > datetime.now()
    ).all()

    # Get Past Show To Venue Venue  
    past_shows = db.session.query(Artist, Show).join(Show).join(Venue).\
        filter(
            Show.venue_id == venue_id,
            Show.artist_id == Artist.id,
            Show.start_time < datetime.now()
    ).all()

    data = {
        "id": venue_target.id,
        "name": venue_target.name,
        "genres": venue_target.genres,
        "address": venue_target.address,
        "city": venue_target.city,
        "state": venue_target.state,
        "phone": venue_target.phone,
        "website": venue_target.website,
        "facebook_link": venue_target.facebook_link,
        "seeking_talent": venue_target.seeking_talent,
        "seeking_description": venue_target.seeking_description,
        "image_link": venue_target.image_link,
        "past_shows": [{
            "artist_id": art.id,
            "artist_name": art.name,
            "artist_image_link": art.image_link, 
            "start_time": show.start_time.strftime(dateTimeFormat_sql)
        } for art,show in past_shows],
        "upcoming_shows": [{
            "artist_id": art.id,
            "artist_name": art.name,
            "artist_image_link": art.image_link, 
            "start_time": show.start_time.strftime(dateTimeFormat_sql)
        }for art,show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
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
    isError = False
    form=VenueForm(request.form)
    try:
        newVenue=Venue()
        form.populate_obj(newVenue)
        db.session.add(newVenue)  # Add New Venue To Session To Insert In Table
        db.session.commit()  # Save Change Now
    except:
        isError = True
        db.session.rollback()  # Undo
        print(sys.exc_info())
    finally:
        db.session.close()  # Close session
        if isError:
            flash('Venue ' + form.name.data + ' Some Error Has Been :(')
        if not isError:
            flash('Venue ' + form.name.data +
                  ' was successfully listed!')
    return render_template('pages/home.html')


@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
    # TODO: Complete this endpoint for taking a venue_id, and using
    # SQLAlchemy ORM to delete a record. Handle cases where the session commit could fail.

    # BONUS CHALLENGE: Implement a button to delete a Venue on a Venue Page, have it so that
    # clicking that button delete it from the db then redirect the user to the homepage
    isError = False
    try:
        db.session.query(Show).filter(
            Show.venue_id == venue_id).delete()  # Delete Shows
        db.session.query(Venue).filter(
            Venue.id == venue_id).delete()  # Delete Venue
        db.session.commit()
    except:
        db.session.rollback()
        isError = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if isError:
            flash('Venue Some Error Has Been :(')
        if not isError:
            flash('Venue was successfully Deleted!')
    return json.dumps({
        'isDeleted': True if not isError else False
    })

#  Artists
#  ----------------------------------------------------------------


@app.route('/artists')
def artists():
    # TODO: replace with real data returned from querying the database
    data = db.session.query(Artist).all()
    return render_template('pages/artists.html', artists=data)


@app.route('/artists/search', methods=['POST'])
def search_artists():
    # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
    # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
    # search for "band" should return "The Wild Sax Band".

    search_term = request.form.get('search_term', '')
    # Filter Now In Artists
    search_term = request.form.get('search_term', '')
    search_result = db.session.query(Artist.id, Artist.name, func.count('*').label('num_upcoming_shows')).filter(Artist.name.like(
        f'%{search_term}%')).join(Show, Show.start_time > datetime.now(), isouter=True).group_by(Artist.id, Artist.name).all()
    response = {
        "count": len(search_result),
        "data": search_result
    }
    return render_template('pages/search_artists.html', results=response, search_term=search_term)


@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
    # shows the venue page with the given venue_id
    # TODO: replace with real venue data from the venues table, using venue_id

    artist_target = db.session.query(Artist).get(artist_id)

    if not artist_target:
        return render_template('errors/404.html')

    # Get Upcomig Show To Artist Target  
    upcoming_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
        filter(
            Show.artist_id == artist_id,
            Show.venue_id == Venue.id,
            Show.start_time > datetime.now()
    ).all()

    # Get Past Show To Artist Trget  
    past_shows = db.session.query(Venue, Show).join(Show).join(Artist).\
        filter(
            Show.artist_id == artist_id,
            Show.venue_id == Venue.id,
            Show.start_time < datetime.now()
    ).all()

    data = {
        "id": artist_target.id,
        "name": artist_target.name,
        "genres": artist_target.genres,
        "city": artist_target.city,
        "state": artist_target.state,
        "phone": artist_target.phone,
        "website": artist_target.website,
        "facebook_link": artist_target.facebook_link,
        "seeking_venue": artist_target.seeking_venue,
        "seeking_description": artist_target.seeking_description,
        "image_link": artist_target.image_link,
        "past_shows": [{
            "venue_id": ven.id,
            "venue_name": ven.name,
            "venue_image_link": ven.image_link, 
            "start_time": show.start_time.strftime(dateTimeFormat_sql)
        } for ven,show in past_shows],
        "upcoming_shows": [{
            "venue_id": ven.id,
            "venue_name": ven.name,
            "venue_image_link": ven.image_link, 
            "start_time": show.start_time.strftime(dateTimeFormat_sql)
        }for ven,show in upcoming_shows],
        "past_shows_count": len(past_shows),
        "upcoming_shows_count": len(upcoming_shows),
    }
    return render_template('pages/show_artist.html', artist=data)

#  Update
#  ----------------------------------------------------------------


@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
    artist = Artist.query.first_or_404(artist_id)
    form = ArtistForm(obj=artist)
    return render_template('forms/edit_artist.html', form=form, artist=artist)


@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
    # TODO: take values from the form submitted, and update existing
    # artist record with ID <artist_id> using the new attributes
    isError = False
    try:
        artist = db.session.query(Artist).get(artist_id)
        if not artist:
            return render_template('errors/404.html')
        form=ArtistForm(request.form)
        artist.name = form.name.data
        artist.city = form.city.data
        artist.state = form.state.data
        artist.phone = form.phone.data
        artist.genres = request.form.getlist('genres')
        artist.image_link = form.image_link.data
        artist.facebook_link = form.facebook_link.data
        artist.website = form.website.data
        artist.seeking_venue = True if 'seeking_venue' in request.form else False
        artist.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        db.session.rollback()
        isError = True
    finally:
        db.session.close()
        if isError:
            flash('Artist ' + form.name.data + ' Some Error Has Been :(')
        if not isError:
            flash('Artist ' + form.name.data +
                  ' was successfully Saved!')
    return redirect(url_for('show_artist', artist_id=artist_id))


@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
    venue = Venue.query.first_or_404(venue_id)
    form = VenueForm(obj=venue)
    return render_template('forms/edit_venue.html', form=form, venue=venue)


@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
    # TODO: take values from the form submitted, and update existing
    # venue record with ID <venue_id> using the new attributes
    isError = False
    try:
        venue_target = db.session.query(Venue).get(venue_id)
        if not venue_target:
            return render_template('errors/404.html')
        form=VenueForm(request.form)
        venue_target.name = form.name.data
        venue_target.city = form.city.data
        venue_target.address = form.address.data
        venue_target.state = form.state.data
        venue_target.phone = form.phone.data
        venue_target.genres = request.form.getlist('genres')
        venue_target.image_link = form.image_link.data
        venue_target.facebook_link = form.facebook_link.data
        venue_target.website = form.website.data
        venue_target.seeking_talent = True if 'seeking_talent' in request.form else False
        venue_target.seeking_description = form.seeking_description.data
        db.session.commit()
    except:
        db.session.rollback()
        isError = True
        print(sys.exc_info())
    finally:
        db.session.close()
        if isError:
            flash('Venue ' + form.name.data + ' Some Error Has Been :(')
        if not isError:
            flash('Venue ' + form.name.data + ' was successfully Saved!')
    return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------


@app.route('/artists/create', methods=['GET'])
def create_artist_form():
    form = ArtistForm()
    return render_template('forms/new_artist.html', form=form)


@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
    # called upon submitting the new artist listing form
    # TODO: insert form data as a new Venue record in the db, instead
    # TODO: modify data to be the data object returned from db insertion
    isError = False
    form=ArtistForm(request.form)
    try:
        newArtist = Artist()
        form.populate_obj(newArtist)
        # Add New Venue To Session To Insert In Table
        db.session.add(newArtist)
        db.session.commit()  # Save Change Now
    except:
        isError = True
        db.session.rollback()  # Undo
        print(sys.exc_info())
    finally:
        db.session.close()  # Close session
        if isError:
            flash('Artist ' + form.name.data + ' Some Error Has Been :(')
        if not isError:
            flash('Artist ' + form.name.data +
                  ' was successfully listed!')
    return render_template('pages/home.html')


#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
    # displays list of shows at /shows
    # TODO: replace with real venues data.
    #       num_shows should be aggregated based on number of upcoming shows per venue.

    data = db.session.query(
        Show.venue_id,
        Venue.name.label('venue_name'),
        Show.artist_id,
        Artist.name.label("artist_name"),
        Artist.image_link.label("artist_image_link"),
        func.to_char(Show.start_time, dateTimeFormat).label("start_time")
    ).join(Artist).join(Venue).all()
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
    isError = False
    try:
        form=ShowForm(request.form)
        newShow = Show()
        form.populate_obj(newShow)
        db.session.add(newShow)  # Add New Venue To Session To Insert In Table
        db.session.commit()  # Save Change Now
    except:
        isError = True
        db.session.rollback()  # Undo
        print(sys.exc_info())
    finally:
        db.session.close()  # Close session
        if isError:
            flash('Show Some Error Has Been :(')
        if not isError:
            flash('Show was successfully listed!')
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
        Formatter(
            '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
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
