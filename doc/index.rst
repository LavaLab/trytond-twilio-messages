Twilio Messages Module
######################

The `Twilio <https://www.twilio.com/>`_ messages module allows to create
messages linked to a resource that will be sent by Twilio as `SMS
<https://en.wikipedia.org/wiki/Short_Message_Service>`_

The status of the message is update thanks to Twilio callback.

Configuration
*************

The configuration of the module is set in the `twilio` section.

account_sid
-----------

The default SID of the Twilio account.

auth_token
----------

The token for the Twilio account.

from
----

The default number to use a `from`.

callback_url
------------

The protocol and hostname part of the callback URL. It must end with a `/`.
Default: `http://<hostname>/`
