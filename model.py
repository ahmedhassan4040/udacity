from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

db=SQLAlchemy()
def db_setup(app):
    app.config.from_object('config')
    db.app=app
    db.init_app(app)
    migrate = Migrate(app, db)
    return db

class Venue(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String)
    genres= db.Column(db.ARRAY(db.String))
    website=db.Column(db.String)
    seeking_talent = db.Column(db.Boolean)
    seeking_description= db.Column(db.String)
    show=db.relationship("Show",backref="venue")
class Artist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String)
    website=db.Column(db.String)
    seeking_venue = db.Column(db.Boolean)# I Ranme It From seeking_talent to seeking_venue
    seeking_description= db.Column(db.String)
    show=db.relationship("Show",backref="artist")
class Show(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    venue_id= db.Column(db.Integer,db.ForeignKey("venue.id"))
    artist_id= db.Column(db.Integer,db.ForeignKey("artist.id"))
    start_time= db.Column(db.DateTime)

    # TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.
