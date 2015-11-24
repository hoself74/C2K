# C2K version 2.0
- 제작자: 김지성
- 메일: jiseong@kaist.ac.kr
- 기관: MachineReading@KAIST

---

이 프로그램(C2K)은 디비피디아 카테고리 트리플에서부터
지식 트리플을 추출하고 저장하는 기능을 합니다. 이 문서는
C2K 프로그램의 파일 구성 및 사용법에 대한 내용을 설명합니다.

---

## 목차:
>1. 구성
>2. 선행 사항
>3. 프로그램 사용법

---

## 구성

### 1-1. 입력 파일 디렉토리(inputs) :
입력 파일은 모두 디비피디아 NT 형식의 덤프 파일을 기준으로 합니다.
입력 파일의 구성은 다음과 같습니다:
- 카테고리 트리플(c_triples.nt): Article categories
- 지식 트리플(k_triples.nt): Mapping-based properties / infobox properties
- 타입 트리플(t_triples.nt): Mapping-based types
- 카테고리 네트워크(c_skos.nt): Categories (Skos)

위의 네가지 입력 파일은 프로그램 실행 전
모두 inputs 디렉토리에 위의 명시된 이름으로 저장되어 있어야 합니다.

### 1-2. 출력 파일 디렉토리(outputs):
C2K 프로그램의 출력 파일은 카테고리 트리플에서 추출된
새로운 지식 혹은 타입 트리플입니다. outputs 디렉토리에 predicted_triples.tsv로 출력됩니다.
predicted_triples.tsv의 각 라인은 다음의 형식을 갖습니다:
- S(space)P(space)O(space).(tab)SALA_Confidence(tab)Source_Category

### 1-3. 명령 프로그램(C2K.py):
이 프로그램을 실행함으로써 본격적으로 룰 마이닝 및 트리플 추출이 시작됩니다.
실행 전 파이썬이 설치되어 있어야 하며, 파이썬을 이용해 이 프로그램을
실행할 수 있습니다.

---

## 선행 사항

### 2-1. 파이썬 설치
이 프로그램은 기본적으로 파이썬으로 작성되었습니다.
프로그램을 실행하려면 파이썬 2.7 버전이 우선 설치되어 있어야 합니다.

### 2-2. 리소스 데이터 준비
이 프로그램은 기본적으로 다음과 같은 리소스 데이터들을 필요로 합니다:
- 리소스 1: 입력 트리플(c_triples.nt, k_triples.nt, t_triples.nt, c_skos.nt)
- 리소스 2: 단어 임베딩 모델(en_500_stem)

이 리소스들은 큰 용량을 가지기 때문에, GitHub로는 공유가 불가능하며,
다음의 사이트에서 다운로드받을 수 있습니다:
- http://elvis.kaist.ac.kr/c2k_v2.0_large_data

리소스 1과 리소스 2를 받으신 후에 각각 소스코드 상에서
다음의 디렉토리 하에 위치시키기 바랍니다:
- 리소스 1 => inputs/
- 리소스 2 => modules/shared_files/

위 사항들을 모두 완료하면, 기본적으로 C2K가 구동가능합니다.

---

## 프로그램 사용법

### 3-1. 명령어 사용법
C2K 프로그램을 사용하기 위한 명령은 다음과 같습니다:

  python C2K.py [-t] [-ko/en] [-def] [-thc floatValue] [-thq floatValue] [-thl floatValue] [-thu floatValue]
  
- t 옵션: 추출할 트리플이 지식 트리플인지 카테고리 트리플인지를 지정합니다.
이 옵션이 전달되면 입력은 기본적으로 mapping-based types로 간주되며,
출력은 새로 추출된 타입 트리플이 됩니다. 지식 트리플과 타입 트리플의 추출은 전혀
다른 로직을 사용하기 때문에 반드시 이 옵션을 명시해야 합니다.
- ko/en 옵션: 덤프 파일의 언어 정보를 제공합니다. 만약 입력 지식 트리플이
한국어 버전의 localized infobox triples라면 반드시 -ko 옵션을 제공해 주어야 합니다.
- def 옵션: 이 옵션을 제공하면 C2K 프로그램의 모든 파라미터들은 기본 값으로 세팅됩니다.
(기본 값: theta_c=0.9, theta_q=0.1, theta_l=5.0, theta_u=1000.0)
-thc floatValue 옵션: 제공된 floatVlaue를 theta_c의 값으로 세팅합니다.
-thq floatValue 옵션: 제공된 floatVlaue를 theta_q의 값으로 세팅합니다.
-thl floatValue 옵션: 제공된 floatVlaue를 theta_l의 값으로 세팅합니다.
-thu floatValue 옵션: 제공된 floatVlaue를 theta_u의 값으로 세팅합니다.
