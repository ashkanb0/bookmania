from django.utils import simplejson
from dajaxice.decorators import dajaxice_register
from books.models import * 

@dajaxice_register
def bid(request,auc_id,price):
	responseDict ={}
	try:
		request.session['user'].bid_on( int(auc_id), int(price) )
		responseDict['has_error']='No'
		responseDict['message']='Your offer has been successfully added.'
	except ValueError, e:
		responseDict['has_error']='Yes'
		responseDict['message'] = price+' is no price!'
		
	except BidException, e:
		responseDict['has_error']='Yes'
		responseDict['message'] = str(e)
	return simplejson.dumps(responseDict)

@dajaxice_register
def close(request,buyer_id,auc_id):
	responseDict ={}
	try:
		request.session['user'].close_off( int(auc_id), str(buyer_id) )
		responseDict['has_error']='No'
		responseDict['message']='Your auction has been successfully closed.\n Your rank has been increased.'
	except CloseException, e:
		responseDict['has_error']='Yes'
		responseDict['message'] = str(e)
	return simplejson.dumps(responseDict)