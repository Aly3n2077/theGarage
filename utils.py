from app import db
from models import Service, VehicleMake, VehicleModel, User, Part
import logging
from datetime import datetime

def create_initial_data():
    """Create initial service types and vehicle makes/models if they don't exist"""
    # Create service types
    if Service.query.count() == 0:
        services = [
            {
                'name': 'Basic Service',
                'description': 'Oil change, filter replacement, and basic inspection',
                'price_estimate': 1200.00,
                'duration_hours': 1.5,
                'category': 'mechanical'
            },
            {
                'name': 'Full Service',
                'description': 'Comprehensive vehicle service including fluid changes, filters, and thorough inspection',
                'price_estimate': 2500.00,
                'duration_hours': 3.0,
                'category': 'mechanical'
            },
            {
                'name': 'Minor Panel Beating',
                'description': 'Repair of minor dents and scratches',
                'price_estimate': 1800.00,
                'duration_hours': 4.0,
                'category': 'panel_beating'
            },
            {
                'name': 'Major Panel Beating',
                'description': 'Repair of significant body damage',
                'price_estimate': 5000.00,
                'duration_hours': 8.0,
                'category': 'panel_beating'
            },
            {
                'name': 'Partial Repaint',
                'description': 'Repaint of specific panels or areas',
                'price_estimate': 2200.00,
                'duration_hours': 6.0,
                'category': 'painting'
            },
            {
                'name': 'Full Vehicle Repaint',
                'description': 'Complete vehicle respray with premium paint',
                'price_estimate': 15000.00,
                'duration_hours': 24.0,
                'category': 'painting'
            },
            {
                'name': 'Brake System Repair',
                'description': 'Inspection and repair of brake system components',
                'price_estimate': 1500.00,
                'duration_hours': 2.0,
                'category': 'mechanical'
            },
            {
                'name': 'Suspension Work',
                'description': 'Repair or replacement of suspension components',
                'price_estimate': 3000.00,
                'duration_hours': 4.0,
                'category': 'mechanical'
            }
        ]
        
        for service_data in services:
            service = Service(**service_data)
            db.session.add(service)
        
        db.session.commit()
        logging.info('Initial service types created')
    
    # Create common vehicle makes and models
    if VehicleMake.query.count() == 0:
        make_models = {
            'Toyota': ['Corolla', 'Hilux', 'Fortuner', 'RAV4', 'Land Cruiser', 'Yaris'],
            'Volkswagen': ['Polo', 'Golf', 'Tiguan', 'Amarok', 'Jetta'],
            'Ford': ['Ranger', 'Fiesta', 'EcoSport', 'Figo', 'Mustang'],
            'BMW': ['3 Series', '5 Series', 'X3', 'X5', 'M3'],
            'Mercedes-Benz': ['C-Class', 'E-Class', 'GLC', 'A-Class', 'AMG GT'],
            'Nissan': ['NP200', 'Navara', 'X-Trail', 'Qashqai', 'Micra'],
            'Honda': ['Civic', 'CR-V', 'Jazz', 'Accord', 'HR-V'],
            'Hyundai': ['i20', 'Tucson', 'Creta', 'Grand i10', 'Santa Fe'],
            'Mazda': ['CX-5', 'Mazda3', 'Mazda2', 'BT-50', 'CX-3'],
            'Suzuki': ['Swift', 'Jimny', 'Vitara', 'Ignis', 'Baleno']
        }
        
        for make_name, models in make_models.items():
            make = VehicleMake(name=make_name)
            db.session.add(make)
            db.session.flush()  # Flush to get the make_id
            
            for model_name in models:
                model = VehicleModel(name=model_name, make_id=make.id)
                db.session.add(model)
        
        db.session.commit()
        logging.info('Initial vehicle makes and models created')
        
    # Create workshop staff if they don't exist
    if User.query.filter_by(username='mechanic1').first() is None:
        # Create a mechanic
        mechanic = User(
            username='mechanic1',
            email='mechanic1@thegarage.co.za',
            first_name='John',
            last_name='Smith',
            phone='+27 82 123 4567',
            country='SA',
            role='mechanic',
            specialization='engine'
        )
        mechanic.set_password('password123')
        db.session.add(mechanic)
        
        # Create a service manager
        service_manager = User(
            username='service_manager',
            email='service@thegarage.co.za',
            first_name='Sarah',
            last_name='Johnson',
            phone='+27 83 456 7890',
            country='SA',
            role='service_manager'
        )
        service_manager.set_password('password123')
        db.session.add(service_manager)
        
        # Create a parts manager
        parts_manager = User(
            username='parts_manager',
            email='parts@thegarage.co.za',
            first_name='Michael',
            last_name='Williams',
            phone='+27 84 789 0123',
            country='SA',
            role='parts_manager'
        )
        parts_manager.set_password('password123')
        db.session.add(parts_manager)
        
        db.session.commit()
        logging.info('Workshop staff created')
    
    # Create initial parts inventory if empty
    if Part.query.count() == 0:
        parts = [
            {
                'name': 'Oil Filter',
                'part_number': 'OIL-F-001',
                'description': 'Standard oil filter for most vehicles',
                'cost_price': 80.00,
                'retail_price': 150.00,
                'quantity_in_stock': 25,
                'category': 'engine'
            },
            {
                'name': 'Air Filter',
                'part_number': 'AIR-F-001',
                'description': 'Standard air filter for most vehicles',
                'cost_price': 120.00,
                'retail_price': 220.00,
                'quantity_in_stock': 18,
                'category': 'engine'
            },
            {
                'name': 'Front Brake Pads',
                'part_number': 'BRK-P-F001',
                'description': 'Front brake pads for sedans and small SUVs',
                'cost_price': 350.00,
                'retail_price': 650.00,
                'quantity_in_stock': 12,
                'category': 'brakes'
            },
            {
                'name': 'Rear Brake Pads',
                'part_number': 'BRK-P-R001',
                'description': 'Rear brake pads for sedans and small SUVs',
                'cost_price': 300.00,
                'retail_price': 550.00,
                'quantity_in_stock': 10,
                'category': 'brakes'
            },
            {
                'name': 'Brake Disc',
                'part_number': 'BRK-D-001',
                'description': 'Standard brake disc for front wheels',
                'cost_price': 480.00,
                'retail_price': 850.00,
                'quantity_in_stock': 8,
                'category': 'brakes'
            },
            {
                'name': 'Spark Plugs (Set of 4)',
                'part_number': 'SPK-001',
                'description': 'Set of 4 standard spark plugs',
                'cost_price': 180.00,
                'retail_price': 320.00,
                'quantity_in_stock': 15,
                'category': 'engine'
            },
            {
                'name': 'Timing Belt',
                'part_number': 'TIM-B-001',
                'description': 'Standard timing belt for most 4-cylinder engines',
                'cost_price': 450.00,
                'retail_price': 780.00,
                'quantity_in_stock': 6,
                'category': 'engine'
            },
            {
                'name': 'Shock Absorber (Front)',
                'part_number': 'SHK-F-001',
                'description': 'Front shock absorber for sedans and compact SUVs',
                'cost_price': 720.00,
                'retail_price': 1200.00,
                'quantity_in_stock': 4,
                'category': 'suspension'
            },
            {
                'name': 'Shock Absorber (Rear)',
                'part_number': 'SHK-R-001',
                'description': 'Rear shock absorber for sedans and compact SUVs',
                'cost_price': 680.00,
                'retail_price': 1150.00,
                'quantity_in_stock': 4,
                'category': 'suspension'
            },
            {
                'name': 'Headlight Bulb',
                'part_number': 'LIT-H-001',
                'description': 'Standard H7 headlight bulb',
                'cost_price': 65.00,
                'retail_price': 120.00,
                'quantity_in_stock': 30,
                'category': 'electrical'
            }
        ]
        
        for part_data in parts:
            part = Part(**part_data)
            db.session.add(part)
        
        db.session.commit()
        logging.info('Initial parts inventory created')

def format_currency(amount):
    """Format currency based on country"""
    if amount is None:
        return ""
    return f"R {amount:,.2f}"  # South African Rand

def get_available_time_slots(date, booked_slots=[]):
    """Return available time slots for booking"""
    # Business hours: 8am to 5pm, 1-hour slots
    all_slots = ["08:00", "09:00", "10:00", "11:00", "12:00", "13:00", "14:00", "15:00", "16:00"]
    
    # Remove already booked slots
    available_slots = [slot for slot in all_slots if slot not in booked_slots]
    return available_slots
