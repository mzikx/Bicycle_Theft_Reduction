# ============================================================
# PROFESSIONAL BICYCLE THEFT MANAGEMENT SYSTEM
# ============================================================
# FEATURES:
# - Public User Registration/Login
# - Separate Police Login Portal
# - Police Verification System
# - Admin Police Officer Creation
# - Bicycle Registration
# - Theft Reporting
# - Investigation Tracking
# - Police Investigation Dashboard
# - Duplicate Prevention
# - Weekly / Monthly / Yearly Filtering
# - Professional CSS Design
# - Error Handling
# - Bicycle Image Uploads
# ============================================================

# -----------------------------
# IMPORT REQUIRED LIBRARIES
# -----------------------------

from flask import (
    Flask,
    render_template_string,
    request,
    redirect,
    session,
    flash,
    send_from_directory
)

from flask_sqlalchemy import SQLAlchemy

from werkzeug.security import (
    generate_password_hash,
    check_password_hash
)

from werkzeug.utils import secure_filename

from datetime import datetime, timedelta

import os

# -----------------------------
# FLASK CONFIGURATION
# -----------------------------

app = Flask(__name__)

app.secret_key = "secretkey"

# SQLite Database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///bicycle_theft.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Upload folder
app.config['UPLOAD_FOLDER'] = 'uploads'

# Automatically create uploads folder
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialise database
# SQLAlchemy manages all database communication

db = SQLAlchemy(app)

# ============================================================
# DATABASE MODELS
# ============================================================

# ------------------------------------------------
# USER TABLE
# Stores public users and police accounts
# ------------------------------------------------

class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    fullname = db.Column(db.String(100))

    email = db.Column(db.String(100), unique=True)

    password = db.Column(db.String(255))

    # public / police / admin_police
    role = db.Column(db.String(30), default='public')

    # Police verification information
    badge_number = db.Column(db.String(50), unique=True)

    police_station = db.Column(db.String(100))

    verified = db.Column(db.Boolean, default=False)

# ------------------------------------------------
# BICYCLE TABLE
# Stores bicycle information
# ------------------------------------------------

