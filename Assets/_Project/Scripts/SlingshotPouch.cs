using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.Interactables;

// 새총 주머니 (결정 008). 새총의 자식이라 새총과 같은 프레임에 같이 움직인다.
// - 쉴 때: 실제 새총처럼 갈래 가운데에서 아래로 축 늘어진다. 중력 방향(월드 아래)으로 매달리고, 새총을 흔들면 살짝 늦게 따라온다.
// - 당길 때: 새총 기준 좌표에서 앞뒤(Z = 세기)와 높이(Y = 쏘는 각도 위아래)만 손을 따라간다. 좌우(X)는 잠근다.
//   손이 옆으로 가거나 돌아도 주머니는 새총 가운데 면을 벗어나지 않아서, 당기는 손의 좌우 떨림이 조준에 섞이지 않는다.
// - 발사 방향 = 주머니 → 갈래 가운데, 세기 = 앞뒤로 당긴 거리 × launchPower. 손을 휘두르는 속도는 쓰지 않는다.
// - XRI는 잡았다/놓았다만 판정한다 (Track Position · Rotation 끔, 잡을 때 부모에서 떼지 않음).
[RequireComponent(typeof(XRGrabInteractable), typeof(AudioSource))]
public class SlingshotPouch : MonoBehaviour
{
    [SerializeField] Transform slingshot;          // 새총 몸체 (+Z = 쏘는 방향)
    [SerializeField] Transform anchorL, anchorR;   // 고무줄이 묶인 갈래 끝. 두 점의 가운데가 당김 축의 시작점
    [SerializeField] Transform stoneSeat;          // 돌멩이가 놓이는 자리 (주머니의 자식 StoneSeat)
    [SerializeField] Stone[] stonePrefabs;         // 돌멩이 10종 중 무작위로 장전
    [Header("쉴 때 (늘어짐)")]
    [SerializeField] float hangLength = 0.12f;     // 갈래 가운데에서 아래로 늘어진 길이 (m)
    [SerializeField] float hangBack = 0.03f;       // 살짝 플레이어 쪽으로
    [SerializeField] float hangSmoothTime = 0.08f; // 새총을 흔들 때 따라오는 시간. 클수록 더 늦게 · 더 출렁임
    [Header("당길 때")]
    [SerializeField] float maxPull = 0.45f;        // 앞뒤로 최대로 당기는 거리 (m)
    [SerializeField] float maxRaise = 0.10f;       // 갈래 가운데보다 위로 올릴 수 있는 높이 (m) → 낮게 쏘기
    [SerializeField] float maxLower = 0.15f;       // 아래로 내릴 수 있는 높이 (m) → 높이 쏘기
    [SerializeField] float pullSharpness = 20f;    // 당긴 위치를 부드럽게 따라가는 정도. 작을수록 부드럽지만 늦다
    [SerializeField] float launchPower = 40f;      // 당긴 1 m 당 발사 속도 (m/s)
    [SerializeField] float minPull = 0.05f;        // 이보다 적게 당기면 쏘지 않음
    [SerializeField] float reloadDelay = 0.3f;
    [Header("소리")]
    [SerializeField] AudioClip stretchClip;        // 주머니를 잡을 때 고무줄 '끼익'
    [SerializeField] AudioClip releaseClip;        // 쏠 때 '팅-슉'

    XRGrabInteractable grab;
    AudioSource audioSource;
    Transform hand;              // 잡은 손의 잡기 기준점
    Vector2 pull;                // 부드럽게 만든 당긴 위치 (x = 높이 Y, y = 앞뒤로 당긴 거리). 새총 기준 좌표
    Vector3 hangVelocity;        // SmoothDamp가 쓰는 속도 기억
    Stone loadedStone;

