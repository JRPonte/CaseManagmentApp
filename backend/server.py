from fastapi import FastAPI, HTTPException, Depends, UploadFile, File, Form
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any, Union
from datetime import datetime, timedelta
import pymongo
import os
import uuid
import json
import jwt
from passlib.context import CryptContext
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Case Management System API")

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Database connection
MONGO_URL = os.environ.get('MONGO_URL', 'mongodb://localhost:27017')
client = pymongo.MongoClient(MONGO_URL)
db = client.case_management

# Security
security = HTTPBearer()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
SECRET_KEY = "your-secret-key-change-in-production"
ALGORITHM = "HS256"

# Pydantic Models
class User(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    username: str
    full_name: str
    email: str
    role: str  # citizen, lawyer, notary, bailiff, registrar, registrar_assistant, supervisor
    team: Optional[str] = None
    is_active: bool = True
    created_at: datetime = Field(default_factory=datetime.utcnow)

class CaseSubmission(BaseModel):
    case_type: str  # birth_registration, business_registration, land_registration
    submitter_data: Dict[str, Any]  # JSON data from form
    documents: List[str] = []  # Document file paths/URLs
    submitted_by: str  # User ID or email
    submitted_at: datetime = Field(default_factory=datetime.utcnow)

class Case(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    case_type: str
    case_number: str  # Auto-generated case number
    submitter_data: Dict[str, Any]
    documents: List[str] = []
    status: str = "submitted"  # submitted, assigned, under_review, pending_documents, approved, rejected
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None
    workflow_history: List[Dict[str, Any]] = []
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class WorkflowAction(BaseModel):
    case_id: str
    action: str  # assign, review, approve, reject, request_documents
    comment: Optional[str] = None
    assigned_to: Optional[str] = None
    assigned_team: Optional[str] = None

class LoginRequest(BaseModel):
    username: str
    password: str

# Authentication functions
def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(hours=24)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt

def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Invalid authentication credentials")
        user = db.users.find_one({"username": username})
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Invalid authentication credentials")

# Initialize default users if not exists
def init_default_users():
    default_users = [
        {"username": "admin", "password": "admin123", "full_name": "Administrator", "email": "admin@system.com", "role": "supervisor"},
        {"username": "registrar1", "password": "reg123", "full_name": "Main Registrar", "email": "registrar@system.com", "role": "registrar"},
        {"username": "assistant1", "password": "ass123", "full_name": "Registrar Assistant", "email": "assistant@system.com", "role": "registrar_assistant"},
        {"username": "lawyer1", "password": "law123", "full_name": "Legal Advisor", "email": "lawyer@system.com", "role": "lawyer"},
    ]
    
    for user_data in default_users:
        if not db.users.find_one({"username": user_data["username"]}):
            user = User(
                username=user_data["username"],
                full_name=user_data["full_name"],
                email=user_data["email"],
                role=user_data["role"]
            )
            user_dict = user.dict()
            user_dict["password"] = pwd_context.hash(user_data["password"])
            db.users.insert_one(user_dict)
            logger.info(f"Created default user: {user_data['username']}")

# Generate case number
def generate_case_number(case_type: str):
    year = datetime.utcnow().year
    prefix_map = {
        "birth_registration": "BR",
        "business_registration": "BUS",
        "land_registration": "LAND"
    }
    prefix = prefix_map.get(case_type, "CASE")
    
    # Get count of cases this year for this type
    count = db.cases.count_documents({
        "case_type": case_type,
        "created_at": {"$gte": datetime(year, 1, 1)}
    })
    
    return f"{prefix}-{year}-{count + 1:04d}"

# API Endpoints

@app.post("/api/auth/login")
async def login(login_data: LoginRequest):
    user = db.users.find_one({"username": login_data.username})
    if not user or not pwd_context.verify(login_data.password, user["password"]):
        raise HTTPException(status_code=401, detail="Incorrect username or password")
    
    access_token = create_access_token(data={"sub": user["username"]})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user["id"],
            "username": user["username"],
            "full_name": user["full_name"],
            "role": user["role"]
        }
    }

@app.post("/api/cases/submit")
async def submit_case(case_submission: CaseSubmission):
    """Endpoint for front-office to submit cases"""
    try:
        case = Case(
            case_type=case_submission.case_type,
            case_number=generate_case_number(case_submission.case_type),
            submitter_data=case_submission.submitter_data,
            documents=case_submission.documents,
            workflow_history=[{
                "action": "submitted",
                "timestamp": datetime.utcnow(),
                "comment": "Case submitted from front-office"
            }]
        )
        
        case_dict = case.dict()
        db.cases.insert_one(case_dict)
        
        logger.info(f"New case submitted: {case.case_number}")
        return {"success": True, "case_id": case.id, "case_number": case.case_number}
    except Exception as e:
        logger.error(f"Error submitting case: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/cases")
