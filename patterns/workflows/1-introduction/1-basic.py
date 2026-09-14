"""Use platform.openai website"""

"""Following helps us get the response that we want to make API call"""
import os

from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


completion = client.chat.completions.create(
    model="gpt-4o",  # Specify the model you want to use
    messages=[  # Here 2 roles are used because first onr tells instructions for ai on what it is
        # 2nd one represent the request or message from user
        {"role": "system", "content": "You're a helpful assistant."},
        {
            "role": "user",
            "content": "Write a limerick about the Python programming language.",
        },
    ],
)


response = completion.choices[0].message.content
#  here choices[0] is used to get the first response from LIST
# if we want multiple or all responses we can use for loop
""" for choice in completion.choices:
    print(choice.message.content)   """
