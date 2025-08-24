from flask import Flask, render_template, request, redirect, url_for, session, flash, jsonify
import json
import os
import secrets
import string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = 'your-secret-key-change-this-in-production'

# Data file paths
DATA_DIR = 'data'
USERS_FILE = os.path.join(DATA_DIR, 'users.json')
KEYS_FILE = os.path.join(DATA_DIR, 'keys.json')
SETTINGS_FILE = os.path.join(DATA_DIR, 'settings.json')
REFERRALS_FILE = os.path.join(DATA_DIR, 'referrals.json')

# Ensure data directory exists
os.makedirs(DATA_DIR, exist_ok=True)

# Initialize data files
def init_data_files():
    # Initialize users with owner account
    if not os.path.exists(USERS_FILE):
        users = {
            "loaoan": {
                "password": generate_password_hash("loaoan123"),
                "role": "OWNER",
                "balance": 2146371656,
                "created_at": datetime.now().isoformat(),
                "status": "active"
            }
        }
        save_json(USERS_FILE, users)
    
    # Initialize keys
    if not os.path.exists(KEYS_FILE):
        save_json(KEYS_FILE, {})
    
    # Initialize settings
    if not os.path.exists(SETTINGS_FILE):
        settings = {
            "prices": {
                "1": 9999,
                "24": 30000,
                "168": 1,
                "720": 4,
                "2160": 8
            },
            "currency": "₹",
            "features": {
                "esp": True,
                "aimbot": True,
                "item": True,
                "bullet": True,
                "memory": True,
                "maintenance": False
            },
            "mod_settings": {
                "name": "AURA PUBG ESP",
                "status": "active"
            }
        }
        save_json(SETTINGS_FILE, settings)
    
    # Initialize referrals
    if not os.path.exists(REFERRALS_FILE):
        save_json(REFERRALS_FILE, {})

def load_json(file_path):
    try:
        with open(file_path, 'r') as f:
            return json.load(f)
    except (FileNotFoundError, json.JSONDecodeError):
        return {}

def save_json(file_path, data):
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)

