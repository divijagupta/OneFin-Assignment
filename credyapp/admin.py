from django.contrib import admin

# Register your models here.
from credyapp.models import Movies, Collection

admin.site.register(Movies)
admin.site.register(Collection)
