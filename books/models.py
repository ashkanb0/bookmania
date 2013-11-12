from django.db import models
from django.db.models import Q
from datetime import date
from datetime import timedelta

import os;

MIN_PRICE = 5
MAX_DURATION = 20

class BidException (Exception):
	def __init__ (self, value):
		self.value=value
	def __str__(self):
		return repr(self.value)
class CloseException (Exception):
	def __init__ (self, value):
		self.value=value
	def __str__(self):
		return repr(self.value)
class CreateException (Exception):
	def __init__ (self, value):
		self.value=value
	def __str__(self):
		return repr(self.value)

class Book (models.Model):
	title = models.CharField(max_length=70 )
	author = models.CharField(max_length=70 )
	edition = models.IntegerField(default=1)
	subject = models.CharField(max_length=70)
	publish_year = models.IntegerField(default=1)

	def __unicode__(self):
		return self.title
	
class User (models.Model):
	email = models.EmailField(primary_key = True)
	student_number = models.IntegerField(null=False)
	name = models.CharField(max_length=70)
	passwd = models.CharField(max_length=70)
	image = models.ImageField(max_length=70, upload_to = 'media/users', null=True, blank=True)
	rank = models.IntegerField(default=0)
	age = models.IntegerField(default=20)
	
	def __unicode__(self):
		return self.name

	def decrease_rank(self):
		self.rank = self.rank -1
		self.save()
	
	def increase_rank(self):
		self.rank = self.rank +1
		self.save()

	def is_involved(self, title, author, edition):
		if Auction.objects.filter(status="OPEN",book__title=title, book__author=author, book__edition=edition, seller=self).exists():
			return True
		if Bid.objects.filter(req__status="OPEN",req__book__title=title, req__book__author=author, req__book__edition=edition, buyer=self).exists():
			return True
		return False
	
	def get_my_messages(self):
		return Message.objects.filter(Q(buyer=self)|Q(seller=self)).order_by('id').reverse().all()
	
	def bid_on (self , auc_id, price_str):
		price = int(price_str)
		auc = Auction.objects.get(id=int(auc_id))
		if price<auc.min_price:
			raise BidException("Amount that you bid is less than seller's minimum price for auction, HOW DID YOU DO THAT?!")
		if self==auc.seller:
			raise BidException("You cannot bid your own auction, hanven't we told you already?!")
		if self.is_involved(auc.book.title, auc.book.author, auc.book.edition):
			raise BidException("You are already selling/buying that book. You cannot bid for it.")
		if auc.status!="OPEN":
			raise BidException("The auction is not open!")
		try:
			bid = Bid.objects.get(buyer=self, req=auc)
			bid.price = price
		except Exception, e:
			bid = Bid(buyer= self,req= auc,price = price)
		bid.save()

	def close_off (self, auc_id, buyer_id):
		auc = Auction.objects.get(id=auc_id)
		buyer = User.objects.get(email=buyer_id)
		if auc.seller!= self :
			raise CloseException("You are not seller of this auction, you cannot close it!")
		if auc.status!="OPEN":
			raise CloseException("The auction is not open!")
		print "increasing rank :" +str(self.rank)
		print self.age
		print self
		self.increase_rank()
		print "increasing rank done"
		sale = Sale(auction=auc, buyer=buyer)
		sale.save()
		send_msg(buyer=buyer, seller=self, msg_type="SUCCESS", book=auc.book)
		auc.status= "SUCCESS"
		auc.save()

	def add_auction(self, title,author, edition, subject, publish_year, min_price, duration, photo ) :
		if self.is_involved( title, author, edition):
			raise CreateException("You are already selling/buying that book. You cannot put it for a new Auction.")
		if(min_price<MIN_PRICE):
			raise CreateException("Minimum for minimum price is: "+ str(MIN_PRICE))
		if(duration>MAX_DURATION):
			raise CreateException("Maximum for duration on an auction is: "+ str(MAX_DURATION))
		book = Book(title=title, author=author, edition=edition, subject=subject, publish_year=publish_year)
		book.save()
		auction = Auction(book=book, seller=self, min_price=min_price, valid_days=duration, new_photo=photo)
		auction.save()
		return auction.id

	@staticmethod
	def authenticate (username, password):
		try:
			u = User.objects.get(email=username)
		except Exception, e:
			return False
		if u.passwd == password :
			return u
		else:
			return False

	
