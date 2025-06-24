# ==============================================================================
# 1. IMPORTS
# ==============================================================================
import os
from flask import Flask, jsonify, request, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text, or_
from sentence_transformers import SentenceTransformer, util
import requests
import torch
from dotenv import load_dotenv
load_dotenv()

# ==============================================================================
# 2. INITIALIZATION AND CONFIGURATION
# ==============================================================================
app = Flask(__name__)

# --- Database Configuration ---
DB_USER = "priyanshu"
DB_PASSWORD = ""
DB_HOST = "localhost"
DB_PORT = "5432"
DB_NAME = "zomato_db"
DATABASE_URL = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# --- Hugging Face API Token ---
HF_API_TOKEN = os.getenv("HF_API_TOKEN")

# ==============================================================================
# 3. DATABASE MODELS
# ==============================================================================
class Country(db.Model):
    __tablename__ = 'countries'
    country_code = db.Column(db.Integer, primary_key=True)
    country_name = db.Column(db.String(100), nullable=False)

class Restaurant(db.Model):
    __tablename__ = 'restaurants'
    restaurant_id = db.Column(db.BigInteger, primary_key=True)
    restaurant_name = db.Column(db.String(255), nullable=False)
    country_code = db.Column(db.Integer, db.ForeignKey('countries.country_code'))
    city = db.Column(db.String(100))
    address = db.Column(db.Text)
    locality = db.Column(db.String(255))
    locality_verbose = db.Column(db.String(255))
    longitude = db.Column(db.Float)
    latitude = db.Column(db.Float)
    cuisines = db.Column(db.String(255))
    average_cost_for_two = db.Column(db.Integer)
    currency = db.Column(db.String(50))
    has_table_booking = db.Column(db.String(10))
    has_online_delivery = db.Column(db.String(10))
    is_delivering_now = db.Column(db.String(10))
    aggregate_rating = db.Column(db.Float)
    rating_color = db.Column(db.String(50))
    rating_text = db.Column(db.String(50))
    votes = db.Column(db.Integer)
    geog = db.Column(db.String)
    country = db.relationship('Country', backref=db.backref('restaurants', lazy=True))

    def to_dict(self):
        return {
            'restaurant_id': self.restaurant_id,
            'restaurant_name': self.restaurant_name,
            'country': self.country.country_name if self.country else None,
            'city': self.city,
            'address': self.address,
            'cuisines': self.cuisines,
            'average_cost_for_two': self.average_cost_for_two,
            'currency': self.currency,
            'has_table_booking': self.has_table_booking,
            'has_online_delivery': self.has_online_delivery,
            'aggregate_rating': self.aggregate_rating,
            'rating_text': self.rating_text,
            'votes': self.votes,
            'location': {'latitude': self.latitude, 'longitude': self.longitude}
        }

# ==============================================================================
# 4. UI-SERVING ROUTES
# ==============================================================================
@app.route('/')
def restaurant_list_page():
    return render_template('restaurant_list.html')

@app.route('/restaurant/<int:restaurant_id>')
def restaurant_detail_page(restaurant_id):
    return render_template('restaurant_detail.html')

# ==============================================================================
# 5. API ROUTES
# ==============================================================================
@app.route('/api/countries', methods=['GET'])
def get_all_countries():
    countries = Country.query.order_by(Country.country_name).all()
    return jsonify([country.country_name for country in countries])

@app.route('/api/restaurant/<int:restaurant_id>', methods=['GET'])
def get_restaurant_by_id(restaurant_id):
    restaurant = Restaurant.query.get_or_404(restaurant_id)
    return jsonify(restaurant.to_dict())

@app.route('/api/restaurants', methods=['GET'])
def get_all_restaurants():
    query = Restaurant.query
    country_filter = request.args.get('country')
    if country_filter:
        query = query.join(Country).filter(Country.country_name == country_filter)
    max_cost_filter = request.args.get('max_cost', type=int)
    if max_cost_filter:
        query = query.filter(Restaurant.average_cost_for_two <= max_cost_filter)
    cuisine_filter = request.args.get('cuisine')
    if cuisine_filter:
        query = query.filter(Restaurant.cuisines.ilike(f'%{cuisine_filter}%'))
    search_term = request.args.get('search')
    if search_term:
        query = query.filter(or_(Restaurant.restaurant_name.ilike(f'%{search_term}%'), Restaurant.cuisines.ilike(f'%{search_term}%')))
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    paginated_restaurants = query.order_by(Restaurant.restaurant_id).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "data": [r.to_dict() for r in paginated_restaurants.items],
        "pagination": {
            "total_items": paginated_restaurants.total,
            "total_pages": paginated_restaurants.pages,
            "current_page": paginated_restaurants.page,
            "items_per_page": paginated_restaurants.per_page,
            "has_next": paginated_restaurants.has_next,
            "has_prev": paginated_restaurants.has_prev
        }
    })

