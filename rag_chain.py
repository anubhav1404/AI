# rag_chain.py
import os
import json
from dotenv import load_dotenv
from langchain_aws import ChatBedrock
from vectorstore import init_vectorstore, query_similar
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain

load_dotenv()

# Bedrock LLM (same credentials as before)
llm = ChatBedrock(
    model_id=os.getenv("BEDROCK_MODEL_ID", "anthropic.claude-3-haiku-20240307-v1:0"),
    region_name=os.getenv("AWS_DEFAULT_REGION"),
    aws_access_key_id=os.getenv("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=os.getenv("AWS_SECRET_ACCESS_KEY")
)

# init vectordb (separate local instance)
VECTORD = init_vectorstore()

# PromptTemplate that expects "context" and "mood"
prompt = PromptTemplate(
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
llm_chain = LLMChain(llm=llm, prompt=prompt)

def generate_with_rag(mood: str, k: int = 3):
    """
    Retrieve similar past moods from Chroma, format context, call LLM, parse JSON.
    Returns: (result_dict_or_text, retrieved_metadata_list)
    """
    docs = query_similar(VECTORD, mood, k=k)
    context = "\n\n".join([f"{d.metadata.get('date_time')}: {d.page_content}" for d in docs]) if docs else "No past moods available."
    inputs = {"context": context, "mood": mood}

    # invoke chain
    # .invoke() returns a dict-like mapping to outputs in many langchain versions
    try:
        llm_output = llm_chain.invoke(inputs)
        # llm_chain.invoke may return the final text under the only output key
        # in some versions it's a raw string — handle both
        if isinstance(llm_output, dict):
            raw = next(iter(llm_output.values()))
        else:
            raw = str(llm_output)
    except Exception as e:
        # As fallback call llm directly with the formatted prompt
        formatted = prompt.format(context=context, mood=mood)
        resp = llm(formatted)  # ChatBedrock callable
        raw = resp if isinstance(resp, str) else getattr(resp, "text", str(resp))

    # Try parse JSON; if fails, return raw text
    parsed = None
    try:
        parsed = json.loads(raw)
    except Exception:
        parsed = {"raw": raw}

    # also return metadata for retrieved docs
    retrieved_meta = [d.metadata for d in docs]
    return parsed, retrieved_meta
