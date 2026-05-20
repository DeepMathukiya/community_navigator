from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_MODEL
import json
import re
from logger_config import get_logger

logger = get_logger(__name__)


def extract_information_from_pdf(pdf_text: str) -> dict:
    """
    Use NVIDIA Nemotron API to extract specific information from PDF text
    
    Args:
        pdf_text: Extracted text from PDF
        
    Returns:
        dict: Extracted information including summary, eligibility, benefits, etc.
    """
    try:
        if not NVIDIA_API_KEY:
            logger.error("NVIDIA_API_KEY not configured")
            raise Exception("NVIDIA_API_KEY not configured. Please set it in .env file")
        
        # Initialize NVIDIA API client
        client = OpenAI(
            base_url="https://integrate.api.nvidia.com/v1",
            api_key=NVIDIA_API_KEY
        )
        
        prompt = f"""
        Please analyze the following PDF text and extract the following information in JSON format:
        1. summary: A brief summary of the document (2-3 sentences)
        2. eligibility: Eligibility criteria (list of requirements)
        3. benefits: Benefits provided (list of benefits)
        4. apply_date: Application deadline or date if mentioned
        5. application_process: Step-by-step application process
        
        If any information is not available in the document, use "Not mentioned" or "N/A".
        
        PDF Text:
        {pdf_text}  # Limit to 4000 characters to avoid token limits
        
        Please respond ONLY with valid JSON format, no additional text.
        """
        
        # Call NVIDIA Nemotron API (non-streaming)
        completion = client.chat.completions.create(
            model=NVIDIA_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that extracts structured information from documents. Always respond with valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            extra_body={
                "chat_template_kwargs": {"enable_thinking": True},
            }
        )
        
        # Extract the response text
        extracted_text = completion.choices[0].message.content.strip()
        logger.info("API response received %s", extracted_text)
        
        # Parse JSON response robustly
        # Try direct load first
        try:
            return json.loads(extracted_text)
        except json.JSONDecodeError:
            # Attempt to extract JSON substring
            json_match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
            if not json_match:
                logger.exception("No JSON object found in API response")
                raise

            json_str = json_match.group()

            # Remove non-printable/control characters which can break json parsing
            cleaned = re.sub(r'[\x00-\x1f]+', ' ', json_str)

            # Remove trailing commas in objects/arrays to improve chances of parsing
            cleaned = re.sub(r',\s*}', '}', cleaned)
            cleaned = re.sub(r',\s*\]', ']', cleaned)

            try:
                extracted_data = json.loads(cleaned)
                return extracted_data
            except json.JSONDecodeError as e2:
                logger.exception("Failed to parse cleaned JSON response")
                raise
        
    except json.JSONDecodeError as e:
        logger.exception("JSON decode error when parsing API response")
        raise Exception(f"Error parsing API response as JSON: {str(e)}")
    except Exception as e:
        logger.exception("Error extracting information from PDF")
        raise Exception(f"Error extracting information from PDF: {str(e)}")


def validate_extracted_data(data: dict) -> dict:
    """
    Validate and ensure all required fields are present
    
    Args:
        data: Extracted data dictionary
        
    Returns:
        dict: Validated data with default values for missing fields
    """
    required_fields = {
        'summary': 'Not mentioned',
        'eligibility': 'Not mentioned',
        'benefits': 'Not mentioned',
        'apply_date': 'Not mentioned',
        'application_process': 'Not mentioned'
    }
    
    validated_data = required_fields.copy()
    
    for field, default_value in required_fields.items():
        if field in data and data[field]:
            validated_data[field] = data[field]
    logger.debug("Validated extracted data fields: %s", ",".join(k for k in validated_data.keys()))
    return validated_data
