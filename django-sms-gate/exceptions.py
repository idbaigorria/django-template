class SmsGateError(StandardError):
    pass


class SmsGateUnknownResponse(SmsGateError):
    pass


class SmsGateUnknownCode(SmsGateError):
    pass
