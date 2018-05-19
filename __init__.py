from trytond.pool import Pool
from . import twilio_messages
from . import routes

__all__ = ['register', 'routes']

def register():
    Pool.register(
        twilio_messages.Message,
        twilio_messages.SendMessageStart,
        module='twilio_messages', type_='model')
    Pool.register(
    	twilio_messages.SendMessage,
        module='twilio_messages', type_='wizard')
