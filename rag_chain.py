# rag_chain.py
import os
import json
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain
from vectorstore import VectorStoreManager

load_dotenv()

class RAGGenerator:
    def __init__(self):
        # Bedrock LLM setup
        self.llm = ChatBedrock(
            model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
            region_name=os.getenv("AWS_DEFAULT_REGION"),
            aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
            aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
        )

        # Init vectorstore manager
        self.vectormanager = VectorStoreManager()

        # PromptTemplate
        self.prompt = PromptTemplate(
            input_variables=["context", "mood"],
            template=(
                "You are MoodAI. Use the 'context' (past mood journal entries) to personalize the output.\n\n"
                "Context:\n{context}\n\n"
                "Current mood: {mood}\n\n"
                "Task:\n1) Write a short creative story (2-4 short paragraphs) reflecting the user's current mood.\n"
                "2) Suggest 1-2 simple, real-life activities the user could do right now.\n\n"
                "Return a JSON object with keys: story (string), story_theme (string - short), activities (array of short strings).\n"
                "Only output valid JSON (no extra commentary)."
            )
        )

        # Wrap in an LLMChain
        self.llm_chain = LLMChain(llm=self.llm, prompt=self.prompt)

    def generate_with_rag(self, mood: str, k: int = 3):
        """
        Retrieve similar past moods from Chroma, format context, call LLM, parse JSON.
        Returns: (result_dict_or_text, retrieved_metadata_list)
        """
        docs = self.vectormanager.query_similar(mood, k=k)
        context = (
            "\n\n".join([f"{d.metadata.get('date_time')}: {d.page_content}" for d in docs])
            if docs else "No past moods available."
        )
        inputs = {"context": context, "mood": mood}

        # Call LLM
        try:
            llm_output = self.llm_chain.invoke(inputs)
            raw = next(iter(llm_output.values())) if isinstance(llm_output, dict) else str(llm_output)
        except Exception:
            formatted = self.prompt.format(context=context, mood=mood)
            resp = self.llm(formatted)
            raw = resp if isinstance(resp, str) else getattr(resp, "text", str(resp))

        # Parse JSON if possible
        try:
            parsed = json.loads(raw)
        except Exception:
            parsed = {"raw": raw}

        # Return parsed output and metadata
        retrieved_meta = [d.metadata for d in docs]
        return parsed, retrieved_meta
