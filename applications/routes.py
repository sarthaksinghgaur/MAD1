from datetime import datetime
from flask import render_template, request, redirect, url_for, flash, session, abort
from flask import current_app as app
from applications.database import db
from applications.models import *
from werkzeug.security import generate_password_hash, check_password_hash
import logging

logging.basicConfig(filename='error.log', level=logging.ERROR)

# Error 500 handler
@app.errorhandler(500)
def internal_server_error(e):
    logging.error(f"An internal server error occurred: {e}")
    return render_template('500.html'), 500

# Error 500 route
@app.route('/500')
def test_500():
    raise Exception("This is a test 500 error.")

# Error 404 handler
@app.errorhandler(404)
def page_not_found(e):
    logging.error(f"404 not found error occurred: {e}")
    return render_template('404.html'), 404

# Error 404 route
@app.route('/404')
def test_404():
    abort(404)

# Before first request
@app.before_first_request
def startup_tasks():
    session.clear()
    db.create_all()
    admin_user = User.query.filter_by(email='admin@admin.admin').first()
    if not admin_user:
        # Create an admin user
        admin_user = User(id=1, username = 'admin', email='admin@admin.admin', password=generate_password_hash('adminpassword'), role='admin')
        db.session.add(admin_user)
        db.session.commit()
        
#Home Route
@app.route('/')
def home():
    return render_template('home.html')

#Signup Route
@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        role = request.form['role']
        
        # Create a new user instance
        new_user = User(username=username, email=email, password=generate_password_hash(password), role=role)
        db.session.add(new_user)
        db.session.commit()
        session['user_id'] = new_user.id

        if role == 'influencer':
            return redirect(url_for('signup_influencer'))
        elif role == 'sponsor':
            return redirect(url_for('signup_sponsor'))
    
    return render_template('signup.html')

