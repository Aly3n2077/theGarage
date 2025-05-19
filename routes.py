import os
from flask import render_template, url_for, flash, redirect, request, jsonify, abort
from flask_login import login_user, current_user, logout_user, login_required
from werkzeug.utils import secure_filename
from datetime import datetime, time, timedelta
from sqlalchemy import or_, and_, func

from app import app, db
from forms import (RegistrationForm, LoginForm, UpdateProfileForm, VehicleForm, 
                  BookingForm, VehicleSearchForm, WorkshopJobForm, JobNoteForm,
                  JobStatusUpdateForm, StartWorkForm, CompleteWorkForm, AddPartForm,
                  PartForm, JobSearchForm)
from models import (User, Vehicle, Booking, Service, VehicleMake, VehicleModel,
                   WorkshopJob, JobNote, Part, PartUsed)
from utils import format_currency, get_available_time_slots

# Home page
@app.route('/')
def home():
    # Get featured vehicles (most recent 6)
    featured_vehicles = Vehicle.query.filter_by(status='available').order_by(Vehicle.created_at.desc()).limit(6).all()
    
    # Get service categories
    services = Service.query.all()
    
    return render_template('home.html', 
                          featured_vehicles=featured_vehicles,
                          services=services,
                          Vehicle=Vehicle,
                          User=User, 
                          Service=Service)

