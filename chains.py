import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate

load_dotenv()

# ----------------- Bedrock LLM Setup -----------------
llm = ChatBedrock(
    model_id="anthropic.claude-3-haiku-20240307-v1:0",
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# Story generation chain
story_prompt = PromptTemplate(
    input_variables=["mood"],
    template="User mood: {mood}\nWrite a short, creative story reflecting this mood."
)
story_chain = LLMChain(llm=llm, prompt=story_prompt, output_key="story")

# Activity generation chain
activity_prompt = PromptTemplate(
    input_variables=["mood"],
    template="User mood: {mood}\nSuggest 1-2 real-life activities matching this mood."
)
activity_chain = LLMChain(llm=llm, prompt=activity_prompt, output_key="activity")

# Combine chains
overall_chain = SequentialChain(
    chains=[story_chain, activity_chain],
    input_variables=["mood"],          # what you provide as input
    output_variables=["story", "activity"],  # what you want as output
    verbose=True
)

