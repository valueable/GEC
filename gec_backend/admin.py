from django.contrib import admin

# Register your models here.
from gec_backend.models import *


admin.site.register(User)
admin.site.register(Sentence)
admin.site.register(Type)
admin.site.register(Word)