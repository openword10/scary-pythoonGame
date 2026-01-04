# 거짓의 방 (Python 3.12 + Pygame)

공포/메타 무대 분위기의 2D 사이드뷰 플랫포머입니다. 산나비의 빠른 이동감과 Have a Nice Death의 날카로운 타격감을 목표로 재구성했습니다.

## 실행 방법

```bash
pip install pygame
py main.py
```

창은 전체화면 창모드(보더리스)로 실행됩니다.

## 조작법

- 이동: A/D 또는 ←/→
- 점프: SPACE (꾹 누르면 차지, 떼면 더 높게)
- 공격: R
- 대시: SHIFT + 방향키
- 달리기: SHIFT
- 표지판 읽기: E
- 도움말: Title에서 E
- 도움말 종료: ↑ 또는 ESC
- 재시작: R (클리어 화면)
- 종료: ESC

## 규칙

- 구멍 아래로 떨어지면 체크포인트로 복귀합니다.
- 피격 시 0.5초 무적(깜빡임)으로 추가 피해를 받지 않습니다.
- 맵 끝의 커튼(Goal)에 도달하면 클리어와 함께 등급이 표시됩니다.

## 에셋 처리

assets/ 폴더에 PNG가 없으면 자동으로 placeholder 이미지를 생성합니다. placeholder에는 한국어 라벨이 표시됩니다(주인공, 괴물1, 괴물2, 하트 등).

## 필요한 이미지 파일명 / 설명 / 권장 화질

픽셀아트는 **원본 픽셀 크기 그대로 제작**하고, 게임에서 정수 배율로 확대합니다(스무딩 금지).

- `assets/player.png` (128x32, 32x32 프레임 4개)
  - 주인공 스프라이트 시트.
  - 화질: 1x 픽셀아트(선명한 윤곽, 2~4색 팔레트 권장).
- `assets/enemy1.png` (16x16)
  - 순찰형 괴물1 스프라이트.
  - 화질: 1x 픽셀아트, 대비를 높게.
- `assets/enemy2.png` (16x16)
  - 돌진형 괴물2 스프라이트.
  - 화질: 1x 픽셀아트, 날카로운 실루엣.
- `assets/tile_floor.png` (16x16)
  - 바닥 타일 텍스처(체커/거친 질감 등).
  - 화질: 1x 픽셀아트, 타일 반복에 어울리게 제작.
- `assets/tile_wall.png` (16x16)
  - 벽/플랫폼 타일.
  - 화질: 1x 픽셀아트, 외곽선 강조.
- `assets/heart.png` (16x16)
  - 회복 하트 아이콘.
  - 화질: 1x 픽셀아트, 눈에 띄는 컬러.
- `assets/goal.png` (16x24)
  - 커튼/문/목표 지점 아이콘.
  - 화질: 1x 픽셀아트, 세로형 비율 유지.
- `assets/bg.png` (16x16 반복 타일)
  - 배경 텍스처(어두운 그라데이션/줄무늬 느낌).
  - 화질: 1x 픽셀아트, 반복 패턴에 어울리게 제작.
- `assets/blood.png` (선택, 권장 4x4)
  - 피 파티클용 작은 점/스플래시.
  - 화질: 1x 픽셀아트, 단색 또는 2색.
- `assets/attack.png` (선택, 권장 16x12)
  - 근접 공격 이펙트.
  - 화질: 1x 픽셀아트, 얇은 선/호 형태.

### 필요한 모든 이미지 요약
- `assets/player.png` (128x32, 32x32 프레임 4개)
- `assets/enemy1.png` (16x16)
- `assets/enemy2.png` (16x16)
- `assets/tile_floor.png` (16x16)
- `assets/tile_wall.png` (16x16)
- `assets/heart.png` (16x16)
- `assets/goal.png` (16x24)
- `assets/bg.png` (16x16 반복)
- `assets/blood.png` (4x4, 선택)
- `assets/attack.png` (16x12, 선택)

placeholder는 pygame으로 생성되며, 사용자가 직접 PNG를 넣으면 자동 교체됩니다.

## 한 줄 소개

"관객은 없었다. 그래도 뛰어야 했다." — 거짓의 방은 무대와 거짓이 뒤섞인 플랫포머입니다.
