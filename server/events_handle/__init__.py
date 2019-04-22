import server.events_handle.login
import server.events_handle.send_message
import server.events_handle.register
import server.events_handle.friends_request
import server.events_handle.add_friend
from util.message import MessageType

events_handle_map = {
    MessageType.login: login,
    MessageType.send_message: send_message,
    MessageType.register: register,
    MessageType.resolve_friend_request: friends_request,
    MessageType.add_friend: add_friend,
}


def handle_event(sc, event_type, parameters):
    events_handle_map[event_type].run(sc, parameters)