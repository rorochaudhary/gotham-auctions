# validation functions for submit listing, place bid
# NOTE: possible validation for adding feature that already exists in here too?
def validate_new_listing(form_data):
    """
    validates form data from submit_listing for required fields:
        year, make, model, mileage, expiration
    param form_data -- information stored in request.from
    return -- error (str of error msg or None)
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
    return -- True if image present, False otherwise
    """
    return True if file_request.filename != '' else False
