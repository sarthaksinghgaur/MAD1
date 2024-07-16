from applications.database import db
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)
    # role = db.Column(db.String(50), nullable=False)

class Influencer(db.Model):
    id = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True)
    Category = db.Column(db.String(100),nullable = False)
    Niche = db.Column(db.String(100),nullable = False)
    Reach = db.Column(db.String(100),nullable = False)

class Sponsor(db.Model):
    id = db.Column(db.Integer,db.ForeignKey('user.id'), primary_key=True)
    CompanyName = db.Column(db.String(100),nullable = False)
    Industry = db.Column(db.String(100),nullable = False)
    Budget = db.Column(db.Integer,nullable = False)

class Ad_request(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    campaign_id = db.Column(db.Integer,db.ForeignKey('campaign.id'))
    influencer_id = db.Column(db.Integer,db.ForeignKey('influencer.id'))
    messages = db.Column(db.String(500))
    requirements = db.Column(db.String(500),nullable = False)
    payment_amount = db.Column(db.Integer,nullable = False)
    status = db.Column(db.String(100),nullable = False)

class Campaign(db.Model):
    id = db.Column(db.Integer,db.ForeignKey('campaign.id'), primary_key=True)
    sponso_id = db.Column(db.Integer,db.ForeignKey('sponsor.id'))
    description = db.Column(db.String(500))
    requirements = db.Column(db.String(500),nullable = False)
    budget = db.Column(db.Integer,nullable = False)
    visibility = db.Column(db.String(100),nullable = False)
    goals = db.Column(db.String(500))

        