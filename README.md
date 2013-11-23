bookmania
=========

A Django Sample Project.

  Everyone can put a book to auction, if the book isn't already added by him/herself, by providing simple information about it: book info, a minimum price below which people can't bid, valid_days as number of days aftre which the aucion is closed automatically by the system, and new_photo which is considered to be a newly taken photo of the book.
  Everyone can bid on an arbitrary book, if they haven't already done so and if they haven't put the same book on auction.
  2 days before the auction is closed automatically by the system, the owner will be notified and asked to close the auction and choose one of the bidders to sell the book to. If they do so, their rate will be increased one, and if they dont, their rate will be decreased one and the auction will be closed automatically.

#crontab configs
supposed that the folder is based on Desktop : 

use

		sudo crontab -e

and add the following line to check for closed auctions everyday on 00:00

		0 0 * * * ~/Desktop/bookmania/check.sh >>~/Desktop/bookmania/log.txt 2>&1

for ajax commands to work, install 

		django-dajaxice
		
you can find it at: http://www.dajaxproject.com/
