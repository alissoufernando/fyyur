
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

# TODO: connect to a local postgresql database



#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#
# ----------------------------- Show class implementation -----------------------------

class Show(db.Model):
    __tablename__ = 'show'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime())

    venue = db.relationship('Venue', backref=db.backref('venue', lazy=True))
    artist = db.relationship('Artist', backref=db.backref('artist', lazy=True))
# -------------------------  show constructor   --------------------------------------------
    def __repr__(self):
        return f'<Show: {self.id}0 {self.venue_id} {self.artist_id} {self.start_time} >'

# ----------------------------- Venue class implementation -----------------------------

class Venue(db.Model):
    __tablename__ = 'venue'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.ARRAY(db.String))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_talent = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(500))
    artist = db.relationship("Artist", secondary="show", lazy="joined", overlaps="shows,venue,artist")

# ------------------------- venue constructor --------------------------------------------
    def __repr__(self):
        return f'<Venue: {self.id} {self.name} {self.city} {self.state} {self.address} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.seeking_talent} {self.seeking_description} {self.website_link}>'

# ----------------------------- Artist class implementation -----------------------------

class Artist(db.Model):
    __tablename__ = 'artist'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean)
    seeking_description = db.Column(db.String(500))
    website_link = db.Column(db.String(500))

    venue = db.relationship("Venue", secondary="show", lazy="joined", overlaps="artist,venue,shows")

    # ------------------------- artist constructor --------------------------------------------
    def __repr__(self):
        return f'<Artist: {self.id} {self.name} {self.city} {self.state} {self.phone} {self.genres} {self.image_link} {self.facebook_link} {self.seeking_venue} {self.seeking_description} {self.website_link}>'


    


