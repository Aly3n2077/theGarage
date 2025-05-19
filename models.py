from datetime import datetime
from app import db, login_manager
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(256), nullable=False)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))
    phone = db.Column(db.String(20))
    country = db.Column(db.String(20))  # 'SA' or 'ZIM'
    is_admin = db.Column(db.Boolean, default=False)
    role = db.Column(db.String(20), default='customer')  # customer, mechanic, service_manager, parts_manager
    specialization = db.Column(db.String(50))  # For mechanics: electrical, engine, transmission, general, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # Relationships
    vehicles = db.relationship('Vehicle', backref='owner', lazy=True)
    bookings = db.relationship('Booking', backref='customer', lazy=True)
    assigned_jobs = db.relationship('WorkshopJob', foreign_keys='WorkshopJob.mechanic_id', backref='mechanic', lazy=True)
    job_notes = db.relationship('JobNote', backref='author', lazy=True)
    
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)
    
    def is_workshop_staff(self):
        return self.role in ['mechanic', 'service_manager', 'parts_manager'] or self.is_admin
    
    def full_name(self):
        if self.first_name and self.last_name:
            return f"{self.first_name} {self.last_name}"
        return self.username
    
    def __repr__(self):
        return f'<User {self.username}>'


class VehicleMake(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    models = db.relationship('VehicleModel', backref='make', lazy=True)
    
    def __repr__(self):
        return f'<VehicleMake {self.name}>'


class VehicleModel(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    make_id = db.Column(db.Integer, db.ForeignKey('vehicle_make.id'), nullable=False)
    
    def __repr__(self):
        return f'<VehicleModel {self.name}>'


class Vehicle(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    make_id = db.Column(db.Integer, db.ForeignKey('vehicle_make.id'), nullable=False)
    model_id = db.Column(db.Integer, db.ForeignKey('vehicle_model.id'), nullable=False)
    vehicle_type = db.Column(db.String(20), default='car')  # car, motorbike
    year = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    mileage = db.Column(db.Integer)
    color = db.Column(db.String(30))
    fuel_type = db.Column(db.String(20))  # petrol, diesel, electric, hybrid
    transmission = db.Column(db.String(20))  # manual, automatic
    condition = db.Column(db.String(20))  # new, used, certified pre-owned
    description = db.Column(db.Text)
    location = db.Column(db.String(100))
    country = db.Column(db.String(20))  # 'SA' or 'ZIM'
    image_urls = db.Column(db.Text)  # Comma-separated list of image URLs
    status = db.Column(db.String(20), default='available')  # available, sold, reserved
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    vehicle_make = db.relationship('VehicleMake', backref='vehicles')
    vehicle_model = db.relationship('VehicleModel', backref='vehicles')
    bookings = db.relationship('Booking', backref='vehicle', lazy=True)
    
    def __repr__(self):
        return f'<Vehicle {self.id}: {self.vehicle_make.name} {self.vehicle_model.name}>'


class Service(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text)
    price_estimate = db.Column(db.Float)  # Base price estimate
    duration_hours = db.Column(db.Float)  # Estimated duration in hours
    category = db.Column(db.String(50))  # mechanical, panel beating, painting, etc.
    
    # Relationships
    bookings = db.relationship('Booking', backref='service_type', lazy=True)
    
    def __repr__(self):
        return f'<Service {self.name}>'


class Booking(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    vehicle_id = db.Column(db.Integer, db.ForeignKey('vehicle.id'), nullable=True)  # Can be null if customer brings their own vehicle
    service_id = db.Column(db.Integer, db.ForeignKey('service.id'), nullable=False)
    booking_date = db.Column(db.Date, nullable=False)
    booking_time = db.Column(db.Time, nullable=False)
    notes = db.Column(db.Text)
    status = db.Column(db.String(20), default='pending')  # pending, confirmed, completed, cancelled
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships for Workshop Dashboard
    workshop_jobs = db.relationship('WorkshopJob', backref='booking', lazy=True)
    
    def __repr__(self):
        return f'<Booking {self.id} for {self.service_type.name}>'


class WorkshopJob(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('booking.id'), nullable=False)
    mechanic_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # Can be null if not assigned yet
    estimated_hours = db.Column(db.Float, default=1.0)  # Estimated time to complete in hours
    actual_hours = db.Column(db.Float)  # Actual time spent in hours
    start_time = db.Column(db.DateTime)  # When work actually started
    end_time = db.Column(db.DateTime)  # When work was completed
    status = db.Column(db.String(20), default='pending')  # pending, in_progress, paused, completed, cancelled
    priority = db.Column(db.Integer, default=2)  # 1=low, 2=normal, 3=high, 4=urgent
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    job_notes = db.relationship('JobNote', backref='workshop_job', lazy=True, cascade="all, delete-orphan")
    parts_used = db.relationship('PartUsed', backref='workshop_job', lazy=True, cascade="all, delete-orphan")
    
    def __repr__(self):
        return f'<WorkshopJob {self.id} for Booking {self.booking_id}>'
    
    
class JobNote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('workshop_job.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)  # Who added the note
    note = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<JobNote {self.id} for Job {self.job_id}>'


class Part(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    part_number = db.Column(db.String(50), unique=True, nullable=False)
    description = db.Column(db.Text)
    cost_price = db.Column(db.Float, nullable=False)  # Cost to the garage
    retail_price = db.Column(db.Float, nullable=False)  # Price charged to customer
    quantity_in_stock = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))  # e.g., brakes, engine, electrical, etc.
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationship
    used_in_jobs = db.relationship('PartUsed', backref='part', lazy=True)
    
    def __repr__(self):
        return f'<Part {self.name} ({self.part_number})>'


class PartUsed(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    job_id = db.Column(db.Integer, db.ForeignKey('workshop_job.id'), nullable=False)
    part_id = db.Column(db.Integer, db.ForeignKey('part.id'), nullable=False)
    quantity = db.Column(db.Integer, default=1, nullable=False)
    unit_price = db.Column(db.Float, nullable=False)  # Price at time of use (may differ from current part price)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __repr__(self):
        return f'<PartUsed: {self.quantity} x Part {self.part_id} for Job {self.job_id}>'
