from django.contrib import admin

# Register your models here.
from .models import Community, Confession, Comment, User, Like, Member, JoinRequest
admin.site.site_header  =  "Confessioner admin"  
admin.site.site_title  =  "Confessioner admin site"
admin.site.index_title  =  "Confessioner Admin"
admin.site.register(Community)
admin.site.register(Confession)
admin.site.register(Comment)
admin.site.register(User)
admin.site.register(Like)
admin.site.register(Member)
admin.site.register(JoinRequest)