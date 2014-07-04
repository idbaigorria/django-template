from __future__ import absolute_import

from ...models import SmsRecipient
from django.core.management.base import BaseCommand, CommandError
import re


class Command(BaseCommand):
    args = '<REMOTE_ID=STATUS_CODE,"STATUS_MESSAGE"> ' * 2 + '...'
    help = ('Set statuses of messages.\n'
            'This may be used by external script for sms status settings, '
            'instead of callback url.')

    arg_pattern = re.compile('(.*?)=(\d+),?\"?\'?(.*)\'?\"?$')

    def handle(self, *args, **options):
        if not args:
            raise CommandError('You must specify at least one argument.')
        for arg in args:
            match = self.arg_pattern.match(arg)
            if not match:
                raise CommandError('"%s" not matched argument pattern. '
                                   'See help for detail.' % arg)
            remote_id, status, status_text = match.groups()
            try:
                recipient = SmsRecipient.objects.get(remote_id=remote_id)
            except SmsRecipient.DoesNotExist:
                raise CommandError('SMS with remote_id "%s" not found.' % remote_id)
            recipient.set_status(int(status), status_text, save=True)
            print 'Status successfully set for %s.' % remote_id
