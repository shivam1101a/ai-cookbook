"""Structured output - ensure adherence to JSON schema"""

import os

from openai import OpenAI
from pydantic import BaseModel
# pydantic library is used data validatoin, parsing and serialization.
# if any invalid input is given it gives validation error

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


class CalenderEvent(BaseModel):
    name: str
    date: str
    participants: list[str]


completion = client.beta.completions.parse(
    # parse is used to create stuctred python object
    # beta is used to access newer functionalities to make model better
    model="gpt-4o",
    messages=[
        {"role": "system", "content": "Extract the event information."},
        {
            "role": "user",
            "content": "Alice and Bob are going to a science fair on friday.",
        },
    ],
    response_format=CalenderEvent,  # We used JSON schema here
)

event = completion.choice[0].message.parsed
event.name
event.date  # It understood that date is friday and not in date format
event.paticipants