    public bool IsPulling => hand != null;
    public Vector3 LaunchPoint => stoneSeat.position;
    // 주머니에서 갈래 가운데로 향하는 방향 × 앞뒤로 당긴 거리 × 세기
    public Vector3 LaunchVelocity => slingshot.TransformDirection(-PullOffset().normalized) * (pull.y * launchPower);
    // 갈래 끝 두 점은 새총의 자식이라 localPosition = 새총 기준 좌표
    Vector3 ForkLocal => (anchorL.localPosition + anchorR.localPosition) * 0.5f;
    Vector3 ForkCenter => slingshot.TransformPoint(ForkLocal);
    Vector3 PullOffset() => new Vector3(0f, pull.x, -pull.y);   // 갈래 가운데 기준 주머니 위치. X는 늘 0 (잠금)

    void Awake()
    {
        grab = GetComponent<XRGrabInteractable>();
        audioSource = GetComponent<AudioSource>();
        grab.selectEntered.AddListener(OnGrab);
        grab.selectExited.AddListener(OnRelease);
        LoadStone();
    }

    void OnGrab(SelectEnterEventArgs args)
    {
        hand = args.interactorObject.GetAttachTransform(grab);
        pull = TargetPull();
        audioSource.PlayOneShot(stretchClip);
    }

    // 손 위치를 새총 기준 좌표로 바꿔서 높이(Y)와 앞뒤(Z)만 쓴다. 좌우(X)는 버린다
    Vector2 TargetPull()
    {
        Vector3 local = slingshot.InverseTransformPoint(hand.position) - ForkLocal;
        return new Vector2(Mathf.Clamp(local.y, -maxLower, maxRaise), Mathf.Clamp(-local.z, 0f, maxPull));
    }

    void LateUpdate()
    {
        if (IsPulling)
        {
            // 프레임 속도와 상관없이 같은 정도로 부드러워지도록 지수 감쇠 비율을 쓴다
            pull = Vector2.Lerp(pull, TargetPull(), 1f - Mathf.Exp(-pullSharpness * Time.deltaTime));
            Vector3 offset = PullOffset();
            transform.localPosition = ForkLocal + offset;
            // 오목한 앞면(+Z)이 갈래 가운데를 보게.
            // 앞뒤로 거의 안 당긴 상태(잡은 직후 등)는 방향이 위 · 아래로만 남아 계산이 안 되므로 새총 앞쪽을 본다 — 정상 상태
            transform.localRotation = pull.y > 1e-3f ? Quaternion.LookRotation(-offset, Vector3.up) : Quaternion.identity;
            return;
        }
        Vector3 target = ForkCenter + Vector3.down * hangLength - slingshot.forward * hangBack;
        transform.position = Vector3.SmoothDamp(transform.position, target, ref hangVelocity, hangSmoothTime);
        // 매달린 주머니: 위쪽(+Y)이 갈래 가운데를 향하고, 오목한 앞면은 새총 앞쪽을 본다
        transform.rotation = Quaternion.LookRotation(slingshot.forward, ForkCenter - transform.position);
    }

    void OnRelease(SelectExitEventArgs args)
    {
        // 쏜 직후 재장전 대기(reloadDelay) 동안은 돌멩이가 없다 — 정상 상태라서 확인한다
        if (loadedStone != null && pull.y >= minPull)
            Fire();
        hand = null;
        pull = Vector2.zero;
        hangVelocity = Vector3.zero;
    }

    void Fire()
    {
        Stone stone = loadedStone;
        loadedStone = null;
        stone.Launch(LaunchVelocity);                    // 여기서 주머니에서 떨어져 나온다 (부모 해제)
        audioSource.PlayOneShot(releaseClip);
        Collider col = stone.GetComponent<Collider>();
        // 주머니 · 새총 콜라이더 안에서 출발하므로 서로 부딪혀 튕기지 않게 한다 (다음 물리 계산 전에 적용됨)
        foreach (Collider c in slingshot.GetComponentsInChildren<Collider>(true)) Physics.IgnoreCollision(col, c);
        Destroy(stone.gameObject, 6f);
        Invoke(nameof(LoadStone), reloadDelay);
    }

    void LoadStone()
    {
        Stone prefab = stonePrefabs[Random.Range(0, stonePrefabs.Length)];
        loadedStone = Instantiate(prefab, stoneSeat.position, stoneSeat.rotation, stoneSeat);
        loadedStone.Load();                              // 주머니에 얹혀 있는 동안은 물리를 끈다
    }
}