@app.route('/signup/influencer', methods=['GET', 'POST'])
def signup_influencer():
    if 'user_id' not in session:
        flash('You need to be logged in to finish your registration.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'influencer':
        flash('You are at the wrong page to complete your registration.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        user_id = session.get('user_id')

        category = request.form['category']
        niche = request.form['niche']
        reach = request.form['reach']
        platform = request.form['platform']

        user = User.query.get(user_id)
        if not user:
            flash('User does not exist')
            return redirect(url_for('signup'))

        existing_influencer = Influencer.query.filter_by(user_id=user.id).first()
        if existing_influencer:
            flash('Influencer profile already exists')
            return redirect(url_for('login'))

        new_influencer = Influencer(
            user_id=user.id, 
            name=user.username, 
            category=category, 
            niche=niche, 
            reach=reach,
            platform=platform
        )
        db.session.add(new_influencer)
        db.session.commit()

        flash('Influencer profile created successfully!')
        return redirect(url_for('login'))

    return render_template('signup_influencer.html')


@app.route('/signup/sponsor', methods=['GET', 'POST'])
def signup_sponsor():
    if 'user_id' not in session:
        flash('You need to be logged in to finish your registration.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You are at the wrong page to complete your registration.')
        return redirect(url_for('home'))

    if request.method == 'POST':
        user_id = session.get('user_id')
        
        company_name = request.form['company_name']
        industry = request.form['industry']
        budget = request.form['budget']

        user = User.query.get(user_id)
        if not user:
            flash('User does not exist')
            return redirect(url_for('signup'))

        existing_sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        if existing_sponsor:
            flash('Sponsor profile already exists')
            return redirect(url_for('login'))

        new_sponsor = Sponsor(user_id=user.id, company_name=company_name, industry=industry, budget=budget)
        db.session.add(new_sponsor)
        db.session.commit()

        flash('Sponsor profile created successfully!')
        return redirect(url_for('login'))

    return render_template('signup_sponsor.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        # Find the user by username
        user = User.query.filter_by(username=username).first()

        # Check if the user exists and the password is correct
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            flash("Sign-in successful!")

            # Redirect based on user role
            if user.role == 'admin':
                return redirect(url_for('admin_dashboard'))
            elif user.role == 'influencer':
                return redirect(url_for('influencer_dashboard'))
            elif user.role == 'sponsor':
                return redirect(url_for('sponsor_dashboard'))
            else:
                return redirect(url_for('home'))
        else:
            flash('Invalid username or password')

    return render_template('login.html')

@app.route('/admin', methods=['GET'])
def admin_dashboard():
    if 'user_id' not in session:
        flash('You need to be logged in to access the admin dashboard.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('home'))


    active_users = User.query.filter_by(active=True).count()
    total_campaigns = Campaign.query.count()
    public_campaigns = Campaign.query.filter_by(visibility='public').count()
    private_campaigns = Campaign.query.filter_by(visibility='private').count()
    ad_requests = AdRequest.query.count()
    flagged_sponsors = Sponsor.query.filter_by(flagged=True).count()
    flagged_influencers = Influencer.query.filter_by(flagged=True).count()

    # Fetch AdRequest statistics
    pending_ad_requests = AdRequest.query.filter(
    AdRequest.status.in_(['Negotiations Underway from Sponsor', 'Negotiations Underway from Influencer'])).count()
    accepted_ad_requests = AdRequest.query.filter_by(status='Accepted').count()
    rejected_ad_requests = AdRequest.query.filter_by(status='Rejected').count()

    # Fetch all sponsors and influencers
    sponsors = Sponsor.query.all()
    influencers = Influencer.query.all()
    campaigns = Campaign.query.all()

    stats = {
        'active_users': active_users,
        'total_campaigns': total_campaigns,
        'public_campaigns': public_campaigns,
        'private_campaigns': private_campaigns,
        'ad_requests': ad_requests,
        'flagged_sponsors': flagged_sponsors,
        'flagged_influencers': flagged_influencers,
        'pending_ad_requests': pending_ad_requests,
        'accepted_ad_requests': accepted_ad_requests,
        'rejected_ad_requests': rejected_ad_requests
    }

    return render_template('admin_dashboard.html', user=user, stats=stats, campaigns=campaigns, sponsors=sponsors, influencers=influencers)

# View Routes
@app.route('/admin/users', methods=['GET'])
def admin_view_users():
    if 'user_id' not in session:
        flash('You need to be logged in to access the admin dashboard.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('home'))

    users = User.query.all()
    return render_template('view_users.html', users=users)

@app.route('/admin/campaigns', methods=['GET'])
def admin_view_campaigns():
    if 'user_id' not in session:
        flash('You need to be logged in to access the admin dashboard.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('home'))

    campaigns = Campaign.query.all()
    return render_template('view_campaigns.html', campaigns=campaigns)

@app.route('/admin/ad_requests', methods=['GET'])
def admin_view_ad_requests():
    if 'user_id' not in session:
        flash('You need to be logged in to access the admin dashboard.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('home'))

    ad_requests = AdRequest.query.all()
    return render_template('view_ad_requests.html', ad_requests=ad_requests)

@app.route('/admin/sponsors', methods=['GET'])
def admin_view_sponsors():
    if 'user_id' not in session:
        flash('You need to be logged in to access the admin dashboard.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('home'))

    sponsors = Sponsor.query.all()
    return render_template('view_sponsors.html', sponsors=sponsors)

@app.route('/admin/influencers', methods=['GET'])
def admin_view_influencers():
    if 'user_id' not in session:
        flash('You need to be logged in to access the admin dashboard.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to access the admin dashboard.')
        return redirect(url_for('home'))

    influencers = Influencer.query.all()
    return render_template('view_influencers.html', influencers=influencers)

# Edit Routes
@app.route('/admin/users/edit/<int:user_id>', methods=['GET', 'POST'])
def admin_edit_user(user_id):
    if 'user_id' not in session:
        flash('You need to be logged in to edit user.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to edit user.')
        return redirect(url_for('home'))

    user = User.query.get_or_404(user_id)
    if request.method == 'POST':
        user.username = request.form['username']
        user.email = request.form['email']
        user.active = 'active' in request.form
        user.role = request.form['role']
        db.session.commit()
        flash('User updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_user.html', user=user)

@app.route('/admin/campaigns/edit/<int:campaign_id>', methods=['GET', 'POST'])
def admin_edit_campaign(campaign_id):
    if 'user_id' not in session:
        flash('You need to be logged in to edit campaign.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to edit campaign.')
        return redirect(url_for('home'))

    campaign = Campaign.query.get_or_404(campaign_id)
    if request.method == 'POST':
        campaign.name = request.form['name']
        campaign.description = request.form['description']
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        campaign.budget = request.form['budget']
        campaign.visibility = request.form['visibility']
        db.session.commit()
        flash('Campaign updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_campaign.html', campaign=campaign)

@app.route('/admin/ad_requests/edit/<int:ad_request_id>', methods=['GET', 'POST'])
def admin_edit_ad_request(ad_request_id):
    if 'user_id' not in session:
        flash('You need to be logged in to edit ad request.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to edit ad request.')
        return redirect(url_for('home'))

    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if request.method == 'POST':
        ad_request.name = request.form['name']
        ad_request.messages = request.form['messages']
        ad_request.requirements = request.form['requirements']
        ad_request.payment_amount = request.form['payment_amount']
        ad_request.status = request.form['status']
        db.session.commit()
        flash('Ad request updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_ad_request.html', ad_request=ad_request)

@app.route('/admin/sponsors/edit/<int:sponsor_id>', methods=['GET', 'POST'])
def admin_edit_sponsor(sponsor_id):
    if 'user_id' not in session:
        flash('You need to be logged in to edit sponsor profile.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to edit sponsor profile.')
        return redirect(url_for('home'))

    sponsor = Sponsor.query.get_or_404(sponsor_id)
    if request.method == 'POST':
        sponsor.company_name = request.form['company_name']
        sponsor.industry = request.form['industry']
        sponsor.budget = request.form['budget']
        sponsor.flagged = 'flagged' in request.form
        db.session.commit()
        flash('Sponsor updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_sponsor.html', sponsor=sponsor)

@app.route('/admin/influencers/edit/<int:influencer_id>', methods=['GET', 'POST'])
def admin_edit_influencer(influencer_id):
    if 'user_id' not in session:
        flash('You need to be logged in to edit influencer profile.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'admin':
        flash('You do not have permission to edit influencer profile.')
        return redirect(url_for('home'))

    influencer = Influencer.query.get_or_404(influencer_id)
    if request.method == 'POST':
        influencer.name = request.form['name']
        influencer.category = request.form['category']
        influencer.niche = request.form['niche']
        influencer.reach = request.form['reach']
        influencer.platform = request.form['platform']
        influencer.flagged = 'flagged' in request.form
        db.session.commit()
        flash('Influencer updated successfully!')
        return redirect(url_for('admin_dashboard'))
    return render_template('edit_influencer.html', influencer=influencer)

# Delete Routes
@app.route('/admin/users/delete/<int:user_id>', methods=['POST'])
def admin_delete_user(user_id):
    user = User.query.get_or_404(user_id)
    db.session.delete(user)
    db.session.commit()
    flash('User deleted successfully!')
    return redirect(url_for('admin_view_users'))

@app.route('/admin/campaigns/delete/<int:campaign_id>', methods=['POST'])
def admin_delete_campaign(campaign_id):
    campaign = Campaign.query.get_or_404(campaign_id)
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign deleted successfully!')
    return redirect(url_for('admin_view_campaigns'))

@app.route('/admin/ad_requests/delete/<int:ad_request_id>', methods=['POST'])
def admin_delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!')
    return redirect(url_for('admin_view_ad_requests'))

@app.route('/admin/sponsors/delete/<int:sponsor_id>', methods=['POST'])
def admin_delete_sponsor(sponsor_id):
    sponsor = Sponsor.query.get_or_404(sponsor_id)
    db.session.delete(sponsor)
    db.session.commit()
    flash('Sponsor deleted successfully!')
    return redirect(url_for('admin_view_sponsors'))

@app.route('/admin/influencers/delete/<int:influencer_id>', methods=['POST'])
def admin_delete_influencer(influencer_id):
    influencer = Influencer.query.get_or_404(influencer_id)
    db.session.delete(influencer)
    db.session.commit()
    flash('Influencer deleted successfully!')
    return redirect(url_for('admin_view_influencers'))

@app.route('/influencer', methods=['GET'])
def influencer_dashboard():
    if 'user_id' not in session:
        flash('You need to be logged in to access the influencer dashboard.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'influencer':
        flash('You do not have permission to access the influencer dashboard.')
        return redirect(url_for('home'))

    influencer = Influencer.query.filter_by(user_id=user.id).first()
    if not influencer:
        flash('Please complete your influencer registration.')
        return redirect(url_for('signup_influencer'))
    
    ad_requests = AdRequest.query.filter_by(influencer_id=influencer.id).all()
    campaign_ids = {ad_request.campaign_id for ad_request in ad_requests}
    campaigns = Campaign.query.filter(Campaign.id.in_(campaign_ids)).all()

    return render_template('influencer_dashboard.html', user=user, influencer=influencer, ad_requests=ad_requests, campaigns=campaigns)

@app.route('/sponsor', methods=['GET'])
def sponsor_dashboard():
    if 'user_id' not in session:
        flash('You need to be logged in to access the sponsor dashboard.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You do not have permission to access the sponsor dashboard.')
        return redirect(url_for('home'))

    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    if not sponsor:
        flash('Please complete your sponsor registration.')
        return redirect(url_for('signup_sponsor'))
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    ad_requests = AdRequest.query.filter_by(sponsor_id=sponsor.id).all()
    return render_template('sponsor_dashboard.html', user=user, sponsor=sponsor,campaigns=campaigns, ad_requests=ad_requests)


@app.route('/create_campaign', methods=['GET', 'POST'])
def create_campaign():
    if 'user_id' not in session:
        flash('You need to be logged in to create a campaign.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You do not have permission to create a campaign.')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        budget = request.form['budget']
        visibility = request.form['visibility']
        goals = request.form['goals']
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        sponsor_id = sponsor.id


        new_campaign = Campaign(
            name=name,
            description=description,
            start_date=start_date,
            end_date=end_date,
            budget=budget,
            visibility=visibility,
            goals=goals,
            sponsor_id=sponsor_id
        )
        db.session.add(new_campaign)
        db.session.commit()
        flash('Campaign created successfully!')
        return redirect(url_for('sponsor_dashboard'))

    return render_template('create_campaign.html')


@app.route('/edit_campaign/<int:campaign_id>', methods=['GET', 'POST'])
def edit_campaign(campaign_id):
    if 'user_id' not in session:
        flash('You need to be logged in to edit a campaign.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You do not have permission to edit this campaign.')
        return redirect(url_for('home'))

    campaign = Campaign.query.get_or_404(campaign_id)

    if request.method == 'POST':
        campaign.name = request.form['name']
        campaign.description = request.form['description']
        campaign.start_date = datetime.strptime(request.form['start_date'], '%Y-%m-%d')
        campaign.end_date = datetime.strptime(request.form['end_date'], '%Y-%m-%d')
        campaign.budget = request.form['budget']
        campaign.visibility = request.form['visibility']
        campaign.goals = request.form['goals']

        db.session.commit()
        flash('Campaign updated successfully!')
        return redirect(url_for('sponsor_dashboard'))

    return render_template('update_campaign.html', campaign=campaign)

@app.route('/delete_campaign/<int:campaign_id>', methods=['POST'])
def delete_campaign(campaign_id):
    if 'user_id' not in session:
        flash('You need to be logged in to delete a campaign.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You do not have permission to delete this campaign.')
        return redirect(url_for('home'))

    campaign = Campaign.query.get_or_404(campaign_id)
    

    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id).all()
    for ad_request in ad_requests:
        db.session.delete(ad_request)
    
    db.session.delete(campaign)
    db.session.commit()
    flash('Campaign and associated ad requests deleted successfully!')
    return redirect(url_for('sponsor_dashboard'))

@app.route('/create_ad_request', methods=['GET', 'POST'])
def create_ad_request():
    if 'user_id' not in session:
        flash('You need to be logged in to create an ad request.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You do not have permission to create an ad request.')
        return redirect(url_for('home'))
    
    if request.method == 'POST':
        name = request.form['name']
        sponsor = Sponsor.query.filter_by(user_id=user.id).first()
        sponsor_id = sponsor.id
        campaign_id = request.form['campaign_id']
        messages = request.form['messages']
        requirements = request.form['requirements']
        payment_amount = request.form['payment_amount']
        status = "Available"
        
        new_ad_request = AdRequest(
            name = name,
            messages=messages,
            requirements=requirements,
            payment_amount=payment_amount,
            status=status,
            sponsor_id=sponsor_id,
            campaign_id=campaign_id
        )
        db.session.add(new_ad_request)
        db.session.commit()
        flash('Ad request created successfully!')
        return redirect(url_for('sponsor_dashboard'))
    
    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    influencers = Influencer.query.all()
    return render_template('create_ad_request.html', campaigns=campaigns, influencers=influencers)


@app.route('/edit_ad_request/<int:ad_request_id>', methods=['GET', 'POST'])
def edit_ad_request(ad_request_id):
    if 'user_id' not in session:
        flash('You need to be logged in to edit an ad request.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You do not have permission to edit this ad request.')
        return redirect(url_for('home'))
    
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    if request.method == 'POST':
        ad_request.influencer_id = request.form['influencer_id']
        ad_request.requirements = request.form['requirements']
        ad_request.payment_amount = request.form['payment_amount']
        ad_request.status = request.form['status']
        
        db.session.commit()
        flash('Ad request updated successfully!')
        return redirect(url_for('sponsor_dashboard'))
    
    campaigns = Campaign.query.all()
    influencers = User.query.filter_by(role='influencer').all()
    return render_template('update_ad_request.html', ad_request=ad_request, campaigns=campaigns, influencers=influencers)

@app.route('/delete_ad_request/<int:ad_request_id>', methods=['POST'])
def delete_ad_request(ad_request_id):
    ad_request = AdRequest.query.get_or_404(ad_request_id)
    db.session.delete(ad_request)
    db.session.commit()
    flash('Ad request deleted successfully!')
    return redirect(url_for('sponsor_dashboard'))

@app.route('/ad_request/<int:id>/action', methods=['GET', 'POST'])
def action_ad_request(id):
    if 'user_id' not in session:
        flash('You need to be logged in to take an action on an ad request.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'influencer':
        flash('You do not have permission to take an action on this ad request.')
        return redirect(url_for('home'))
    
    ad_request = AdRequest.query.get_or_404(id)
    if request.method == 'POST':
        action = request.form['action']
        if action == 'accept':
            ad_request.status = 'Accepted'
        if action == 'reject':
            ad_request.status = 'Rejected'
        elif action == 'negotiate':
            new_payment_amount = request.form['new_payment_amount']
            ad_request.payment_amount = new_payment_amount
            ad_request.status = 'Negotiations Underway from influencer'
        influencer = Influencer.query.filter_by(user_id=user.id).first()
        ad_request.influencer_id = influencer.id
        db.session.commit()
        flash('Action taken successfully!')
        return redirect(url_for('influencer_dashboard'))
    
    return render_template('action_ad_requests.html', ad_request=ad_request)

@app.route('/find_campaigns', methods=['GET', 'POST'])
def find_campaigns():
    if 'user_id' not in session:
        flash('You need to be logged in to find campaigns.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'influencer':
        flash('You do not have permission to find campaigns.')
        return redirect(url_for('home'))
    
    campaigns = []
    if request.method == 'POST':
        name = request.form.get('name')
        start_date = request.form.get('start_date')
        end_date = request.form.get('end_date')
        budget = request.form.get('budget')

        query = Campaign.query.filter_by(visibility='public')
        
        if name:
            query = query.filter(Campaign.name.ilike(f'%{name}%'))
        if start_date:
            query = query.filter(Campaign.start_date >= start_date)
        if end_date:
            query = query.filter(Campaign.end_date <= end_date)
        if budget:
            query = query.filter(Campaign.budget <= budget)

        campaigns = query.all()

    return render_template('find_campaigns.html', campaigns=campaigns)

@app.route('/campaign/<int:campaign_id>/ad_requests', methods=['GET'])
def find_ad_requests(campaign_id):
    if 'user_id' not in session:
        flash('You need to be logged in to view ad requests.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'influencer':
        flash('You do not have permission to view ad requests.')
        return redirect(url_for('home'))
    campaign = Campaign.query.get_or_404(campaign_id)
    ad_requests = AdRequest.query.filter_by(campaign_id=campaign_id, status='Available').all()
    return render_template('find_ad_requests.html', campaign=campaign, ad_requests=ad_requests)

@app.route('/find_influencers', methods=['GET', 'POST'])
def find_influencers():
    if 'user_id' not in session:
        flash('You need to be logged in to find influencers.')
        return redirect(url_for('login'))

    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You do not have permission to find influencers.')
        return redirect(url_for('home'))
    
    influencers = []
    if request.method == 'POST':
        name = request.form.get('name')
        category = request.form.get('category')
        niche = request.form.get('niche')
        reach = request.form.get('reach')
        followers = request.form.get('followers')

        query = Influencer.query
        if name:
            query = query.filter(Influencer.name.ilike(f'%{name}%'))
        if category:
            query = query.filter(Influencer.category.ilike(f'%{category}%'))
        if niche:
            query = query.filter(Influencer.niche.ilike(f'%{niche}%'))
        if reach:
            query = query.filter(Influencer.reach >= reach)

        influencers = query.all()

    return render_template('find_influencers.html', influencers=influencers)

@app.route('/influencer/profile/edit', methods=['GET', 'POST'])
def update_influencer_profile():
    if 'user_id' not in session:
        flash('You need to be logged in to update your profile.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'influencer':
        flash('You do not have permission to update influencer profile.')
        return redirect(url_for('home'))

    influencer = Influencer.query.filter_by(user_id=user.id).first()
    if request.method == 'POST':
        influencer.name = request.form['name']
        influencer.category = request.form['category']
        influencer.niche = request.form['niche']
        influencer.reach = request.form['reach']
        influencer.platform = request.form['platform']
        db.session.commit()
        flash('Profile updated successfully!')
        return redirect(url_for('influencer_dashboard'))
    return render_template('update_influencer_profile.html', influencer=influencer)

@app.route('/influencer/<int:influencer_id>', methods=['GET', 'POST'])
def action_influencer(influencer_id):
    if 'user_id' not in session:
        flash('You need to be logged in to employ an influencer.')
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id'])
    if not user or user.role != 'sponsor':
        flash('You do not have permission to employ an influencer.')
        return redirect(url_for('home'))
    
    influencer = Influencer.query.get_or_404(influencer_id)
    if request.method == ['POST']: 
        ad_request_id = request.form['ad_request_id']
        influencer_id = request.form['influencer_id']
        action = request.form['action']
        
        ad_request = AdRequest.query.get_or_404(ad_request_id)
        ad_request.influencer_id = influencer_id
        ad_request.status = action
        db.session.commit()
        flash('Ad request created successfully!')
        return redirect(url_for('sponsor_dashboard'))
    
    sponsor = Sponsor.query.filter_by(user_id=user.id).first()
    campaigns = Campaign.query.filter_by(sponsor_id=sponsor.id).all()
    adrequests=AdRequest.query.filter_by(sponsor_id=sponsor.id).all()
    return render_template('action_influencer.html', influencer=influencer, campaigns=campaigns, ad_requests=adrequests)


@app.route('/logout')
def logout():
    session.clear()
    flash('You have been logged out successfully.')
    return render_template('logout.html')