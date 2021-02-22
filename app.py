from flask import Flask, render_template, request, redirect, g, url_for
import os
import database.db_connector as db
from datetime import date
from werkzeug.utils import secure_filename
import auth

UPLOAD_FOLDER = 'static/img/'

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
# TODO: change to random bytes when deploying!
app.config.from_mapping(SECRET_KEY='dev')
app.register_blueprint(auth.bp)


@app.route('/', methods=['GET', 'POST'])
def root():
    db_conn = db.connect_to_database()

    query = "SELECT featureID, carFeature FROM features;"
    features = db.execute_query(
        db_connection=db_conn, query=query).fetchall()

    query = "SELECT listingID, featureID FROM FeaturesListings;"
    listings_features = db.execute_query(
        db_connection=db_conn, query=query).fetchall()

    query = "SELECT bidID, bidAmt FROM bids;"
    bids = db.execute_query(db_connection=db_conn, query=query).fetchall()

    query = "SELECT listingID, photoPath FROM photos;"
    photos = db.execute_query(
        db_connection=db_conn, query=query).fetchall()

    if request.method == 'GET':
        query = "SELECT * FROM listings WHERE userID IS NOT NULL;"
        listings = db.execute_query(
            db_connection=db_conn, query=query).fetchall()

    elif request.method == 'POST':
        search_query = f"%{request.form['searchquery']}%"

        if request.form['search-filter'] == 'cars':
            query = "SELECT * FROM listings WHERE make LIKE %s OR model LIKE %s OR year LIKE %s"
            listings = db.execute_query(db_connection=db_conn, query=query,
                                        query_params=(search_query, search_query, search_query)).fetchall()
        elif request.form['search-filter'] == 'features':
            query = "SELECT featureID FROM features WHERE carFeature LIKE %s"
            feature_id = db.execute_query(db_connection=db_conn, query=query,
                                          query_params=(search_query,)).fetchone()
            query = "SELECT * FROM listings WHERE listingID IN (SELECT listingID FROM FeaturesListings WHERE featureID = %s);"
            listings = db.execute_query(db_connection=db_conn, query=query,
                                        query_params=(feature_id['featureID'],)).fetchall()

    return render_template('main.j2', listings=listings, listings_features=listings_features, features=features, bids=bids, photos=photos)


@app.route('/place-bid/<int:list_id>', methods=['GET', 'POST'])
def place_bid(list_id):
    if request.method == 'POST':
        bid_amt = request.form['bid']
        bid_date = date.today()

        db_conn = db.connect_to_database()

        query = "INSERT INTO bids (userID, listingID, bidAmt, bidDate) VALUES (%s, %s, %s, %s)"
        cursor = db.execute_query(db_connection=db_conn, query=query,
                                  query_params=(g.user['userID'], list_id, bid_amt, bid_date))
        bid_id = cursor.lastrowid

        query = "UPDATE listings SET bidID = %s WHERE listingID = %s;"
        db.execute_query(db_connection=db_conn, query=query,
                         query_params=(bid_id, list_id))

    return redirect('/')


@app.route('/submit-listing', methods=['GET', 'POST'])
@auth.login_required
def submit_listing():
    # display standard features on form
    db_conn = db.connect_to_database()
    query = "SELECT carFeature FROM features WHERE featureID BETWEEN 1 AND 4;"
    features = db.execute_query(db_connection=db_conn, query=query).fetchall()

    if request.method == 'POST':
        data = request.form
        make = data['make']
        model = data['model']
        year = int(data['year'])
        mileage = int(data['mileage'])
        reserve = int(data['reserve'])
        list_date = date.today()
        expiration = data['expiration']

        # save photo to static/img/
        photo = request.files['photo']
        filename = secure_filename(photo.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        photo.save(filepath)

        query = "INSERT INTO listings (userID, make, model, year, mileage, reserve, listDate, expirationDate) VALUES (%s, %s, %s, %s, %s, %s, %s, %s);"
        cursor = db.execute_query(
            db_connection=db_conn, query=query, query_params=(g.user['userID'], make, model, year, mileage, reserve, list_date, expiration))
        list_id = cursor.lastrowid

        query = "INSERT INTO photos (photoPath, listingID) VALUES (%s, %s);"
        db.execute_query(db_connection=db_conn, query=query,
                         query_params=(filepath, list_id))

        sel_features = request.form.getlist('features')  # selected features
        usr_feature = request.form['usrfeature']  # feature inputted by user

        # if included, add inputted feature to table
        if len(usr_feature) != 0:
            query = "INSERT INTO features (carFeature) VALUES (%s);"
            db.execute_query(
                db_connection=db_conn, query=query, query_params=(usr_feature,))
            sel_features.append(usr_feature)

        # get all feature ids for this listing
        format_str = ','.join(['%s'] * len(sel_features))
        query = "SELECT featureID FROM features WHERE carFeature IN (" + \
            format_str + ");"
        feature_ids = db.execute_query(
            db_connection=db_conn, query=query, query_params=tuple(sel_features)).fetchall()

        # insert all feature ids for this listing
        listing_features = [(list_id, feature_id['featureID'])
                            for feature_id in feature_ids]
        query = "INSERT INTO FeaturesListings (listingID, featureID) VALUES (%s, %s);"
        db.execute_many(
            db_connection=db_conn, query=query, query_params=listing_features)

    return render_template('submit_listing.j2', features=features)


@ app.route('/profile', methods=['GET', 'POST'])
def profile():
    db_conn = db.connect_to_database()

    # requesting user profile stats
    if request.method == "GET":
        # gather user's active listings
        user_id = (g.user['userID'], )
        query = \
            "SELECT listings.listingID, listings.year, listings.make, listings.model, bids.bidAmt, listings.reserve, listings.expirationDate FROM listings \
            LEFT JOIN bids ON listings.bidID = bids.bidID \
            WHERE listings.userID = %s;"
        active_listings = db.execute_query(db_conn, query, user_id)

        # gather user's bid history
        query = \
            "SELECT bids.bidDate, listings.year, listings.make, listings.model, bids.bidAmt FROM bids \
            INNER JOIN listings ON bids.listingID = listings.listingID \
            WHERE bids.userID = %s;"
        bid_history = db.execute_query(db_conn, query, user_id)

        return render_template('profile.j2', active_listings=active_listings, bid_history=bid_history)

    # user requesting listing deletion
    elif request.method == "POST":
        # gather relevant data to delete listing
        listing_to_delete = request.form['listingID']
        delete_query = 'DELETE FROM FeaturesListings WHERE listingID = %s;'
        update_query = 'UPDATE listings SET listings.userID = NULL WHERE listingID = %s;'
        
        db.execute_query(db_conn, delete_query, (listing_to_delete,))
        db.execute_query(db_conn, update_query, (listing_to_delete,))

        return redirect(url_for('profile'))


# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112))
    app.run(port=port, debug=True)
