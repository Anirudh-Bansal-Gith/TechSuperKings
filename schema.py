from enum import Enum
from pydantic import BaseModel, Field


class Department(str, Enum):
    AGRICULTURE = "Agriculture and Farmers Welfare"
    ANIMAL_HUSBANDRY = "Animal Husbandry and Fisheries"
    CIVIL_SUPPLIES = "Civil Supplies and Consumer Affairs"
    EDUCATION = "Education"
    ELECTRICITY = "Electricity and Power"
    ENVIRONMENT = "Environment and Forest"
    FINANCE = "Finance and Treasury"
    FOOD_PROCESSING = "Food Processing"
    HEALTH = "Health and Family Welfare"
    HOME = "Home Affairs and Police"
    HOUSING = "Housing and Urban Development"
    INDUSTRIES = "Industries and Commerce"
    IT = "Information Technology"
    LABOUR = "Labour and Employment"
    LAND_REVENUE = "Land Revenue and Registration"
    PANCHAYATI_RAJ = "Panchayati Raj and Rural Development"
    PWD = "Public Works Department (PWD)"
    PUBLIC_HEALTH_ENGINEERING = "Public Health Engineering"
    TRANSPORT = "Road Transport and Highways"
    SOCIAL_WELFARE = "Social Welfare and Social Justice"
    TRIBAL_WELFARE = "Tribal Welfare"
    MUNICIPAL = "Urban Local Bodies and Municipal Administration"
    WATER_RESOURCES = "Water Resources and Irrigation"
    WOMEN_CHILD = "Women and Child Development"
    YOUTH_SPORTS = "Youth Affairs and Sports"
    RAILWAYS = "Railways"
    POSTAL = "Postal Services"
    TELECOMMUNICATIONS = "Telecommunications"
    DEFENCE = "Defence"
    OTHER = "Other"


class Schema(BaseModel):
    query_description: str
    department: Department
    importance_score: int = Field(ge=-100, le=100)

class UserInfo(BaseModel):
    name: str
    phone: str
    address: str