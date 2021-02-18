from flask import Flask, render_template, request
import os
import database.db_connector as db
from datetime import date
from werkzeug.utils import secure_filename
import auth

UPLOAD_FOLDER = 'static/img/'

# Configuration
app = Flask(__name__)
db_conn = db.connect_to_database()
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config.from_mapping(SECRET_KEY='dev')   # TODO: change to random bytes when deploying!
app.register_blueprint(auth.bp)

# Routes
@app.route('/', methods=['GET', 'POST'])
def root():

    if request.method == 'GET':

        # get listings
        query = "SELECT listingID, bidID, make, model, year, reserve, expirationDate FROM listings;"
        cursor = db.execute_query(db_connection=db_conn, query=query)
        listings = cursor.fetchall()

        # get features
        query = "SELECT featureID, carFeature FROM features;"
        cursor = db.execute_query(db_connection=db_conn, query=query)
        features = cursor.fetchall()

        # get listings_features
        query = "SELECT listingID, featureID FROM FeaturesListings;"
        cursor = db.execute_query(db_connection=db_conn, query=query)
        listings_features = cursor.fetchall()

        # get bids
        query = "SELECT bidID, bidAmt FROM bids;"
        cursor = db.execute_query(db_connection=db_conn, query=query)
        bids = cursor.fetchall()

        # get photos
        query = "SELECT listingID, photoPath FROM photos;"
        cursor = db.execute_query(db_connection=db_conn, query=query)
        photos = cursor.fetchall()

    return render_template('main.j2', listings=listings, listings_features=listings_features, features=features, bids=bids, photos=photos)

@app.route('/submit-listing', methods=['GET', 'POST'])
@auth.login_required
def submit_listing():

    # display standard features
    query = "SELECT carFeature FROM features WHERE featureID BETWEEN 1 AND 4;"
    cursor = db.execute_query(db_connection=db_conn, query=query)
    features = cursor.fetchall()

    if request.method == 'POST':

        # get form data
        data = request.form

        # get userID from users table using email
        query = "SELECT userID FROM users WHERE email = %s;"
        cursor = db.execute_query(
            db_connection=db_conn, query=query, query_params=(data['email'],))
        usr = cursor.fetchall()[0]['userID']

        # get car and auction information
        make = data['make']
        model = data['model']
        year = int(data['year'])
        mileage = int(data['mileage'])
        reserve = int(data['reserve'])
        list_date = date.today()
        expiration = data['expiration']

        # save photo
        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)

        # insert listing info
        query = "INSERT INTO listings (userID, make, model, year, mileage, reserve, listDate, expirationDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        cursor = db.execute_query(
            db_connection=db_conn, query=query, query_params=(usr, make, model, year, mileage, reserve, list_date, expiration))
        list_id = cursor.lastrowid

        # insert photo path for listing
        query = "INSERT INTO photos (photoPath, listingID) VALUES (%s, %s);"
        db.execute_query(db_connection=db_conn, query=query,
                         query_params=(filepath, list_id))

        # get listing features
        sel_features = request.form.getlist('features')  # selected features
        usr_feature = request.form['usrfeature']  # inputted feature

        # if included, add inputted feature to table
        if len(usr_feature) != 0:

            query = "INSERT INTO features (carFeature) VALUES (%s);"
            db.execute_query(
                db_connection=db_conn, query=query, query_params=(usr_feature,))
            sel_features.append(usr_feature)

        # formatting for query params
        format_str = ','.join(['%s'] * len(sel_features))

        # get all feature ids for this listing
        query = "SELECT featureID FROM features WHERE carFeature IN (" + \
            format_str + ");"
        cursor = db.execute_query(
            db_connection=db_conn, query=query, query_params=tuple(sel_features))
        feature_ids = cursor.fetchall()

        # formatting for query params
        listing_features = []
        for feature in feature_ids:
            listing_features.append((list_id, feature['featureID']))

        # insert into FeaturesListings table
        query = "INSERT INTO FeaturesListings (listingID, featureID) VALUES (%s, %s);"
        db.execute_many(
            db_connection=db_conn, query=query, query_params=listing_features)

    return render_template('submit_listing.j2', features=features)

@ app.route('/profile', methods=['GET', 'POST'])
def profile():

    if request.method == 'GET':

        # get user info
        query = "SELECT firstName, lastName, email, userName, password, dateJoined FROM users WHERE userID = 1;"
        cursor = db.execute_query(db_connection=db_conn, query=query)
        usr = cursor.fetchall()[0]

        # get user listings

        # get user bids

    return render_template('profile.j2', user=usr)

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112))
    app.run(port=port, debug=True)