async def get_cases(current_user: dict = Depends(get_current_user)):
    """Get cases based on user role and assignments"""
    filter_query = {}
    
    # Role-based filtering
    if current_user["role"] in ["registrar_assistant", "lawyer", "notary", "bailiff"]:
        filter_query["$or"] = [
            {"assigned_to": current_user["id"]},
            {"status": "submitted"}  # Unassigned cases
        ]
    elif current_user["role"] == "registrar":
        # Registrars can see all cases
        pass
    elif current_user["role"] == "supervisor":
        # Supervisors can see all cases
        pass
    
    cases = list(db.cases.find(filter_query).sort("created_at", -1))
    
    # Convert ObjectId to string and format dates
    for case in cases:
        case["_id"] = str(case["_id"])
        case["created_at"] = case["created_at"].isoformat()
        case["updated_at"] = case["updated_at"].isoformat()
    
    return cases

@app.get("/api/cases/{case_id}")
async def get_case(case_id: str, current_user: dict = Depends(get_current_user)):
    """Get specific case details"""
    case = db.cases.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Check access permissions
    can_access = (
        current_user["role"] in ["registrar", "supervisor"] or
        case.get("assigned_to") == current_user["id"] or
        case["status"] == "submitted"
    )
    
    if not can_access:
        raise HTTPException(status_code=403, detail="Access denied")
    
    case["_id"] = str(case["_id"])
    case["created_at"] = case["created_at"].isoformat()
    case["updated_at"] = case["updated_at"].isoformat()
    
    return case

@app.post("/api/cases/{case_id}/workflow")
async def update_case_workflow(case_id: str, workflow_action: WorkflowAction, current_user: dict = Depends(get_current_user)):
    """Update case workflow"""
    case = db.cases.find_one({"id": case_id})
    if not case:
        raise HTTPException(status_code=404, detail="Case not found")
    
    # Prepare workflow history entry
    workflow_entry = {
        "action": workflow_action.action,
        "timestamp": datetime.utcnow(),
        "performed_by": current_user["id"],
        "performed_by_name": current_user["full_name"],
        "comment": workflow_action.comment
    }
    
    # Update case based on action
    update_data = {
        "updated_at": datetime.utcnow(),
        "$push": {"workflow_history": workflow_entry}
    }
    
    if workflow_action.action == "assign":
        update_data["assigned_to"] = workflow_action.assigned_to
        update_data["status"] = "assigned"
    elif workflow_action.action == "review":
        update_data["status"] = "under_review"
    elif workflow_action.action == "approve":
        update_data["status"] = "approved"
    elif workflow_action.action == "reject":
        update_data["status"] = "rejected"
    elif workflow_action.action == "request_documents":
        update_data["status"] = "pending_documents"
    
    db.cases.update_one({"id": case_id}, {"$set": update_data})
    
    return {"success": True, "message": f"Case {workflow_action.action} successfully"}

@app.get("/api/users")
async def get_users(current_user: dict = Depends(get_current_user)):
    """Get users for assignment"""
    if current_user["role"] not in ["registrar", "supervisor"]:
        raise HTTPException(status_code=403, detail="Access denied")
    
    users = list(db.users.find({"is_active": True}, {"password": 0}))
    for user in users:
        user["_id"] = str(user["_id"])
        user["created_at"] = user["created_at"].isoformat()
    
    return users

@app.get("/api/dashboard/stats")
async def get_dashboard_stats(current_user: dict = Depends(get_current_user)):
    """Get dashboard statistics"""
    stats = {}
    
    # Total cases by status
    pipeline = [
        {"$group": {"_id": "$status", "count": {"$sum": 1}}}
    ]
    status_counts = list(db.cases.aggregate(pipeline))
    stats["by_status"] = {item["_id"]: item["count"] for item in status_counts}
    
    # Cases by type
    pipeline = [
        {"$group": {"_id": "$case_type", "count": {"$sum": 1}}}
    ]
    type_counts = list(db.cases.aggregate(pipeline))
    stats["by_type"] = {item["_id"]: item["count"] for item in type_counts}
    
    # My assigned cases
    if current_user["role"] not in ["supervisor"]:
        my_cases = db.cases.count_documents({"assigned_to": current_user["id"]})
        stats["my_assigned"] = my_cases
    
    return stats

# Initialize on startup
@app.on_event("startup")
async def startup_event():
    init_default_users()
    logger.info("Case Management System API started")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)