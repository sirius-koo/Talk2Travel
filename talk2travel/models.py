from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class User(db.Model):
    id       = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    # password hash, etc.

class Schedule(db.Model):
    id         = db.Column(db.Integer, primary_key=True)
    user_id    = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    title      = db.Column(db.String(120))        # e.g. "Osaka Trip"
    city       = db.Column(db.String(64))
    start      = db.Column(db.Date)
    end        = db.Column(db.Date)
    passengers = db.Column(db.Integer)
    budget     = db.Column(db.Integer)
    user       = db.relationship('User', backref=db.backref('schedules', lazy=True))