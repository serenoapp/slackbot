# test_slack_responder.py

from domain.slack_responder import SlackResponder

def test_responder_is_user():
  user_responder = SlackResponder('UserResponderID')
  is_user = user_responder.is_user()
  is_channel = user_responder.is_channel()
  assert True == is_user
  assert False == is_channel

def test_responder_is_channel():
  channel_responder = SlackResponder('ChannelResponderID')
  is_channel = channel_responder.is_channel()
  is_user = channel_responder.is_user()
  assert True == is_channel
  assert False == is_user