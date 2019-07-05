# new glint api, maybe make this part of glint utils?

def create_placeholder_image(glance, image_name, disk_format, container_format):
    image = glance.images.create(
        name=image_name,
        disk_format=disk_format,
        container_format=container_format)
    return image.id


# Upload an image to repo, returns image id if successful
# if there is no image_id it is a direct upload and no placeholder exists
def upload_image(glance, image_id, image_name, scratch_dir, disk_format=None, container_format=None):
    if image_id is not None:
        #this is the 2nd part of a transfer not a direct upload
        file_path = scratch_dir + image_name
        glance.images.upload(image_id, open(file_path, 'rb'))
        return image_id

    else:
        #this is a straight upload not part of a transfer
        image = glance.images.create(
            name=image_name,
            disk_format=disk_format,
            container_format=container_format)
        glance.images.upload(image.id, open(scratch_dir, 'rb'))
        logger.info("Upload complete")
        return image.id


# Download an image from the repo, returns True if successful or False if not
def download_image(glance, image_name, image_id, scratch_dir):
    #open file then write to it
    file_path = scratch_dir + image_name
    image_file = open(file_path, 'wb')
    for chunk in glance.images.data(image_id):
        image_file.write(bytes(chunk))

    return True

def delete_image(glance, image_id):
    try:
        glance.images.delete(image_id)
    except Exception:
        logger.error("Unknown error, unable to delete image")
        return False
    return True


def update_image_name(glance, image_id, image_name):
    glance.images.update(image_id, name=image_name)


def get_checksum(glance, image_id):
    image = glance.images.get(image_id)
    return image['checksum']