class Bicycle(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    mpn = db.Column(db.String(100))

    brand = db.Column(db.String(100))

    model = db.Column(db.String(100))

    bike_type = db.Column(db.String(100))

    wheel_size = db.Column(db.String(50))

    colour = db.Column(db.String(100))

    gears = db.Column(db.String(50))

    brake_type = db.Column(db.String(100))

    suspension = db.Column(db.String(100))

    frame_number = db.Column(db.String(100), unique=True)

    image = db.Column(db.String(255))

# ------------------------------------------------
# THEFT REPORT TABLE
# Stores theft reports and investigations
# ------------------------------------------------

class TheftReport(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    bicycle_id = db.Column(db.Integer)

    location = db.Column(db.String(255))

    description = db.Column(db.Text)

    status = db.Column(
        db.String(100),
        default='Investigation Open'
    )

    date_reported = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

# ============================================================
# GLOBAL CSS STYLING
# ============================================================

STYLE = """

<style>

*{
    margin:0;
    padding:0;
    box-sizing:border-box;
    font-family:Arial;
}

body{
    background:#f4f7fb;
}

.navbar{
    background:#0d1b2a;
    padding:20px 40px;
    display:flex;
    justify-content:space-between;
    align-items:center;
}

.logo{
    color:white;
    font-size:28px;
    font-weight:bold;
}

.nav-links a{
    color:white;
    text-decoration:none;
    margin-left:20px;
    font-weight:bold;
}

.nav-links a:hover{
    color:#00b4d8;
}

.hero{
    min-height:100vh;

    background:
    linear-gradient(rgba(0,0,0,0.6),
    rgba(0,0,0,0.6)),

    url('https://images.unsplash.com/photo-1511994298241-608e28f14fde?q=80&w=1974&auto=format&fit=crop');

    background-size:cover;
    background-position:center;

    display:flex;
    justify-content:center;
    align-items:center;

    text-align:center;

    color:white;

    padding:40px;
}

.hero h1{
    font-size:65px;
    margin-bottom:20px;
}

.hero p{
    font-size:22px;
    margin-bottom:30px;
}

.btn{
    padding:14px 28px;
    border:none;
    border-radius:8px;
    background:#00b4d8;
    color:white;
    text-decoration:none;
    font-size:16px;
    cursor:pointer;
}

.btn:hover{
    background:#0096c7;
}

.form-container{

    width:500px;

    margin:50px auto;

    background:white;

    padding:40px;

    border-radius:15px;

    box-shadow:0 5px 20px rgba(0,0,0,0.1);

}

.form-container h2{
    text-align:center;
    margin-bottom:30px;
}

.form-group{
    margin-bottom:20px;
}

.form-group input,
.form-group select,
.form-group textarea{

    width:100%;

    padding:14px;

    border:1px solid #ccc;

    border-radius:8px;
}

.container{
    width:90%;
    max-width:1200px;
    margin:auto;
    padding:40px 0;
}

.cards{
    display:grid;

    grid-template-columns:
    repeat(auto-fit, minmax(320px,1fr));

    gap:25px;
}

.card{
    background:white;
    border-radius:15px;
    overflow:hidden;
    box-shadow:0 4px 15px rgba(0,0,0,0.1);
}

.card img{
    width:100%;
    height:220px;
    object-fit:cover;
}

.card-body{
    padding:20px;
}

.card-body h3{
    margin-bottom:10px;
}

.card-body p{
    margin-bottom:8px;
}

.flash{
    background:#ffdddd;
    color:#900;
    padding:15px;
    border-radius:8px;
    margin-bottom:20px;
    text-align:center;
}

.footer{
    background:#0d1b2a;
    color:white;
    text-align:center;
    padding:20px;
    margin-top:50px;
}

</style>

"""

# ============================================================
# SERVE UPLOADED IMAGES
# ============================================================

@app.route('/uploads/<filename>')
def uploaded_file(filename):

    return send_from_directory(
        app.config['UPLOAD_FOLDER'],
        filename
    )

# ============================================================
# HOME PAGE
# ============================================================

@app.route('/')
def home():

    return render_template_string(STYLE + '''

    <div class="navbar">

        <div class="logo">
            BikeSecure
        </div>

        <div class="nav-links">

            <a href="/">Home</a>

            <a href="/register">Register</a>

            <a href="/login">Public Login</a>

            <a href="/police_login">Police Login</a>

        </div>

    </div>

    <section class="hero">

        <div>

            <h1>Protect Your Bicycle</h1>

            <p>
                Register bikes, report thefts,
                and track investigations.
            </p>

            <a href="/register" class="btn">
                Get Started
            </a>

        </div>

    </section>

    <div class="footer">
        Bicycle Theft Reduction System © 2026
    </div>

    ''')

# ============================================================
# REGISTER USER
# ============================================================

@app.route('/register', methods=['GET', 'POST'])
def register():

    if request.method == 'POST':

        try:

            fullname = request.form['fullname']

            email = request.form['email']

            password = request.form['password']

            existing_user = User.query.filter_by(
                email=email
            ).first()

            if existing_user:

                flash('Email already registered')

                return redirect('/register')

            hashed_password = generate_password_hash(password)

            user = User(
                fullname=fullname,
                email=email,
                password=hashed_password,
                role='public'
            )

            db.session.add(user)

            db.session.commit()

            flash('Registration Successful')

            return redirect('/login')

        except Exception as e:

            db.session.rollback()

            return f"Error: {str(e)}"

    return render_template_string(STYLE + '''

    <div class="form-container">

        <h2>Create Public Account</h2>

        <form method="POST" onsubmit="return validateForm()">

            <div class="form-group">
                <input type="text"
                name="fullname"
                placeholder="Full Name"
                required>
            </div>

            <div class="form-group">
                <input type="email"
                name="email"
                placeholder="Email"
                required>
            </div>

            <div class="form-group">
                <input type="password"
                id="password"
                name="password"
                placeholder="Password"
                required>
            </div>

            <button class="btn">
                Register
            </button>

        </form>

    </div>

    <script>

    function validateForm() {

        let password =
        document.getElementById("password").value;

        if(password.length < 6){

            alert(
            "Password must contain at least 6 characters"
            );

            return false;
        }

        return true;
    }

    </script>

    ''')

# ============================================================
# PUBLIC LOGIN
# ============================================================

@app.route('/login', methods=['GET', 'POST'])
def login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        user = User.query.filter_by(
            email=email
        ).first()

        if not user:

            flash('Account does not exist')

            return redirect('/login')

        if user.role != 'public':

            flash('Use Police Login Portal')

            return redirect('/police_login')

        if not check_password_hash(user.password, password):

            flash('Incorrect password')

            return redirect('/login')

        session['user_id'] = user.id

        session['role'] = user.role

        return redirect('/dashboard')

    return render_template_string(STYLE + '''

    <section class="hero">

        <div class="form-container">

            <h2>Public Login</h2>

            <form method="POST">

                <div class="form-group">
                    <input type="email"
                    name="email"
                    placeholder="Email"
                    required>
                </div>

                <div class="form-group">
                    <input type="password"
                    name="password"
                    placeholder="Password"
                    required>
                </div>

                <button class="btn">
                    Login
                </button>

            </form>

        </div>

    </section>

    ''')

# ============================================================
# POLICE LOGIN
# ============================================================

@app.route('/police_login', methods=['GET', 'POST'])
def police_login():

    if request.method == 'POST':

        email = request.form['email']

        password = request.form['password']

        badge_number = request.form['badge_number']

        officer = User.query.filter_by(
            email=email,
            badge_number=badge_number
        ).first()

        if not officer:

            flash('Police account not found')

            return redirect('/police_login')

        if officer.role not in ['police', 'admin_police']:

            flash('Access denied')

            return redirect('/police_login')

        if not check_password_hash(
            officer.password,
            password
        ):

            flash('Incorrect password')

            return redirect('/police_login')

        if not officer.verified:

            flash('Officer account pending verification')

            return redirect('/police_login')

        session['user_id'] = officer.id
        session['role'] = officer.role

        return redirect('/police_dashboard')

    return render_template_string(STYLE + '''

    <section class="hero">

        <div class="form-container">

            <h2>Police Officer Login</h2>

            <form method="POST">

                <div class="form-group">

                    <input type="email"
                    name="email"
                    placeholder="Police Email"
                    required>

                </div>

                <div class="form-group">

                    <input type="text"
                    name="badge_number"
                    placeholder="Badge Number"
                    required>

                </div>

                <div class="form-group">

                    <input type="password"
                    name="password"
                    placeholder="Password"
                    required>

                </div>

                <button class="btn">
                    Officer Login
                </button>

            </form>

        </div>

    </section>

    ''')

# ============================================================
# PUBLIC DASHBOARD
# ============================================================

@app.route('/dashboard')
def dashboard():

    if 'user_id' not in session:
        return redirect('/login')

    bikes = Bicycle.query.filter_by(
        user_id=session['user_id']
    ).all()

    bike_html = ""

    for bike in bikes:

        report = TheftReport.query.filter_by(
            bicycle_id=bike.id
        ).first()

        status = "Not Reported"

        if report:
            status = report.status

        bike_html += f'''

        <div class="card">

            <img src="/uploads/{bike.image}">

            <div class="card-body">

                <h3>{bike.brand} {bike.model}</h3>

                <p><b>Type:</b> {bike.bike_type}</p>

                <p><b>Colour:</b> {bike.colour}</p>

                <p><b>Frame:</b> {bike.frame_number}</p>

                <p><b>Status:</b> {status}</p>

                <br>

                <a class="btn"
                href="/report_theft/{bike.id}">
                Report Theft
                </a>

            </div>

        </div>

        '''

    return render_template_string(STYLE + f'''

    <div class="container">

        <h1>Your Registered Bicycles</h1>

        <br>

        <a href="/register_bike" class="btn">
            Register Bicycle
        </a>

        <a href="/logout" class="btn">
            Logout
        </a>

        <br><br>

        <div class="cards">

            {bike_html}

        </div>

    </div>

    ''')

# ============================================================
# REGISTER BICYCLE
# ============================================================

@app.route('/register_bike', methods=['GET', 'POST'])
def register_bike():

    if 'user_id' not in session:
        return redirect('/login')

    if request.method == 'POST':

        try:

            frame_number = request.form['frame_number']

            existing_bike = Bicycle.query.filter_by(
                frame_number=frame_number
            ).first()

            if existing_bike:

                flash('This bicycle is already registered')

                return redirect('/register_bike')

            image = request.files['image']

            filename = secure_filename(image.filename)

            image.save(
                os.path.join(
                    app.config['UPLOAD_FOLDER'],
                    filename
                )
            )

            bike = Bicycle(

                user_id=session['user_id'],

                mpn=request.form['mpn'],

                brand=request.form['brand'],

                model=request.form['model'],

                bike_type=request.form['bike_type'],

                wheel_size=request.form['wheel_size'],

                colour=request.form['colour'],

                gears=request.form['gears'],

                brake_type=request.form['brake_type'],

                suspension=request.form['suspension'],

                frame_number=frame_number,

                image=filename
            )

            db.session.add(bike)

            db.session.commit()

            flash('Bicycle Registered Successfully')

            return redirect('/dashboard')

        except Exception as e:

            db.session.rollback()

            return f"Error: {str(e)}"

    return render_template_string(STYLE + '''

    <div class="form-container">

        <h2>Register Bicycle</h2>

        <form method="POST"
        enctype="multipart/form-data">

            <div class="form-group">
                <input type="text"
                name="mpn"
                placeholder="Manufacturer Part Number"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="brand"
                placeholder="Brand"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="model"
                placeholder="Model"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="bike_type"
                placeholder="Bike Type"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="wheel_size"
                placeholder="Wheel Size"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="colour"
                placeholder="Colour"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="gears"
                placeholder="Number of Gears"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="brake_type"
                placeholder="Brake Type"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="suspension"
                placeholder="Suspension"
                required>
            </div>

            <div class="form-group">
                <input type="text"
                name="frame_number"
                placeholder="Frame Number"
                required>
            </div>

            <div class="form-group">
                <input type="file"
                name="image"
                required>
            </div>

            <button class="btn">
                Register Bicycle
            </button>

        </form>

    </div>

    ''')

# ============================================================
# REPORT THEFT
# ============================================================

@app.route('/report_theft/<int:bike_id>',
methods=['GET', 'POST'])
def report_theft(bike_id):

    if request.method == 'POST':

        report = TheftReport(

            bicycle_id=bike_id,

            location=request.form['location'],

            description=request.form['description']
        )

        db.session.add(report)

        db.session.commit()

        return redirect('/dashboard')

    return render_template_string(STYLE + '''

    <div class="form-container">

        <h2>Report Stolen Bicycle</h2>

        <form method="POST">

            <div class="form-group">

                <input type="text"
                name="location"
                placeholder="Theft Location"
                required>

            </div>

            <div class="form-group">

                <textarea name="description"
                placeholder="Description"
                required></textarea>

            </div>

            <button class="btn">
                Submit Report
            </button>

        </form>

    </div>

    ''')

# ============================================================
# POLICE DASHBOARD
# ============================================================

@app.route('/police_dashboard')
def police_dashboard():

    if 'role' not in session:
        return redirect('/login')

    if session['role'] not in ['police', 'admin_police']:
        return redirect('/dashboard')

    filter_type = request.args.get('filter')

    reports = TheftReport.query.order_by(
        TheftReport.date_reported.desc()
    )

    if filter_type == 'week':

        reports = reports.filter(
            TheftReport.date_reported >=
            datetime.utcnow() - timedelta(days=7)
        )

    elif filter_type == 'month':

        reports = reports.filter(
            TheftReport.date_reported >=
            datetime.utcnow() - timedelta(days=30)
        )

    elif filter_type == 'year':

        reports = reports.filter(
            TheftReport.date_reported >=
            datetime.utcnow() - timedelta(days=365)
        )

    reports = reports.all()

    report_html = ""

    for report in reports:

        bike = Bicycle.query.get(report.bicycle_id)

        report_html += f'''

        <div class="card">

            <img src="/uploads/{bike.image}">

            <div class="card-body">

                <h3>{bike.brand} {bike.model}</h3>

                <p><b>Location:</b> {report.location}</p>

                <p><b>Status:</b> {report.status}</p>

                <p><b>Date:</b> {report.date_reported}</p>

                <br>

                <a class="btn"
                href="/update_status/{report.id}">
                Update Investigation
                </a>

            </div>

        </div>

        '''

    return render_template_string(STYLE + f'''

    <div class="container">

        <h1>Police Investigation Dashboard</h1>

        <br>

        <a href="/police_dashboard?filter=week" class="btn">
        This Week
        </a>

        <a href="/police_dashboard?filter=month" class="btn">
        This Month
        </a>

        <a href="/police_dashboard?filter=year" class="btn">
        This Year
        </a>

        <a href="/create_police" class="btn">
            Create Police Account
        </a>

        <a href="/logout" class="btn">
            Logout
        </a>

        <br><br>

        <div class="cards">

            {report_html}

        </div>

    </div>

    ''')

# ============================================================
# CREATE POLICE ACCOUNT
# ============================================================

@app.route('/create_police',
methods=['GET', 'POST'])
def create_police():

    if session.get('role') != 'admin_police':
        return "Access Denied"

    if request.method == 'POST':

        try:

            existing_officer = User.query.filter_by(
                email=request.form['email']
            ).first()

            if existing_officer:

                flash('Officer already exists')

                return redirect('/create_police')

            officer = User(

                fullname=request.form['fullname'],

                email=request.form['email'],

                password=generate_password_hash(
                    request.form['password']
                ),

                role='police',

                badge_number=request.form['badge_number'],

                police_station=request.form['police_station'],

                verified=True
            )

            db.session.add(officer)

            db.session.commit()

            flash('Police officer created successfully')

            return redirect('/police_dashboard')

        except Exception as e:

            db.session.rollback()

            return str(e)

    return render_template_string(STYLE + '''

    <div class="form-container">

        <h2>Create Police Officer</h2>

        <form method="POST">

            <div class="form-group">

                <input type="text"
                name="fullname"
                placeholder="Officer Full Name"
                required>

            </div>

            <div class="form-group">

                <input type="email"
                name="email"
                placeholder="Police Email"
                required>

            </div>

            <div class="form-group">

                <input type="text"
                name="badge_number"
                placeholder="Badge Number"
                required>

            </div>

            <div class="form-group">

                <input type="text"
                name="police_station"
                placeholder="Police Station"
                required>

            </div>

            <div class="form-group">

                <input type="password"
                name="password"
                placeholder="Password"
                required>

            </div>

            <button class="btn">
                Create Officer
            </button>

        </form>

    </div>

    ''')

# ============================================================
# UPDATE INVESTIGATION STATUS
# ============================================================

@app.route('/update_status/<int:report_id>',
methods=['GET', 'POST'])
def update_status(report_id):

    if session.get('role') not in ['police', 'admin_police']:
        return redirect('/login')

    report = TheftReport.query.get(report_id)

    if request.method == 'POST':

        report.status = request.form['status']

        db.session.commit()

        return redirect('/police_dashboard')

    return render_template_string(STYLE + '''

    <div class="form-container">

        <h2>Update Investigation</h2>

        <form method="POST">

            <div class="form-group">

                <select name="status">

                    <option>
                    Investigation Open
                    </option>

                    <option>
                    Under Investigation
                    </option>

                    <option>
                    Bicycle Recovered
                    </option>

                    <option>
                    Investigation Closed
                    </option>

                </select>

            </div>

            <button class="btn">
                Update Status
            </button>

        </form>

    </div>

    ''')

# ============================================================
# LOGOUT
# ============================================================

@app.route('/logout')
def logout():

    session.clear()

    return redirect('/')

# ============================================================
# START APPLICATION
# ============================================================

if __name__ == '__main__':

    with app.app_context():

        db.create_all()

        # Create default admin police account
        admin_exists = User.query.filter_by(
            email='admin@police.com'
        ).first()

        if not admin_exists:

            admin = User(

                fullname='Police Administrator',

                email='admin@police.com',

                password=generate_password_hash('admin123'),

                role='admin_police',

                badge_number='ADMIN001',

                police_station='Central Police HQ',

                verified=True
            )

            db.session.add(admin)

            db.session.commit()


