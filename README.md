# 거짓의 방 (Scary Pythoon Game MVP)

탑다운이 아니라 **마리오처럼 좌우 이동 + 점프가 중심인 2D 사이드 스크롤 액션**입니다. 모든 그래픽은 16x16 픽셀을 기준으로 렌더링되며, 외부 에셋이 없어도 자동으로 플레이스홀더 픽셀 패턴을 생성합니다.

## 실행 방법

```bash
pip install pygame
python main.py
```

## 게임 조작

- 이동: A / D
- 점프: SPACE (또는 W)
- 발사: 방향키
- 레벨 리셋: R (지우개 아이템 획득 시)

## 주요 특징

- 넓은 한 장의 스크롤 맵(120 타일 폭)
- 적 2종: 느린 추적형, 돌진형
- 아이템 6종: 종이 가면, 테이프, 대본, 스포트라이트, 지우개, 가위
- 레벨 진입 시 연출 문구 표시
- HUD: 체력, 층, 플레이어 위치 X, 아이템 효과 텍스트

## 파일 구조 예시

```
scary-pythoonGame/
├─ assets/
├─ assets.py
├─ entities.py
├─ game.py
├─ items.py
├─ main.py
├─ ui.py
├─ world.py
└─ README.md
```

## 에셋 이미지 이름 규칙 (선택)

assets/ 폴더에 아래 이름의 PNG를 넣으면 자동으로 로드됩니다. 없으면 플레이스홀더가 생성됩니다.

- player.png
- enemy_chaser.png
- enemy_dasher.png
- bullet.png
- floor.png
- wall.png
- door_closed.png
- door_open.png
- prop_tape.png
- prop_mark.png
- prop_curtain.png
- item_paper_mask.png
- item_tape.png
- item_script.png
- item_spotlight.png
- item_eraser.png
- item_scissors.png

## 개발 노트

- 내부 해상도(뷰포트): 480x272 (30x17 타일)
- 월드 해상도: 1920x320 (120x20 타일)
- 렌더링: 정수 배율(기본 3x) 스케일 업, 픽셀 보존
