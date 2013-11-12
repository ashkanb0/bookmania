bookmania
=========

A Django Sample Project.
Some books are being put to auction and being sold to bidders!

#crontab configs
supposed that the folder is based on Desktop : 

use

		sudo crontab -e

and add the following line to check for closed auctions everyday on 00:00

		0 0 * * * ~/Desktop/bookmania/check.sh >>~/Desktop/bookmania/log.txt 2>&1
