# 피드백 사운드 생성 (Blender 불필요, 순수 Python) — AI-Assist: generated
# 실행 (프로젝트 루트에서):  python Tools/AssetGen/make_sfx.py
# 결과: Assets/_Project/Audio/SFX_*.wav  (모노, 44.1 kHz, 16 bit)
#
# 녹음 파일 없이 사인파 · 잡음을 더해서 만든다. 난수 시드가 고정되어 매번 같은 소리가 나온다.
import math
import os
import random
import struct
import wave

SR = 44100
OUT = os.path.join(os.path.dirname(__file__), "..", "..", "Assets", "_Project", "Audio")
TAU = math.tau


def silence(sec):
    return [0.0] * int(SR * sec)


def mix(dst, src, at=0.0, gain=1.0):
    """src를 dst의 at초 위치에 더한다 (dst가 짧으면 늘림)."""
    start = int(at * SR)
    need = start + len(src) - len(dst)
    if need > 0:
        dst.extend([0.0] * need)
    for i, v in enumerate(src):
        dst[start + i] += v * gain
    return dst


def tone(sec, f0, f1=None, decay=0.0, attack=0.002, harmonics=((1, 1.0),), vibrato=0.0):
    """f0 → f1 로 미끄러지는 음. decay = 지수 감쇠 속도(클수록 빨리 사라짐)."""
    f1 = f0 if f1 is None else f1
    n = int(SR * sec)
    out = []
    phase = 0.0
    for i in range(n):
        t = i / SR
        k = i / max(1, n - 1)
        f = f0 * (f1 / f0) ** k                       # 음정은 지수적으로 변해야 자연스럽다
        if vibrato:
            f *= 1.0 + 0.012 * math.sin(TAU * vibrato * t)
        phase += TAU * f / SR
        env = min(1.0, t / attack) * math.exp(-decay * t)
        env *= min(1.0, (sec - t) / 0.01)             # 끝에서 딸깍 소리 안 나게
        out.append(env * sum(a * math.sin(phase * h) for h, a in harmonics))
    return out


def noise(sec, decay=0.0, attack=0.001, lowpass=1.0, highpass=0.0, rng=random):
    """잡음. lowpass(0~1)가 작을수록 먹먹하고, highpass(0~1)가 클수록 쉿 소리만 남는다."""
    n = int(SR * sec)
    out = []
    lp = 0.0
    hp_prev = 0.0
    for i in range(n):
        t = i / SR
        x = rng.uniform(-1.0, 1.0)
        lp += lowpass * (x - lp)
        y = lp
        if highpass:
            hp_prev += highpass * (y - hp_prev)
            y = y - hp_prev
        env = min(1.0, t / attack) * math.exp(-decay * t) * min(1.0, (sec - t) / 0.01)
        out.append(env * y)
    return out


def drips(sec, count, rng, f_lo=500, f_hi=1800):
    """물방울 '뽀글' 소리 여러 개: 짧게 음이 올라가는 사인파."""
    out = silence(sec)
    for _ in range(count):
        at = rng.uniform(0.0, sec - 0.09) ** 1.0
        f = rng.uniform(f_lo, f_hi)
        d = rng.uniform(0.03, 0.07)
        mix(out, tone(d, f, f * rng.uniform(1.4, 2.2), decay=40), at, rng.uniform(0.15, 0.45))
    return out[: int(SR * sec)]


def normalize(samples, peak=0.89):
    m = max(abs(v) for v in samples) or 1.0
    return [v * peak / m for v in samples]


def save(name, samples, peak=0.89):
    os.makedirs(OUT, exist_ok=True)
    samples = normalize(samples, peak)
    path = os.path.join(OUT, name + ".wav")
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes(b"".join(struct.pack("<h", int(max(-1.0, min(1.0, v)) * 32767)) for v in samples))
    print(f"{name}.wav  {len(samples) / SR:.2f}s")


# ---------------------------------------------------------------- 개별 소리
def pop(rng):
    """팡: 날카로운 터짐(잡음) + 묵직한 '툭'(낮은 음) + 물 튀는 꼬리."""
    s = silence(0.45)
    mix(s, noise(0.09, decay=70, lowpass=0.9, highpass=0.05, rng=rng), 0.0, 1.0)
    mix(s, tone(0.12, 190, 55, decay=28), 0.0, 0.9)
    mix(s, noise(0.40, decay=11, lowpass=0.35, highpass=0.25, rng=rng), 0.012, 0.45)
    mix(s, drips(0.35, 7, rng), 0.05, 0.5)
    return s


