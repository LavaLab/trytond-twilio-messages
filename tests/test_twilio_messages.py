import unittest

from mock import Mock, patch

from trytond.pool import Pool
from trytond.tests.test_tryton import ModuleTestCase, with_transaction
from trytond.tests.test_tryton import suite as test_suite
from trytond.transaction import Transaction
from trytond.modules.twilio_messages import twilio_messages


class TwilioMessagesTestCase(ModuleTestCase):
    'Test Twilio Messages module'
    module = 'twilio_messages'

    @with_transaction()
    def test_sendmessage(self):
        "Test sendmessage"
        client = Mock()
        message = {'to': '+123456', 'body': "Message"}

        twilio_messages.sendmessage(message, client=client)

        client.messages.create.assert_called_once_with(*message)

    @patch.object(twilio_messages, 'get_twilio_client')
    @with_transaction()
    def test_MessageDataManager_multiple_join(self, get_twilio_client):
        "Test MessageDataManager multiple join"
        transaction = Transaction()

        datamanager = transaction.join(twilio_messages.MessageDataManager())

        self.assertIs(
            transaction.join(twilio_messages.MessageDataManager()),
            datamanager)

    @patch.object(twilio_messages, 'sendmessage')
    @patch.object(twilio_messages, 'get_twilio_client')
    @with_transaction()
    def test_MessageDataManager_commit(self, get_twilio_client, sendmessage):
        "Test MessageDataManager commit"
        transaction = Transaction()
        get_twilio_client.return_value = client = Mock()

        datamanager = transaction.join(twilio_messages.MessageDataManager())
        message = {'to': '+123456', 'body': "Message"}
        datamanager.put(message)
        transaction.commit()

        sendmessage.assert_called_once_with(message, client=client)

    @patch.object(twilio_messages, 'sendmessage')
    @patch.object(twilio_messages, 'get_twilio_client')
    @with_transaction()
    def test_MessageDataManager_rollback(self, get_twilio_client, sendmessage):
        "Test MessageDataManager rollback"
        transaction = Transaction()

        datamanager = transaction.join(twilio_messages.MessageDataManager())
        message = {}
        datamanager.put(message)
        transaction.rollback()

        sendmessage.assert_not_called()
        self.assertFalse(datamanager.queue)

    @patch.object(twilio_messages, 'MessageDataManager')
    @with_transaction()
    def test_Message_send(self, MessageDataManager):
        "test Message.send"
        pool = Pool()
        Message = pool.get('twilio.message')
        User = pool.get('res.user')
        MessageDataManager.return_value = datamanager = Mock()

        message = Message(body="Message", to='+123456', resource=User(1))
        message.save()
        message.send()

        datamanager.put.assert_called_once_with(message.values)

    @with_transaction()
    def test_Message_values(self):
        pool = Pool()
        Message = pool.get('twilio.message')
        User = pool.get('res.user')

        message = Message(
            body="Message", to='+12345', from_='+67890', resource=User(1))
        message.save()

        self.assertDictEqual(
            message.values,
            {'body': "Message", 'to': '+12345', 'from_': '+67890',
                'status_callback': message.callback_url})


def suite():
    suite = test_suite()
    suite.addTests(unittest.TestLoader().loadTestsFromTestCase(
            TwilioMessagesTestCase))
    return suite
