# Web Test Docs

This document is an overview of the various common web test modules and functions. It is intended for people extending the web tests.

## Web Test Assertions (v2)

The `web_test_assertions` v1 file is no longer in use.

The `web_test_assertions_v2` module is a set of assertions on csv2 objects. The four functions that should be called from outside the module are `assertExists` (which checks for the presence of an object), `assertNotExists` (which checks for the lack of presence of an object), `assertHasAttribute` (which checks that a certain object has a certain attribute), and `assertHasNotAttribute` (which checks that a certain object does not have a certain attribute).

Each assertion takes a list of arguments, as follows:

| Argument Name  | Argument Meaning                                       | Example          | Specified For                         | Default   |
|----------------|--------------------------------------------------------|------------------|---------------------------------------|-----------|
| type           | the type of object                                     | cloud            | all methods                           | N/A       |
| name           | the name of the object being asserted on               | {user}-wic1      | all methods                           | N/A       |
| attribute      | the name of the type of attribute                      | metadata_names   | attribute assertions                  | N/A       |
| attribute_name | the name of the attribute being asserted about         | {user}-wim1.yaml | attribute assertions                  | N/A       |
| group          | the name of the group the object is in                 | {user}-wig0      | assertions on objects in groups       | `None`    |
| err            | the margin of error of the assertion                   | 3                | integer assertions with a range       | `None`    |
| metadata_cloud | the cloud a cloud metadata is in                       | {user}-wic1      | cloud metadata assertions             | `None`    |
| defaults       | whether the object is a default                        | `True`           | default object assertions             | `False`   |
| name_field     | whether the object has a name flag in the list command | `False`          | objects with no name flag             | `True`    |
| settings       | whether the object is a user setting                   | `True`           | user setting object assertions        | `False`   |
| server         | the name of the server to assert on                    | {user}-wis1      | objects requiring an alternate server | unit-test |
| image_cloud    | the cloud a cloud image is in                          | {user}-wic1      | cloud image assertions                | `None`    |
| is_retry       | whether this is the second try of an assertion         | `False`          | never (internal use only)             | `False`   |