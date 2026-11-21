using UnityEngine;

// 금빛 풍선을 맞히면 '금빛 팡(동전 소리)'과 팡파르를 함께 낸다 (기획서 7장).
// 풍선은 맞는 순간 사라지므로 풍선 대신 씬에 늘 있는 이 오브젝트가 소리를 낸다.
// 콤보 '팡'(ComboSound)은 따로 나므로 여기서는 금빛 전용 소리만 더한다.
[RequireComponent(typeof(AudioSource))]
public class GoldFanfare : MonoBehaviour
{
    [SerializeField] AudioClip goldPopClip;
    [SerializeField] AudioClip fanfareClip;
    [SerializeField] float fanfareDelay = 0.25f;   // 동전 소리가 먼저 들리고 팡파르가 이어지게

    AudioSource audioSource;

    void Awake()
    {
        audioSource = GetComponent<AudioSource>();
    }

    // static 이벤트는 씬이 바뀌어도 남으므로, 꺼질 때 꼭 구독을 푼다
    void OnEnable()
    {
        WaterBalloon.OnAnyBalloonPopped += OnBalloonPopped;
    }

    void OnDisable()
    {
        WaterBalloon.OnAnyBalloonPopped -= OnBalloonPopped;
    }

    void OnBalloonPopped(BalloonType type)
    {
        if (type != BalloonType.Gold) return;
        audioSource.PlayOneShot(goldPopClip);
        Invoke(nameof(PlayFanfare), fanfareDelay);
    }

    void PlayFanfare()
    {
        audioSource.PlayOneShot(fanfareClip);
    }
}
