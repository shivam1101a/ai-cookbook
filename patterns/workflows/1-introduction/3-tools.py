"""AI will not call the tools(function) itself, it will not provide the 
paramenter that the functions need"""

import os
import json

import requests
from openai import OpenAI
from pydantic import BaseModel, Field

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

"""
docs: https://platform.openai.com/docs/guides/function-calling
"""

# --------------------------------------------------------------
# Define the tool (function) that we want to call
# --------------------------------------------------------------

def get_weather(latitude,longitiude):
    response = requests.get(
        f"https://api.open-meteo.com/v1/forecast?latitude={latitude}&longitude={longitude}&current=temperature_2m,wind_speed_10m&hourly=temperature_2m,relative_humidity_2m,wind_speed_10m"
    )
    data = response.json()
    return data["current"]


# --------------------------------------------------------------
# Step 1: Call model with get_weather tool defined
# --------------------------------------------------------------
# The format of tool as syntax is provided by openai
tools = [
    {
        "type": "function",
        "function":{
            "name":"get_weather",
            "description": "Get current temperature for provided coordinates in celsius.",
            #The name and description helps llm decide whether to call it or not
            "parameter": {
                "type": "object",
                "properties": {
                    "latitude":{"type": "number"},
                    "longitude":{"type": "number"},
                },
                "required": ["latitude", "longitude"],
                "additional properties": False,
            },
            "strict": True,
            },
        }
]

system_prompt = "You are a helpful weather assistant."

messages = [
    {"role":"system","content": system_prompt},
    {"role":"user","content": "What's the weather like in paris today?"},
]

completion = client.chat.completions.create{
    model="get-4o",
    messages=messages,
    tools=tools     #Additional thing that we provided
}


# --------------------------------------------------------------
# Step 2: Model decides to call function(s)
# --------------------------------------------------------------

completion.model_dump()     #Response of OpenAI


# --------------------------------------------------------------
# Step 3: Execute get_weather function
# --------------------------------------------------------------

def call_function(name, args):
    if name == "get_weather":
        return get_weather(**args)
    #Here ** is used bcz we want to unpack the args as dictionary,
    #for more clarity use chat-gpt or next peice of code below

for tool_call in completion.choices[0].message.tool_calls:  #Go through every tool_call one at a time
    name = tool_call.function.name   #What is the name of the function the model wants me to call?
    args = json.loads(tool_call.function.arguments) 
    messages.append(completion.choices[0].message)  #Adding assistent msg to convertion history, as append add the info to the end of the list
                                                    #MEMORY part of basics
    result = call_function(name, args)
    messages.append(
        {"role":"tool", #Because we are model result produced by function and not system or user
         "tool_call_id":tool_call.id, 
         "content": json.dumps(result)} 
    )


# --------------------------------------------------------------
# Step 4: Supply result and call model again
# --------------------------------------------------------------

class WeatherResponse(BaseModel):
    temperature:float = Field(
        description= "The current temperature in celsius for current location."
    )
    response: str = Field(  #Field is not necessary but it gives llm idea on variable like temperature so that we can get close to good result like temperature not in farenhite
        description= "A natural language response to the user question"
    )  

completion_2 =  client.beta.chat.completions.parse(
    model = "gpt-4o",
    messages= messages,
    tools= tools,
    response_format= WeatherResponse,
)
#Here model did not decide to make the tool call bcz it
# already had the information in messages

# --------------------------------------------------------------
# Step 5: Check model response
# --------------------------------------------------------------

final_response = completion_2.choices[0].message.parsed
final_response.temperature 
final_response.response