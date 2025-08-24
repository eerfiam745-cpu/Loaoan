from flask import Flask, render_template_string, request, redirect, url_for, session, flash, jsonify
import json
import os
import secrets
import string
from datetime import datetime, timedelta
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'your-secret-key-change-this-in-production')

# Data storage in memory (for free hosting)
users_data = {
    "loaoan": {
        "password": generate_password_hash("loaoan123"),
        "role": "OWNER",
        "balance": 2146371656,
        "created_at": datetime.now().isoformat(),
        "status": "active"
    }
}

keys_data = {}
referrals_data = {}

settings_data = {
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

def generate_random_key(length=10):
    return ''.join(secrets.choice(string.ascii_letters + string.digits) for _ in range(length))

def generate_referral_code():
    return ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(8))

# HTML Templates as strings
BASE_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>AURA SERVER EDITION</title>
    <style>
        * { margin: 0; padding: 0; box-sizing: border-box; }
        body { 
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            background: linear-gradient(135deg, #1e3c72 0%, #2a5298 100%);
            min-height: 100vh; color: white;
        }
        .navbar { 
            background: linear-gradient(90deg, #4a90e2, #7b68ee); padding: 15px 30px;
            display: flex; justify-content: space-between; align-items: center;
            box-shadow: 0 2px 10px rgba(0,0,0,0.3);
        }
        .navbar h1 { font-size: 24px; font-weight: bold; }
        .btn { 
            padding: 12px 25px; border: none; border-radius: 8px; cursor: pointer;
            font-weight: bold; transition: all 0.3s ease; margin: 5px;
            text-decoration: none; display: inline-block;
        }
        .btn-primary { background: linear-gradient(45deg, #4CAF50, #45a049); color: white; }
        .btn-danger { background: linear-gradient(45deg, #f44336, #da190b); color: white; }
        .btn-warning { background: linear-gradient(45deg, #ff9800, #f57c00); color: white; }
        .btn-info { background: linear-gradient(45deg, #2196F3, #0b7dda); color: white; }
        .btn:hover { transform: translateY(-2px); box-shadow: 0 5px 15px rgba(0,0,0,0.3); }
        .form-group { margin-bottom: 20px; }
        .form-group label { display: block; margin-bottom: 8px; font-weight: bold; }
        .form-group input, .form-group select { 
            width: 100%; padding: 12px; border: none; border-radius: 8px;
            background: rgba(255,255,255,0.9); color: #333;
        }
        .alert { padding: 15px; margin-bottom: 20px; border-radius: 8px; font-weight: bold; }
        .alert-success { background: #4CAF50; color: white; }
        .alert-error { background: #f44336; color: white; }
        .main-container { padding: 30px; max-width: 1400px; margin: 0 auto; }
        .login-form { 
            max-width: 400px; margin: 100px auto; background: rgba(255,255,255,0.1);
            padding: 40px; border-radius: 20px; backdrop-filter: blur(10px);
            border: 1px solid rgba(255,255,255,0.2);
        }
        .profile-pic { 
            width: 80px; height: 80px; border-radius: 50%; margin: 0 auto 20px auto;
            background: linear-gradient(45deg, #4CAF50, #45a049); display: flex;
            align-items: center; justify-content: center; font-size: 2em; color: white;
        }
        .panel-section { 
            background: rgba(255,255,255,0.1); border-radius: 15px; padding: 25px;
            backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); margin-bottom: 20px;
        }
        .panel-section h2 { margin-bottom: 20px; color: #4CAF50; font-size: 1.5em; }
        .stats-grid { 
            display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px; margin-bottom: 30px;
        }
        .stat-card { 
            background: rgba(255,255,255,0.1); padding: 20px; border-radius: 15px;
            backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.2); text-align: center;
        }
        .stat-card h3 { font-size: 2em; margin-bottom: 10px; color: #4CAF50; }
        .content-grid { display: grid; grid-template-columns: 1fr 1fr; gap: 30px; margin-bottom: 30px; }
        .keys-table { width: 100%; background: rgba(255,255,255,0.1); border-radius: 10px; overflow: hidden; margin-top: 20px; }
        .keys-table th, .keys-table td { padding: 12px; text-align: left; border-bottom: 1px solid rgba(255,255,255,0.2); }
        .keys-table th { background: rgba(0,0,0,0.3); color: #4CAF50; font-weight: bold; }
        .status-active { background: #4CAF50; color: white; padding: 4px 8px; border-radius: 15px; font-size: 0.8em; }
        .status-expired { background: #f44336; color: white; padding: 4px 8px; border-radius: 15px; font-size: 0.8em; }
        .welcome-bar { 
            background: rgba(255,255,255,0.1); padding: 15px 20px; border-radius: 10px;
            margin-bottom: 30px; text-align: center; backdrop-filter: blur(10px);
        }
        @media (max-width: 768px) { 
            .content-grid { grid-template-columns: 1fr; }
            .navbar { flex-direction: column; gap: 15px; }
        }
    </style>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>
</head>
<body>
    {% if session.username %}
    <nav class="navbar">
        <h1>🔹 AURA SERVER EDITION</h1>
        <div style="display: flex; align-items: center; gap: 15px;">
            <span>👤 {{ session.username }}</span>
            <span class="status-active">{{ session.role }}</span>
            <a href="{{ url_for('logout') }}" class="btn btn-danger">Logout</a>
        </div>
    </nav>
    {% endif %}
    <div class="main-container">
        {% with messages = get_flashed_messages(with_categories=true) %}
            {% if messages %}
                {% for category, message in messages %}
                    <div class="alert alert-{{ 'success' if category == 'success' else 'error' }}">{{ message }}</div>
                {% endfor %}
            {% endif %}
        {% endwith %}
        {{ content|safe }}
    </div>
    <script>
        setTimeout(function() { $('.alert').fadeOut(); }, 3000);
        function showAlert(message, type) {
            const alertClass = type === 'success' ? 'alert-success' : 'alert-error';
            const alertHtml = '<div class="alert ' + alertClass + '">' + message + '</div>';
            $('.main-container').prepend(alertHtml);
            setTimeout(() => $('.alert').first().fadeOut(), 3000);
        }
    </script>
</body>
</html>
"""

LOGIN_TEMPLATE = """
<div class="login-form">
    <div class="profile-pic">AL</div>
    <h2 style="text-align: center; margin-bottom: 30px;">Welcome back</h2>
    <p style="text-align: center; margin-bottom: 30px; color: rgba(255,255,255,0.7);">Sign in to continue to your account</p>
    
    <form method="POST" action="{{ url_for('login') }}">
        <div class="form-group">
            <label>Username</label>
            <input type="text" name="username" placeholder="Enter your username" required>
        </div>
        <div class="form-group">
            <label>Password</label>
            <input type="password" name="password" placeholder="Enter your password" required>
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin: 20px 0;">Sign In</button>
    </form>
    
    <div style="text-align: center;">
        <a href="{{ url_for('register') }}" style="color: #4CAF50; text-decoration: none;">Register</a>
    </div>
    
    <div style="text-align: center; margin-top: 30px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
        <h4 style="color: #4CAF50; margin-bottom: 10px;">Owner Account</h4>
        <p><strong>Username:</strong> loaoan</p>
        <p><strong>Password:</strong> loaoan123</p>
    </div>
</div>
"""

REGISTER_TEMPLATE = """
<div class="login-form">
    <div class="profile-pic">AL</div>
    <h2 style="text-align: center; margin-bottom: 30px;">Create account</h2>
    <p style="text-align: center; margin-bottom: 30px; color: rgba(255,255,255,0.7);">Join to continue</p>
    
    <form method="POST" action="{{ url_for('register') }}">
        <div class="form-group">
            <input type="text" name="username" placeholder="Welcome Stranger" required>
        </div>
        <div class="form-group">
            <input type="password" name="password" placeholder="Password" required>
        </div>
        <div class="form-group">
            <input type="password" name="confirm_password" placeholder="Confirm your password" required>
        </div>
        <div class="form-group">
            <input type="text" name="referral_code" placeholder="Enter referral code (required)" required>
        </div>
        <button type="submit" class="btn btn-primary" style="width: 100%; margin: 20px 0;">Create Account</button>
    </form>
    
    <div style="text-align: center;">
        <a href="{{ url_for('login') }}" style="color: #4CAF50; text-decoration: none;">Login</a>
    </div>
    
    <div style="text-align: center; margin-top: 30px; padding: 15px; background: rgba(255,255,255,0.1); border-radius: 10px;">
        <h4 style="color: #ff9800; margin-bottom: 10px;">⚠️ Notice</h4>
        <p style="font-size: 0.9em;">Referral code is required for registration. Only OWNER can create referral codes.</p>
    </div>
</div>
"""

DASHBOARD_TEMPLATE = """
<div class="welcome-bar"><h2>Welcome {{ username }}</h2></div>
<div class="stats-grid">
    <div class="stat-card"><h3 id="balanceAmount">₹{{ "{:,}".format(user.balance) }}</h3><p>Balance</p></div>
    <div class="stat-card"><h3>{{ role }}</h3><p>Level</p></div>
    <div class="stat-card"><h3>Just now</h3><p>Session</p></div>
    <div class="stat-card"><h3 id="totalKeys">{{ stats.total_keys }}</h3><p>Total Keys</p></div>
    <div class="stat-card"><h3 id="activeKeys">{{ stats.active_keys }}</h3><p>Active Keys</p></div>
    <div class="stat-card"><h3 id="expiredKeys">{{ stats.expired_keys }}</h3><p>Expired Keys</p></div>
</div>

<div class="content-grid">
    <div class="panel-section">
        <h2>🔑 Key Management</h2>
        <form id="keyGenerationForm">
            <div class="form-group">
                <label>Game Selection</label>
                <select id="gameSelect" name="game">
                    <option value="PUBG">PUBG</option>
                    <option value="BGMI">BGMI</option>
                    <option value="COD">Call of Duty</option>
                </select>
            </div>
            <div class="form-group">
                <label>Duration</label>
                <select id="durationSelect" name="duration">
                    {% for duration, price in settings.prices.items() %}
                    <option value="{{ duration }}">
                        {% if duration == '1' %}1 Hour{% elif duration == '24' %}1 Day{% elif duration == '168' %}7 Days{% elif duration == '720' %}30 Days{% elif duration == '2160' %}90 Days{% endif %} 
                        - {{ settings.currency }}{{ price }}
                    </option>
                    {% endfor %}
                </select>
            </div>
            <div class="form-group">
                <label>Max Devices</label>
                <select id="deviceSelect" name="devices">
                    <option value="1">1 Device</option>
                    <option value="2">2 Devices</option>
                    <option value="5">5 Devices</option>
                </select>
            </div>
            <div class="form-group">
                <label>Key Type</label>
                <select id="keyType" name="key_type" onchange="toggleNameInput()">
                    <option value="random">Random Key</option>
                    <option value="name">Name Key</option>
                    <option value="nameRandom">Name + Random Key</option>
                </select>
            </div>
            <div class="form-group" id="nameInput" style="display: none;">
                <label>Custom Name</label>
                <input type="text" id="customName" name="custom_name" placeholder="Enter custom name">
            </div>
            <div style="text-align: center; margin: 20px 0;">
                <button type="button" class="btn btn-primary" onclick="generateKey()">🔹 Generate Keys</button>
                <button type="button" class="btn btn-warning" onclick="generateNameKey()">🔸 Name Generate</button>
            </div>
        </form>
        <div style="display: flex; gap: 10px; flex-wrap: wrap; justify-content: center;">
            <button class="btn btn-danger" onclick="deleteAllKeys()">🗑️ Delete All Keys</button>
            <button class="btn btn-danger" onclick="deleteExpiredKeys()">🗑️ Delete Expired</button>
            <button class="btn btn-danger" onclick="deleteUnusedKeys()">🗑️ Delete Unused</button>
        </div>
    </div>

    <div class="panel-section">
        {% if role == 'OWNER' %}
        <h2>💰 Owner Panel</h2>
        <h3>Create Referral Code</h3>
        <button class="btn btn-primary" onclick="createReferral()" style="width: 100%; margin-bottom: 20px;">🎫 Generate Referral Code</button>
        <div id="referralResult" style="margin-bottom: 20px;"></div>
        <hr style="margin: 20px 0; border: 1px solid rgba(255,255,255,0.2);">
        <h3>Add Balance to User</h3>
        <div class="form-group">
            <label>Username</label>
            <input type="text" id="targetUser" placeholder="Enter username">
        </div>
        <div class="form-group">
            <label>Amount</label>
            <input type="number" id="addBalanceAmount" placeholder="Enter amount to add">
        </div>
        <button class="btn btn-info" onclick="addBalance()" style="width: 100%;">Add Balance</button>
        {% else %}
        <h2>💰 Reseller Panel</h2>
        <p style="text-align: center; padding: 20px;">Contact owner to add balance to your account.</p>
        {% endif %}
    </div>
</div>

<div class="panel-section">
    <h2>📋 Your Keys</h2>
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <div>
            <button class="btn btn-primary" onclick="loadKeys()">🔄 Refresh</button>
            <button class="btn btn-warning" onclick="toggleKeysTable()">👁️ Toggle</button>
        </div>
    </div>
    <table class="keys-table" id="keysTable">
        <thead>
            <tr><th>#</th><th>Game</th><th>User Keys</th><th>Devices</th><th>Duration</th><th>Status</th><th>Action</th></tr>
        </thead>
        <tbody id="keysTableBody"></tbody>
    </table>
</div>

<script>
let userKeys = [];
$(document).ready(function() { loadKeys(); });

function generateKey() {
    const formData = new FormData(document.getElementById('keyGenerationForm'));
    $.ajax({
        url: '/generate_key', method: 'POST', data: formData, processData: false, contentType: false,
        success: function(response) {
            if (response.success) {
                showAlert(response.message, 'success');
                $('#balanceAmount').text('₹' + response.remaining_balance.toLocaleString());
                loadKeys();
                showAlert('Generated Key: ' + response.key, 'success');
            } else { showAlert(response.message, 'error'); }
        },
        error: function() { showAlert('Error generating key!', 'error'); }
    });
}

function generateNameKey() {
    $('#keyType').val('name');
    toggleNameInput();
    showAlert('Please enter custom name and generate key!', 'success');
}

function toggleNameInput() {
    const keyType = $('#keyType').val();
    if (keyType === 'name' || keyType === 'nameRandom') {
        $('#nameInput').show();
    } else { $('#nameInput').hide(); }
}

function loadKeys() {
    $.ajax({
        url: '/get_keys', method: 'GET',
        success: function(response) {
            if (response.success) {
                userKeys = response.keys;
                renderKeysTable();
                updateKeyStats();
            }
        }
    });
}

function renderKeysTable() {
    const tbody = $('#keysTableBody');
    tbody.empty();
    userKeys.forEach((key, index) => {
        const expiresAt = new Date(key.expires_at);
        const now = new Date();
        const isExpired = expiresAt < now;
        const row = '<tr><td>' + (index + 1) + '</td><td>' + key.game + '</td><td style="font-family: monospace; color: #4CAF50;">' + key.key + '</td><td><span class="status-active">' + key.current_devices + '/' + key.max_devices + '</span></td><td>' + getDurationText(key.duration) + '</td><td><span class="' + (isExpired ? 'status-expired' : 'status-active') + '">' + (isExpired ? 'Expired' : 'Active') + '</span></td><td><button class="btn btn-danger" onclick="deleteKey(\'' + key.id + '\')" style="padding: 5px 10px; margin: 2px;">🗑️ Delete</button></td></tr>';
        tbody.append(row);
    });
}

function getDurationText(hours) {
    if (hours == '1') return '1 Hour';
    if (hours == '24') return '1 Day';
    if (hours == '168') return '7 Days';
    if (hours == '720') return '30 Days';
    if (hours == '2160') return '90 Days';
    return hours + ' Hours';
}

function updateKeyStats() {
    const now = new Date();
    const activeKeys = userKeys.filter(key => new Date(key.expires_at) >= now).length;
    const expiredKeys = userKeys.filter(key => new Date(key.expires_at) < now).length;
    $('#totalKeys').text(userKeys.length);
    $('#activeKeys').text(activeKeys);
    $('#expiredKeys').text(expiredKeys);
}

function deleteKey(keyId) {
    if (confirm('Are you sure you want to delete this key?')) {
        $.ajax({
            url: '/delete_key/' + keyId, method: 'POST',
            success: function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    loadKeys();
                } else { showAlert(response.message, 'error'); }
            }
        });
    }
}

function deleteAllKeys() {
    if (confirm('Are you sure you want to delete ALL keys? This cannot be undone!')) {
        $.ajax({
            url: '/delete_all_keys', method: 'POST',
            success: function(response) {
                if (response.success) {
                    showAlert(response.message, 'success');
                    loadKeys();
                }
            }
        });
    }
}

function deleteExpiredKeys() {
    if (confirm('Are you sure you want to delete all expired keys?')) {
        const now = new Date();
        const expiredKeys = userKeys.filter(key => new Date(key.expires_at) < now);
        if (expiredKeys.length === 0) {
            showAlert('No expired keys found!', 'error');
            return;
        }
        expiredKeys.forEach((key, index) => {
            $.ajax({
                url: '/delete_key/' + key.id, method: 'POST',
                success: function(response) {
                    if (index === expiredKeys.length - 1) {
                        showAlert(expiredKeys.length + ' expired keys deleted!', 'success');
                        loadKeys();
                    }
                }
            });
        });
    }
}

function deleteUnusedKeys() {
    if (confirm('Are you sure you want to delete all unused keys?')) {
        const unusedKeys = userKeys.filter(key => key.current_devices === 0);
        if (unusedKeys.length === 0) {
            showAlert('No unused keys found!', 'error');
            return;
        }
        unusedKeys.forEach((key, index) => {
            $.ajax({
                url: '/delete_key/' + key.id, method: 'POST',
                success: function(response) {
                    if (index === unusedKeys.length - 1) {
                        showAlert(unusedKeys.length + ' unused keys deleted!', 'success');
                        loadKeys();
                    }
                }
            });
        });
    }
}

function createReferral() {
    $.ajax({
        url: '/create_referral', method: 'POST',
        success: function(response) {
            if (response.success) {
                showAlert(response.message, 'success');
                $('#referralResult').html('<div style="background: rgba(0,0,0,0.3); padding: 15px; border-radius: 8px;"><strong>New Referral Code:</strong><br><span style="font-family: monospace; color: #4CAF50; font-size: 1.2em;">' + response.referral_code + '</span><br><button class="btn btn-info" onclick="copyReferralCode(\'' + response.referral_code + '\')" style="margin-top: 10px;">📋 Copy Code</button></div>');
            } else { showAlert(response.message, 'error'); }
        }
    });
}

function copyReferralCode(code) {
    navigator.clipboard.writeText(code).then(() => {
        showAlert('Referral code copied to clipboard!', 'success');
    });
}

function addBalance() {
    const targetUser = $('#targetUser').val();
    const amount = $('#addBalanceAmount').val();
    if (!targetUser || !amount) {
        showAlert('Please fill all fields!', 'error');
        return;
    }
    $.ajax({
        url: '/add_balance', method: 'POST',
        data: { username: targetUser, amount: amount },
        success: function(response) {
            if (response.success) {
                showAlert(response.message, 'success');
                $('#targetUser').val('');
                $('#addBalanceAmount').val('');
            } else { showAlert(response.message, 'error'); }
        }
    });
}

function toggleKeysTable() {
    $('#keysTable').toggle();
}
</script>
"""

# Routes
@app.route('/')
def index():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    content = render_template_string(LOGIN_TEMPLATE)
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        if username in users_data and check_password_hash(users_data[username]['password'], password):
            session['username'] = username
            session['role'] = users_data[username]['role']
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid credentials!', 'error')
    
    content = render_template_string(LOGIN_TEMPLATE)
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        referral_code = request.form['referral_code']
        
        if username in users_data:
            flash('Username already exists!', 'error')
        elif password != confirm_password:
            flash('Passwords do not match!', 'error')
        elif not referral_code or referral_code not in referrals_data:
            flash('Valid referral code is required!', 'error')
        elif referrals_data[referral_code]['used']:
            flash('Referral code already used!', 'error')
        else:
            users_data[username] = {
                "password": generate_password_hash(password),
                "role": "RESELLER",
                "balance": 0,
                "created_at": datetime.now().isoformat(),
                "status": "active",
                "referred_by": referrals_data[referral_code]['created_by']
            }
            
            referrals_data[referral_code]['used'] = True
            referrals_data[referral_code]['used_by'] = username
            referrals_data[referral_code]['used_at'] = datetime.now().isoformat()
            
            flash('Account created successfully! Please login.', 'success')
            return redirect(url_for('login'))
    
    content = render_template_string(REGISTER_TEMPLATE)
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        return redirect(url_for('login'))
    
    user_data = users_data[session['username']]
    user_keys = [key for key in keys_data.values() if key.get('owner') == session['username']]
    
    total_keys = len(user_keys)
    now = datetime.now()
    active_keys = len([key for key in user_keys if datetime.fromisoformat(key['expires_at']) >= now])
    expired_keys = len([key for key in user_keys if datetime.fromisoformat(key['expires_at']) < now])
    
    content = render_template_string(DASHBOARD_TEMPLATE, 
                                   user=user_data, 
                                   username=session['username'],
                                   role=session['role'],
                                   settings=settings_data,
                                   stats={
                                       'total_keys': total_keys,
                                       'active_keys': active_keys,
                                       'expired_keys': expired_keys
                                   })
    return render_template_string(BASE_TEMPLATE, content=content)

@app.route('/generate_key', methods=['POST'])
def generate_key():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    game = request.form['game']
    duration = request.form['duration']
    devices = request.form['devices']
    key_type = request.form['key_type']
    custom_name = request.form.get('custom_name', '')
    
    user_data = users_data[session['username']]
    price = settings_data['prices'][duration]
    
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
    key_id = str(len(keys_data) + 1)
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
    
    keys_data[key_id] = new_key
    users_data[session['username']]['balance'] -= price
    
    return jsonify({
        'success': True, 
        'message': 'Key generated successfully!',
        'key': generated_key,
        'remaining_balance': users_data[session['username']]['balance']
    })

@app.route('/create_referral', methods=['POST'])
def create_referral():
    if 'username' not in session or session['role'] != 'OWNER':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    referral_code = generate_referral_code()
    referrals_data[referral_code] = {
        'code': referral_code,
        'created_by': session['username'],
        'created_at': datetime.now().isoformat(),
        'used': False,
        'used_by': None,
        'used_at': None
    }
    
    return jsonify({
        'success': True,
        'message': 'Referral code created successfully!',
        'referral_code': referral_code
    })

@app.route('/get_keys')
def get_keys():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    user_keys = [key for key in keys_data.values() if key.get('owner') == session['username']]
    return jsonify({'success': True, 'keys': user_keys})

@app.route('/delete_key/<key_id>', methods=['POST'])
def delete_key(key_id):
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    if key_id in keys_data and keys_data[key_id].get('owner') == session['username']:
        del keys_data[key_id]
        return jsonify({'success': True, 'message': 'Key deleted successfully!'})
    
    return jsonify({'success': False, 'message': 'Key not found or unauthorized'})

@app.route('/delete_all_keys', methods=['POST'])
def delete_all_keys():
    if 'username' not in session:
        return jsonify({'success': False, 'message': 'Not logged in'})
    
    keys_to_delete = [key_id for key_id, key in keys_data.items() if key.get('owner') == session['username']]
    for key_id in keys_to_delete:
        del keys_data[key_id]
    
    return jsonify({'success': True, 'message': f'{len(keys_to_delete)} keys deleted!'})

@app.route('/add_balance', methods=['POST'])
def add_balance():
    if 'username' not in session or session['role'] != 'OWNER':
        return jsonify({'success': False, 'message': 'Unauthorized'})
    
    target_user = request.form['username']
    amount = float(request.form['amount'])
    
    if target_user in users_data:
        users_data[target_user]['balance'] += amount
        return jsonify({'success': True, 'message': f'Balance added successfully!'})
    
    return jsonify({'success': False, 'message': 'User not found!'})

@app.route('/logout')
def logout():
    session.clear()
    flash('Logged out successfully!', 'success')
    return redirect(url_for('login'))

@app.errorhandler(404)
def not_found_error(error):
    content = '<div style="text-align: center; padding: 100px;"><h1>404 - Page Not Found</h1><a href="/" class="btn btn-primary">Go Home</a></div>'
    return render_template_string(BASE_TEMPLATE, content=content), 404

@app.errorhandler(500)
def internal_error(error):
    content = '<div style="text-align: center; padding: 100px;"><h1>500 - Internal Server Error</h1><a href="/" class="btn btn-primary">Go Home</a></div>'
    return render_template_string(BASE_TEMPLATE, content=content), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(debug=False, host='0.0.0.0', port=port)
