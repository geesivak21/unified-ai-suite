# Import the necessary libraries 
from openai import AzureOpenAI
from config import (openai_api_key, openai_api_version, 
                    openai_deployment_name, openai_endpoint)

# Instantiate the Azure OpenAI client
client = AzureOpenAI(
    api_key=openai_api_key,
    api_version=openai_api_version,
    azure_endpoint=openai_endpoint
)
# Define the function to generate transcripts from OpenAI
def get_transcripts(output_file_path:str) -> str:
    """
    Returns the transcript of a meeting using OpenAI model.
    Args:
        output_file_path (str): The file path for the output audio in .webm format.
    Returns:
        str: Transcript of the meeting.
    """
    with open(output_file_path, "rb") as f:
        transcript = client.audio.transcriptions.create(
            model=openai_deployment_name,  # whipser 1
            file=f,
            temperature=0,
            language="en"
        )

    transcript_text = transcript.text

    print(f"Transcription: {transcript_text}")
    return transcript_text

