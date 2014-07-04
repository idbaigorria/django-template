from __future__ import absolute_import

from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from ... models import SmsRecipient


class Command(BaseCommand):
    help = ('Retrieve statuses of sent messages.\n'
            'If you want to fetch statuses not only on sent messages, '
            'see --sms_statuses option.')
    option_list = BaseCommand.option_list + (
      make_option('--sms_statuses',
        metavar='STATUS_LIST',
        dest='sms_statuses',
        default='3,5',
        help=('Specify comma separated sms statuses ids'
              '(see smsgate.constants module)')
      ),)

    def handle(self, *args, **options):
        statuses = map(int, options['sms_statuses'].split(','))
        count = SmsRecipient.get_statuses(statuses)
        print '%s/%s statuses retrieved.' % count
