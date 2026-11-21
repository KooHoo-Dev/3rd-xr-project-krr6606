using UnityEngine;

// 고무줄 두 줄을 갈래 끝(BandAnchor)에서 주머니 매듭(BandTie)까지 잇는다.
// Band.fbx는 길이 1 m, 피벗 = 시작점, +Z로 뻗은 관이라서 "앵커에 두고 → 매듭을 바라보게 → Z 스케일 = 거리"면 된다.
// 주머니(SlingshotPouch)가 LateUpdate에서 움직인 다음에 그려야 한 프레임 늦지 않으므로 실행 순서를 뒤로 둔다.
[DefaultExecutionOrder(100)]
public class SlingshotBands : MonoBehaviour
{
    [SerializeField] Transform anchorL, anchorR;   // 새총 갈래 끝
    [SerializeField] Transform tieL, tieR;         // 주머니 양 끝
    [SerializeField] Transform bandL, bandR;       // Band.fbx 인스턴스 두 개

    void LateUpdate()
    {
        Stretch(bandL, anchorL.position, tieL.position);
        Stretch(bandR, anchorR.position, tieR.position);
    }

    void Stretch(Transform band, Vector3 from, Vector3 to)
    {
        Vector3 dir = to - from;
        float length = dir.magnitude;
        band.SetPositionAndRotation(from, Quaternion.LookRotation(dir / length, transform.up));
        // 늘어날수록 살짝 가늘어지게 (부피가 비슷하게 유지되는 느낌)
        float thin = Mathf.Clamp(Mathf.Sqrt(0.12f / length), 0.6f, 1f);
        band.localScale = new Vector3(thin, thin, length);
    }
}
