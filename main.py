from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from pathlib import Path

from api import ( food_log_api, user_api, spent_naf_api, blood_test_api, patient_api, 
                 food_item_api, admin_api)

app = FastAPI()

app.include_router(user_api.router, prefix="/api/v0.1")
app.include_router(spent_naf_api.router, prefix="/api/v0.1")
app.include_router(blood_test_api.router, prefix="/api/v0.1")
app.include_router(food_log_api.router, prefix="/api/v0.1")
app.include_router(food_item_api.router, prefix="/api/v0.1")
app.include_router(patient_api.router, prefix="/api/v0.1")
app.include_router(admin_api.router, prefix="/api/v0.1")
origins = [
    "http://localhost:5173",
    "localhost:5173"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"]
)

BASE_DIR = Path(__file__).resolve().parent

# app.mount(
#     "/static",
#     StaticFiles(directory=BASE_DIR / "static"),
#     name="static"
# )

@app.get("/", tags=["Root"])
def read_root():
    """
    A simple root endpint to confirm that api is running
    """

    return { "message" : "Welcome to backend sever with line liff"}