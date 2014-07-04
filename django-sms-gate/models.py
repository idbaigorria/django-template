from smsgate import settings
from smsgate import send_sms, send_mass_sms, get_sms_statuses
from smsgate.constants import *

from django.db import models
from django.core.validators import RegexValidator
from django.utils.translation import ugettext_lazy as _

from datetime import datetime

phone_validator = RegexValidator('\d{12}', message=_('Telephone number must be'
'in international format (12 digits, without +), see http://en.wikipedia.org/'
'wiki/List_of_country_calling_codes for your country telephone format.'))


class Sms(models.Model):
    '''
    Class for creating, sending, storing message body of SMS.
    Note that if your workflow oriented on one recipient per one SMS -
    you may be more interested with SmsRecipient class.
    '''
    text = models.TextField(_('SMS text'))
    sender = models.CharField(
        _('Sender'), max_length=32, default=settings.SENDER
    )

    def __unicode__(self):
        if len(self.text) > 16:
            return u'%s...' % self.text[:13]
        else:
            return self.text

    class Meta:
        verbose_name = _('SMS message')
        verbose_name_plural = _('SMS messages')
        permissions = (
            ('send_sms', 'Can send SMS'),
        )

    def send(self, statuses=(STATUS_QUEUED,), recipients=None, **kwargs):
        '''
        Send SMS to its recipients with given statuses (default - queued).
        Returns count of sent recipients.

        If you specify recipients - ignore fetching and send only to them.
        You may also specify keyword arguments for passing to smsgate.send_sms.
        '''
        if recipients == None:
            recipients = self.recipients.filter(status__in=statuses)
        sent_data = send_sms(
          self.text,
          [r.phone for r in recipients],
          self.id,
          sender=self.sender,
          **kwargs
        )
        for n, (remote_id, status, status_text) in enumerate(sent_data):
            recipients[n].set_processed(remote_id, status, status_text)
        return len(sent_data)

    def recipients_count(self):
        return self.recipients.all().count()
    recipients_count.short_description = _('Total recipients')

    def recipients_success_count(self):
        return self.recipients.filter(status__in=settings.SUCCESS_STATUSES).count()
    recipients_success_count.short_description = _('Successed recipients')

    @classmethod
    def create(cls, text, recipients_list, sender=settings.SENDER,
               send=settings.SEND_ON_SAVE, **kwargs):
        '''
        Creates and returns Sms object for phone numbers in recipients_list.

        Phone numbers must be in international format, without +.
        Sender defaults to SMSGATE_SENDER setting.
        if send = True - sends message immediately.
        You may also specify keyword arguments for passing to send method.
        '''
        sms = cls(text, sender)
        sms.save()
        recipients = []
        for phone in recipients_list:
            recipient = SmsRecipient(sms=sms, phone=phone)
            recipient.save()
            recipients.append(recipient)
        if send:
            sms.send(recipients=recipients, **kwargs)
        return sms

    @classmethod
    def mass_send(cls, statuses=(STATUS_QUEUED,), *kwargs):
        '''
        Send all stored SMS messages with given statuses (default - queued).
        Returns tuple of total and sent recipients count.

        You may also specify keyword arguments for passing to
        smsgate.send_mass_sms.
        '''
        datatuple = []
        recipients_lists = []
        for sms in Sms.objects.filter(recipients__status__in = statuses).distinct():
            recipients = sms.recipients.filter(status__in = statuses)
            datatuple.append((
                sms.text,
                [r.phone for r in recipients],
                self.id,
            ))
            recipients_lists.append(recipients)

        result_count = 0
        for x, sent_data in enumerate(send_mass_sms(datatuple, **kwargs)):
        # Setting SMS statuses
            recipients = recipients_lists[x]
            for n, (remote_id, status, status_text) in enumerate(sent_data):
                recipients[n].set_processed(remote_id, status, status_text)
                if status in settings.SUCCESS_STATUSES:
                    result_count += 1
        return sum(map(len, recipients_lists)), result_count


