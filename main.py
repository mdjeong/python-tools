import os
import requests
import json
from dotenv import load_dotenv

# .env 파일에서 환경변수를 불러옵니다. (API 키 등 비밀 정보를 담고 있는 파일)
load_dotenv()

# 환경변수에서 네이버와 구글 API 인증 정보를 가져와 변수에 저장합니다.
NAVER_CLIENT_ID = os.getenv("NAVER_CLIENT_ID")
NAVER_CLIENT_SECRET = os.getenv("NAVER_CLIENT_SECRET")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
GOOGLE_SEARCH_ENGINE_ID = os.getenv("GOOGLE_SEARCH_ENGINE_ID")

def search_naver(query, search_type="blog"):
    """
    네이버 블로그나 뉴스를 검색하는 함수입니다.
    query: 검색할 단어 (예: "맛집")
    search_type: "blog"(블로그) 또는 "news"(뉴스) 중 하나를 선택합니다.
    """
    # 블로그 검색인지 뉴스 검색인지에 따라 요청할 주소(URL)와 출처 이름을 설정합니다.
    if search_type == "blog":
        url = "https://openapi.naver.com/v1/search/blog.json"
        source_label = "naver_blog"
    elif search_type == "news":
        url = "https://openapi.naver.com/v1/search/news.json"
        source_label = "naver_news"
    else:
        # 블로그나 뉴스가 아니면 빈 리스트([])를 반환하고 함수를 종료합니다.
        return []

    # 네이버 API에 전송할 헤더 정보입니다. 클라이언트 아이디와 비밀번호를 포함합니다.
    headers = {
        "X-Naver-Client-Id": NAVER_CLIENT_ID,
        "X-Naver-Client-Secret": NAVER_CLIENT_SECRET
    }
    # 네이버 API에 전송할 검색 파라미터입니다.
    params = {
        "query": query,  # 검색어
        "display": 5     # 한 번에 가져올 검색 결과 개수 (여기서는 5개로 설정)
    }

    try:
        # 설정한 주소, 헤더, 파라미터로 네이버에 데이터를 요청(GET)합니다.
        response = requests.get(url, headers=headers, params=params)
        
        # 요청이 성공했는지 확인합니다. 실패했다면 에러를 발생시킵니다.
        response.raise_for_status()
        
        # 응답받은 데이터를 JSON 형식(파이썬 딕셔너리 형태)으로 변환합니다.
        data = response.json()
        
        results = []
        # 가져온 데이터에 "items"라는 항목이 있다면 반복문을 통해 하나씩 처리합니다.
        if "items" in data:
            for item in data["items"]:
                # 각 검색 결과에서 필요한 정보(제목, 내용, 링크)만 뽑아서 리스트에 추가합니다.
                # 참고: 네이버 검색 결과에는 <b> 태그 같은 HTML 태그가 포함될 수 있습니다.
                results.append({
                    "source": source_label,        # 출처 (naver_blog 또는 naver_news)
                    "title": item.get("title"),    # 제목
                    "content": item.get("description"), # 내용 요약
                    "url": item.get("link") or item.get("originallink") # 링크 (뉴스는 originallink가 있을 수 있음)
                })
        # 정리된 결과 리스트를 반환합니다.
        return results
    except Exception as e:
        # 에러가 발생하면 에러 내용을 출력하고, 빈 리스트를 반환합니다.
        print(f"네이버 검색 중 오류 발생 ({search_type}): {e}")
        return []

def search_google(query):
    """
    구글 커스텀 검색(Google Custom Search)을 수행하는 함수입니다.
    """
    # 구글 검색 API 주소입니다.
    url = "https://www.googleapis.com/customsearch/v1"
    
    # 구글 API에 전송할 파라미터입니다. API 키, 검색엔진 ID, 검색어를 포함합니다.
    params = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_SEARCH_ENGINE_ID,
        "q": query
    }

    try:
        # 구글에 데이터를 요청(GET)합니다.
        response = requests.get(url, params=params)
        
        # 요청이 성공했는지 확인합니다.
        response.raise_for_status()
        
        # 응답 데이터를 JSON 형식으로 변환합니다.
        data = response.json()

        results = []
        # 결과 항목인 "items"가 있으면 반복문을 돌며 정보를 추출합니다.
        if "items" in data:
            for item in data["items"]:
                results.append({
                    "source": "google",            # 출처 (google)
                    "title": item.get("title"),    # 제목
                    "content": item.get("snippet"),# 내용 요약 (snippet)
                    "url": item.get("link")        # 링크
                })
        # 정리된 결과 리스트를 반환합니다.
        return results
    except Exception as e:
        # 에러가 발생하면 출력하고 빈 리스트를 반환합니다.
        print(f"구글 검색 중 오류 발생: {e}")
        return []

def search(query, include_blog=True, include_news=True, include_google=True):
    """
    모든 검색(네이버 블로그, 네이버 뉴스, 구글)을 통합해서 실행하는 함수입니다.
    query: 검색어
    include_blog: 블로그 검색 포함 여부 (True면 포함)
    include_news: 뉴스 검색 포함 여부 (True면 포함)
    include_google: 구글 검색 포함 여부 (True면 포함)
    """
    aggregated_results = [] # 모든 결과를 담을 빈 리스트를 만듭니다.

    # 블로그 검색이 켜져 있으면(True) 실행해서 결과에 추가합니다.
    if include_blog:
        aggregated_results.extend(search_naver(query, "blog"))
    
    # 뉴스 검색이 켜져 있으면(True) 실행해서 결과에 추가합니다.
    if include_news:
        aggregated_results.extend(search_naver(query, "news"))

    # 구글 검색이 켜져 있으면(True) 실행해서 결과에 추가합니다.
    if include_google:
        aggregated_results.extend(search_google(query))

    # 최종적으로 모인 모든 결과를 반환합니다.
    return aggregated_results

# 이 파일이 직접 실행될 때만 아래 코드가 작동합니다. (다른 파일에서 import 할 때는 실행되지 않음)
if __name__ == "__main__":
    # 테스트를 위한 검색어 설정
    test_query = "LangChain"
    print(f"검색어: {test_query}")
    
    # search 함수를 호출하여 결과를 가져옵니다.
    results = search(test_query)
    
    # 결과를 보기 좋게(들여쓰기 적용) JSON 형태로 출력합니다.
    # ensure_ascii=False는 한글이 깨지지 않고 제대로 보이게 해줍니다.
    print(json.dumps(results, indent=2, ensure_ascii=False))
