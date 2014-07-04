from django.core.management.base import BaseCommand, CommandError
from optparse import make_option
from smsgate.models import Sms


class Command(BaseCommand):
    help = ('Mass send local queue of sms messages.\n'
            'If you want to resend processed early messages, '
            'see --sms_statuses option.')
    option_list = BaseCommand.option_list + (
      make_option('--sms_statuses',
        metavar='STATUS_LIST',
        dest='sms_statuses',
        default='1',
        help=('Specify comma separated sms statuses ids'
              '(see smsgate.constants module)')
      ),)

    def handle(self, *args, **options):
        statuses = map(int, options['sms_statuses'].split(','))
        count = Sms.mass_send(statuses)
        print '%s/%s messages sent.' % count
