from groq import Groq
import instructor
from pydantic import BaseModel, Field
from typing import List, Optional, Literal
from config import Config
from datetime import datetime, date


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

class ClaimExtraction(BaseModel):
    status: Literal['In Progress'] = Field(
        default='In Progress', 
        description="Current status of the claim"
    )
    last_updated_date: datetime = Field(
        default_factory=datetime.utcnow,
        description="Last updated timestamp in ISO format"
    )
    collision_type: Optional[Literal['Side Collision', 'Rear Collision', 'Front Collision']] = Field(
        None,
        description="Type of collision if applicable"
    )
    incident_type: Literal[
        'Single Vehicle Collision', 
        'Multi-vehicle Collision', 
        'Vehicle Theft', 
        'Parked Car'
    ] = Field(..., description="Type of incident")
    id: str = Field(..., alias="claim_id", description="Unique claim identifier")
    severity: Literal[
        'Major Damage', 
        'Minor Damage', 
        'Total Loss', 
        'Trivial Damage'
    ] = Field(..., description="Severity of the damage")
    total_claim_amount: float = Field(..., description="Total claim amount requested")
    injury_claim_amount: float = Field(..., description="Amount claimed for injuries")
    property_claim_amount: float = Field(..., description="Amount claimed for property damage")
    vehicle_claim_amount: float = Field(..., description="Amount claimed for vehicle damage")
    date: datetime = Field(..., description="Date of the incident in ISO format")
    time: str = Field(..., description="Time of the incident in HH:MM format (24-hour)")
    location: str = Field(..., description="Location where the incident occurred")
    city: str = Field(..., description="City of the incident")
    no_of_vehicles_involved: int = Field(
        ..., 
        ge=1,
        description="Number of vehicles involved (minimum 1)"
    )
    no_of_witnesses: int = Field(
        ..., 
        ge=0,
        description="Number of witnesses reported (non-negative)"
    )
    property_damage: Literal['Yes', 'No'] = Field(
        ..., 
        description="Indicates if property damage occurred"
    )
    bodily_injuries: Literal['Yes', 'No'] = Field(
        ..., 
        description="Indicates if there were bodily injuries"
    )
    police_report: Literal['Yes', 'No'] = Field(
        ..., 
        description="Indicates if a police report was filed"
    )
    authorities_contacted: List[Literal['Police', 'Fire', 'Ambulance', 'Others']] = Field(
        ..., 
        description="List of authorities contacted"
    )
    incident_description: str = Field(
        ..., 
        description="Detailed description of the incident"
    )


class DocumentProcessor:
    def __init__(self):
        self.groq_client = instructor.from_groq(
            Groq(api_key=Config.GROQ_API_KEY),
            mode=instructor.Mode.JSON
        )
    
    def process_insurance_extraction(self, ocr_text: str) -> InsuranceExtraction:
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
            "5. You can choose the add ons only from these labels: [Zero Depreciation, Engine Protection, Roadside Assistance, Consumables Cover, Personal Accident Cover]. If none of the add ons match, return an empty list.\n"
            "6. Always return the status as 'Pending'.\n"
            "7. Handle missing fields by omitting them (don't invent data)\n\n"
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
        

    def process_claim_extraction(self, ocr_text: str) -> ClaimExtraction:
        """
        Processes OCR text from claim documents to extract structured data
        """
        prompt = (
            "You are an expert claims document parser. Extract structured data from the OCR text.\n"
            "Follow these rules:\n"
            "1. Convert dates to ISO format (YYYY-MM-DD)\n"
            "2. Format time as HH:MM in 24-hour format\n"
            "3. For incident_type, use only: Single Vehicle Collision, Multi-vehicle Collision, Vehicle Theft, Parked Car\n"
            "4. For collision_type, use only if applicable: Side Collision, Rear Collision, Front Collision\n"
            "5. severity must be one of: Major Damage, Minor Damage, Total Loss, Trivial Damage\n"
            "6. Answer Yes/No for property_damage, bodily_injuries, police_report\n"
            "7. authorities_contacted can include: Police, Fire, Ambulance, Others\n"
            "8. Always set status to 'In Progress'\n"
            "9. last_updated_date should be current UTC datetime\n"
            "10. If information is missing, omit the field (do not guess)\n\n"
            f"OCR TEXT:\n{ocr_text}"
        )

        try:
            response = self.groq_client.chat.completions.create(
                model=Config.GROQ_MODEL,
                messages=[
                    {"role": "system", "content": "Extract claim details from document text"},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                response_model=ClaimExtraction,
                max_retries=3
            )
            return response
        except Exception as e:
            print(f"Claim Extraction Error: {str(e)}")
            return ClaimExtraction(
                incident_type="Single Vehicle Collision",  # Required field
                id="ERROR",
                severity="Minor Damage",
                total_claim_amount=0.0,
                injury_claim_amount=0.0,
                property_claim_amount=0.0,
                vehicle_claim_amount=0.0,
                date=date.today(),
                time="00:00",
                location="N/A",
                city="N/A",
                no_of_vehicles_involved=1,
                no_of_witnesses=0,
                property_damage="No",
                bodily_injuries="No",
                police_report="No",
                authorities_contacted=["Police"],
                incident_description="Error processing claim"
            )