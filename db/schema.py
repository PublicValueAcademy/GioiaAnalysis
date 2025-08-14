from pydantic_settings import BaseSettings, \
    SettingsConfigDict
from pydantic import BaseModel, Field
from pathlib import Path
from typing import List

class Settings(BaseSettings):
    OPENAI_API_KEY: str
    BASE_DIR: Path = Path(__file__).parent.parent


    model_config = SettingsConfigDict(
        env_file= BASE_DIR / ".env",
        env_file_encoding="utf-8",
        extra='ignore'
    )

settings = Settings()




class QAItem(BaseModel):

    question: str = Field(description="Question text")
    question_summary: str = Field(description="Question summary")
    answer: str = Field(description="Answer text")
    answer_summary: str= Field(description="Answer summary")
    keywords: List[str]= Field(description="Keywords")
    concept_label: str =Field(description="Concept label")
    concept_reasoning: str =Field(description="Concept reasoning")

class QACollection(BaseModel):
    interviewer:str
    interviewee:str
    items: List[QAItem]

class SecondLevelThemes(BaseModel):
    pattern_name:str = Field(description="Descriptive name for the pattern")
    reasoning: List[str] = Field(description="Descriptive name for the reasoning")
    weight: int = Field(description="Weight of the pattern")
    broader_aggregate_dimensions: List[str] = Field(description="Broader aggregate dimensions")

class MultipleSecondLevelThemes(BaseModel):
    themes: List[SecondLevelThemes] = Field(description="List of second-order themes")