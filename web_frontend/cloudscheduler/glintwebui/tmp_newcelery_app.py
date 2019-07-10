#new celery_app.py


#instead of having a task type for each transaction we will split it up into 2 worker types
# for now i think having 2 of each should be sufficient
#1)pull requests
#2)transfer requests

#logic will be similar for both both work off different database tables




# type 1, pull requests
@app.task(bind=True)
def pull_request(self, tx_id):
    # get tx row from database
    # check if the image is in the cache, if so return complete
    # else get the cloud row for the source and create a glance client and call download function
    # update the cache table and return complete

    return None


# type 2, transaction requests (transfers)

@app.task(bind=True)
def transfer_request(self, tx_id):
    # get tx row from database
    # triple check target image doesn't exist
    # if not, check cache for source image, if it's not there check that a pull request is queue'd
    # if none are queued queue one and wait for it to appear in cache
    # once image is in cache get the cloud row for the target and call the upload function,
    # maybe upload cloud image table and return complete

    return None