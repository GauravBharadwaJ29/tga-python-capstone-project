from fastapi.responses import JSONResponse

def custom_error(message: str, code: int = 400):
    return JSONResponse(
        status_code=code,
        content={"error": {"code": code, "message": message}}
    )

