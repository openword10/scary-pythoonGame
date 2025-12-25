# 거짓의 방 (탑다운 룸 클리어 MVP)

Python 3.x + Pygame으로 만든 탑다운 2D 룸 클리어(아이작 느낌) 미니 게임입니다. 외부 에셋이 없어도 실행되며, 없을 경우 자동으로 16x16 픽셀아트 느낌의 placeholder PNG를 생성합니다.

## 실행 방법

```bash
pip install pygame
python main.py
```

## 조작

- 이동: W/A/S/D
- 공격: 방향키 (4방향 발사)
- 방 리셋: R (지우개 아이템 획득 시)

## 특징

- 3x3 룸 맵, 적 처치 후 문 개방
- 적 2종: 괴물1(추적형), 괴물2(돌진형)
- 아이템 6종: 종이 가면, 테이프, 대본, 스포트라이트, 지우개, 가위
- 룸 진입 시 랜덤 문구 표시
- 픽셀아트: 내부 해상도 320x240, 4x 정수배 스케일

## 에셋 파일명 규칙

assets/ 폴더에 아래 이름의 PNG를 넣으면 자동으로 로드됩니다. 없으면 코드가 자동 생성합니다.

- player.png
- enemy1.png
- enemy2.png
- bullet.png
- floor.png
- wall.png
- door_closed.png
- door_open.png
- prop_tape.png
- prop_mark.png
- prop_curtain.png
- item_mask.png
- item_tape.png
- item_script.png
- item_spotlight.png
- item_eraser.png
- item_scissors.png
