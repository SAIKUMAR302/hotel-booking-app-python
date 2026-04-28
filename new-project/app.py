from flask import Flask, render_template, request, jsonify, session, redirect, url_for
from datetime import datetime, timedelta
import json
import uuid
from functools import wraps

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-in-production'

# Sample hotel data
HOTELS = [
    {
        'id': 1,
        'name': 'Grand Plaza Hotel',
        'location': 'New York',
        'price_per_night': 250,
        'rating': 4.8,
        'image': 'https://images.unsplash.com/photo-1566073771259-6a8506099945?w=400',
        'amenities': ['Free WiFi', 'Pool', 'Spa', 'Restaurant']
    },
    {
        'id': 2,
        'name': 'Ocean View Resort',
        'location': 'Miami',
        'price_per_night': 350,
        'rating': 4.9,
        'image': 'https://images.unsplash.com/photo-1584132967334-10e028bd69f7?w=400',
        'amenities': ['Beach Access', 'Pool', 'Free Breakfast', 'Parking']
    },
    {
        'id': 3,
        'name': 'Mountain Lodge',
        'location': 'Denver',
        'price_per_night': 180,
        'rating': 4.6,
        'image': 'https://images.unsplash.com/photo-1455587734955-081b22074882?w=400',
        'amenities': ['Hiking Trails', 'Free WiFi', 'Fireplace', 'Restaurant']
    },
    {
        'id': 4,
        'name': 'Urban Stay',
        'location': 'Chicago',
        'price_per_night': 200,
        'rating': 4.5,
        'image': 'https://images.unsplash.com/photo-1551882547-ff40c63fe5fa?w=400',
        'amenities': ['Gym', 'Business Center', 'Free WiFi', 'Bar']
    },
    {
        'id': 5,
        'name': 'Sunset Paradise',
        'location': 'Los Angeles',
        'price_per_night': 300,
        'rating': 4.7,
        'image': 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?w=400',
        'amenities': ['Ocean View', 'Pool', 'Spa', 'Restaurant']
    },
    {
        'id': 6,
        'name': 'Historic Inn',
        'location': 'Boston',
        'price_per_night': 160,
        'rating': 4.4,
        'image': 'https://images.unsplash.com/photo-1522798514-97ceb3c4f1f8?w=400',
        'amenities': ['Free Breakfast', 'Free WiFi', 'Historical Tours', 'Library']
    }
]

# Store bookings (in production, use a database)
BOOKINGS = {}

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return jsonify({'error': 'Please login first'}), 401
        return f(*args, **kwargs)
    return decorated_function

@app.route('/')
def index():
    return render_template('index.html', hotels=HOTELS)

@app.route('/api/hotels')
def get_hotels():
    location = request.args.get('location', '')
    check_in = request.args.get('check_in')
    check_out = request.args.get('check_out')
    
    filtered_hotels = HOTELS
    if location:
        filtered_hotels = [h for h in HOTELS if location.lower() in h['location'].lower()]
    
    return jsonify(filtered_hotels)

@app.route('/hotel/<int:hotel_id>')
def hotel_detail(hotel_id):
    hotel = next((h for h in HOTELS if h['id'] == hotel_id), None)
    if not hotel:
        return redirect(url_for('index'))
    return render_template('booking.html', hotel=hotel)

@app.route('/api/book', methods=['POST'])
def create_booking():
    data = request.json
    
    required_fields = ['hotel_id', 'guest_name', 'email', 'check_in', 'check_out', 'guests']
    if not all(field in data for field in required_fields):
        return jsonify({'error': 'Missing required fields'}), 400
    
    hotel = next((h for h in HOTELS if h['id'] == data['hotel_id']), None)
    if not hotel:
        return jsonify({'error': 'Hotel not found'}), 404
    
    # Calculate total price
    check_in_date = datetime.strptime(data['check_in'], '%Y-%m-%d')
    check_out_date = datetime.strptime(data['check_out'], '%Y-%m-%d')
    nights = (check_out_date - check_in_date).days
    
    if nights <= 0:
        return jsonify({'error': 'Check-out must be after check-in'}), 400
    
    total_price = nights * hotel['price_per_night']
    
    # Create booking
    booking_id = str(uuid.uuid4())[:8]
    booking = {
        'booking_id': booking_id,
        'hotel': hotel,
        'guest_name': data['guest_name'],
        'email': data['email'],
        'phone': data.get('phone', ''),
        'check_in': data['check_in'],
        'check_out': data['check_out'],
        'nights': nights,
        'guests': data['guests'],
        'total_price': total_price,
        'booking_date': datetime.now().isoformat(),
        'status': 'confirmed'
    }
    
    BOOKINGS[booking_id] = booking
    
    return jsonify({
        'message': 'Booking confirmed!',
        'booking_id': booking_id,
        'total_price': total_price,
        'nights': nights
    }), 201

@app.route('/booking/<booking_id>')
def booking_confirmation(booking_id):
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return redirect(url_for('index'))
    return render_template('confirmation.html', booking=booking)

@app.route('/api/bookings/<booking_id>')
def get_booking(booking_id):
    booking = BOOKINGS.get(booking_id)
    if not booking:
        return jsonify({'error': 'Booking not found'}), 404
    return jsonify(booking)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