def water_spill(rng):
    """촤아악: 물이 쏟아져 바닥에 떨어지는 소리 (올 클리어 연출용)."""
    sec = 1.6
    s = silence(sec)
    body = noise(sec, lowpass=0.22, highpass=0.12, rng=rng)
    hiss = noise(sec, lowpass=0.8, highpass=0.5, rng=rng)
    for i in range(len(body)):
        t = i / SR
        env = min(1.0, t / 0.12) * math.exp(-2.2 * max(0.0, t - 0.5))   # 차오르다가 잦아듦
        s[i] += env * (body[i] * 1.0 + hiss[i] * 0.35)
    mix(s, drips(1.5, 34, rng, 350, 1500), 0.05, 0.9)
    return s


def coin(rng):
    """띠링: 동전 소리. 높은 두 음을 금속 배음과 함께 연달아."""
    bell = ((1, 1.0), (2.76, 0.35), (5.4, 0.15))      # 정수배가 아닌 배음 = 금속 느낌
    s = silence(0.7)
    mix(s, tone(0.25, 1976, decay=14, harmonics=bell), 0.0, 0.8)     # B6
    mix(s, tone(0.60, 2637, decay=7, harmonics=bell), 0.075, 1.0)    # E7
    return s


def gold_pop(rng):
    """금빛 풍선: 팡 + 동전 + 반짝이는 높은 음 몇 개."""
    s = pop(rng)
    mix(s, coin(rng), 0.04, 0.9)
    for i, f in enumerate((3136, 3951, 4699, 5274)):                  # 위로 흩어지는 반짝임
        mix(s, tone(0.18, f, decay=22), 0.22 + i * 0.07, 0.22)
    return s


def fanfare(rng):
    """빰빠바밤~: 도-미-솔 올라간 뒤 높은 도 화음으로 마무리 (목표 달성 / 올 클리어)."""
    brass = ((1, 1.0), (2, 0.5), (3, 0.33), (4, 0.18), (5, 0.1))
    s = silence(1.9)
    for at, f, d in ((0.00, 523.25, 0.16), (0.14, 659.25, 0.16), (0.28, 783.99, 0.16)):
        mix(s, tone(d, f, decay=5, attack=0.008, harmonics=brass), at, 0.6)
    for f, g in ((1046.5, 0.6), (783.99, 0.4), (659.25, 0.35), (523.25, 0.3)):   # 마지막 화음
        mix(s, tone(1.4, f, decay=2.2, attack=0.01, harmonics=brass, vibrato=5.5), 0.44, g)
    return s


def balloon_rise(rng):
    """뾰롱: 풍선이 떠오를 때. 부드럽게 올라가는 음 + 약한 바람 소리."""
    s = silence(0.5)
    soft = ((1, 1.0), (2, 0.2))
    mix(s, tone(0.38, 330, 820, decay=4, attack=0.03, harmonics=soft), 0.0, 0.8)
    mix(s, noise(0.45, decay=5, attack=0.08, lowpass=0.12, highpass=0.05, rng=rng), 0.0, 0.6)
    return s


def ui_click(rng):
    """딸깍: 버튼 누름."""
    s = silence(0.09)
    mix(s, tone(0.07, 1250, 880, decay=55), 0.0, 1.0)
    mix(s, noise(0.012, decay=250, lowpass=0.9, highpass=0.3, rng=rng), 0.0, 0.4)
    return s


def miss(rng):
    """툭: 돌멩이가 풍선을 못 맞히고 땅 · 물에 떨어졌을 때."""
    s = silence(0.22)
    mix(s, tone(0.16, 140, 70, decay=30), 0.0, 1.0)
    mix(s, noise(0.10, decay=45, lowpass=0.18, rng=rng), 0.0, 0.6)
    return s


def sling_stretch(rng):
    """끼이익: 주머니를 잡아 고무줄을 당길 때. 음이 천천히 올라가며 거칠게 떨리는 고무 소리."""
    sec = 0.45
    s = silence(sec)
    rubber = ((1, 1.0), (2, 0.45), (3, 0.25), (5, 0.1))
    body = tone(sec, 210, 360, decay=2.5, attack=0.04, harmonics=rubber)
    for i in range(len(body)):                      # 30Hz로 세기를 떨게 해서 '끼긱끼긱' 마찰 느낌
        body[i] *= 0.6 + 0.4 * math.sin(TAU * 30 * i / SR) ** 2
    mix(s, body, 0.0, 0.8)
    mix(s, noise(sec, decay=3, attack=0.05, lowpass=0.3, highpass=0.2, rng=rng), 0.0, 0.25)
    return s


