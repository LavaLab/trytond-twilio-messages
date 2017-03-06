try:
    from trytond.modules.twilio_messages.tests.test_twilio_messages import suite
except ImportError:
    from .test_twilio_messages import suite

__all__ = ['suite']
