# RAG Service
## RAG Query
* Embedding Query 받아서 Weaviate Vector DB 조회

## RAG Info
* Plugin Workspace Embedding 처리
* RAG 문서 처리
* RAG Pipeline 수행
* Embedding 처리

## 로컬 실행
```bash
$ pip install -r requirements.txt
# ai-assistant-k8s private repo weaviate-vector-db 실행
$ uvicorn app:app --host 0.0.0.0 --port 8001 --reload
```

## Docker 실행
```bash
# 이미지 빌드
$ docker build -t rag-service:ai-assistant .
# 컨테이너 실행
$ docker run -d -p 8001:8001 --name rag-service rag-service:ai-assistant
```

## 테스트
```bash
# RAG 에서 유사 Chunk 조회
$ curl -X POST http://localhost:8001/search \
  -H "Content-Type: application/json" \
  -d '{
        "query": "fast api 란?"
      }'
```