@app.route('/api/restaurants/search/nearby', methods=['GET'])
def search_nearby_restaurants():
    try:
        lat = request.args.get('lat', type=float)
        lon = request.args.get('lon', type=float)
        radius = request.args.get('radius', 3000, type=int)
        if lat is None or lon is None:
            return jsonify({"error": "Missing 'lat' or 'lon' query parameters"}), 400
    except (ValueError, TypeError):
        return jsonify({"error": "Invalid parameter type."}), 400

    id_query = text("""
        SELECT restaurant_id FROM restaurants
        WHERE ST_DWithin(geog, ST_MakePoint(:lon, :lat)::geography, :radius)
    """)
    id_results = db.session.execute(id_query, {"lon": lon, "lat": lat, "radius": radius})
    nearby_ids = [row[0] for row in id_results]
    if not nearby_ids:
        return jsonify({"data": [], "pagination": {"total_items": 0, "total_pages": 0, "current_page": 1}})

    query = Restaurant.query.filter(Restaurant.restaurant_id.in_(nearby_ids))
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 6, type=int)
    paginated_restaurants = query.order_by(Restaurant.restaurant_id).paginate(page=page, per_page=per_page, error_out=False)
    return jsonify({
        "data": [r.to_dict() for r in paginated_restaurants.items],
        "pagination": {
            "total_items": paginated_restaurants.total,
            "total_pages": paginated_restaurants.pages,
            "current_page": paginated_restaurants.page,
            "items_per_page": per_page,
            "has_next": paginated_restaurants.has_next,
            "has_prev": paginated_restaurants.has_prev
        }
    })

# Load semantic model once
model = SentenceTransformer('all-MiniLM-L6-v2')

# Define general food categories
FOOD_CATEGORIES = [
    "burger", "pizza", "pasta", "coffee", "bread", "dessert", "ice cream",
    "indian", "japanese", "mexican", "chinese", "korean", "salad", "fried chicken",
    "noodles", "soup", "hot dog", "sandwich", "sushi", "beverage", "bakery"
]

# Pre-compute embeddings for the categories
category_embeddings = model.encode(FOOD_CATEGORIES, convert_to_tensor=True)

@app.route('/api/search/by-image', methods=['POST'])
def search_by_image():
    if 'food_image' not in request.files:
        return jsonify({"error": "No image file provided"}), 400

    file = request.files['food_image']
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    image_data = file.read()

    api_url = "https://api-inference.huggingface.co/models/microsoft/resnet-50"
    headers = {
        "Authorization": f"Bearer {HF_API_TOKEN}",
        "Content-Type": "image/jpeg"
    }

    try:
        hf_response = requests.post(api_url, headers=headers, data=image_data, timeout=30)
        hf_response.raise_for_status()
        image_labels = hf_response.json()
    except requests.exceptions.RequestException as e:
        return jsonify({"error": f"Failed to call image recognition API: {e}"}), 500

    if not image_labels or not isinstance(image_labels, list):
        return jsonify({"error": "Could not identify the food item from the image."}), 400

    top_label = image_labels[0]['label']
    food_item = top_label.split(',')[0].strip().lower()

    food_embedding = model.encode(food_item, convert_to_tensor=True)
    cosine_scores = util.cos_sim(food_embedding, category_embeddings)
    best_match_idx = cosine_scores.argmax().item()
    generalized_food = FOOD_CATEGORIES[best_match_idx]

    matching_restaurants = Restaurant.query.filter(
        Restaurant.cuisines.ilike(f'%{generalized_food}%')
    ).limit(20).all()

    results = [r.to_dict() for r in matching_restaurants]

    return jsonify({
        "identified_food": food_item,
        "generalized_food": generalized_food,
        "data": results
    })

# ==============================================================================
# 6. APPLICATION RUNNER
# ==============================================================================
if __name__ == '__main__':
    app.run(debug=True)