def sling_release(rng):
    """팅-슉: 놓는 순간 고무줄이 튕기는 소리 + 돌이 날아가는 바람 소리."""
    s = silence(0.5)
    mix(s, noise(0.03, decay=120, lowpass=0.95, highpass=0.1, rng=rng), 0.0, 0.9)          # 탁 (가죽이 튕김)
    mix(s, tone(0.22, 900, 170, decay=18, harmonics=((1, 1.0), (2, 0.3))), 0.0, 0.8)     # 팅 (고무줄 진동)
    mix(s, noise(0.40, decay=7, attack=0.03, lowpass=0.25, highpass=0.15, rng=rng), 0.02, 0.5)  # 슉 (바람)
    return s


def sling_return(rng):
    """톡: 새총이 통나무 받침대에 내려앉을 때. 정수배가 아닌 배음 = 나무 두드리는 느낌."""
    s = silence(0.25)
    mix(s, tone(0.18, 420, 380, decay=35, harmonics=((1, 1.0), (2.4, 0.4), (4.1, 0.15))), 0.0, 1.0)
    mix(s, tone(0.12, 120, 80, decay=40), 0.0, 0.6)
    mix(s, noise(0.02, decay=200, lowpass=0.7, rng=rng), 0.0, 0.3)
    return s



def win(rng):
    """승리: 솔-도-미-솔 빠르게 올라간 뒤 높은 도 화음을 길게 + 반짝임 (게임 끝, 목표 점수 달성)."""
    brass = ((1, 1.0), (2, 0.5), (3, 0.33), (4, 0.18), (5, 0.1))
    s = silence(2.4)
    for i, f in enumerate((392.0, 523.25, 659.25, 783.99)):
        mix(s, tone(0.13, f, decay=6, attack=0.006, harmonics=brass), i * 0.11, 0.55)
    for f, g in ((1046.5, 0.6), (783.99, 0.45), (659.25, 0.4), (523.25, 0.35), (261.63, 0.3)):
        mix(s, tone(1.8, f, decay=1.6, attack=0.01, harmonics=brass, vibrato=5.5), 0.46, g)
    for i, f in enumerate((2093, 2637, 3136, 4186, 3136, 4186)):    # 위에서 흩날리는 반짝임
        mix(s, tone(0.2, f, decay=18), 0.5 + i * 0.12, 0.18)
    return s


def lose(rng):
    """패배: '뿌-뿌-뿌-뿌우~' 반음씩 내려가는 낮은 금관 + 마지막 음은 처지며 떨림."""
    horn = ((1, 1.0), (2, 0.6), (3, 0.35), (4, 0.15))
    s = silence(2.0)
    for i, f in enumerate((311.13, 293.66, 277.18)):              # 미♭ - 레 - 레♭
        mix(s, tone(0.32, f, decay=3, attack=0.02, harmonics=horn), i * 0.36, 0.6)
    mix(s, tone(0.95, 261.63, 233.08, decay=1.5, attack=0.02, harmonics=horn, vibrato=6.5), 1.08, 0.65)  # 도 → 처짐
    return s


SOUNDS = (
    ("SFX_Pop", pop, 0.89),
    ("SFX_GoldPop", gold_pop, 0.89),
    ("SFX_WaterSpill", water_spill, 0.80),
    ("SFX_Fanfare", fanfare, 0.80),
    ("SFX_BalloonRise", balloon_rise, 0.60),
    ("SFX_UIClick", ui_click, 0.60),
    ("SFX_StoneMiss", miss, 0.70),
    ("SFX_SlingStretch", sling_stretch, 0.55),
    ("SFX_SlingRelease", sling_release, 0.80),
    ("SFX_SlingReturn", sling_return, 0.60),
    ("SFX_Win", win, 0.80),
    ("SFX_Lose", lose, 0.75),
)

if __name__ == "__main__":
    for i, (name, fn, peak) in enumerate(SOUNDS):
        save(name, fn(random.Random(1000 + i)), peak)
