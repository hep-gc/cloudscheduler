from django.contrib import admin
''' These are now handled directly through sqlalchemy and should no long need to leverage the django models
from .models import Group_Resources, Glint_User, Group, User_Group

admin.site.register(Group_Resources)
admin.site.register(Glint_User)
admin.site.register(Group)
admin.site.register(User_Group)
'''