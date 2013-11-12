from django.contrib import admin
from books.models import *

class BidAdmin (admin.ModelAdmin):
	list_display=('buyer', 'req','get_seller' , 'price')
class AuctionAdmin (admin.ModelAdmin):
	list_display=('id','book','seller', 'status' , 'new_photo')
class BookAdmin (admin.ModelAdmin):
	list_display=('id','title','author', 'edition')


admin.site.register(Book, BookAdmin)
admin.site.register(User)
admin.site.register(Auction , AuctionAdmin)
admin.site.register(Bid, BidAdmin)
admin.site.register(Message)
