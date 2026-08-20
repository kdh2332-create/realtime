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
pip install -r requirements.txt
python app.py
```

→ http://localhost:5000

## GitHub에 올리기

```bash
git init
git add .
git commit -m "portfolio real-time tracker"
git branch -M main
git remote add origin https://github.com/본인아이디/저장소이름.git
git push -u origin main
```

## Render.com 배포 (중요 설정)

1. [render.com](https://render.com) 가입 후 GitHub 연동
2. **New → Web Service** → 저장소 선택
3. **반드시 아래처럼 설정**하세요:

| 항목 | 값 |
|------|-----|
| **Name** | 원하는 이름 (예: portfolio-tracker) |
| **Region** | Oregon (US West) 또는 Singapore |
| **Runtime** | Python 3 |
| **Build Command** | `pip install -r requirements.txt` |
| **Start Command** | `gunicorn app:app --bind 0.0.0.0:$PORT --workers 1 --threads 2 --timeout 120` |
| **Instance Type** | Free |

4. **Advanced** → Add Environment Variable (선택):
   - Key: `PYTHON_VERSION`  Value: `3.12.0`

5. **Create Web Service**

### 배포 후 확인

- 메인 페이지: `https://서비스이름.onrender.com`
- 헬스체크: `https://서비스이름.onrender.com/api/health`
- 시세 API: `https://서비스이름.onrender.com/api/quotes?symbols=QLD,SOXL`

> Free 플랜은 15분 동안 요청이 없으면 슬립합니다.  
> 처음 접속 시 30초~1분 정도 걸릴 수 있습니다.

### Internal Server Error 가 날 때

1. Render 대시보드 → 해당 서비스 → **Logs** 탭을 확인하세요.
2. Start Command가 위에 적은 것과 **정확히 같은지** 다시 확인하세요.  
   (`$PORT`가 빠져 있으면 거의 항상 에러가 납니다)
3. Build가 성공했는지 확인하세요.

## API 예시

```
GET /api/quotes?symbols=QLD,SPYM,TQQQ
```

## 라이선스

MIT