class Auction (models.Model):
	book = models.ForeignKey(Book)
	seller = models.ForeignKey(User)
	min_price = models.IntegerField(default=2) 
	date_created = models.DateField(auto_now_add=True)
	valid_days = models.IntegerField(default=5) 
	new_photo = models.ImageField(max_length=256 , upload_to = 'media/auctions', null=True, blank=True)
	status = models.CharField(max_length = 10, default = "OPEN")

	def __unicode__(self):
		return self.book.__unicode__()
	
	def highest_bid(self):
		ordered = self.bid_set.order_by('price')
		if(len(ordered)==0):
			return False
		return ordered[len(ordered)-1]

	def is_active (self):
		if self.status!="OPEN":
			return False
		if self.date_created + timedelta(days = self.valid_days-2) <= date.today() :
			print "-----------**********-------sending alert : +"+self.book.title+"+---------------"
			send_msg(msg_type="ALERT" , seller=self.seller , book=self.book)
		if self.date_created + timedelta(days = self.valid_days) >= date.today() :
			return True
		else:
			if self.status=="OPEN" :
				self.status = "FAILURE"
				self.seller.decrease_rank()
				send_msg( msg_type="FAILURE" , seller=self.seller , book=self.book)				
				self.save()
			return False
	
	@staticmethod
	def search_for(query):
		return Auction.objects.filter(Q(book__title__contains=query)|Q(book__author__contains=query)).all()

class Bid (models.Model):
	buyer = models.ForeignKey(User)
	req = models.ForeignKey(Auction)
	price = models.IntegerField(default=2)

	def get_seller(self):
		return self.req.seller

class Sale(models.Model):
	auction = models.ForeignKey(Auction)
	buyer = models.ForeignKey(User)	

class Message(models.Model):
	buyer = models.ForeignKey(User, blank=True, null=True, default=None, related_name="msg_buyer")	
	seller = models.ForeignKey(User, related_name="msg_seller")	
	book = models.ForeignKey(Book)
	msg_type = models.CharField(max_length=10)

	def __unicode__(self):
		return self.msg_type+ " |seller: " + self.seller.__str__() 

def send_msg(seller, book, msg_type,buyer = None):
	try:
		msg_dub = Message.objects.get(seller=seller , book=book)
		if msg_dub.msg_type!=msg_type:
			send_email(seller=seller, buyer=buyer,book=book, msg_type=msg_type )
			msg_dub.msg_type=msg_type
			msg_dub.save()
			return
	except Exception, e:
		send_email(seller=seller, buyer=buyer,book=book, msg_type=msg_type )
		msg = Message(buyer=buyer, msg_type=msg_type , seller=seller , book=book)
		msg.save()	

def send_email(seller, buyer, book, msg_type):
	sellerpathname=os.path.dirname("emails/"+seller.email+'/')
	if not os.path.exists(sellerpathname):
		os.makedirs(sellerpathname)
	if buyer!= None and msg_type=="SUCCESS":
		buyerpathname=os.path.dirname("emails/"+buyer.email+'/')
		if not os.path.exists(buyerpathname):
			os.makedirs(buyerpathname)
		file = open("emails/"+buyer.email+'/'+seller.name+" has piked you - "+str(date.today())+".txt", "a+")
		file. write("Hello, "+buyer.name+",\n"+seller.name+" has picked you as buyer for his/her book: '"+ book.title+"', please contact <"+seller.email+"> for further instructions.\n \nRegards, 'bookmania' group.")
	if seller!= None and msg_type=="SUCCESS":
		file = open("emails/"+seller.email+'/'+"Auction went well - "+str(date.today())+".txt", "a+")
		file. write("Hello, "+seller.name+",\nYou have picked "+buyer.name+" as buyer for your book: '"+ book.title+"', Your rank will be increased.\n \nRegards, 'bookmania' group.")
	if seller!= None and msg_type=="FAILURE":
		file = open("emails/"+seller.email+'/'+"Auction outdated - "+str(date.today())+".txt", "a+")
		file. write("Hello, "+seller.name+",\nYou have not closed auction on your book: '"+ book.title+"', Your rank will be decreased.\n \nRegards, 'bookmania' group.")
	if seller!= None and msg_type=="ALERT":
		file = open("emails/"+seller.email+'/'+"Auction soon to be outdated - "+str(date.today())+".txt", "a+")
		file. write("Hello, "+seller.name+",\nYou have not closed auction on your book: '"+ book.title+"' yet. Please give us a visit and close it.\n \nRegards, 'bookmania' group.")

def check_daily():
	auctions = Auction.objects.filter(status="OPEN").all()
	for auc in auctions:
		auc.is_active()
