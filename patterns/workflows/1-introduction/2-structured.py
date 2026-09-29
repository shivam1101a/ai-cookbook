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


"""Using Instructor library(advanced pydantic) for changing the query and giving time and search locations"""
"""For more info read https://pydantic.dev/articles/llm-intro"""

from typing import List
import datetime
from pydantic import BaseModel


class DateRange(BaseModel):
    start: datetime.date
    end: datetime.date


class SearchQuery(BaseModel):
    rewritten_query: str
    published_daterange: DateRange
    domains_allow_list: List[str]

    async def execute(self):
        # Return the search results of the rewritten query
        return api.search(json=self.model_dump())


import instructor
from openai import OpenAI


# Enables response_model in the openai client
client = instructor.patch(OpenAI())


def search(query: str) -> SearchQuery:
    return client.chat.completions.create(
        model="gpt-4",
        response_model=SearchQuery,
        messages=[
            {
                "role": "system",
                "content": f"You're a query understanding system for a search engine. Today's date is {datetime.date.today()}",
            },
            {"role": "user", "content": query},
        ],
    )


search("recent advancements in AI")