def generate_random_key(length=10):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_referral_code():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    return render_template('login.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        users = load_json(USERS_FILE)
        
        if username in users and check_password_hash(users[username]['password'], password):
            session['username'] = username
            session['role'] = users[username]['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        referral_code = request.form['referral_code']
        
        users = load_json(USERS_FILE)
        referrals = load_json(REFERRALS_FILE)
        
        # Validation
        if username in users:
            flash('Username already exists!', 'error')
            return render_template('register.html')
        
        if password != confirm_password:
            flash('Passwords do not match!', 'error')
            return render_template('register.html')
        
        if not referral_code or referral_code not in referrals:
            flash('Valid referral code is required!', 'error')
            return render_template('register.html')
        
        # Check if referral code is still valid
        if referrals[referral_code]['used']:
            flash('Referral code already used!', 'error')
            return render_template('register.html')
        
        # Create new user
        users[username] = {
            "password": generate_password_hash(password),
            "role": "RESELLER",
            "balance": 0,
            "created_at": datetime.now().isoformat(),
            "status": "active",
            "referred_by": referrals[referral_code]['created_by']
        }
        
        # Mark referral as used
        referrals[referral_code]['used'] = True
        referrals[referral_code]['used_by'] = username
        referrals[referral_code]['used_at'] = datetime.now().isoformat()
        
        save_json(USERS_FILE, users)
        save_json(REFERRALS_FILE, referrals)
        
        flash('Account created successfully! Please login.', 'success')
        return redirect(url_for('login'))
    
    return render_template('register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    users = load_json(USERS_FILE)
    keys = load_json(KEYS_FILE)
    settings = load_json(SETTINGS_FILE)
    
    user_data = users[session['username']]
    
    # Calculate key statistics
    user_keys = [key for key in keys.values() if key.get('owner') == session['username']]
    total_keys = len(user_keys)
    active_keys = len([key for key in user_keys if key.get('status') == 'active'])
    expired_keys = len([key for key in user_keys if key.get('status') == 'expired'])
    
    return render_template('dashboard.html', 
                         user=user_data, 
                         username=session['username'],
                         role=session['role'],
                         settings=settings,
                         stats={
                             'total_keys': total_keys,
                             'active_keys': active_keys,
                             'expired_keys': expired_keys
                         },
                         keys=user_keys)

@app.route('/generate_key', methods=['POST'])
def generate_key():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    game = request.form['game']
    duration = request.form['duration']
    devices = request.form['devices']
    key_type = request.form['key_type']
    custom_name = request.form.get('custom_name', '')
    
    users = load_json(USERS_FILE)
    keys = load_json(KEYS_FILE)
    settings = load_json(SETTINGS_FILE)
    
    user_data = users[session['username']]
    price = settings['prices'][duration]
    
    if user_data['balance'] < price:
        return jsonify({'success': False, 'message': 'Insufficient balance!'})
    
    # Generate key based on type
    if key_type == 'random':
        generated_key = generate_random_key()
    elif key_type == 'name':
        if not custom_name:
            return jsonify({'success': False, 'message': 'Custom name required!'})
        generated_key = custom_name
    elif key_type == 'nameRandom':
        if not custom_name:
            return jsonify({'success': False, 'message': 'Custom name required!'})
        generated_key = custom_name + generate_random_key(4)
    else:
        generated_key = generate_random_key()
    
    # Create new key
    key_id = str(len(keys) + 1)
    new_key = {
        'id': key_id,
        'key': generated_key,
        'game': game,
        'duration': duration,
        'max_devices': devices,
        'current_devices': 0,
        'status': 'active',
        'owner': session['username'],
        'created_at': datetime.now().isoformat(),
        'expires_at': (datetime.now() + timedelta(hours=int(duration))).isoformat(),
        'price': price
    }
    
    keys[key_id] = new_key
    
    # Deduct balance
    users[session['username']]['balance'] -= price
    
    save_json(KEYS_FILE, keys)
    save_json(USERS_FILE, users)
    
    return jsonify({
        'success': True, 
        'message': 'Key generated successfully!',
        'key': generated_key,
        'remaining_balance': users[session['username']]['balance']
    })

@app.route('/create_referral', methods=['POST'])
def create_referral():
    if 'username' not in session or session['role'] != 'OWNER':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    referrals = load_json(REFERRALS_FILE)
    
    referral_code = generate_referral_code()
    referrals[referral_code] = {
        'code': referral_code,
        'created_by': session['username'],
        'created_at': datetime.now().isoformat(),
        'used': False,
        'used_by': None,
        'used_at': None
    }
    
    save_json(REFERRALS_FILE, referrals)
    
    return jsonify({
        'success': True,
        'message': 'Referral code created successfully!',
        'referral_code': referral_code
    })

@app.route('/get_keys')
def get_keys():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    keys = load_json(KEYS_FILE)
    user_keys = [key for key in keys.values() if key.get('owner') == session['username']]
    
    return jsonify({'success': True, 'keys': user_keys})

@app.route('/delete_key/<key_id>', methods=['POST'])
def delete_key(key_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    keys = load_json(KEYS_FILE)
    
    if key_id in keys and keys[key_id].get('owner') == session['username']:
        del keys[key_id]
        save_json(KEYS_FILE, keys)
        return jsonify({'success': True, 'message': 'Key deleted successfully!'})
    
    return jsonify({'success': False, 'message': 'Key not found or unauthorized'})

@app.route('/delete_all_keys', methods=['POST'])
def delete_all_keys():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    keys = load_json(KEYS_FILE)
    
    # Delete only user's keys
    keys_to_delete = [key_id for key_id, key in keys.items() if key.get('owner') == session['username']]
    for key_id in keys_to_delete:
        del keys[key_id]
    
    save_json(KEYS_FILE, keys)
    return jsonify({'success': True, 'message': f'{len(keys_to_delete)} keys deleted!'})

@app.route('/update_settings', methods=['POST'])
def update_settings():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    settings = load_json(SETTINGS_FILE)
    
    setting_type = request.form['type']
    
    if setting_type == 'price':
        duration = request.form['duration']
        new_price = float(request.form['price'])
        settings['prices'][duration] = new_price
    elif setting_type == 'feature':
        feature = request.form['feature']
        enabled = request.form['enabled'] == 'true'
        settings['features'][feature] = enabled
    elif setting_type == 'mod':
        settings['mod_settings']['name'] = request.form['name']
        settings['mod_settings']['status'] = request.form['status']
    
    save_json(SETTINGS_FILE, settings)
    return jsonify({'success': True, 'message': 'Settings updated successfully!'})

@app.route('/add_balance', methods=['POST'])
def add_balance():
    if 'username' not in session or session['role'] != 'OWNER':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    target_user = request.form['username']
    amount = float(request.form['amount'])
    
    users = load_json(USERS_FILE)
    
    if target_user in users:
        users[target_user]['balance'] += amount
        save_json(USERS_FILE, users)
        return jsonify({'success': True, 'message': f'Balance added successfully!'})
    
    return jsonify({'success': False, 'message': 'User not found!'})

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

# Error handlers
@app.errorhandler(404)
def not_found_error(error):
    return render_template('404.html'), 404

@app.errorhandler(500)
def internal_error(error):
    return render_template('500.html'), 500

if __name__ == '__main__':
    init_data_files()
    app.run(debug=False, host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))