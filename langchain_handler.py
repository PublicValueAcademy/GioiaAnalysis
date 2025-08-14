from langchain_openai import ChatOpenAI
from langchain_core.messages import SystemMessage, HumanMessage

from db.schema import settings, QACollection, MultipleSecondLevelThemes
from helper_functions import timing_wrapper

from typing import List




def create_llm() -> ChatOpenAI:
    """Initialize the LLM client."""
    return ChatOpenAI(
        model="gpt-5-nano",
        temperature=0,
        timeout=60,
        api_key=settings.OPENAI_API_KEY
    )


@timing_wrapper
def extract_qa_with_llm(text: str) -> QACollection:
    """Call LLM to extract QACollection from a single chunk."""
    prompt = """
    You are analyzing an interview transcript in order to 
    create a concept map/ table using the Gioia principle
    The transcript may not have clear Q/A labels.

    Task:
    1. Identify the interviewer and the interviewee.
    2. Identify all questions and answers.
    3. Return a list of QA items with:
       - question
       - question summary
       - answer
       - answer summary
       - keywords
       - concept_label - used later for second order themes
       - concept_reasoning - the reason you chose this theme
    """
    client = create_llm()
    structured_llm = client.with_structured_output(QACollection)
    messages = [SystemMessage(content=prompt), HumanMessage(content=text)]

    print("Calling LLM...")
    results = structured_llm.invoke(messages)
    print("LLM returned results")
    return results

@timing_wrapper
def create_second_level_themes(concepts: str) -> MultipleSecondLevelThemes:
    """create second level themes"""
    prompt = """
    You are an analyst proficient in the Gioia method for qualitative data analysis.
    You will be given a list of first-order concept labels. 
    Your task:
    1. Group related concept labels into **multiple second-order themes (depending on content).
    Do not merge all concepts into one theme.
    2. For each second-order theme:
        - Give it a short descriptive name.
        - Provide a brief explanation (reasoning) of why the concepts belong together.
        - Count how many concept labels are in the theme (this is the "weight").
    3. If applicable, group second-order themes into broader aggregate dimensions and name them.

    """
    structured_llm = create_llm().with_structured_output(MultipleSecondLevelThemes)
    messages = [SystemMessage(content=prompt), HumanMessage(content=concepts)]
    results = structured_llm.invoke(messages)
    return results

@timing_wrapper
def aggregate_normalise_themes(second_level_themes: str) -> MultipleSecondLevelThemes:
    print("Aggregating normalise themes...")
    """aggregate normalise themes"""
    prompt = """
    You are an analyst working with second-level themes from qualitative data analysis.

    Your task:
    1. You will be given a list of second-level themes, each with:
       - pattern_name
       - reasoning (a paragraph describing the theme)
       - weight (an integer)
       - broader_aggregate_dimensions (comma-separated)

    2. Identify themes that are small (weight=1 or low) or overlapping in meaning.

    3. Merge similar themes into a single theme:
       - Combine their reasoning text into one coherent explanation.
       - Sum the weights of merged themes to get the new weight.
       - Combine broader aggregate dimensions into a single list, removing duplicates.
       - Give the merged theme a clear, descriptive pattern_name.

    Make sure weights are recalculated correctly, reasoning is merged coherently, and dimensions have no duplicates.
    """
    structured_llm = create_llm().with_structured_output(MultipleSecondLevelThemes)
    messages = [SystemMessage(content=prompt), HumanMessage(content=second_level_themes)]
    results = structured_llm.invoke(messages)
    return results

