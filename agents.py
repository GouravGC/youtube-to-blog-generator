import os

from dotenv import load_dotenv
from crewai import Agent, LLM

load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

if not OPENROUTER_API_KEY:
    raise ValueError(
        "OPENROUTER_API_KEY missing in .env"
    )


my_llm = LLM(
    model="openrouter/openrouter/free",
    api_key=OPENROUTER_API_KEY,
    base_url="https://openrouter.ai/api/v1",
    temperature=0.2
)


blog_researcher = Agent(
    role="YouTube Video Researcher",

    goal=(
        "Carefully analyze the supplied YouTube transcript "
        "and identify its important concepts, explanations, "
        "examples, technical details and key takeaways."
    ),

    backstory=(
        "You are an experienced technical researcher specializing "
        "in Artificial Intelligence, Machine Learning, Data Science, "
        "Deep Learning and Generative AI. You extract meaningful "
        "knowledge from video transcripts without inventing facts."
    ),

    verbose=True,
    memory=False,
    tools=[],
    llm=my_llm,
    allow_delegation=False
)


blog_writer = Agent(
    role="Professional Technical Blog Writer",

    goal=(
        "Transform the research findings into a comprehensive, "
        "well-structured and engaging technical blog post."
    ),

    backstory=(
        "You are a professional technical content writer. "
        "You explain complex topics in clear language, use "
        "appropriate headings, practical examples and logical "
        "sections, while maintaining technical accuracy."
    ),

    verbose=True,
    memory=False,
    tools=[],
    llm=my_llm,
    allow_delegation=False
)