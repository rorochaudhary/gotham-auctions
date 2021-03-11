# validation functions for submit listing, photo with listing, and place bid
def validate_new_listing(form_data):
    """
    validates form data from submit_listing for required fields:
        year, make, model, mileage, expiration
    param form_data -- information stored in request.form (dict)
    return error -- str or None
    """
    error = None

    if not form_data['year'] or form_data['year'] == 'Select year':
        error = "Please add a year to this listing."
        print(error)
        return error
    elif not form_data['make'] or form_data['make'] == 'Select make':
        error = "Please add a make to this listing."
        print(error)
        return error
    elif not form_data['model']:
        error = "Please add a model to this listing."
        print(error)
        return error
    elif not form_data['mileage']:
        error = "Please add a mileage to this listing."
        print(error)
        return error
    elif not form_data['expiration']:
        error = "Please add an expiration date to this listing."
        print(error)
        return error
    else:
        return error


def validate_photo(file_request):
    """
    function determines whether request contains a file or not
    param file_request -- contains request information of user photo (dict)
    return -- True if image present, False otherwise (bool)
    """
    return True if file_request.filename != '' else False

def validate_bid(user_bid, high_bid):
    """
    determines whether bid amount from user higher than current high bid.
    param user_bid -- user submitted bid information from db (int)
    param high_bid -- current high bid associated with listing (dict)
    return (validity, message) -- tuple of (False, str)
    """
    message = f"Congratulations! Your bid of ${user_bid} placed successfully."
    if user_bid <= high_bid["amount"]:
        message = "Your bid is not high enough! Try again."
        return False, message
    return True, message