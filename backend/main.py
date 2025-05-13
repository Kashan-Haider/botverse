from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database.db import create_db_and_tables
from users.routes import router as user_router
from chatbots.routes import router as chatbot_router

async def lifespan_handler():
    create_db_and_tables()
    yield


app = FastAPI(lifespan=lifespan_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"message": "Hello World"}

app.include_router(user_router, prefix="/users")
app.include_router(chatbot_router, prefix="/chatbots")
