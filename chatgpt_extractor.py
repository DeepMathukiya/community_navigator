from openai import OpenAI
from config import NVIDIA_API_KEY, NVIDIA_MODEL
import json
import re


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
        {pdf_text[:4000]}  # Limit to 4000 characters to avoid token limits
        
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
            temperature=0.5,
            max_tokens=1500,
            extra_body={
                "chat_template_kwargs": {"enable_thinking": True},
                "reasoning_budget": 1024
            }
        )
        
        # Extract the response text
        extracted_text = completion.choices[0].message.content.strip()
        
        # Parse JSON response
        # Try to find JSON in the response
        json_match = re.search(r'\{.*\}', extracted_text, re.DOTALL)
        if json_match:
            extracted_data = json.loads(json_match.group())
        else:
            extracted_data = json.loads(extracted_text)
        
        return extracted_data
        
    except json.JSONDecodeError as e:
        raise Exception(f"Error parsing API response as JSON: {str(e)}")
    except Exception as e:
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
    
    return validated_data
