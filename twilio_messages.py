import logging
import urllib
import uuid

from trytond.config import config
from trytond.ir.resource import ResourceMixin
from trytond.model import fields
from trytond.pyson import Eval
from trytond.transaction import Transaction
from trytond.url import HOSTNAME

from twilio import TwilioException, TwimlException
from twilio.rest import TwilioRestClient

__all__ = ['Message', 'sendmessage']
logger = logging.getLogger(__name__)
STATUS = [
    (None, ''),
    ('accepted', 'Accepted'),
    ('queued', 'Queued'),
    ('sending', 'Sending'),
    ('sent', 'Sent'),
    ('failed', 'Failed'),
    ('delivered', 'Delivered'),
    ('undelivered', 'Undelivered'),
    ('receiving', 'Receiving'),
    ('received', 'Received'),
    ]
ACCOUNT_SID = config.get('twilio', 'account_sid', default=None)
AUTH_TOKEN = config.get('twilio', 'auth_token', default=None)
CALLBACK_URL = config.get(
    'twilio', 'callback_url',
    default='http%s://%s/' % (
        's' if config.get('ssl', 'privatekey') else '', HOSTNAME))


class Message(ResourceMixin):
    "Twilio Message"
    __name__ = 'twilio.message'

    from_ = fields.Char("From", readonly=True)
    to = fields.Char("To", required=True, readonly=True)
    body = fields.Text("Body", size=1600, readonly=True)
    sid = fields.Char("SID", readonly=True)
    status = fields.Selection(STATUS, "Status", readonly=True)
    error_code = fields.Char(
        "Error Code", readonly=True,
        states={
            'invisible': ~Eval('status').in_(['failed', 'undelivered']),
            },
        depends=['status'])
    error_message = fields.Char(
        "Error Message", readonly=True,
        states={
            'invisible': ~Eval('status').in_(['failed', 'undelivered']),
            },
        depends=['status'])
    uuid = fields.Char("UUID", required=True, select=True, readonly=True)

    @classmethod
    def default_from_(cls):
        return config.get('twilio', 'from', default=None)

    @classmethod
    def default_uuid(cls):
        return str(uuid.uuid4())

    def send(self, transaction=None, datamanager=None):
        assert self.id >= 0, self.id
        if transaction is None:
            transaction = Transaction()
        assert isinstance(transaction, Transaction), transaction
        if datamanager is None:
            datamanager = MessageDataManager()
        datamanager = transaction.join(datamanager)
        datamanager.put(self.values)

    @property
    def callback_url(self):
        url = urllib.quote('%(database)s/twilio_messages/%(uuid)s' % {
                'database': Transaction().database.name,
                'uuid': self.uuid,
                })
        return CALLBACK_URL + url

    @property
    def values(self):
        return {
            'body': self.body,
            'to': self.to,
            'from_': self.from_,
            'status_callback': self.callback_url,
            }


class MessageDataManager(object):

    def __init__(self, account_sid=ACCOUNT_SID, auth_token=AUTH_TOKEN):
        self.account_sid = account_sid
        self.auth_token = auth_token
        self.queue = []
        self._client = None

    def put(self, message):
        self.queue.append(message)

    def __eq__(self, other):
        if not isinstance(other, MessageDataManager):
            return NotImplemented
        return self.account_sid == other.account_sid

    def abort(self, trans):
        self._finish()

    def tpc_begin(self, trans):
        pass

    def commit(self, trans):
        pass

    def tpc_vote(self, trans):
        if self._client is None:
            self._client = get_twilio_client(self.account_sid, self.auth_token)

    def tpc_finish(self, trans):
        if self._client is not None:
            for message in self.queue:
                sendmessage(message, client=self._client)
            self._finish()

    def tpc_abort(self, trans):
        self._finish()

    def _finish(self):
        self._client = None
        self.queue = []


def sendmessage(message, client=None):
    if client is None:
        client = get_twilio_client()
    try:
        return client.messages.create(*message)
    except (TwilioException, TwimlException):
        logger.error('fail to send message', exc_info=True)


def get_twilio_client(account_sid=ACCOUNT_SID, auth_token=AUTH_TOKEN):
    return TwilioRestClient(account_sid, auth_token)
