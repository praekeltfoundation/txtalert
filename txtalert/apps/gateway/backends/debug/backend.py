import sys


class Gateway(object):

    # for test stubbing
    stdout = sys.stdout

    def send_sms(self, *args, **kwargs):
        return self.send_bulk_sms(*args, **kwargs)

    def send_one_sms(self, user, msisdn, smstext, delivery=None, expiry=None,
                     priority='standard', receipt='Y'):
        self.stdout.write(
            "Sending '%s' to '%s' from '%s'\n" % (
                smstext, msisdn, user.username))

    def send_bulk_sms(self, user, msisdns, smstexts, *args, **kwargs):
        return [self.send_one_sms(user, msisdn, smstext, *args, **kwargs)
                for (msisdn, smstext) in zip(msisdns, smstexts)]


gateway = Gateway()

# no sms receipt handling for dummy gateway
sms_receipt_handler = None
