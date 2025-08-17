import glob
import shutil
from pathlib import Path
from docx import Document
from typing import List

from db.schema import settings, QAItem, QACollection
from langchain_handler import extract_qa_with_llm
from helper_functions import timing_wrapper, store_data_in_json
# ----------------------------
# Globals
# ----------------------------
all_interview_data: List[dict] = []




def get_list_of_files_to_process() -> List[str]:
    """Return list of DOCX files in the '01_to_process' folder."""
    to_process = settings.BASE_DIR / "01_to_process"
    return glob.glob(f"{to_process}/*.docx")


@timing_wrapper
def get_content_from_file(filename: str) -> str:
    """Read all text from a DOCX file."""
    print(f"Getting content from {Path(filename).name}")
    doc = Document(filename)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)


def chunk_text(text: str, max_words: int = 1000):
    """Yield chunks of text up to max_words words each."""
    words = text.split()
    for i in range(0, len(words), max_words):
        yield " ".join(words[i:i + max_words])





def extract_qa_in_chunks(full_text: str, chunk_size: int = 1000) -> QACollection:
    """Process large transcripts in chunks and merge results into one QACollection."""
    all_items: List[QAItem] = []
    interviewer = None
    interviewee = None

    for chunk in chunk_text(full_text, max_words=chunk_size):
        chunk_result = extract_qa_with_llm(chunk)

        if interviewer is None:
            interviewer = chunk_result.interviewer
            interviewee = chunk_result.interviewee

        all_items.extend(chunk_result.items)

    return QACollection(
        interviewer=interviewer,
        interviewee=interviewee,
        items=all_items
    )


def move_file_after_processing(filename: str):
    """Move processed file to '02_processed' folder."""
    print("Moving file after processing...")
    dest_folder = settings.BASE_DIR / "02_processed"
    dest_folder.mkdir(exist_ok=True)
    dest_path = dest_folder / Path(filename).name
    shutil.move(filename, dest_path)


def store_data(structured_data: QACollection):
    """Append QACollection to global list for later JSON export."""
    print("Storing data...")
    all_interview_data.append(structured_data.model_dump())





def main():
    files = get_list_of_files_to_process()
    for file in files:
        print("-" * 40)
        print(f"Processing {Path(file).name}")
        content = get_content_from_file(file)
        structured_content = extract_qa_in_chunks(content, chunk_size=1000)
        store_data(structured_content)
        move_file_after_processing(file)
        print("-" * 40)

    store_data_in_json(filename="all_interviews", data=all_interview_data)
    print("All files processed!")


if __name__ == "__main__":
    main()