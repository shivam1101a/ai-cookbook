from typing import Optional #Optional means that our variable can have value or can be null
from datetime import datetime
from pydantic import BaseModel, Field
from openai import OpenAI
import os
import logging  #to record information about what is happening while it runs.

""" use https://www.anthropic.com/engineering/building-effective-agents for all patterns"""

# Set up logging configration
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = "gpt-4o"

# --------------------------------------------------------------
# Step 1: Define the data models for each stage
# --------------------------------------------------------------

class EventExtraction(BaseModel):
    """First LLM call: Extract basic event information"""

    description: str = Field(description="Raw description of the event")
    is_calender_event: bool = Field(
        description="Whether this text describe a calender event"
    )
    confidence_score: float = Field(description="Confidence score between 0 and 1")


class EventDetails(BaseModel):
    """Second LLM call: Parse specific event details"""

    name: str = Field(description="Name of the event")
    date: str = Field(
        description="Date and time of the event. Use ISO 8601 to format this value."
    )
    duration_minutes: int = Field(description="Expected duration in minutes")
    participants: list[str] = Field(description="List of participants")


class EventConfirmation(BaseModel):
    "Third LLM call: Generate confirmation message"

    confirmation_message: str = Field(
        description="Natural language confirmation message"
    )

    calender_link: Optional[str] = Field(
        description="Generate calender link if applicable"
    )

# --------------------------------------------------------------
# Step 2: Define the functions
# --------------------------------------------------------------

def extract_event_info(user_input: str) -> EventExtraction:
    """ First LLM call to determine if input is a calender event"""
    logger.info("Starting event extraction analysis")
    logger.debug(f"Input text: {user_input}")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model= model,
        messages=[
            {
                "role":"system",
                "content": f"{date_context} Analyze if the text describes a calender event.",
            },
            {
                "role": "user", "content" : user_input
            },
        ],
        response_format= EventExtraction,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Extraction complete - Is calender event: {result.is_calender_event}, Confidence: {result.confidence_score:.2f}"
    )
    return result

def parse_event_details(description: str) -> EventDetails:
    """Second LLM call to extract specific event details"""
    logger.info("Starting event details parsing")

    today = datetime.now()
    date_context = f"Today is {today.strftime('%A, %B %d, %Y')}."

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": f"{date_context} Extract detailed event information. When dates references 'next Tuesday' or similar relative dates, use this current date as reference.",
            },
            {"role": "user", "content": description},
        ],
        response_format=EventDetails,
    )
    result = completion.choices[0].message.parsed
    logger.info(
        f"Parsed event details - Name: {result.name}, Date: {result.date}, Duration: {result.duration_minutes}min"
    )
    logger.debug(f"Participants: {', '.join(result.participants)}")
    return result

def generate_confiramtion(event_details: EventDetails) -> EventConfirmation:
    """Third LLM call to generate a confirmation message"""
    logger.info("Generating confiramation message")

    completion = client.beta.chat.completions.parse(
        model=model,
        messages=[
            {
                "role": "system",
                "content": "Generate a natural confirmation message for the event. Sign of with your name; Susie",
            },
            {
                "role":"user", "content": str(event_details.model_dump())
            },
        ],
        response_format=EventConfirmation,
    )
    result = completion.choices[0].message.parsed
    logger.info("Confirmation message generated successfully")
    return result

# --------------------------------------------------------------
# Step 3: Chain the functions together
# --------------------------------------------------------------

def process_calender_request(user_input: str) -> Optional[EventConfirmation]:
    """Main function implementing the propmt chain with gate check"""
    logger.info("Processing calender request")
    logger.debug(f"Raw input: {user_input}")

    #First LLM call: extract basic info
    initial_extraction = extract_event_info(user_input)

    #Gate check: Verify if it's a calender event with sufficient confidence
    if (
        not initial_extraction.is_calender_event
        or initial_extraction.confidence_score < 0.7
    ):
        logger.warning(
            f"Gate check failed - is_calender_event: {initial_extraction.is_calender_event}, confidence: {initial_extraction.confidence_score:.2f}"
        )
        return None

    logger.info("Gate check passed, proceeding with event processing")

    # Second LLM call: Get detailed event information
    event_details = parse_event_details(initial_extraction.description)

    # Third LLM call: Generate confirmation
    confirmation = generate_confiramtion(event_details=)

    logger.info("Calender request processing completed successfully")
    return confirmation

# --------------------------------------------------------------
# Step 4: Test the chain with a valid input
# --------------------------------------------------------------

user_imput = "Let's schedule a 1h team meeting next Tuesday at 2pm with Alice and Bob to discuss the project roadmap."

result = process_calender_request(user_imput)
if result:
    print(f"Confirmation: {result.confirmation_message}")
    if result.calender_link:
        print(f"Calender Link: {result.calender_link}")
else:
    print("This doesn't appear to be a calender request.")


# --------------------------------------------------------------
# Step 5: Test the chain with an invalid input
# --------------------------------------------------------------

user_input = "Can you send an email to Alice and Bob to discuss the project roadmap?"

result = process_calender_request(user_imput)
if result:
    print(f"Confirmation: {result.confirmation_message}")
    if result.calender_link:
        print(f"Calender Link: {result.calender_link}")
else:
    print("This doesn't appear to be a calender request.")

