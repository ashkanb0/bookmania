from django.core.management.base import BaseCommand, CommandError
from books.models import check_daily

class Command(BaseCommand):
    help = 'Checks for closed or soon to be closed by system auctions.'

    def handle(self, *args, **options):
        check_daily()
        