
# Requirements Document (요구사항 문서)

## 1. Product Overview (제품 개요)

### 1.1 Purpose (목적)
This web application aims to efficiently manage, edit, and monitor EPICS PV (Process Variable) data in a closed network environment.  
이 웹 애플리케이션은 폐쇄망 환경에서 EPICS PV (Process Variable) 데이터를 효율적으로 관리, 편집 및 모니터링하기 위한 목적으로 개발됩니다.

It provides functionality for setting (caput) and retrieving (caget) PV values to ensure reliable experimental data processing and operational efficiency.  
이 앱은 PV 값을 설정(caput)하고 확인(caget)하여 실험 데이터를 신뢰성 있게 처리하고 작업 효율성을 극대화합니다.

### 1.2 Background (개발 배경)
EPICS currently offers the CSS GUI tool, including a **PVtable** feature, which allows users to edit and set PV datasets.  
EPICS는 현재 CSS GUI 도구를 제공하며, 여기에는 **PVtable**이라는 기능이 포함되어 있습니다.

However, PVtable has critical limitations:  
그러나 PVtable에는 다음과 같은 한계점이 존재합니다:

1. **Lack of PV Confirmation**: There is no way to verify if the PV values were successfully set.  
1. **PV 확인 기능 부재**: PV 값이 성공적으로 설정되었는지 확인할 방법이 없습니다.

2. **Insufficient Readback Monitoring**: Continuous monitoring of Readback values to ensure they stay within defined ranges is missing.  
2. **리드백(Readback) 모니터링 부족**: 리드백 값을 지속적으로 모니터링하고, 정의된 범위를 벗어날 경우 경고를 제공하는 기능이 없습니다.

The proposed tool will address these limitations by providing a robust, web-based interface for PV management and monitoring.  
본 도구는 이러한 한계를 보완하여 PV 관리 및 모니터링을 위한 웹 기반 인터페이스를 제공합니다.

---

## 2. Functional Requirements (기능 요구 사항)

### 2.1 Core Features (핵심 기능)
1. **PV Data Management (PV 데이터 관리)**  
   - Manage, edit, and save EPICS PV datasets on a server.  
     - EPICS PV 데이터를 서버에 저장, 관리, 편집.  
   - Provide an intuitive UI for PV dataset visualization (Excel-like table format).  
     - PV 데이터셋의 직관적 UI 제공 (엑셀 스타일의 테이블 형식).

2. **PV Setting (caput) (PV 설정 기능)**  
   - Apply PV values to the EPICS system from the dataset.  
     - 데이터셋의 PV 값을 EPICS 시스템에 적용.  
   - Verify if the values were successfully set.  
     - 값이 성공적으로 설정되었는지 확인.

3. **PV Monitoring (caget) (PV 모니터링)**  
   - Monitor Readback PV values in real-time.  
     - 리드백(Readback) PV 값을 실시간으로 모니터링.  
   - Ensure Readback values stay within predefined ranges.  
     - 리드백 값이 정의된 범위를 유지하는지 확인.

4. **Error Handling and Alerts (에러 처리 및 알림)**  
   - Retry PV settings up to a defined number of attempts (e.g., 3).  
     - PV 설정 실패 시 정의된 횟수(예: 3회)까지 재시도.  
   - Generate alerts if Readback values deviate from the acceptable range or if PV setting fails.  
     - 리드백 값이 허용 범위를 벗어나거나 PV 설정 실패 시 경고 알림 생성.

5. **Experiment State Logging (실험 상태 기록)**  
   - Record experiment states, actions, and errors on the server for multi-user environments.  
     - 다중 사용자 환경에서 실험 상태, 작업, 에러를 서버에 기록.

---

## 3. Non-Functional Requirements (비기능 요구 사항)

### 3.1 Platform and Performance (플랫폼 및 성능)
- **Platform**: Web-based, accessible through modern browsers.  
  - **플랫폼**: 최신 브라우저를 통해 접근 가능한 웹 기반.  
- **Performance**:  
  - Real-time monitoring with response times under 10ms.  
    - 실시간 모니터링은 10ms 이내의 응답 속도로 작동.  
  - Capable of handling multiple simultaneous user sessions.  
    - 다중 사용자 동시 세션을 처리 가능.

### 3.2 Security (보안)
- Ensure data integrity and user authentication for accessing the system.  
  - 데이터 무결성과 사용자 인증을 통해 시스템 접근을 보호.  
- Data storage should support concurrent usage without conflicts.  
  - 데이터 저장은 충돌 없이 동시 사용을 지원.

---

## 4. Technical Requirements (기술 요구 사항)

### 4.1 Technology Stack (기술 스택)
1. **Frontend (프론트엔드)**  
   - HTML, CSS, JavaScript.  
     - HTML, CSS, JavaScript.  
   - Optional: React.js or Vue.js for dynamic and scalable UI.  
     - 선택사항: 동적이고 확장 가능한 UI를 위해 React.js 또는 Vue.js.

2. **Backend (백엔드)**  
   - Python (Flask) for lightweight and EPICS-compatible backend.  
     - 경량화된 EPICS 호환 백엔드를 위해 Python (Flask) 사용.  
   - Integration with EPICS caput and caget APIs.  
     - EPICS caput 및 caget API와의 통합.  

3. **Database (데이터베이스)**  
   - MySQL, PostgreSQL, or SQLite for storing PV datasets and experiment logs.  
     - PV 데이터셋 및 실험 로그 저장을 위해 MySQL, PostgreSQL, 또는 SQLite 사용.

4. **Deployment (배포)**  
   - Docker for containerization.  
     - 컨테이너화를 위해 Docker 사용.  
   - Nginx for reverse proxy and load balancing.  
     - 리버스 프록시 및 로드 밸런싱을 위해 Nginx 사용.

5. **Real-Time Updates (실시간 업데이트)**  
   - WebSocket for live monitoring and alerts.  
     - 실시간 모니터링 및 알림을 위해 WebSocket 사용.

---

## 5. Constraints (제약 사항)
- Operates in a closed network environment, requiring all dependencies to be preloaded.  
  - 폐쇄망 환경에서 동작하며 모든 종속성이 사전에 로드되어야 함.  
- Handles network instability by implementing retry mechanisms for PV commands.  
  - PV 명령어의 재시도 메커니즘을 통해 네트워크 불안정을 처리.

---

## 6. Success Criteria (성공 기준)
1. Successfully setting and monitoring EPICS PV values without errors.  
   1. EPICS PV 값을 에러 없이 설정 및 모니터링 성공.  
2. Real-time alerts for out-of-range Readback values.  
   2. 범위를 초과한 리드백 값에 대한 실시간 경고 알림 제공.  
3. Experiment data and logs are reliably stored on the server.  
   3. 실험 데이터와 로그가 서버에 신뢰성 있게 저장.  
4. Positive user feedback (90% or above satisfaction rating).  
   4. 사용자 피드백에서 90% 이상의 만족도 획득.

---
