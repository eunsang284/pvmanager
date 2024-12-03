/var/www/app2/
├── app/
│   ├── __init__.py               # Flask 앱 초기화
│   ├── core/                     # 핵심 비즈니스 로직
│   │   ├── __init__.py
│   │   ├── pv_manager.py        # PV 관리 클래스
│   │   └── experiment.py        # 실험 제어 클래스
│   │
│   ├── models/                   # 데이터베이스 모델
│   │   ├── __init__.py
│   │   └── pv_dataset.py        # PV 데이터셋 모델
│   │
│   ├── routes/                   # API 라우트
│   │   ├── __init__.py
│   │   └── api.py               # (기존 routes.py)
│   │
│   └── utils/                    # 유틸리티 함수들
│       ├── __init__.py
│       └── validators.py         # 데이터 검증 유틸리티
│
├── static/                       # (기존 디렉토리)
│   ├── css/
│   ├── js/
│   └── img/
│
├── templates/                    # (기존 디렉토리)
│   ├── base.html
│   └── index.html
│
├── venv/                        # (기존 디렉토리)
├── requirements.txt             # (기존 파일)
├── requirements.md              # (기존 파일)
├── VERSION.md                   # (기존 파일)
└── filetree.md                 # (기존 파일)