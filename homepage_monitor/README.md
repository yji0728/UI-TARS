# 홈페이지 위변조 탐지 웹앱

UI-TARS 기반의 홈페이지 위변조 탐지 시스템입니다.

## 기능 소개

### 핵심 기능
- **자동 모니터링**: 등록된 웹사이트의 정기적인 자동 스크린샷 촬영
- **위변조 탐지**: 기준 이미지와의 실시간 비교를 통한 변경사항 감지
- **실시간 알림**: 변경 감지 시 즉시 알림 발송
- **시각적 분석**: 변경된 부분을 강조한 차이 이미지 생성
- **웹 대시보드**: 직관적인 웹 인터페이스를 통한 모니터링 관리

### UI-TARS 통합
- UI-TARS의 action_parser 모듈을 활용한 GUI 자동화
- 브라우저 자동화를 통한 정확한 스크린샷 캡처
- 좌표 기반 요소 인식 및 상호작용

## 설치 및 실행

### 1. 의존성 설치
```bash
pip install -r requirements.txt
```

### 2. ChromeDriver 설치
Selenium을 위한 ChromeDriver가 필요합니다:
```bash
# Ubuntu/Debian
sudo apt-get update
sudo apt-get install chromium-browser chromium-chromedriver

# 또는 수동으로 ChromeDriver 다운로드
# https://chromedriver.chromium.org/
```

### 3. 실행
```bash
python app.py
```

웹 브라우저에서 `http://localhost:5000` 접속

## 사용법

### 1. 사이트 추가
1. '사이트 추가' 버튼 클릭
2. 모니터링할 웹사이트의 URL과 이름 입력
3. 검사 간격 설정 (5분~24시간)
4. '사이트 추가' 버튼으로 등록 완료

### 2. 기준 설정
- 사이트 추가 시 첫 번째 스크린샷이 자동으로 기준으로 설정됨
- '기준 설정' 버튼으로 언제든 새로운 기준 이미지로 업데이트 가능

### 3. 모니터링 관리
- **검사**: 개별 사이트의 수동 검사
- **전체 검사**: 모든 등록된 사이트 일괄 검사
- **알림 확인**: 탐지된 위변조 알림 및 상세 분석

## 디렉터리 구조

```
homepage_monitor/
├── app.py              # Flask 메인 애플리케이션
├── requirements.txt    # Python 의존성 목록
├── README.md          # 이 파일
├── templates/         # HTML 템플릿
│   ├── base.html      # 기본 템플릿
│   ├── dashboard.html # 대시보드
│   ├── add_site.html  # 사이트 추가
│   └── alerts.html    # 알림 페이지
├── static/            # 정적 파일
│   ├── css/style.css  # 스타일시트
│   └── js/app.js      # JavaScript
├── data/              # 설정 및 데이터
│   ├── monitor_config.json  # 모니터링 설정
│   └── alerts.json    # 알림 데이터
└── screenshots/       # 스크린샷 저장
    ├── {site_id}_{timestamp}.png
    └── {site_id}_diff_{timestamp}.png
```

## 기술적 특징

### 이미지 비교 알고리즘
- **Perceptual Hashing**: 이미지의 구조적 특성 기반 해시 생성
- **MSE (Mean Squared Error)**: 픽셀 단위 차이 계산
- **Structural Similarity**: 이미지의 구조적 유사성 측정

### 탐지 정확도
- 유사도 임계값: 85% (조정 가능)
- 동적 콘텐츠 필터링으로 오탐 최소화
- 시각적 차이 이미지로 정확한 변경 부분 식별

### 성능 최적화
- 백그라운드 스케줄러를 통한 비동기 모니터링
- 효율적인 이미지 리사이징 및 압축
- 메모리 최적화된 이미지 처리

## 보안 고려사항

- 스크린샷 데이터의 로컬 저장으로 프라이버시 보호
- HTTPS 사이트 모니터링 권장
- 접근 제어 및 인증 시스템 추가 가능

## 확장 가능성

- 이메일/SMS 알림 연동
- 데이터베이스 연동 (SQLite, PostgreSQL 등)
- API를 통한 외부 시스템 통합
- 머신러닝 기반 이상 탐지 고도화
- 클러스터 환경에서의 분산 모니터링

## 라이선스

이 프로젝트는 UI-TARS의 라이선스를 따릅니다.