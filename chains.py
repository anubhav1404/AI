# chains.py
import os
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain.chains import LLMChain, SequentialChain
from langchain.prompts import PromptTemplate

load_dotenv()

class StoryActivityGenerator:
    def __init__(self):
        self.llm = ChatBedrock(
            model_id="anthropic.claude-3-haiku-20240307-v1:0",
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

        # Story chain
        story_prompt = PromptTemplate(
            input_variables=["mood"],
            template="User mood: {mood}\nWrite a short, creative story reflecting this mood."
        )
        story_chain = LLMChain(llm=self.llm, prompt=story_prompt, output_key="story")

        # Activity chain
        activity_prompt = PromptTemplate(
            input_variables=["mood"],
            template="User mood: {mood}\nSuggest 1-2 real-life activities matching this mood."
        )
        activity_chain = LLMChain(llm=self.llm, prompt=activity_prompt, output_key="activity")

        # Sequential chain
        self.chain = SequentialChain(
            chains=[story_chain, activity_chain],
            input_variables=["mood"],
            output_variables=["story", "activity"],
            verbose=True
        )

    def generate(self, mood: str):
        return self.chain.invoke({"mood": mood})
