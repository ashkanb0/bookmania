from django import forms
from books.models import Auction, Book

class AuctionForm(forms.Form):
	title = forms.CharField(max_length=70 )
	author = forms.CharField(max_length=70 )
	edition = forms.IntegerField()
	subject = forms.CharField(max_length=70)
	publish_year = forms.IntegerField()
	minimum_price = forms.IntegerField() 
	auction_duration = forms.IntegerField() 
	new_photo_of_book = forms.ImageField(max_length=70, allow_empty_file=True)
	

