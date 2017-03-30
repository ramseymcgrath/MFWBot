import json
import logging
import re

logger = logging.getLogger(__name__)


class RtmEventHandler(object):
    def __init__(self, slack_clients, msg_writer, users_watched):
        self.clients = slack_clients
        self.msg_writer = msg_writer
        self.users_watched = users_watched

    def handle(self, event):

        if 'type' in event:
            self._handle_by_type(event['type'], event)

    def _handle_by_type(self, event_type, event):
        # See https://api.slack.com/rtm for a full list of events
        if event_type == 'error':
            # error
            self.msg_writer.write_error(event['channel'], json.dumps(event))
        elif event_type == 'message':
            # message was sent to channel
            self._handle_message(event)
        elif event_type == 'channel_joined':
            # you joined a channel
            self.msg_writer.write_help_message(event['channel'])
        elif event_type == 'group_joined':
            # you joined a private group
            self.msg_writer.write_help_message(event['channel'])
        else:
            pass

    def _handle_message(self, event):
        # Filter out messages from the bot itself, and from non-users (eg. webhooks)
        if ('user' in event) and (not self.clients.is_message_from_me(event['user'])):
            msg_txt = event['text']
            user = event['user']
            channel_id = event['channel']
            strings = ['mfw','MFW']
            if any (x in msg_txt for x in strings):
                self.msg_writer.send_message(channel_id,"Better post a face...")
                msg_count = 0
                obj = (user,msg_count,channel_id)
                self.users_watched.append(obj)
            else:
                for watched in self.users_watched:
                    if(user == watched[0] and channel_id == watched[2]):
                        if (watched[1]>3):
                            obj = (user,watched[1],channel_id)
                            self.msg_writer.send_message(channel_id,"NO FACE FOR " + str(user))
                            self.users_watched.remove(obj)
                        else:
                            if(event.has_key('attachments')):
                                obj = (user,watched[1],channel_id)
                                self.users_watched.remove(obj)
                            else: 
                                obj = (user,watched[1],channel_id)
                                self.users_watched.remove(obj)
                                new_obj = (user,watched[1],channel_id)
                                self.users_watched.append(new_obj)

    def _is_direct_message(self, channel):
        """Check if channel is a direct message channel

        Args:
            channel (str): Channel in which a message was received
        """
        return channel.startswith('D')
