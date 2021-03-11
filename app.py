from flask import Flask, render_template, request, redirect, g, url_for, flash
import os
import database.db_connector as db
from datetime import date
from werkzeug.utils import secure_filename
import auth
from validation import validate_new_listing, validate_photo

UPLOAD_FOLDER = 'static/img/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# TODO: change to random bytes when deploying!
app.config.from_mapping(SECRET_KEY='dev')
app.register_blueprint(auth.bp)


@app.route('/', methods=['GET', 'POST'])
def root():
    db_conn = db.connect_to_database()

    query = "SELECT featureID, carFeature FROM Features;"
    features = db.execute_query(
        db_connection=db_conn, query=query).fetchall()

    query = "SELECT listingID, featureID FROM FeaturesListings;"
    listings_features = db.execute_query(
        db_connection=db_conn, query=query).fetchall()

    query = "SELECT bidID, bidAmt FROM Bids;"
    bids = db.execute_query(db_connection=db_conn, query=query).fetchall()

    query = "SELECT listingID, photoPath FROM Photos;"
    photos = db.execute_query(
        db_connection=db_conn, query=query).fetchall()

    if request.method == 'GET':
        query = "SELECT * FROM Listings WHERE userID IS NOT NULL AND expirationDate >= NOW();"
        listings = db.execute_query(
            db_connection=db_conn, query=query).fetchall()

    elif request.method == 'POST':
        search_query = f"%{request.form['searchquery']}%"
        query = "SELECT * FROM Listings WHERE listingID IN (SELECT listingID FROM (SELECT L.listingID, CONCAT_WS(' ', L.year, L.make, L.model, F.carFeature) AS carInfo FROM Listings L INNER JOIN FeaturesListings FL ON L.listingID = FL.listingID INNER JOIN Features F ON FL.featureID = F.featureID) AS tmp WHERE tmp.carInfo LIKE %s) AND userID IS NOT NULL AND expirationDate >= NOW();"
        listings = db.execute_query(db_connection=db_conn, query=query,
                                    query_params=(search_query,)).fetchall()

    return render_template('main.j2', listings=listings, listings_features=listings_features, features=features, bids=bids, photos=photos)


@app.route('/place-bid/<int:list_id>', methods=['GET', 'POST'])
def place_bid(list_id):
    if request.method == 'POST':
        bid_amt = request.form['bid']
        bid_date = date.today()

        db_conn = db.connect_to_database()

        query = "INSERT INTO Bids (userID, listingID, bidAmt, bidDate) VALUES (%s, %s, %s, %s)"
        cursor = db.execute_query(db_connection=db_conn, query=query,
                                  query_params=(g.user['userID'], list_id, bid_amt, bid_date))
        bid_id = cursor.lastrowid

        query = "UPDATE Listings SET bidID = %s WHERE listingID = %s;"
        db.execute_query(db_connection=db_conn, query=query,
                         query_params=(bid_id, list_id))

    return redirect('/')


@app.route('/submit-listing', methods=['GET', 'POST'])
@auth.login_required
def submit_listing():
    # display standard features on form
    db_conn = db.connect_to_database()
    query = "SELECT carFeature FROM Features WHERE featureID BETWEEN 1 AND 4;"
    features = db.execute_query(db_connection=db_conn, query=query).fetchall()

    if request.method == 'POST':
        data = request.form
        error = validate_new_listing(data)

        if error:
            flash(error)
            return render_template('submit_listing.j2', features=features)

        # validated, parse form and add listing
        make = data['make']
        model = data['model']
        year = int(data['year'])
        mileage = int(data['mileage'])
        reserve = int(data['reserve']) if data['reserve'] != '' else 0
        list_date = date.today()
        expiration = data['expiration']

        # user photo stored at static/img/ otherwise default photo used
        photo = request.files['photo']
        filepath = "./static/img/No_image_available.jpg"
        if validate_photo(photo): 
            filename = secure_filename(photo.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            photo.save(filepath)

        query = "INSERT INTO Listings (userID, make, model, year, mileage, reserve, listDate, expirationDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        cursor = db.execute_query(
            db_connection=db_conn, query=query, query_params=(g.user['userID'], make, model, year, mileage, reserve, list_date, expiration))
        list_id = cursor.lastrowid

        query = "INSERT INTO Photos (photoPath, listingID) VALUES (%s, %s);"
        db.execute_query(db_connection=db_conn, query=query,
                         query_params=(filepath, list_id))

        # handling of features input
        sel_features = request.form.getlist('features')  # selected features
        usr_feature = request.form['usrfeature']  # feature inputted by user

        # determine whether user creating already existing feature
        if len(usr_feature) != 0:
            query = "SELECT * FROM Features WHERE carFeature=%s"
            feature_dups = db.execute_query(
                db_connection=db_conn,
                query=query,
                query_params=(usr_feature,)).fetchall()

            # no duplicate, add new feature
            if len(feature_dups) == 0:
                query = "INSERT INTO Features (carFeature) VALUES (%s);"
                db.execute_query(
                    db_connection=db_conn,
                    query=query,
                    query_params=(usr_feature,))
                sel_features.append(usr_feature)
            # duplicate, associate existing feature with new listing
            else:
                sel_features.append(feature_dups[0]['carFeature']) 

        # add all features associated with listing into featuresListings
        if len(sel_features) > 0:
            format_str = ','.join(['%s'] * len(sel_features))
            query = "SELECT featureID FROM Features WHERE carFeature IN (" + \
                format_str + ");"
            feature_ids = db.execute_query(db_connection=db_conn, query=query, query_params=tuple(sel_features)).fetchall()

            # insert all feature ids for this listing
            listing_features = [(list_id, feature_id['featureID'])
                                for feature_id in feature_ids]
            query = "INSERT INTO FeaturesListings (listingID, featureID) VALUES (%s, %s);"
            db.execute_many(
                db_connection=db_conn, query=query, query_params=listing_features)

        return redirect(url_for('root'))

    return render_template('submit_listing.j2', features=features)


@ app.route('/profile', methods=['GET', 'POST'])
def profile():
    db_conn = db.connect_to_database()

    # requesting user profile stats
    if request.method == "GET":
        # gather user's active listings
        user_id = (g.user['userID'], )
        query = \
            "SELECT l.listingID, l.year, l.make, l.model, b.bidAmt, l.reserve, l.expirationDate FROM Listings l\
            LEFT JOIN Bids b ON l.bidID = b.bidID \
            WHERE l.userID = %s;"
        active_listings = db.execute_query(db_conn, query, user_id)

        # gather user's bid history
        query = \
            "SELECT b.bidDate, l.year, l.make, l.model, b.bidAmt FROM Bids b \
            INNER JOIN Listings l ON b.listingID = l.listingID \
            WHERE b.userID = %s;"
        bid_history = db.execute_query(db_conn, query, user_id)

        return render_template('profile.j2', active_listings=active_listings, bid_history=bid_history)

    # user requesting listing deletion
    elif request.method == "POST":
        # gather relevant data to delete listing
        listing_to_delete = request.form['listingID']
        delete_query = 'DELETE FROM FeaturesListings WHERE listingID = %s;'
        update_query = 'UPDATE Listings SET Listings.userID = NULL WHERE listingID = %s;'

        db.execute_query(db_conn, delete_query, (listing_to_delete,))
        db.execute_query(db_conn, update_query, (listing_to_delete,))

        return redirect(url_for('profile'))


# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112))
    app.run(port=port, debug=True)
