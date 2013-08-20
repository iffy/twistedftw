from twisted.trial.unittest import TestCase
from twisted.internet import defer
from mock import MagicMock, create_autospec

from txftw.demo.room import Room
from txftw.demo.web import WebRoomMember, sseMsg


class WebRoomMemberTest(TestCase):


    def test_init(self):
        """
        The WebRoomMember should know about the request
        """
        request = MagicMock()
        guy = WebRoomMember(request)
        self.assertEqual(guy.request, request)
        self.assertEqual(guy.room, None)


    def test_setRoom(self):
        """
        Should set the room attribute
        """
        request = MagicMock()
        room = Room()

        guy = WebRoomMember(request)
        guy.setRoom(room, 'hey')
        self.assertEqual(guy.room, room)
        self.assertEqual(guy.name, 'hey')


    def test_requestFinished(self):
        """
        When a request is finished, the WebRoomMember should remove itself from
        the Room
        """
        request = MagicMock()
        request_done = defer.Deferred()
        request.notifyFinish.return_value = request_done
        
        room = Room()
        room.leave = create_autospec(room.leave)

        guy = WebRoomMember(request)
        guy.setRoom(room, 'bar')

        # finish the request
        request_done.callback('foo')
        room.leave.assert_called_once_with('bar')


    def test_requestFinished_noRoom(self):
        """
        When a request is finished, and the user isn't in any room, don't die.
        """
        request = MagicMock()
        request_done = defer.Deferred()
        request.notifyFinish.return_value = request_done

        guy = WebRoomMember(request)

        # finish the request
        request_done.callback('foo')
        return request_done


    def test_leaveRoom(self):
        """
        Leaving the room should write something to the request.
        """
        request = MagicMock()

        room = Room()

        guy = WebRoomMember(request)
        room.enter('bob', guy)
        request.write.reset_mock()

        room.leave('bob')
        request.write.assert_called_once_with(sseMsg('status', 'youleft'))


    def test_messageReceived(self):
        """
        messages received should be written to the request as server sent
        events.
        """
        request = MagicMock()

        guy = WebRoomMember(request)
        guy.messageReceived('foo')
        request.write.assert_any_call(sseMsg('d', 'foo'))


    def test_messageReceived_afterRequestFinished(self):
        """
        Messages received after a request has finished should not be sent.
        """
        request = MagicMock()
        request.notifyFinish.return_value = defer.succeed(None)

        guy = WebRoomMember(request)
        guy.messageReceived('foo')
        guy.setRoom(None, 'hey')
        self.assertEqual(request.write.call_count, 0)



