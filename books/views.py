from django.shortcuts import render 
from django.views.decorators.csrf import csrf_protect
from django.core.context_processors import csrf
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.template import RequestContext, Context, loader

from books.models import Auction
from books.models import User
from books.forms import AuctionForm

def index (request):
	if request.method == 'POST':
		return login(request)
	usr = request.session.get('user', 0)
	if usr==0:
		return login_view (request)
	else:
		return blist (request)

def blist (request):
	template=loader.get_template('books/index.html')
	user = request.session['user']
	messages = user.get_my_messages()[0:10]
	context = RequestContext(request,{
			'view_name' :'home',
			'name' : user.name,
			'email' : user.email,
			'pict' : user.image,
			'auc_list' : Auction.objects.all(),
			'msgs' : messages,
		})
	return HttpResponse(template.render(context))

def login_view (request ):
	template = loader.get_template('books/login.html')
	context = RequestContext(request,{
			'error' : request.session.get('error', False)
		})
	return HttpResponse(template.render(context))

def login (request):
	requestcontext = RequestContext( request)
	username = request.POST['username']
	password = request.POST['password']
	u =  User.authenticate(username, password);
	if not u:
		request.session['error'] ="Wrong username/password combination"
		return handle_403(request)
	request.session['user']= u
	return blist(request)

def bid (request , auc_id):
	user = request.session.get('user', 0)
	if user==0:
		return handle_403(request)
	try:
		auc = Auction.objects.get(id=auc_id)
	except Exception, e:
		return handle_404(request)
	context = RequestContext(request,{
			'view_name' :'bid',
			'name' : request.session['user'].name,
			'new_photo': auc.new_photo,
			'pict' : user.image,
			'email' : user.email,
			'book_name' : auc.book.title,
			'book_authname' : auc.book.author,
			'book_subject' : auc.book.subject,
			'book_edition' : auc.book.edition,
			'book_pubyr' : auc.book.publish_year,
			'seller_name' : auc.seller.name,
			'seller_rank' : auc.seller.rank,
			'seller_id' : auc.seller.email,
			'min_price' : auc.min_price,
			'max_bid' : auc.highest_bid(),
			'auc_id' : auc.id,
			'is_seller' : user==auc.seller,
	})
	template = loader.get_template('books/bid.html')
	return HttpResponse(template.render(context))

def close (request, auc_id):
	user = request.session.get('user', 0)
	if user==0:
		return handle_403(request)
	else:
		user = User.objects.get(email=user.email)
	try:
		auc = Auction.objects.get(id=auc_id)
	except Exception, e:
		return handle_404(request)
	bids = auc.bid_set.all()
	context = RequestContext(request,{
			'view_name' :'close',
			'name' : user.name,
			'email' : user.email,
			'pict' : user.image,
			'bid_list' : bids,
			'show_list' : len(bids)>0,
			'book_name' : auc.book.title,
			'auc' : auc,
			'not_owner' : user!=auc.seller,
	})
	template = loader.get_template('books/close.html')
	return HttpResponse(template.render(context))

def create (request):
	user = request.session['user']
	error = None
	if request.method== 'POST':
		view_form = AuctionForm(request.POST, request.FILES)
		if view_form.is_valid():
			try:
				auc_id= user.add_auction(
					title = view_form.cleaned_data['title'],
					author = view_form.cleaned_data['author'],
					edition = view_form.cleaned_data['edition'],
					subject = view_form.cleaned_data['subject'],
					publish_year = view_form.cleaned_data['publish_year'],
					min_price = view_form.cleaned_data['minimum_price'],
					duration = view_form.cleaned_data['auction_duration'],
					photo = view_form.cleaned_data['new_photo_of_book'],
					)#TODO : configuration?
				return close(request,auc_id)
			except Exception, e:
				error = e.__str__()
	else:	
		view_form = AuctionForm
	context = RequestContext(request,{
			'view_name' :'create',
			'email' : user.email,
			'error' : error,
			'hasError' : error!=None,
			'name' : user.name,
			'pict' : user.image,
			'form' : view_form,		
	})
	template = loader.get_template('books/create.html')
	return HttpResponse(template.render(context))	

def search(request):
	if request.method== "GET":
		return index(request)
	user = request.session['user']
	query = request.POST['q']
	res = Auction.search_for(query)
	context = RequestContext(request,{
			'view_name' :'search',
			'name' : user.name,
			'pict' : user.image,
			'email' : user.email,
			# 'auc_list' : Auction.objects.all(),			
			'auc_list' : res,			
			'q' : query,	
			'nores' : len(res)==0,	
	})
	template = loader.get_template('books/search.html')
	return HttpResponse(template.render(context))

def profile(request,user_id):
	user = request.session['user']
	profile_user = User.objects.get(email=user_id)
	view_name = ""
	if user== profile_user:
		view_name="profile"
	context = RequestContext(request,{
			'view_name' :view_name,
			'name' : user.name,
			'pict' : user.image,
			'email' : user.email,
			'profile_name' : profile_user.name,
			'profile_photo' : profile_user.image,
			'profile_email' : profile_user.email,
			'profile_age' : profile_user.age,
			'profile_rank' : profile_user.rank,
	})
	template = loader.get_template('books/profile.html')
	return HttpResponse(template.render(context))

def handle_404(request):
	user = request.session['user']
	context = RequestContext(request,{
			'view_name' :'404',
			'name' : user.name,
			'user' : user,
			'email' : user.email,
			
	})
	template = loader.get_template('books/404.html')
	return HttpResponse(template.render(context))

def handle_403(request):
	template = loader.get_template('books/403.html')
	context = RequestContext(request,{
			'view_name' :'403',
	})
	return HttpResponse(template.render(context))

def logout(request):
	request.session['user']=0
	return HttpResponseRedirect('/books/')	

