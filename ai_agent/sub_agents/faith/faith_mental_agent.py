from google.adk.agents import Agent
from . import prompt

# Define the Faith / Mental Guidance Agent with full prompt as instruction
faith_mental_agent = Agent(
    model='gemini-2.0-flash',
    name='faith_mental_agent',
    description='Provides basketball-specific mental guidance, motivation, habit-building, and optional Christian reflections.',
    instruction=prompt.FAITH_PROMPT
)