# Auth routes
@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(
            username=form.username.data,
            email=form.email.data,
            first_name=form.first_name.data,
            last_name=form.last_name.data,
            phone=form.phone.data,
            country=form.country.data
        )
        user.set_password(form.password.data)
        
        db.session.add(user)
        db.session.commit()
        
        flash('Your account has been created! You can now log in.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html', title='Register', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
        
    form = LoginForm()
    if form.validate_on_submit():
        # Check if input is email or username
        input_value = form.username_or_email.data
        
        # Try to find user by email or username
        if '@' in input_value:
            user = User.query.filter_by(email=input_value).first()
        else:
            user = User.query.filter_by(username=input_value).first()
        
        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            
            # If user is workshop staff, redirect to workshop dashboard
            if user.is_workshop_staff() and not next_page:
                flash('Login successful! Welcome to the Workshop Dashboard.', 'success')
                return redirect(url_for('workshop_dashboard'))
            else:
                flash('Login successful!', 'success')
                return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Login unsuccessful. Please check your username/email and password.', 'danger')
            
    return render_template('login.html', title='Login', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('home'))

@app.route('/profile', methods=['GET', 'POST'])
@login_required
def profile():
    form = UpdateProfileForm(current_user.username, current_user.email)
    
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.email = form.email.data
        current_user.first_name = form.first_name.data
        current_user.last_name = form.last_name.data
        current_user.phone = form.phone.data
        current_user.country = form.country.data
        
        db.session.commit()
        flash('Your profile has been updated!', 'success')
        return redirect(url_for('profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
        form.first_name.data = current_user.first_name
        form.last_name.data = current_user.last_name
        form.phone.data = current_user.phone
        form.country.data = current_user.country
    
    # Get user's vehicles
    vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    
    # Get user's bookings
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    
    return render_template('profile.html', title='Profile', 
                          form=form, vehicles=vehicles, bookings=bookings)

# Vehicle routes
@app.route('/vehicles')
def vehicle_list():
    form = VehicleSearchForm()
    
    # Populate make dropdown
    form.make_id.choices = [(0, 'All Makes')] + [(make.id, make.name) for make in VehicleMake.query.order_by(VehicleMake.name).all()]
    
    # Get search parameters
    vehicle_type = request.args.get('vehicle_type', '')
    make_id = request.args.get('make_id', type=int)
    model_id = request.args.get('model_id', type=int)
    min_price = request.args.get('min_price', type=float)
    max_price = request.args.get('max_price', type=float)
    min_year = request.args.get('min_year', type=int)
    max_year = request.args.get('max_year', type=int)
    location = request.args.get('location', '')
    country = request.args.get('country', '')
    condition = request.args.get('condition', '')
    fuel_type = request.args.get('fuel_type', '')
    transmission = request.args.get('transmission', '')
    category = request.args.get('category', '')  # Parameter for vehicle categories
    
    # Base query
    query = Vehicle.query.filter_by(status='available')
    
    # Apply filters
    if vehicle_type:
        query = query.filter_by(vehicle_type=vehicle_type)
    if make_id and make_id > 0:
        query = query.filter_by(make_id=make_id)
    if model_id and model_id > 0:
        query = query.filter_by(model_id=model_id)
    if min_price:
        query = query.filter(Vehicle.price >= min_price)
    if max_price:
        query = query.filter(Vehicle.price <= max_price)
    if min_year:
        query = query.filter(Vehicle.year >= min_year)
    if max_year:
        query = query.filter(Vehicle.year <= max_year)
    if location:
        query = query.filter(Vehicle.location.ilike(f'%{location}%'))
    if country:
        query = query.filter_by(country=country)
    if condition:
        query = query.filter_by(condition=condition)
    if fuel_type:
        query = query.filter_by(fuel_type=fuel_type)
    if transmission:
        query = query.filter_by(transmission=transmission)
        
    # Filter by category (new feature)
    if category:
        if category == 'electric':
            query = query.filter(Vehicle.fuel_type == 'electric')
        elif category == 'hybrid':
            query = query.filter(Vehicle.fuel_type == 'hybrid')
        elif category == 'luxury':
            # For demo purposes, consider luxury cars as those priced above 50000
            query = query.filter(Vehicle.price > 50000)
        # Note: In a real application, you would have a vehicle_type field
        # This is a placeholder implementation for category filtering
    
    # Execute query
    vehicles = query.order_by(Vehicle.created_at.desc()).all()
    
    # Add datetime objects to template context for "New" badges
    from datetime import datetime, timedelta
    
    return render_template(
        'vehicles/list.html', 
        title='Vehicles', 
        vehicles=vehicles, 
        form=form,
        now=datetime.utcnow(),
        timedelta=timedelta
    )

@app.route('/vehicles/<int:vehicle_id>')
def vehicle_detail(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Get related vehicles (same make and model)
    related_vehicles = Vehicle.query.filter(
        Vehicle.id != vehicle_id,
        Vehicle.make_id == vehicle.make_id,
        Vehicle.status == 'available'
    ).limit(3).all()
    
    return render_template('vehicles/detail.html', title=f'{vehicle.vehicle_make.name} {vehicle.vehicle_model.name}',
                          vehicle=vehicle, related_vehicles=related_vehicles)

@app.route('/vehicles/create', methods=['GET', 'POST'])
@login_required
def create_vehicle():
    form = VehicleForm()
    
    # Populate make dropdown
    form.make_id.choices = [(make.id, make.name) for make in VehicleMake.query.order_by(VehicleMake.name).all()]
    
    # Populate model dropdown based on the selected make
    if form.make_id.data:
        form.model_id.choices = [(model.id, model.name) 
                                for model in VehicleModel.query.filter_by(make_id=form.make_id.data).all()]
    else:
        form.model_id.choices = [(0, 'Select Make First')]
    
    if form.validate_on_submit():
        image_urls = []
        if form.images.data:
            # TODO: Handle image uploads to cloud storage
            image_urls = ['https://via.placeholder.com/500']
        
        vehicle = Vehicle(
            user_id=current_user.id,
            vehicle_type=form.vehicle_type.data,
            make_id=form.make_id.data,
            model_id=form.model_id.data,
            year=form.year.data,
            price=form.price.data,
            mileage=form.mileage.data,
            color=form.color.data,
            fuel_type=form.fuel_type.data,
            transmission=form.transmission.data,
            condition=form.condition.data,
            description=form.description.data,
            location=form.location.data,
            country=form.country.data,
            image_urls=','.join(image_urls),
            status='available'
        )
        
        db.session.add(vehicle)
        db.session.commit()
        
        flash('Your vehicle has been listed!', 'success')
        return redirect(url_for('vehicle_detail', vehicle_id=vehicle.id))
    
    return render_template('vehicles/create.html', title='Add Vehicle', form=form)

@app.route('/vehicles/<int:vehicle_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_vehicle(vehicle_id):
    vehicle = Vehicle.query.get_or_404(vehicle_id)
    
    # Check if the current user is the owner
    if vehicle.user_id != current_user.id and not current_user.is_admin:
        abort(403)
    
    form = VehicleForm()
    
    # Populate make dropdown
    form.make_id.choices = [(make.id, make.name) for make in VehicleMake.query.order_by(VehicleMake.name).all()]
    
    # Populate model dropdown based on the selected make
    if form.make_id.data:
        form.model_id.choices = [(model.id, model.name) 
                                for model in VehicleModel.query.filter_by(make_id=form.make_id.data).all()]
    else:
        models = VehicleModel.query.filter_by(make_id=vehicle.make_id).all()
        form.model_id.choices = [(model.id, model.name) for model in models]
    
    if form.validate_on_submit():
        vehicle.vehicle_type = form.vehicle_type.data
        vehicle.make_id = form.make_id.data
        vehicle.model_id = form.model_id.data
        vehicle.year = form.year.data
        vehicle.price = form.price.data
        vehicle.mileage = form.mileage.data
        vehicle.color = form.color.data
        vehicle.fuel_type = form.fuel_type.data
        vehicle.transmission = form.transmission.data
        vehicle.condition = form.condition.data
        vehicle.description = form.description.data
        vehicle.location = form.location.data
        vehicle.country = form.country.data
        
        if form.images.data:
            # TODO: Handle image uploads to cloud storage
            new_image = 'https://via.placeholder.com/500'
            if vehicle.image_urls:
                vehicle.image_urls += f',{new_image}'
            else:
                vehicle.image_urls = new_image
        
        db.session.commit()
        flash('Your vehicle listing has been updated!', 'success')
        return redirect(url_for('vehicle_detail', vehicle_id=vehicle.id))
    
    elif request.method == 'GET':
        form.vehicle_type.data = vehicle.vehicle_type
        form.make_id.data = vehicle.make_id
        form.model_id.data = vehicle.model_id
        form.year.data = vehicle.year
        form.price.data = vehicle.price
        form.mileage.data = vehicle.mileage
        form.color.data = vehicle.color
        form.fuel_type.data = vehicle.fuel_type
        form.transmission.data = vehicle.transmission
        form.condition.data = vehicle.condition
        form.description.data = vehicle.description
        form.location.data = vehicle.location
        form.country.data = vehicle.country
    
    return render_template('vehicles/edit.html', title='Edit Vehicle', form=form, vehicle=vehicle)

# Booking routes
@app.route('/bookings/calendar')
def booking_calendar():
    services = Service.query.all()
    return render_template('bookings/calendar.html', title='Service Booking Calendar', services=services)

@app.route('/bookings/create', methods=['GET', 'POST'])
@login_required
def create_booking():
    form = BookingForm()
    
    # Populate service dropdown
    form.service_id.choices = [(service.id, service.name) for service in Service.query.all()]
    
    # Populate vehicle dropdown with user's vehicles
    user_vehicles = Vehicle.query.filter_by(user_id=current_user.id).all()
    form.vehicle_id.choices = [(0, 'No Vehicle / Other Vehicle')] + [(v.id, f'{v.vehicle_make.name} {v.vehicle_model.name} ({v.year})') for v in user_vehicles]
    
    # Generate time slots
    # For demo purposes, just showing fixed time slots
    form.booking_time.choices = [
        ('08:00', '8:00 AM'), ('09:00', '9:00 AM'), ('10:00', '10:00 AM'),
        ('11:00', '11:00 AM'), ('12:00', '12:00 PM'), ('13:00', '1:00 PM'),
        ('14:00', '2:00 PM'), ('15:00', '3:00 PM'), ('16:00', '4:00 PM')
    ]
    
    if form.validate_on_submit():
        # Convert string time to time object
        hour, minute = map(int, form.booking_time.data.split(':'))
        booking_time_obj = time(hour=hour, minute=minute)
        
        # Create booking
        booking = Booking(
            user_id=current_user.id,
            service_id=form.service_id.data,
            booking_date=form.booking_date.data,
            booking_time=booking_time_obj,
            notes=form.notes.data,
            status='pending'
        )
        
        # Link to vehicle if selected
        if form.vehicle_id.data and form.vehicle_id.data > 0:
            booking.vehicle_id = form.vehicle_id.data
        
        db.session.add(booking)
        db.session.commit()
        
        flash('Your service booking has been created! We will confirm shortly.', 'success')
        return redirect(url_for('booking_list'))
    
    # If service_id is provided in URL params, pre-select it
    service_id = request.args.get('service_id', type=int)
    if service_id:
        form.service_id.data = service_id
    
    return render_template('bookings/create.html', title='Book a Service', form=form)

@app.route('/bookings')
@login_required
def booking_list():
    bookings = Booking.query.filter_by(user_id=current_user.id).order_by(Booking.booking_date.desc()).all()
    return render_template('bookings/list.html', title='My Bookings', bookings=bookings)

# API endpoints for AJAX calls
@app.route('/get_makes')
def get_makes():
    makes = VehicleMake.query.order_by(VehicleMake.name).all()
    return jsonify([{'id': make.id, 'name': make.name} for make in makes])

@app.route('/api/models/<int:make_id>')
def get_models(make_id):
    models = VehicleModel.query.filter_by(make_id=make_id).all()
    return jsonify([{'id': model.id, 'name': model.name} for model in models])

@app.route('/api/timeslots/<date>')
def get_time_slots(date):
    try:
        booking_date = datetime.strptime(date, '%Y-%m-%d').date()
        
        # Get already booked time slots for the selected date
        booked_slots = db.session.query(Booking.booking_time).filter(
            Booking.booking_date == booking_date,
            Booking.status.in_(['pending', 'confirmed'])
        ).all()
        
        booked_time_strings = [slot[0].strftime('%H:%M') for slot in booked_slots]
        
        # Get available slots
        available_slots = get_available_time_slots(booking_date, booked_time_strings)
        
        return jsonify({
            'available': [{'value': slot, 'label': f"{int(slot.split(':')[0]):d}:{slot.split(':')[1]} {'AM' if int(slot.split(':')[0]) < 12 else 'PM'}"} 
                        for slot in available_slots]
        })
    except ValueError:
        return jsonify({'error': 'Invalid date format'}), 400

# Admin routes
@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    if not current_user.is_admin:
        abort(403)
        
    total_users = User.query.count()
    total_vehicles = Vehicle.query.count()
    total_bookings = Booking.query.count()
    
    recent_vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).limit(5).all()
    recent_bookings = Booking.query.order_by(Booking.created_at.desc()).limit(5).all()
    
    return render_template('admin/dashboard.html', title='Admin Dashboard',
                          total_users=total_users, total_vehicles=total_vehicles,
                          total_bookings=total_bookings, recent_vehicles=recent_vehicles,
                          recent_bookings=recent_bookings)

@app.route('/admin/vehicles')
@login_required
def admin_vehicles():
    if not current_user.is_admin:
        abort(403)
        
    vehicles = Vehicle.query.order_by(Vehicle.created_at.desc()).all()
    return render_template('admin/vehicles.html', title='Manage Vehicles', vehicles=vehicles)

@app.route('/admin/bookings')
@login_required
def admin_bookings():
    if not current_user.is_admin:
        abort(403)
        
    bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', title='Manage Bookings', bookings=bookings)

@app.route('/admin/users')
@login_required
def admin_users():
    if not current_user.is_admin:
        abort(403)
        
    users = User.query.order_by(User.created_at.desc()).all()
    return render_template('admin/users.html', title='Manage Users', users=users)

@app.route('/admin/bookings/<int:booking_id>/status', methods=['POST'])
@login_required
def update_booking_status(booking_id):
    if not current_user.is_admin:
        abort(403)
        
    booking = Booking.query.get_or_404(booking_id)
    status = request.form.get('status')
    
    if status in ['pending', 'confirmed', 'completed', 'cancelled']:
        booking.status = status
        db.session.commit()
        flash(f'Booking status updated to {status}', 'success')
    else:
        flash('Invalid status', 'danger')
        
    return redirect(url_for('admin_bookings'))

# Workshop Dashboard Routes
@app.route('/workshop')
@login_required
def workshop_dashboard():
    if not current_user.is_workshop_staff():
        abort(403)
    
    # Get pending and in-progress jobs
    pending_jobs = WorkshopJob.query.filter_by(status='pending').order_by(WorkshopJob.priority.desc()).all()
    in_progress_jobs = WorkshopJob.query.filter_by(status='in_progress').all()
    
    # Get jobs assigned to current mechanic (if applicable)
    my_jobs = []
    if current_user.role == 'mechanic':
        my_jobs = WorkshopJob.query.filter_by(mechanic_id=current_user.id).filter(
            WorkshopJob.status.in_(['pending', 'in_progress', 'paused'])
        ).all()
    
    # Count statistics
    stats = {
        'total_jobs': WorkshopJob.query.count(),
        'pending_jobs': WorkshopJob.query.filter_by(status='pending').count(),
        'in_progress_jobs': WorkshopJob.query.filter_by(status='in_progress').count(),
        'completed_jobs': WorkshopJob.query.filter_by(status='completed').count(),
        'jobs_today': WorkshopJob.query.filter(
            func.date(WorkshopJob.created_at) == datetime.utcnow().date()
        ).count()
    }
    
    return render_template('workshop/dashboard.html', 
                          title='Workshop Dashboard',
                          pending_jobs=pending_jobs,
                          in_progress_jobs=in_progress_jobs,
                          my_jobs=my_jobs,
                          stats=stats)


@app.route('/workshop/jobs')
@login_required
def workshop_jobs():
    if not current_user.is_workshop_staff():
        abort(403)
    
    form = JobSearchForm()
    
    # Populate mechanic dropdown
    mechanics = User.query.filter(User.role == 'mechanic').all()
    form.mechanic_id.choices = [(0, 'All Mechanics')] + [(m.id, m.full_name()) for m in mechanics]
    
    # Get search parameters
    status = request.args.get('status', '')
    mechanic_id = request.args.get('mechanic_id', type=int)
    priority = request.args.get('priority', type=int, default=0)
    date_from = request.args.get('date_from')
    date_to = request.args.get('date_to')
    
    # Base query
    query = WorkshopJob.query
    
    # Apply filters
    if status:
        query = query.filter_by(status=status)
    if mechanic_id and mechanic_id > 0:
        query = query.filter_by(mechanic_id=mechanic_id)
    if priority and priority > 0:
        query = query.filter_by(priority=priority)
    if date_from:
        try:
            from_date = datetime.strptime(date_from, '%Y-%m-%d').date()
            query = query.filter(func.date(WorkshopJob.created_at) >= from_date)
        except ValueError:
            pass
    if date_to:
        try:
            to_date = datetime.strptime(date_to, '%Y-%m-%d').date()
            query = query.filter(func.date(WorkshopJob.created_at) <= to_date)
        except ValueError:
            pass
    
    # Execute query
    jobs = query.order_by(WorkshopJob.created_at.desc()).all()
    
    return render_template('workshop/jobs.html', 
                          title='Workshop Jobs',
                          jobs=jobs,
                          form=form)


@app.route('/workshop/jobs/<int:job_id>')
@login_required
def job_detail(job_id):
    if not current_user.is_workshop_staff():
        abort(403)
    
    job = WorkshopJob.query.get_or_404(job_id)
    note_form = JobNoteForm()
    status_form = JobStatusUpdateForm()
    status_form.status.data = job.status
    
    # Forms based on job status
    start_work_form = None
    complete_work_form = None
    
    if job.status == 'pending':
        start_work_form = StartWorkForm()
    elif job.status == 'in_progress':
        complete_work_form = CompleteWorkForm()
    
    # Get parts used
    parts_used = PartUsed.query.filter_by(job_id=job.id).all()
    
    # Calculate total parts cost
    total_parts_cost = sum(part.unit_price * part.quantity for part in parts_used)
    
    # If there are actual hours, calculate labor cost (assumed $50/hour)
    labor_cost = job.actual_hours * 50 if job.actual_hours else 0
    
    return render_template('workshop/job_detail.html',
                          title=f'Job #{job.id}',
                          job=job,
                          note_form=note_form,
                          status_form=status_form,
                          start_work_form=start_work_form,
                          complete_work_form=complete_work_form,
                          parts_used=parts_used,
                          total_parts_cost=total_parts_cost,
                          labor_cost=labor_cost)


@app.route('/workshop/bookings')
@login_required
def workshop_bookings():
    if not current_user.is_workshop_staff():
        abort(403)
    
    # Get bookings without job cards
    bookings_without_jobs = db.session.query(Booking).outerjoin(
        WorkshopJob, Booking.id == WorkshopJob.booking_id
    ).filter(
        WorkshopJob.id == None,
        Booking.status == 'confirmed'
    ).order_by(Booking.booking_date.desc()).all()
    
    # Get all confirmed bookings
    all_bookings = Booking.query.filter(
        Booking.status.in_(['confirmed', 'completed'])
    ).order_by(Booking.booking_date.desc()).all()
    
    return render_template('workshop/bookings.html',
                          title='Workshop Bookings',
                          bookings_without_jobs=bookings_without_jobs,
                          all_bookings=all_bookings)


@app.route('/workshop/jobs/create/<int:booking_id>', methods=['GET', 'POST'])
@login_required
def create_job(booking_id):
    if not current_user.is_workshop_staff():
        abort(403)
    
    booking = Booking.query.get_or_404(booking_id)
    form = WorkshopJobForm()
    
    # Populate mechanic dropdown
    mechanics = User.query.filter(User.role == 'mechanic').all()
    form.mechanic_id.choices = [(0, 'Unassigned')] + [(m.id, m.full_name()) for m in mechanics]
    
    if form.validate_on_submit():
        # Create new job
        job = WorkshopJob(
            booking_id=booking.id,
            estimated_hours=form.estimated_hours.data,
            priority=form.priority.data,
            status=form.status.data
        )
        
        # Assign mechanic if provided
        if form.mechanic_id.data > 0:
            job.mechanic_id = form.mechanic_id.data
        
        db.session.add(job)
        
        # Add initial note if provided
        if form.notes.data:
            job_note = JobNote(
                job_id=job.id,
                user_id=current_user.id,
                note=form.notes.data
            )
            db.session.add(job_note)
        
        db.session.commit()
        flash('Workshop job created successfully', 'success')
        return redirect(url_for('job_detail', job_id=job.id))
    
    # Pre-fill form with service duration
    form.estimated_hours.data = booking.service_type.duration_hours if booking.service_type.duration_hours else 1.0
    
    return render_template('workshop/create_job.html',
                          title='Create Workshop Job',
                          form=form,
                          booking=booking)


@app.route('/workshop/jobs/<int:job_id>/add-note', methods=['POST'])
@login_required
def add_job_note(job_id):
    if not current_user.is_workshop_staff():
        abort(403)
    
    job = WorkshopJob.query.get_or_404(job_id)
    form = JobNoteForm()
    
    if form.validate_on_submit():
        note = JobNote(
            job_id=job.id,
            user_id=current_user.id,
            note=form.note.data
        )
        
        db.session.add(note)
        db.session.commit()
        
        flash('Note added successfully', 'success')
    
    return redirect(url_for('job_detail', job_id=job.id))


@app.route('/workshop/jobs/<int:job_id>/update-status', methods=['POST'])
@login_required
def update_job_status(job_id):
    if not current_user.is_workshop_staff():
        abort(403)
    
    job = WorkshopJob.query.get_or_404(job_id)
    form = JobStatusUpdateForm()
    
    if form.validate_on_submit():
        old_status = job.status
        job.status = form.status.data
        
        # Add a note about the status change
        note_text = form.note.data if form.note.data else f"Status changed from {old_status} to {job.status}"
        note = JobNote(
            job_id=job.id,
            user_id=current_user.id,
            note=note_text
        )
        
        db.session.add(note)
        db.session.commit()
        
        flash(f'Job status updated to {job.status}', 'success')
    
    return redirect(url_for('job_detail', job_id=job.id))


@app.route('/workshop/jobs/<int:job_id>/start-work', methods=['POST'])
@login_required
def start_job_work(job_id):
    if not current_user.is_workshop_staff():
        abort(403)
    
    job = WorkshopJob.query.get_or_404(job_id)
    
    if job.status != 'pending':
        flash('Job cannot be started because it is not in pending status', 'danger')
        return redirect(url_for('job_detail', job_id=job.id))
    
    # If not assigned to anyone, assign to current user if they're a mechanic
    if not job.mechanic_id and current_user.role == 'mechanic':
        job.mechanic_id = current_user.id
    
    job.status = 'in_progress'
    job.start_time = datetime.utcnow()
    
    # Add a note
    note = JobNote(
        job_id=job.id,
        user_id=current_user.id,
        note=f"Work started by {current_user.full_name()}"
    )
    
    db.session.add(note)
    db.session.commit()
    
    flash('Job has been started', 'success')
    return redirect(url_for('job_detail', job_id=job.id))


@app.route('/workshop/jobs/<int:job_id>/complete-work', methods=['POST'])
@login_required
def complete_job_work(job_id):
    if not current_user.is_workshop_staff():
        abort(403)
    
    job = WorkshopJob.query.get_or_404(job_id)
    form = CompleteWorkForm()
    
    if form.validate_on_submit():
        if job.status != 'in_progress':
            flash('Job cannot be completed because it is not in progress', 'danger')
            return redirect(url_for('job_detail', job_id=job.id))
        
        job.status = 'completed'
        job.end_time = datetime.utcnow()
        job.actual_hours = form.actual_hours.data
        
        # Add a note
        note_text = form.note.data if form.note.data else "Work completed"
        note = JobNote(
            job_id=job.id,
            user_id=current_user.id,
            note=note_text
        )
        
        # Also update booking status
        job.booking.status = 'completed'
        
        db.session.add(note)
        db.session.commit()
        
        flash('Job has been completed', 'success')
    
    return redirect(url_for('job_detail', job_id=job.id))


@app.route('/workshop/parts')
@login_required
def parts_inventory():
    if not current_user.is_workshop_staff():
        abort(403)
    
    parts = Part.query.order_by(Part.name).all()
    
    return render_template('workshop/parts.html',
                          title='Parts Inventory',
                          parts=parts)


@app.route('/workshop/parts/create', methods=['GET', 'POST'])
@login_required
def create_part():
    if not current_user.is_workshop_staff():
        abort(403)
    
    form = PartForm()
    
    if form.validate_on_submit():
        part = Part(
            name=form.name.data,
            part_number=form.part_number.data,
            description=form.description.data,
            cost_price=form.cost_price.data,
            retail_price=form.retail_price.data,
            quantity_in_stock=form.quantity_in_stock.data,
            category=form.category.data
        )
        
        db.session.add(part)
        db.session.commit()
        
        flash('Part added to inventory', 'success')
        return redirect(url_for('parts_inventory'))
    
    return render_template('workshop/create_part.html',
                          title='Add New Part',
                          form=form)


@app.route('/workshop/parts/<int:part_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_part(part_id):
    if not current_user.is_workshop_staff():
        abort(403)
    
    part = Part.query.get_or_404(part_id)
    form = PartForm()
    
    if form.validate_on_submit():
        part.name = form.name.data
        part.part_number = form.part_number.data
        part.description = form.description.data
        part.cost_price = form.cost_price.data
        part.retail_price = form.retail_price.data
        part.quantity_in_stock = form.quantity_in_stock.data
        part.category = form.category.data
        
        db.session.commit()
        
        flash('Part updated successfully', 'success')
        return redirect(url_for('parts_inventory'))
    
    elif request.method == 'GET':
        form.name.data = part.name
        form.part_number.data = part.part_number
        form.description.data = part.description
        form.cost_price.data = part.cost_price
        form.retail_price.data = part.retail_price
        form.quantity_in_stock.data = part.quantity_in_stock
        form.category.data = part.category
    
    return render_template('workshop/edit_part.html',
                          title='Edit Part',
                          form=form,
                          part=part)


@app.route('/workshop/jobs/<int:job_id>/add-part', methods=['GET', 'POST'])
@login_required
def add_part_to_job(job_id):
    if not current_user.is_workshop_staff():
        abort(403)
    
    job = WorkshopJob.query.get_or_404(job_id)
    form = AddPartForm()
    
    # Populate parts dropdown
    form.part_id.choices = [(p.id, f"{p.name} ({p.part_number}) - {p.quantity_in_stock} in stock") 
                           for p in Part.query.filter(Part.quantity_in_stock > 0).order_by(Part.name).all()]
    
    if form.validate_on_submit():
        part = Part.query.get(form.part_id.data)
        
        if not part:
            flash('Part not found', 'danger')
            return redirect(url_for('job_detail', job_id=job.id))
        
        # Check if quantity is available
        if part.quantity_in_stock < form.quantity.data:
            flash(f'Not enough parts in stock. Only {part.quantity_in_stock} available.', 'danger')
            return redirect(url_for('job_detail', job_id=job.id))
        
        # Add part to job
        part_used = PartUsed(
            job_id=job.id,
            part_id=part.id,
            quantity=form.quantity.data,
            unit_price=part.retail_price
        )
        
        # Reduce inventory
        part.quantity_in_stock -= form.quantity.data
        
        db.session.add(part_used)
        
        # Add a note
        note = JobNote(
            job_id=job.id,
            user_id=current_user.id,
            note=f"Added {form.quantity.data} x {part.name} (Part #{part.part_number}) to job"
        )
        
        db.session.add(note)
        db.session.commit()
        
        flash('Part added to job', 'success')
        return redirect(url_for('job_detail', job_id=job.id))
    
    return render_template('workshop/add_part.html',
                          title='Add Part to Job',
                          form=form,
                          job=job)


@app.route('/workshop/technicians')
@login_required
def workshop_technicians():
    if not current_user.is_workshop_staff() and not current_user.is_admin:
        abort(403)
    
    mechanics = User.query.filter(User.role == 'mechanic').all()
    managers = User.query.filter(User.role.in_(['service_manager', 'parts_manager'])).all()
    
    return render_template('workshop/technicians.html',
                          title='Workshop Staff',
                          mechanics=mechanics,
                          managers=managers)


# Error handlers
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

@app.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

@app.errorhandler(500)
def server_error(e):
    return render_template('500.html'), 500

# Template filters
@app.template_filter('currency')
def currency_filter(value):
    return format_currency(value)


@app.template_filter('job_status_class')
def job_status_class(status):
    status_classes = {
        'pending': 'bg-warning',
        'in_progress': 'bg-primary',
        'paused': 'bg-secondary',
        'completed': 'bg-success',
        'cancelled': 'bg-danger'
    }
    return status_classes.get(status, 'bg-secondary')


@app.template_filter('priority_badge')
def priority_badge(priority):
    priority_classes = {
        1: 'bg-secondary',
        2: 'bg-info',
        3: 'bg-warning',
        4: 'bg-danger'
    }
    priority_labels = {
        1: 'Low',
        2: 'Normal',
        3: 'High',
        4: 'Urgent'
    }
    return f'<span class="badge {priority_classes.get(priority, "bg-secondary")}">{priority_labels.get(priority, "Unknown")}</span>'
