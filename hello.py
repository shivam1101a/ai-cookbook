from dotenv import load_dotenv
import os

load_dotenv()  # This loads the .env file

# Test if it works
print(os.getenv("API_KEY"))


print("hello")
