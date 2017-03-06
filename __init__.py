from trytond.pool import Pool
from . import twilio_messages
from . import routes

__all__ = ['register', 'routes']


def register():
    Pool.register(
        twilio_messages.Message,
        module='twilio_messages', type_='model')
    Pool.register(
        module='twilio_messages', type_='wizard')
    Pool.register(
        module='twilio_messages', type_='report')