class SmsRecipient(models.Model):
    '''
    This class describes each recipient of SMS, and actually works with SMS
    statuses, so class Sms only stores the message body and sender.
    '''
    STATUS_CHOICES = (
        (STATUS_QUEUED, _('Queued')),
        (STATUS_CANCELED, _('Canceled')),
        (STATUS_SENT, _('Sent')),
        (STATUS_UNSENT, _('Not sent')),
        (STATUS_UNKNOWN, _('Unknown')),
        (STATUS_REMOTE_QUEUED, _('Queued on server')),
        (STATUS_DELIVERED, _('Delivered')),
        (STATUS_UNDELIVERED, _('Undelivered')),
        (STATUS_EXPIRED, _('Expired')),
    )
    phone = models.CharField(
        _('Phone number'), max_length=12, validators=[phone_validator,],
    )
    remote_id = models.CharField(
        _('Remote id'), max_length=32, editable=False,
    )
    status = models.SmallIntegerField(
        _('Status'), choices=STATUS_CHOICES, default=STATUS_QUEUED,
    )
    queued_time = models.DateTimeField(
        _('Queued time'), default=datetime.now, editable=False,
    )
    status_time = models.DateTimeField(
        _('Status renew time'), null=True, blank=True, editable=False,
    )
    sent_time = models.DateTimeField(
        _('Sent time'), null=True, blank=True, editable=False,
    )
    status_text = models.CharField(
        _('Status message'), max_length=64, null=True, blank=True,
        editable=False,
    )
    # You may use credits field to store data for billing system
    credits = models.IntegerField(_('Credits'), default=1)
    sms = models.ForeignKey(Sms, related_name='recipients')

    class Meta:
        verbose_name = _('SMS recipient')
        verbose_name_plural = _('SMS recipients')
        unique_together = (('phone', 'sms'),)
        ordering = (('-queued_time'),)
        permissions = (
            ('get_sms_status', 'Can retrieve SMS status'),
        )

    def __unicode__(self):
        return u'%s(%s)' % (self.phone, self.get_status_display())

    def send(self):
        '''
        Send (or resend) SMS only to this recipient.
        '''
        self.sms.send(recipients=(self,))

    def set_status(self, status, status_text=None, time=None, save=True):
        '''
        Set status to this recipient.
        '''
        self.status, self.status_text = status, status_text
        self.status_time = time if time else datetime.now()
        if save:
            self.save()

    def set_processed(self, remote_id, status, status_text, time=None, save=True):
        '''
        Set SMS status after send (or trying to send).
        '''
        self.sent_time = time if time else datetime.now()
        if remote_id:
            self.remote_id = remote_id
        self.set_status(status, status_text, time=self.sent_time, save=False)
        if save:
            self.save()

    def renew_status(self, save=True):
        '''
        Retrieve SMS status from gateway and set it.
        Note that it do nothing if remote_id is empty.
        '''
        if self.remote_id:
            status, status_text = get_sms_statuses((self.remote_id,))[0]
            self.set_status(status, status_text, save=save)

    def status_color(self):
        return settings.STATUS_COLORS[self.status]

    def status_colored(self):
        return u'<span style="color: %s;">%s</span>' % (self.status_color(),
                                                        self.get_status_display())
    status_colored.short_description = _('Status')
    status_colored.allow_tags = True
    status_colored.admin_order_field = 'status'

    def status_text_translated(self):
        return _(self.status_text) if self.status_text else ''
    status_text_translated.short_description = _('Status message')

    @classmethod
    def get_statuses(cls, statuses=(STATUS_SENT, STATUS_UNKNOWN),
                     set_expired=True, recipients=None):
        '''
        Retrieve and set statuses of SMS with given statuses (defaults to sent
        or unknown). Note that it skips recipients with empty remote_id.

        Returns tuple of total and fetched statuses count.
        '''
        time = datetime.now()
        if not recipients:
            recipients = cls.objects.filter(status__in=statuses,
                                            remote_id__isnull=False)

        # We can fetch recipients only with remote_id
        fetch_recipients = []
        for obj in recipients:
            if set_expired and obj.sent_time and \
               (time.date() - obj.sent_time.date()).days > settings.STATUS_MAX_DAYS:
                obj.set_status(STATUS_EXPIRED, time=time)
            elif obj.remote_id:
                fetch_recipients.append(obj)

        remote_ids = [r.remote_id for r in fetch_recipients]
        result_count = 0
        for n, (status, status_text) in enumerate(get_sms_statuses(remote_ids)):
            fetch_recipients[n].set_status(status, status_text, time=time)
            result_count += 1
        return len(fetch_recipients), result_count
