using UnityEngine;

// 새총 탄환 돌멩이 (결정 008). 예전 Dart.cs를 이름을 바꿔 정리한 것이다 (파일 GUID는 그대로).
// - 다트를 손으로 잡고 던지던 부분(XR Grab Interactable 이벤트, Throw()의 추가 힘, ResetTransform)은 새총 방식에서 쓰지 않아 뺐다.
//   필요하면 git 기록의 Dart.cs에서 볼 수 있다.
// - 남긴 것: "발사됐는지(IsThrown)"와 "던지는 선을 통과했는지(IsThrownSuccess)".
//   WaterBalloon은 주머니에 얹혀 있는(아직 안 쏜) 돌멩이에 닿아도 터지지 않게 IsThrown을 본다.
// - Dart.cs의 lock은 뺐다. Unity의 Update · 물리 콜백은 모두 메인 스레드 하나에서 돌아서 동시에 접근할 일이 없다.
[RequireComponent(typeof(Rigidbody))]
public class Stone : MonoBehaviour
{
    public Rigidbody rb { get; private set; }
    public bool IsThrown { get; private set; }
    public bool IsThrownSuccess { get; set; }

    [SerializeField] AudioClip landClip;   // 쏜 돌이 처음 땅 · 바위에 부딪힐 때 '툭'
    bool landed;                           // 굴러가며 여러 번 부딪혀도 한 번만 소리 낸다

    void Awake()
    {
        rb = GetComponent<Rigidbody>();
    }

    // 주머니에 얹을 때: 물리를 끄고 콜라이더도 꺼서 주머니 · 손과 부딪히지 않게 한다
    // 보간도 끈다. 보간은 매 프레임 '물리 계산 시점의 위치'로 Transform을 덮어써서,
    // 부모(주머니 · 새총)가 옮겨 준 위치를 되돌려 돌이 원래 자리 근처에 남아 있었다
    public void Load()
    {
        rb.interpolation = RigidbodyInterpolation.None;
        rb.isKinematic = true;
        GetComponent<Collider>().enabled = false;
        IsThrown = false;
        IsThrownSuccess = false;
        landed = false;
    }

    // 쏠 때: 물리를 켜고 속도를 준다
    // 날아갈 때는 보간을 켠다. 물리는 50Hz, Quest 화면은 72~90Hz라서 보간이 없으면 날아가는 돌이 끊겨 보인다
    public void Launch(Vector3 velocity)
    {
        transform.SetParent(null, true);
        rb.isKinematic = false;
        rb.interpolation = RigidbodyInterpolation.Interpolate;
        GetComponent<Collider>().enabled = true;
        rb.linearVelocity = velocity;
        IsThrown = true;
    }

    // 풍선은 트리거라서 여기 오지 않는다. 처음 부딪힌 것 = 땅 · 물 · 바위
    void OnCollisionEnter(Collision collision)
    {
        if (landed) return;
        landed = true;
        // 돌은 6초 뒤 사라지므로 돌에 AudioSource를 달지 않고, 그 자리에 잠깐 생기는 소리를 쓴다
        AudioSource.PlayClipAtPoint(landClip, transform.position);
    }
}
