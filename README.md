# 거짓의 방 - 플랫포머 MVP

어둡고 상징적인 무대에서 달리고 뛰는 2D 도트 플랫포머입니다. "사실은 전부 가짜"라는 아이작 느낌의 메타 톤을 텍스트와 배경으로 전달합니다.

## 실행 방법

```bash
pip install pygame
py main.py
```

## 조작법 (마리오 스타일)

- 이동: A/D 또는 ←/→
- 점프: SPACE
- 달리기: SHIFT
- 재시작: R
- 종료: ESC

## 에셋 처리

assets/ 폴더에 PNG가 없으면 자동으로 placeholder 이미지를 생성합니다. placeholder에는 한국어 라벨이 표시됩니다(주인공, 괴물1, 괴물2 등).

## 필요한 이미지 파일명 / 권장 크기

- assets/player.png (16x16 또는 32x32)
- assets/enemy1.png (16x16)
- assets/enemy2.png (16x16)
- assets/tile_floor.png (16x16)
- assets/tile_wall.png (16x16)
- assets/coin.png (16x16)
- assets/goal.png (16x24)
- assets/bg.png (16x16 반복 타일)

placeholder는 pygame으로 생성되며, 사용자가 직접 PNG를 넣으면 자동 교체됩니다.

## 한 줄 소개

"관객은 없었다. 그래도 뛰어야 했다." — 거짓의 방은 무대와 거짓이 뒤섞인 플랫포머입니다.
