import random
import re

from telethon import events

from __main__ import client

@client.on(events.NewMessage(incoming=True, pattern=re.compile(r"(?i)(I'm|im|.+(am|are|is))\s+trash$")))
def trash(event):
    event.reply("and so am i")

@client.on(events.NewMessage(incoming=True, pattern=re.compile(r"(?i)^(-\d+|incorrect|bad bot)$")))
def downvote(event):
    if random.randrange(5) == 0:
        event.reply("-1")
