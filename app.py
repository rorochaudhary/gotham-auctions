from flask import Flask, render_template
import os
from database import example_listings

# Configuration
app = Flask(__name__)

# Routes 
@app.route('/')
def root():
    return render_template('main.j2', listings=example_listings)

@app.route('/post-listing')
def post_listing():
    return render_template('post_listing.j2')

@app.route('/signup')
def signup():
    return render_template('signup.j2')

# @app.route('/test_postings')
# def test_postings():
#     return render_template('test_postings.j2', listings=example_listings)

# Listener
if __name__ == "__main__":
    port = int(os.environ.get('PORT', 9112))
    app.run(port=port, debug=True)
