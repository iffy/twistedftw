# Copyright (c) The TwistedFTW Team
# See LICENSE for details.
from klein import Klein
from twisted.internet import defer
import json


class ChatApp(object):

    app = Klein()

    def __init__(self, html):
        self.html = html
        self.subscribers = []

    @app.route('/')
    def room(self, request):
        """
        Deliver HTML for chat room application.
        """
        return self.html

    @app.route('/say', methods=['POST'])
    def say(self, request):
        """
        Send a message to all subscribers.
        """
        # Prepare message to be sent.
        message = request.args['message'][0]
        name = request.args['name'][0]
        event = self.sse('message', json.dumps([name, message]))

        # Send message to every subscriber
        for subscriber in self.subscribers:
            subscriber.write(event)

    @app.route('/events')
    def subscribe(self, request):
        """
        Subscribe to messages.
        """
        # Indicate that the response is an event stream
        request.setHeader('Content-Type', 'text/event-stream')
        
        # Save this request so that we can send messages to it later.
        self.subscribers.append(request)

        # Watch for the request finishing (if they close the browser tab)
        finish = request.notifyFinish()
        finish.addBoth(self.unsubscribe, request)

        # Never finish the request
        return defer.Deferred()


    def unsubscribe(self, reason, request):
        """
        Unsubscribe a request from receiving messages.
        """
        self.subscribers.remove(request)


    def sse(self, name, value):
        """
        Format a message for transmission as a Server Sent Event.
        """
        return 'event: %s\ndata: %s\n\n' % (name, value)


chatroomhtml = '''<!doctype html>
<html>
    <head><title>Chat room</title></head>
    <body>
        <input type="text" id="name_input" placeholder="Name" value="Bob">
        <input type="text" id="message_input" placeholder="Message" autofocus>
        <button id="sendbtn">Send</button>
        
        <div id="messages"></div>
        
        <script src="//ajax.googleapis.com/ajax/libs/jquery/1.10.2/jquery.min.js">
        </script>
        <script>
        var source = new EventSource('/events');
        source.addEventListener('message', function(sse_message) {
            var data = JSON.parse(sse_message.data);
            messageReceived(data[0], data[1]);
        });

        function messageReceived(name, message) {
            var elem = $('<div></div>')
            elem.text(name + ': ' + message);
            $('#messages').append(elem);
        }
        
        function sendMessage() {
            $.post('/say', {
                'name': $('#name_input').val(),
                'message': $('#message_input').val() 
            });
            $('#message_input').val('');
        }
        $('#sendbtn').click(sendMessage);
        $('#message_input').on('keyup', function(ev) {
            if (ev.keyCode == 13) {
                // pressed enter
                sendMessage();
            }
        })
        </script>
    </body>
</html>'''

if __name__ == '__main__':
    chatapp = ChatApp(chatroomhtml)
    chatapp.app.run('0.0.0.0', 8080)
