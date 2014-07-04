from smsgate.models import Sms, SmsRecipient
from smsgate import settings
from django.contrib import admin
from django.utils.translation import ugettext_lazy as _
from django.contrib import messages


def sms_send_queued(self, request, queryset):
    for sms in queryset:
        sms.send()
    self.message_user(request, _('%s SMS messages sent') % len(queryset))
sms_send_queued.short_description = _('Send SMS to queued recipients')


class SmsRecipientInline(admin.TabularInline):
    model = SmsRecipient


class SmsAdmin(admin.ModelAdmin):
    list_display = ('__unicode__', 'sender', 'recipients_count',
                    'recipients_success_count')
    actions = [sms_send_queued, ]
    inlines = (
      SmsRecipientInline,
    )
    ordering = ('-id',)

    def save_formset(self, request, form, formset, change):
        instances = formset.save()
        if settings.SEND_ON_SAVE and instances:
            count = instances[0].sms.send()
        messages.info(request, _('SMS sent to %s recipients') % count)

    def get_actions(self, request):
        actions = super(SmsAdmin, self).get_actions(request)
        if not request.user.has_perm('smsgate.send_sms'):
            del actions['sms_send_queued']
        return actions


def sms_recipient_get_status(self, request, queryset):
    count = SmsRecipient.get_statuses(recipients=queryset)
    self.message_user(request, _('%s SMS statuses fetched') % len(queryset))
sms_recipient_get_status.short_description = _('Retrieve SMS current status')


def sms_recipient_resend(self, request, queryset):
    for sms_recipient in queryset:
        sms_recipient.send()
    self.message_user(request, _('%s SMS messages sent') % len(queryset))
sms_recipient_resend.short_description = _('Resend SMS to recipient')


class SmsRecipientAdmin(admin.ModelAdmin):
    actions = [sms_recipient_get_status, sms_recipient_resend]
    list_display = ('phone', 'sms', 'status_colored', 'status_text_translated',
                    'status_time', 'sent_time', 'queued_time', 'remote_id')
    list_filter = ('status',)
    ordering = ('-queued_time', '-sent_time', '-status_time')

    def get_actions(self, request):
        actions = super(SmsRecipientAdmin, self).get_actions(request)
        if not request.user.has_perm('smsgate.send_sms'):
            del actions['sms_recipient_resend']
        if not request.user.has_perm('smsgate.get_sms_status'):
            del actions['sms_recipient_get_status']
        return actions


admin.site.register(Sms, SmsAdmin)
admin.site.register(SmsRecipient, SmsRecipientAdmin)
