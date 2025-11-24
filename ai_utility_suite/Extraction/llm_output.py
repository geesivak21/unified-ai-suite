from .schema import MultiDocumentInformation
from openai import AzureOpenAI


def extract_with_llm_structured(raw_text: str,
                                client_llm: AzureOpenAI,
                                deployment_name: str) -> MultiDocumentInformation:
    """
    Extract structured document information using Azure OpenAI with Pydantic schema enforcement.
    """
    completion = client_llm.beta.chat.completions.parse(
        model=deployment_name,
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an intelligent document information extractor. "
                    "Analyze the text and extract all relevant structured fields."
                )
            },
            {
                "role": "user",
                "content": f"Extract all relevant information from the following document text:\n{raw_text}"
            },
        ],
        response_format=MultiDocumentInformation,  # 👈 key point
        temperature=0.2,
    )

    parsed = completion.choices[0].message.parsed  # Typed Pydantic model
    return parsed.model_dump()
