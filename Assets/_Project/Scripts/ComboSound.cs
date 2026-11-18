using UnityEngine;

// 풍선이 터질 때마다 같은 '팡' 소리를 콤보만큼 한 음씩 높여 재생한다 (최대 8단계, 기획서 7장).
// GameManager · ComboCounter와 같은 오브젝트에 AudioSource와 함께 붙인다.
[RequireComponent(typeof(AudioSource))]
public class ComboSound : MonoBehaviour
{
    [SerializeField] private ComboCounter comboCounter;
    [SerializeField] private AudioClip popClip;

    // 도레미파솔라시도. 반음(12분의 1 옥타브) 단위로 몇 칸 올릴지
    private int[] scaleSteps = { 0, 2, 4, 5, 7, 9, 11, 12 };
    private AudioSource audioSource;

    private void Awake()
    {
        audioSource = GetComponent<AudioSource>();
    }
    private void OnEnable()
    {
        comboCounter.OnComboChanged += PlayComboPop;
    }
    private void OnDisable()
    {
        comboCounter.OnComboChanged -= PlayComboPop;
    }
    private void PlayComboPop(int combo)
    {
        // 0은 콤보가 끊겼다는 알림이라 소리를 내지 않는다
        if (combo <= 0) return;

        int index = Mathf.Min(combo - 1, scaleSteps.Length - 1);
        // 반음 하나 = 주파수 2^(1/12)배. pitch는 재생 속도 배율이라 곧 음 높이가 된다
        audioSource.pitch = Mathf.Pow(2f, scaleSteps[index] / 12f);
        audioSource.PlayOneShot(popClip);
    }
}
