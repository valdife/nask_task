from fastapi import FastAPI

app = FastAPI(title="NASK Task", description="NASK Task")


@app.get("/")
def read_root():
    return {"message": "Hello, World!"}
