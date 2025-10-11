# RAG Service
## RAG Search
* Embedding Query 받아서 Weaviate Vector DB 조회

## RAG Document
* RAG 문서 처리 CRUD

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
      
# RAG 문서 리스트 조회
$ curl "http://localhost:8001/documents?limit=10" | jq
# RAG 문서 id 조회
$ curl "http://localhost:8001/documents/{document_id}" | jq
# RAG 문서 title 조회
$ curl -X GET "http://localhost:8001/documents/title/{title}" | jq
# RAG 문서 추가
$ curl -X POST "http://localhost:8001/documents" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Title",
    "content": "이것은 100자 단위로 청크 분할되어 저장될 긴 본문 예시입니다. 모 델 서버를 통해 각 청크가 임베딩되어 Weaviate에 저장됩니다. 이것은 30자 단위로 청크 분할되어 3저장될 긴 본문 예시입니다. 모델 서버를 통해 각 청크가 3임베딩되어 Weaviate에 저장됩니다."
  }'
# RAG 문서 수정
$ curl -X PUT "http://localhost:8001/documents/{document_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Updated Title",
    "content": "수정된 본문 내용입니다. 이 내용은 100자 단위로 청크 분할되어 임베딩이 다시 생성됩니다."
  }'
# RAG 문서 수정 오류 (길이 실패)
$ curl -X PUT "http://localhost:8001/documents/{document_id}" \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Test Titleㄴ",
    "content": "이 본문은 100자를 초과하도록 매우 길게 작성된 예시입니다. 따라서 서버에서 ValueError가 발생하며 업데이트가 거부됩니다. Weaviate에는 아무런 변경이 저장되지 않습니다."
  }'
# RAG 문서 id 삭제
$ curl -X DELETE "http://localhost:8001/documents/{document_id}"
# RAG 문서 title 삭제
$ curl -X DELETE "http://localhost:8001/documents/title/{title}"
```
