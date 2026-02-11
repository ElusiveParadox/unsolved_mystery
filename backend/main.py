from fastapi import FastAPI, UploadFile, File, HTTPException, Depends
from fastapi.security import OAuth2PasswordBearer
import os
import shutil
import time

from dotenv import load_dotenv
from schemas import QueryRequest, QueryResponse, UserAuth, TokenResponse
from rag_engine import query_rag, build_index
from db import SessionLocal, User, Chat, init_db
from auth import hash_password, verify_password, create_token, decode_token

load_dotenv()

app = FastAPI(title="Cold Case Detective API")
init_db()

@app.get("/healthz")
def health():
    return {"status": "ok"}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

EVIDENCE_FOLDER = "evidence"
os.makedirs(EVIDENCE_FOLDER, exist_ok=True)

USER_LIMIT = 15
reset_time = time.time() + 86400


def get_current_user(token: str = Depends(oauth2_scheme)):
    username = decode_token(token)
    if not username:
        raise HTTPException(status_code=401, detail="Invalid token")
    return username


@app.post("/register")
async def register(user: UserAuth):
    db = SessionLocal()

    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(status_code=400, detail="User exists")

    new_user = User(
        username=user.username,
        password_hash=hash_password(user.password),
        daily_count=0
    )

    db.add(new_user)
    db.commit()

    return {"status": "registered"}


@app.post("/login", response_model=TokenResponse)
async def login(user: UserAuth):
    db = SessionLocal()
    u = db.query(User).filter(User.username == user.username).first()

    if not u or not verify_password(user.password, u.password_hash):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = create_token(u.username)
    return {"access_token": token, "token_type": "bearer"}


@app.get("/quota")
async def quota(username: str = Depends(get_current_user)):
    db = SessionLocal()
    u = db.query(User).filter(User.username == username).first()

    return {
        "used": u.daily_count,
        "remaining": USER_LIMIT - u.daily_count
    }


@app.get("/history")
async def history(username: str = Depends(get_current_user)):
    db = SessionLocal()

    chats = (
        db.query(Chat)
        .filter(Chat.username == username)
        .order_by(Chat.id.desc())
        .limit(5)
        .all()
    )

    return [
        {"question": c.question, "answer": c.answer}
        for c in reversed(chats)
    ]


@app.post("/upload")
async def upload_file(
    file: UploadFile = File(...),
    username: str = Depends(get_current_user)
):
    filepath = os.path.join(EVIDENCE_FOLDER, file.filename)

    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    build_index()

    return {"status": "uploaded", "filename": file.filename}


@app.post("/ask", response_model=QueryResponse)
async def ask_question(
    req: QueryRequest,
    username: str = Depends(get_current_user)
):
    global reset_time
    db = SessionLocal()

    if time.time() > reset_time:
        for u in db.query(User).all():
            u.daily_count = 0
        db.commit()
        reset_time = time.time() + 86400

    u = db.query(User).filter(User.username == username).first()

    if u.daily_count >= USER_LIMIT:
        raise HTTPException(status_code=429, detail="Daily limit reached")

    u.daily_count += 1
    db.commit()

    answer, citations, chunks = query_rag(req.question)

    chat = Chat(username=username, question=req.question, answer=answer)
    db.add(chat)
    db.commit()

    all_chats = (
        db.query(Chat)
        .filter(Chat.username == username)
        .order_by(Chat.id.desc())
        .all()
    )

    if len(all_chats) > 5:
        for old_chat in all_chats[5:]:
            db.delete(old_chat)
        db.commit()

    return QueryResponse(answer=answer, citations=citations, chunks=chunks)


@app.delete("/history")
async def clear_history(username: str = Depends(get_current_user)):
    db = SessionLocal()
    db.query(Chat).filter(Chat.username == username).delete()
    db.commit()
    return {"status": "cleared"}
