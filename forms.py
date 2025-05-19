from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, PasswordField, SubmitField, BooleanField, TextAreaField, SelectField
from wtforms import IntegerField, FloatField, DateField, TimeField, HiddenField
from wtforms.validators import DataRequired, Length, Email, EqualTo, ValidationError, Optional, NumberRange
from models import User, VehicleMake, VehicleModel
from datetime import date

class RegistrationForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])
    confirm_password = PasswordField('Confirm Password', validators=[DataRequired(), EqualTo('password')])
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    country = SelectField('Country', choices=[('SA', 'South Africa'), ('ZIM', 'Zimbabwe')])
    submit = SubmitField('Sign Up')
    
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user:
            raise ValidationError('That username is taken. Please choose a different one.')
            
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()
        if user:
            raise ValidationError('That email is taken. Please choose a different one.')
            

class LoginForm(FlaskForm):
    username_or_email = StringField('Username or Email', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
    remember = BooleanField('Remember Me')
    submit = SubmitField('Login')


class UpdateProfileForm(FlaskForm):
    username = StringField('Username', validators=[DataRequired(), Length(min=3, max=20)])
    email = StringField('Email', validators=[DataRequired(), Email()])
    first_name = StringField('First Name', validators=[Optional(), Length(max=50)])
    last_name = StringField('Last Name', validators=[Optional(), Length(max=50)])
    phone = StringField('Phone Number', validators=[Optional(), Length(max=20)])
    country = SelectField('Country', choices=[('SA', 'South Africa'), ('ZIM', 'Zimbabwe')])
    submit = SubmitField('Update')
    
    def __init__(self, original_username, original_email, *args, **kwargs):
        super(UpdateProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username
        self.original_email = original_email
        
    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=username.data).first()
            if user:
                raise ValidationError('That username is taken. Please choose a different one.')
                
    def validate_email(self, email):
        if email.data != self.original_email:
            user = User.query.filter_by(email=email.data).first()
            if user:
                raise ValidationError('That email is taken. Please choose a different one.')


class VehicleForm(FlaskForm):
    vehicle_type = SelectField('Vehicle Type', choices=[
        ('car', 'Car'),
        ('motorbike', 'Motorcycle')
    ], validators=[DataRequired()])
    make_id = SelectField('Make', coerce=int, validators=[DataRequired()])
    model_id = SelectField('Model', coerce=int, validators=[DataRequired()])
    year = IntegerField('Year', validators=[DataRequired(), NumberRange(min=1900, max=date.today().year + 1)])
    price = FloatField('Price', validators=[DataRequired(), NumberRange(min=0)])
    mileage = IntegerField('Mileage (km)', validators=[Optional(), NumberRange(min=0)])
    color = StringField('Color', validators=[Optional(), Length(max=30)])
    fuel_type = SelectField('Fuel Type', choices=[
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ], validators=[DataRequired()])
    transmission = SelectField('Transmission', choices=[
        ('manual', 'Manual'),
        ('automatic', 'Automatic')
    ], validators=[DataRequired()])
    condition = SelectField('Condition', choices=[
        ('new', 'New'),
        ('used', 'Used'),
        ('certified', 'Certified Pre-Owned')
    ], validators=[DataRequired()])
    description = TextAreaField('Description', validators=[Optional()])
    location = StringField('Location', validators=[DataRequired(), Length(max=100)])
    country = SelectField('Country', choices=[('SA', 'South Africa'), ('ZIM', 'Zimbabwe')])
    images = FileField('Add Photos', validators=[Optional(), FileAllowed(['jpg', 'jpeg', 'png'])])
    submit = SubmitField('Submit')


class BookingForm(FlaskForm):
    service_id = SelectField('Service Type', coerce=int, validators=[DataRequired()])
    booking_date = DateField('Date', validators=[DataRequired()])
    booking_time = SelectField('Time', choices=[], validators=[DataRequired()])
    vehicle_id = SelectField('Vehicle', coerce=int, validators=[Optional()])
    notes = TextAreaField('Notes', validators=[Optional()])
    submit = SubmitField('Book Appointment')
    
    def validate_booking_date(self, booking_date):
        if booking_date.data < date.today():
            raise ValidationError('Booking date cannot be in the past.')


class VehicleSearchForm(FlaskForm):
    vehicle_type = SelectField('Vehicle Type', choices=[
        ('', 'All Types'),
        ('car', 'Cars Only'),
        ('motorbike', 'Motorcycles Only')
    ], validators=[Optional()])
    make_id = SelectField('Make', coerce=int, choices=[], validators=[Optional()])
    model_id = SelectField('Model', coerce=int, choices=[], validators=[Optional()])
    min_price = FloatField('Min Price', validators=[Optional(), NumberRange(min=0)])
    max_price = FloatField('Max Price', validators=[Optional(), NumberRange(min=0)])
    min_year = IntegerField('Min Year', validators=[Optional(), NumberRange(min=1900)])
    max_year = IntegerField('Max Year', validators=[Optional(), NumberRange(max=date.today().year + 1)])
    location = StringField('Location', validators=[Optional()])
    country = SelectField('Country', choices=[('', 'All'), ('SA', 'South Africa'), ('ZIM', 'Zimbabwe')], validators=[Optional()])
    condition = SelectField('Condition', choices=[
        ('', 'All'),
        ('new', 'New'),
        ('used', 'Used'),
        ('certified', 'Certified Pre-Owned')
    ], validators=[Optional()])
    fuel_type = SelectField('Fuel Type', choices=[
        ('', 'All'),
        ('petrol', 'Petrol'),
        ('diesel', 'Diesel'),
        ('electric', 'Electric'),
        ('hybrid', 'Hybrid')
    ], validators=[Optional()])
    transmission = SelectField('Transmission', choices=[
        ('', 'All'),
        ('manual', 'Manual'),
        ('automatic', 'Automatic')
    ], validators=[Optional()])
    submit = SubmitField('Search')


# Workshop Dashboard Forms
class WorkshopJobForm(FlaskForm):
    mechanic_id = SelectField('Assign Mechanic', coerce=int, validators=[Optional()])
    estimated_hours = FloatField('Estimated Hours', validators=[DataRequired(), NumberRange(min=0.1, max=100)])
    priority = SelectField('Priority', choices=[
        (1, 'Low'),
        (2, 'Normal'),
        (3, 'High'),
        (4, 'Urgent')
    ], coerce=int, validators=[DataRequired()])
    status = SelectField('Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    notes = TextAreaField('Initial Notes', validators=[Optional()])
    submit = SubmitField('Create Job')


class JobNoteForm(FlaskForm):
    note = TextAreaField('Add Note', validators=[DataRequired()])
    submit = SubmitField('Add Note')


class JobStatusUpdateForm(FlaskForm):
    status = SelectField('Update Status', choices=[
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[DataRequired()])
    note = TextAreaField('Status Update Note', validators=[Optional()])
    submit = SubmitField('Update Status')


class StartWorkForm(FlaskForm):
    submit = SubmitField('Start Work')


class CompleteWorkForm(FlaskForm):
    actual_hours = FloatField('Actual Hours Spent', validators=[DataRequired(), NumberRange(min=0.1, max=100)])
    note = TextAreaField('Completion Notes', validators=[Optional()])
    submit = SubmitField('Complete Work')


class AddPartForm(FlaskForm):
    part_id = SelectField('Select Part', coerce=int, validators=[DataRequired()])
    quantity = IntegerField('Quantity', validators=[DataRequired(), NumberRange(min=1, max=100)])
    submit = SubmitField('Add Part')


class PartForm(FlaskForm):
    name = StringField('Part Name', validators=[DataRequired(), Length(min=2, max=100)])
    part_number = StringField('Part Number', validators=[DataRequired(), Length(min=2, max=50)])
    description = TextAreaField('Description', validators=[Optional()])
    cost_price = FloatField('Cost Price', validators=[DataRequired(), NumberRange(min=0)])
    retail_price = FloatField('Retail Price', validators=[DataRequired(), NumberRange(min=0)])
    quantity_in_stock = IntegerField('Quantity in Stock', validators=[DataRequired(), NumberRange(min=0)])
    category = SelectField('Category', choices=[
        ('engine', 'Engine'),
        ('transmission', 'Transmission'),
        ('brakes', 'Brakes'),
        ('electrical', 'Electrical'),
        ('suspension', 'Suspension'),
        ('exhaust', 'Exhaust'),
        ('body', 'Body'),
        ('other', 'Other')
    ], validators=[DataRequired()])
    submit = SubmitField('Save Part')


class JobSearchForm(FlaskForm):
    status = SelectField('Status', choices=[
        ('', 'All Statuses'),
        ('pending', 'Pending'),
        ('in_progress', 'In Progress'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    ], validators=[Optional()])
    mechanic_id = SelectField('Mechanic', coerce=int, choices=[], validators=[Optional()])
    priority = SelectField('Priority', choices=[
        (0, 'All Priorities'),
        (1, 'Low'),
        (2, 'Normal'),
        (3, 'High'),
        (4, 'Urgent')
    ], coerce=int, validators=[Optional()])
    date_from = DateField('From Date', validators=[Optional()])
    date_to = DateField('To Date', validators=[Optional()])
    vehicle_id = SelectField('Vehicle', coerce=int, choices=[], validators=[Optional()])
    submit = SubmitField('Search')
