from fastapi import FastAPI, Header, HTTPException, Depends
from pydantic import BaseModel
from main import search
import uvicorn

def verify_api_key(key: str = Header(..., description="API Access Key")):
    """
    헤더에 포함된 API 키를 검증하는 함수입니다.
    키가 일치하지 않으면 403 에러를 반환합니다.
    """
    if key != "Art12@Body34":
        raise HTTPException(status_code=403, detail="Unauthorized: Invalid API Key")

# FastAPI 앱 인스턴스를 생성할 때 dependencies를 설정하여 모든 엔드포인트에 적용합니다.
app = FastAPI(dependencies=[Depends(verify_api_key)])

class SearchRequest(BaseModel):
    query: str
    include_blog: bool = True
    include_news: bool = True
    include_google: bool = True

@app.get("/")
def read_root():
    """
    서버 상태를 확인하기 위한 기본 경로입니다.
    """
    return {"status": "ok", "message": "Search API is running"}

@app.post("/search")
def search_endpoint(request: SearchRequest):
    """
    통합 검색 API 엔드포인트입니다.
    JSON Body를 통해 검색 파라미터를 받습니다.
    """
    # main.py에 있는 search 함수를 호출하여 결과를 가져옵니다.
    results = search(request.query, request.include_blog, request.include_news, request.include_google)
    return results

if __name__ == "__main__":
    # 이 파일이 직접 실행되면 uvicorn 서버를 8000번 포트에서 실행합니다.
    uvicorn.run(app, host="0.0.0.0", port=8000)
