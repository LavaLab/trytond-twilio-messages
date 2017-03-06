from werkzeug.exceptions import abort, Response

from trytond.wsgi import app
from trytond.protocols.wrappers import with_pool, with_transaction


@app.route('/<database_name>/twilio_messages/<uuid>', methods=['POST'])
@with_pool
@with_transaction()
def callback(request, pool, uuid):
    Message = pool.get('twilio.message')
    try:
        message, = Message.search([
                ('uuid', '=', uuid),
                ])
    except ValueError:
        abort(404)
    message.sid = request.values.get('MessageSid', None)
    message.status = request.values.get('MessageStatus', None)
    if message.status in {'failed', 'undelivered'}:
        message.error_code = request.values.get('MessageErrorCode', None)
        message.error_message = request.values.get('MessageErrorMessage', None)
    message.save()
    return Response(None, 204)
