from django.contrib import admin
from django.contrib.admin import AdminSite


from . models import*

admin.site.register(User)
admin.site.register(UserFriend)
admin.site.register(Wishlist)
admin.site.register(Gift)


class CustomAdminSite(AdminSite):
    admin.site.site_title = 'Vekushka'
    admin.site.site_header = 'Vist'
    admin.site.index_title = 'Vist Admin Pannel'


  

   
    