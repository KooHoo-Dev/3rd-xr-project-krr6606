"""데모 씬 배치표 (Unity 좌표, m / 도). DemoSceneBuilder.cs의 값과 같게 유지할 것.

플레이어는 원점 근처에서 +Z(다트판)를 바라본다. 던지는 선 = z 0.
"""
BOARD_CENTER = (0.0, 1.73, 2.0)       # 다트판 앞면 중심 (던지는 선에서 2.0 m)
LAYOUT = [
    # (모델 이름, 위치, Y 회전)
    ("DartRoom",       (0.0, 0.0, 0.0), 0),
    ("OcheLine",       (0.0, 0.0, 0.0), 0),
    ("Dartboard",      BOARD_CENTER, 0),
    ("BoardBackboard", BOARD_CENTER, 0),
    ("ScoreBoard",     (-1.15, 1.62, 2.075), 0),
    ("NeonSign_Title", (0.0, 2.55, 2.1), 0),
    ("NeonSign_777",   (1.15, 1.75, 2.1), 0),
    ("PendantLamp",    (0.0, 3.0, 1.25), 0),
    ("PendantLamp",    (-1.45, 3.0, -0.25), 0),
    ("BarTable",       (0.55, 0.0, -0.1), 0),
    ("DartHolder",     (0.55, 1.0, -0.1), 20),
    ("BarTable",       (-1.45, 0.0, -0.25), 0),
    ("BarStool",       (-1.45, 0.0, -0.85), 0),
    ("BarStool",       (-1.05, 0.0, 0.3), 0),
    ("PosterFrame",    (2.0, 1.65, 0.9), 90),
    ("PosterFrame",    (-2.0, 1.65, 1.1), -90),
]
PLAYER = (0.0, 0.0, -0.25)
