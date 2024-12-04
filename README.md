### Product Requirements Document (PRD)

---

**Product Name**: EPICS PV Data Management and Monitoring Tool

**Version**: 1.0

**Author**: 권은상

**Date**: 2024-11-26

---

## 1. 제품 개요

### 1.1 제품 목적

이 웹 애플리케이션은 EPICS 환경에서 PV(Property Value) 데이터를 효율적으로 관리, 편집하고, 실시간으로 모니터링하며 PV값을 설정(set) 및 확인(get)할 수 있는 기능을 제공합니다. 이를 통해 실험 중 데이터 신뢰성을 높이고 작업의 효율성을 극대화합니다.

---

### 1.2 개발 계기

EPICS에는 CSS라는 GUI 도구가 있으며, 그 중 **PVtable** 기능은 PV 데이터셋의 편집 및 설정 작업을 제공합니다. 그러나 다음과 같은 한계점이 존재하여 실험 진행 중 오류 가능성이 발생할 수 있습니다:

1. **PV 값 확인 기능 부재**: 네트워크 오류 등으로 인해 PV가 제대로 설정되지 않는 경우를 실시간으로 확인할 수 없음.
2. **Readback 값 모니터링 부족**: 실험 중 PV의 입력값이 제대로 반영되었는지 지속적으로 확인하고, 범위 초과 시 알림 기능이 필요.

따라서, 기존 PVtable의 부족한 기능을 보완하는 **웹 기반 관리 도구**가 필요합니다.

---

## 2. 기능 요구 사항

### 2.1 주요 기능

1. **PV 데이터 관리**:
    - EPICS PV 데이터를 서버에 저장, 관리, 편집.
    - PV 데이터셋의 직관적 UI 제공 (표 형태, 엑셀 스타일 편집 가능).
2. **PV 설정 (caput)**:
    - PVtable에서 사용자가 지정한 값들을 EPICS PV에 적용.
    - 값 적용 후, 설정된 값이 EPICS 시스템에 성공적으로 반영되었는지 확인.
3. **PV 모니터링 (caget)**:
    - 설정된 PV값과 Readback PV 값을 실시간으로 모니터링.
    - PV 설정 이후 Readback 값이 정의된 범위에 있는지 지속 확인.
4. **에러 처리 및 상태 확인**:
    - PV값 설정 실패 시 일정 횟수 반복 시도 (ex: 3회).
    - 반복 실패 시 사용자에게 에러 메시지 표시.
    - Readback 값이 지정된 범위를 벗어날 경우 경고 및 알림.
5. **실험 상태 저장**:
    - 실험 진행 과정 및 상태 데이터를 서버에 기록.
    - 다수 사용자가 시스템을 공유하는 환경에서 실험 이력을 효과적으로 관리.

---

### 2.2 추가 고려사항

- **서버 기반 데이터 관리**: 로컬 실행이 아닌 서버에 실험 데이터를 저장하여 다중 사용자 환경에서 충돌 방지.
- **실시간 업데이트**: 실시간 모니터링 및 알림 기능 제공.
- **UI/UX 최적화**: 사용자 친화적인 웹 인터페이스 구현.

---

## 3. 사용자 시나리오

### 3.1 사용자 프로필

- **연구원**: EPICS PV를 사용하여 실험 데이터를 입력 및 관리.
- **엔지니어**: 시스템 상태를 점검하고 데이터 이상을 탐지.

### 3.2 주요 사용 흐름

1. 사용자는 웹 인터페이스를 통해 PV 데이터셋을 관리.
2. **실험 실행 버튼**을 클릭하여 PV 값을 EPICS 시스템에 설정.
3. 시스템은 설정된 PV 값을 caget을 통해 확인.
4. 설정 값 확인 실패 시, 최대 3회 반복 후 오류 상태 저장.
5. 성공적으로 값 설정 시, Readback 값을 실시간으로 모니터링.
6. Readback 값이 설정된 범위를 벗어나면 사용자에게 경고 알림.
7. 모든 상태 및 진행 기록을 서버에 저장.

---

## 4. 기술 요구 사항

### 4.1 플랫폼 및 기술 스택

### 1. **프론트엔드**

- **기능**: 사용자 인터페이스(UI) 구현
- **주요 요구 사항**:
    - PV 데이터셋을 표시하는 테이블 뷰 구현
    - 실시간 PV값 모니터링 (caget 결과 표시)
    - 알림/에러 상태 표시
    - 사용자 친화적인 실험 진행 버튼 및 상태 표시
- **기술 스택**:
    - HTML, CSS, JavaScript
    - (선택사항) React.js 또는 Vue.js

### 2. **백엔드**

- **기능**: PV 데이터 관리 및 실시간 데이터 처리
- **주요 요구 사항**:
    - caput/caget 명령을 통해 EPICS와 상호작용
    - PV 설정 실패 시 재시도 로직 구현
    - Readback 모니터링 및 상태 관리
    - 서버 데이터 저장 및 로깅
- **기술 스택**:
    - Python (Flask)
    - EPICS caput/caget API
    - RESTful API 제공

### 3. **데이터베이스**

- **기능**: 실험 데이터 저장 및 관리
- **주요 요구 사항**:
    - PV 데이터셋 저장 (이름, 설정값, 리드백값 등)
    - 실험 로그 기록 (설정 시각, 결과 상태 등)
    - 다중 사용자 환경에서 데이터 무결성 유지
- **기술 스택**:
    - MySQL, PostgreSQL, 또는 SQLite

### 4. **배포 및 네트워크**

- **기능**: 안정적인 서비스 제공
- **주요 요구 사항**:
    - 서버 배포 (Linux 기반 서버)
    - 네트워크 안정성을 고려한 재시도 로직
- **기술 스택**:
    - Docker (컨테이너화)
    - Nginx (리버스 프록시)

### 5. **알림 시스템**

- **기능**: 실험 오류 및 상태 변화 알림
- **주요 요구 사항**:
    - 설정 값 초과 시 사용자 알림 제공
    - 설정 실패 및 에러 상태 표시
- **기술 스택**:
    - WebSocket (실시간 알림)

### 4.2 성능 요구 사항

- 실시간 모니터링이 가능한 안정적 네트워크 처리 속도.
- 10ms 이내의 PV값 읽기/쓰기 지연.

---

## 5. 제약 조건

1. 네트워크 안정성에 따라 PV 설정/확인 실패 가능성.
2. 다중 사용자의 동시 접속 처리 요구.

---

## 6. 성공 기준

1. EPICS PV 데이터 입력 및 Readback 모니터링이 문제없이 수행.
2. PV값 범위 초과 시 즉각적인 사용자 알림.
3. 모든 실험 상태가 서버에 정확히 저장.
4. 사용자 만족도 평가에서 90% 이상 긍정적인 피드백.

---
