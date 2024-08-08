from flask_sqlalchemy import SQLAlchemy
from applications.database import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(128), nullable=False)
    role = db.Column(db.String(120), nullable=False)
    active = db.Column(db.Boolean, default=True)
    
    # One-to-One relationship with Influencer and Sponsor
    influencer = db.relationship('Influencer', uselist=False, back_populates='user', cascade="all, delete-orphan")
    sponsor = db.relationship('Sponsor', uselist=False, back_populates='user', cascade="all, delete-orphan")

    def __repr__(self):
        return f'<User {self.username}>'


class Influencer(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    name = db.Column(db.String(120), nullable=False)
    category = db.Column(db.String(120), nullable=False)
    niche = db.Column(db.String(120), nullable=False)
    reach = db.Column(db.Integer, nullable=False)
    platform = db.Column(db.String(120), nullable=False)
    engagement_rate = db.Column(db.Float, nullable=False)
    flagged = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='influencer')
    ad_requests = db.relationship('AdRequest', back_populates='influencer')

    def __repr__(self):
        return f'<Influencer {self.name} - {self.category}>'


class Sponsor(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    company_name = db.Column(db.String(120), nullable=False)
    industry = db.Column(db.String(120), nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    flagged = db.Column(db.Boolean, default=False)

    user = db.relationship('User', back_populates='sponsor')
    campaigns = db.relationship('Campaign', back_populates='sponsor')
    ad_requests = db.relationship('AdRequest', back_populates='sponsor')

    def __repr__(self):
        return f'<Sponsor {self.company_name} - {self.industry}>'


class Campaign(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    start_date = db.Column(db.Date, nullable=False)
    end_date = db.Column(db.Date, nullable=False)
    budget = db.Column(db.Integer, nullable=False)
    visibility = db.Column(db.String(10), nullable=False)  # 'public' or 'private'
    goals = db.Column(db.Text, nullable=False)
    
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    is_public = db.Column(db.Boolean, default=True)

    ad_requests = db.relationship('AdRequest', backref='campaign', lazy=True)
    sponsor = db.relationship('Sponsor', back_populates='campaigns')

    def __repr__(self):
        return f'<Campaign {self.name} - {self.visibility}>'


class AdRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    sponsor_id = db.Column(db.Integer, db.ForeignKey('sponsor.id'), nullable=False)
    campaign_id = db.Column(db.Integer, db.ForeignKey('campaign.id'), nullable=False)
    influencer_id = db.Column(db.Integer, db.ForeignKey('influencer.id'), nullable=False)
    messages = db.Column(db.Text, nullable=True)
    requirements = db.Column(db.Text, nullable=False)
    payment_amount = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(10), nullable=False)  # 'Pending', 'Accepted', 'Rejected'

    influencer = db.relationship('Influencer', back_populates='ad_requests')
    sponsor = db.relationship('Sponsor', back_populates='ad_requests')

    def __repr__(self):
        return f'<AdRequest {self.id} - {self.status}>'
