from database import engine, Base
from models import Complaint, ComplaintAttachment

Base.metadata.create_all(bind=engine)