.. File generated by /opt/cloudscheduler/utilities/schema_doc - DO NOT EDIT
..
.. To modify the contents of this file:
..   1. edit the template file ".../cloudscheduler/docs/schema_doc/views/view_ec2_images.yaml"
..   2. run the utility ".../cloudscheduler/utilities/schema_doc"
..

Database View: view_ec2_images
==============================

.. _view_ec2_images: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_ec2_images.html

.. _view_ec2_instance_types: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_views/view_ec2_instance_types.html

This view is one of a suite of related views used by
the User Interface (UI) processes to present Amazon EC2 information. The suite
includes:

#. view_ec2_images_

#. view_ec2_instance_types_

The **view_ec2_images** presents the content of ec2_images CSV2 table interpreting and appending
the architecture, operating system and lower case location fields.


Columns:
^^^^^^^^

* **region** (String(32)):

      Is the Amazon EC2 cloud/region this image is available on.

* **id** (String(128)):

      This is the unique ID of the image as defined by Amazon
      EC2.

* **borrower_id** (String(32)):

      Is a field indicating whether this (kernel) image has been specifically shared
      with your Amazon EC2 ID. If it has, this field will contain
      the Amazon account ID associated with the CSV2 cloud that retrieved this
      entry. Otherwise, it will contain the value 'not_shared'.

* **owner_id** (String(32)):

      Is the Amazon EC2 ID of the user owning this image. In
      order for you to see this image, they will have either shared
      it with your ID or made the image public.

* **owner_alias** (String(64)):

      Is the Amazon account alias that owns this image.

* **disk_format** (String(128)):

      Is the type of disk required by this image, eg. ebs, instance-store,
      etc.

* **size** (Integer):

      Is the number of gigabytes of disk required by this image.

* **image_location** (String(512)):

      Is the location of the image.

      The image location must be set by the owner and must be
      unique. Since this information is normally very descriptive of what the image
      is, it is generally much more reliable than either the name or
      the description which are both optional.

* **visibility** (String(128)):

      Is a string indicating how you have access to this image. You
      either own it, or it is public, or it is shared with
      you.

* **name** (String(256)):

      Is the name of the image, and is optionally set by the
      owner (see 'location' above).

* **description** (String(256)):

      Is a description of the image, and is optionally set by the
      owner (see 'location' above).

* **last_updated** (Integer):

      Is the last time this information was updated.

* **lower_location** (String(512)):

      This field contains a lower case version of the image location and
      is provided to assist in searching for images as part of the
      image filtering process (see ec2_image_filters_ for more information).

      .. _ec2_image_filters: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_tables/ec2_image_filters.html

* **opsys** (String(8)):

      This field contains a simple, one word digest of the **lower_location** field
      to indicate the type of operating system supported by this (kernel) image.
      Values can include 'manifest', 'windows', and 'linux'. The field is provided as
      a feature of the image filtering process (see ec2_image_filters_ for more information).`

      .. _ec2_image_filters: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_tables/ec2_image_filters.html

* **arch** (String(5)):

      This field contains a simple, one word digest of the **lower_location** field
      to indicate the type of hardware architecture supported by this (kernel) image.
      Values can include 'arm32', 'arm32', '32bit', and '64bit'. The field is provided
      as a feature of the image filtering process (see ec2_image_filters_ for more
      information).`

      .. _ec2_image_filters: https://cloudscheduler.readthedocs.io/en/latest/_architecture/_data_services/_database/_tables/ec2_image_filters.html

