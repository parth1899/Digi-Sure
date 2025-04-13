from groq import Groq
import instructor
from pydantic import BaseModel, Field
from typing import List, Optional
from config import Config
from datetime import datetime


class InsuranceExtraction(BaseModel):
    addons: List[str] = Field(default_factory=list, description="List of additional coverage options or riders")
    address: str = Field(..., description="Applicant's complete residential address")
    applicant_name: str = Field(..., description="Full name of the policy applicant")
    application_id: str = Field(..., description="Unique application/policy reference number")
    city: str = Field(..., description="City component of the address")
    created_at: datetime = Field(..., description="Policy creation date in ISO format")
    email: str = Field(..., description="Applicant's email address")
    idv: float = Field(..., description="Insured Declared Value of the vehicle")
    make: str = Field(..., description="Vehicle manufacturer brand name")
    mobile: str = Field(..., description="Applicant's contact phone number")
    model: str = Field(..., description="Vehicle model name/year variant")
    ncb: float = Field(..., description="No Claim Bonus percentage")
    policy_annual_premium: float = Field(..., description="Yearly insurance premium amount")
    policy_csl: str = Field(..., description="Compulsory Third Party Liability coverage details")
    registration_number: str = Field(..., description="Official vehicle registration number")
    state: str = Field(..., description="State component of the address")
    status: str = Field(..., description="Current policy status (active/pending/expired)")
    total_insurance_amount: float = Field(..., description="Total sum insured amount")
    umbrella_limit: float = Field(..., description="Additional coverage limit if applicable")
    updated_at: datetime = Field(..., description="Policy last update timestamp in ISO format")
    vehicle_type: str = Field(..., description="Type of vehicle (car/bike/commercial)")
    year: int = Field(..., description="Manufacturing year of the vehicle")

class DocumentProcessor:
    def __init__(self):
        self.groq_client = instructor.from_groq(
            Groq(api_key=Config.GROQ_API_KEY),
            mode=instructor.Mode.JSON
        )
    
    def process_extraction(self, ocr_text: str) -> InsuranceExtraction:
        """
        Processes OCR text from insurance documents to extract structured data
        """
        prompt = (
            "You are an expert insurance document parser. Extract structured data from the OCR text.\n"
            "Follow these rules:\n"
            "1. Convert all dates to ISO format (YYYY-MM-DD)\n"
            "2. Format phone numbers as country code + number (+91XXXXXXXXXX)\n"
            "3. Amounts should be converted to numerical values\n"
            "4. Vehicle registration numbers should be in all caps without spaces\n"
            "5. Handle missing fields by omitting them (don't invent data)\n\n"
            f"OCR TEXT:\n{ocr_text}"
        )

        try:
            response = self.groq_client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Extract insurance policy details from document text"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_model=InsuranceExtraction,
                max_retries=3
            )
            return response
        except Exception as e:
            print(f"Extraction Error: {str(e)}")
            return InsuranceExtraction()  # Return empty structure with validation errors