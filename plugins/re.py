import logging
from collections import defaultdict, deque
import re

import regex
from telethon import events, utils

from walrinator import client

logger = logging.getLogger(__name__)

# Heavily based on https://github.com/SijmenSchoon/regexbot/blob/master/regexbot.py

last_msgs = defaultdict(deque)

def save_msg(chat_id, message):
    global last_msgs

    if chat_id not in last_msgs:
        last_msgs[chat_id] = deque(maxlen=10)

    last_msgs[chat_id].append(message)

def doit(chat_id, match, original):
    fr = match.group(1)
    to = match.group(2)
    to = to.replace('\\/', '/')
    try:
        fl = match.group(3)
        if fl == None:
            fl = ''
        fl = fl[1:]
    except IndexError:
        fl = ''

    # Build Python regex flags
    count = 1
    flags = 0
    for f in fl:
        if f == 'i':
            flags |= regex.IGNORECASE
        elif f == 'g':
            count = 0
        else:
            return None, f"Unknown flag: {f}"

    if original is not None:
        try:
            s, i = regex.subn(fr, to, original.message, count=count, flags=flags)
            if i > 0:
                return original, s
        except Exception as e:
            return None, f"u dun goofed m8: {str(e)}"

    # Try matching the last few messages
    global last_msgs
    if chat_id not in last_msgs:
        return None, None

    for original in reversed(last_msgs[chat_id]):
        try:
            s, i = regex.subn(fr, to, original.message, count=count, flags=flags)
            if i > 0:
                return original, s
        except Exception as e:
            return None, f"u dun goofed m8: {str(e)}"

    return None, None

@client.on(events.NewMessage(pattern=re.compile(r"^s/((?:\\/|[^/])+)/((?:\\/|[^/])*)(/.*)?")))
def on_regex(event):
    if not event.is_private:
        return

    chat_id = utils.get_peer_id(event.input_chat)

    m, s = doit(chat_id, event.pattern_match, event.reply_message)

    if m is not None:
        out = client.send_message(event.input_chat, s, reply_to=m.id)
        save_msg(chat_id, out)
    elif s is not None:
        event.reply(s)

    raise events.StopPropagation

@client.on(events.NewMessage)
def on_message(event):
    if not event.is_private:
        return

    chat_id = utils.get_peer_id(event.input_chat)
    save_msg(chat_id, event.message)