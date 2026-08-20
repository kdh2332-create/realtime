# 포트폴리오 실시간 시세 (Yahoo Finance)

티커와 수량을 직접 입력하고, Yahoo Finance에서 실시간 시세를 가져와 페어별 평가금액·비중·차이를 보여줍니다.

서버에서 시세를 조회하기 때문에 **브라우저 CORS 문제 없이** 안정적으로 동작합니다.

## 주요 기능

- 티커 / 수량 직접 입력·수정
- 페어 추가·삭제, 종목 추가·삭제
- 실시간 시세 (Yahoo Finance)
- 비중·평가금액·페어 차이 자동 계산
- 브라우저 로컬 저장 (설정 유지)
- 60초 자동 갱신

## 로컬 실행

```bash
# 1. 의존성 설치
pip install -r requirements.txt

# 2. 실행
python app.py
```

브라우저에서 http://localhost:5000 접속

## GitHub에 올리기

1. 새 저장소 생성 (예: `portfolio-tracker`)
2. 이 폴더 내용을 전부 업로드 (또는 git push)

```bash
git init
git add .
git commit -m "Initial commit: portfolio real-time tracker"
git branch -M main
git remote add origin https://github.com/본인아이디/portfolio-tracker.git
git push -u origin main
```

## Render.com에 배포하기 (추천)

1. [Render.com](https://render.com) 가입 (GitHub 연동)
2. **New → Web Service**
3. GitHub 저장소 연결
4. 설정:
   - **Name**: `portfolio-tracker` (원하는 이름)
   - **Runtime**: `Python 3`
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `gunicorn app:app`
   - **Instance Type**: Free
5. **Create Web Service** 클릭

배포가 끝나면 `https://포트폴리오이름.onrender.com` 주소가 생성됩니다.

> Free 플랜은 15분 동안 요청이 없으면 슬립 상태로 들어갑니다.  
> 처음 접속 시 30초 정도 걸릴 수 있습니다.

## Railway / Fly.io 등에도 동일하게 배포 가능

Start Command만 `gunicorn app:app` 으로 설정하면 됩니다.

## API

```
GET /api/quotes?symbols=QLD,SPYM,TQQQ
```

응답 예시:

```json
{
  "quotes": {
    "QLD": { "ticker": "QLD", "price": 89.44, "currency": "USD", "name": "...", "error": null }
  },
  "fetched_at": "2026-08-20 14:30:00 UTC"
}
```

## 라이선스

MIT – 자유롭게 사용·수정하세요.
