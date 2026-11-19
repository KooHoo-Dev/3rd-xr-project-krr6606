using System;
using UnityEngine;
using DG;
using DG.Tweening;
public enum BalloonType
{
    Red,
    Blue,
    Green,
    Gold,
}
public class WaterBalloon : MonoBehaviour
{
    
    GameManager gameManager;
    Renderer rend;
    private Collider col;
    LayerMask DartLayer;
    public BalloonType balloonType;
    public GameObject[] PopsVFXPrefab;
    public int BalloonScore = 1;

    public Action<int> OnBalloonPops;
    // 점수 없이 사라질 때(체공 시간 만료) 알림. 스폰 포인트를 비우는 용도
    public Action OnBalloonExpired;

    [Header("체공 연출")]
    [SerializeField] private float riseHeight = 1.5f;   // 스폰 위치에서 얼마나 떠오를지
    [SerializeField] private float riseDuration = 1f;
    [SerializeField] private float hoverTime = 5f;      // 공중에 머무는 시간
    [SerializeField] private float bobAmount = 0.1f;    // 둥실둥실 위아래 폭
    [SerializeField] private float bobDuration = 1f;    // 한 방향으로 움직이는 시간
    [SerializeField] private float fallBelow = 0.5f;    // 스폰 높이보다 이만큼 더 내려가면 삭제
    [SerializeField] private float fallDuration = 2f;
    void Awake()
    {
        rend = GetComponent<Renderer>();
        col = GetComponent<Collider>();
    }

    private void Start()
    {
        DartLayer = LayerMask.NameToLayer("Dart");
        gameManager = GameManager._instance;
    }
    private void OnEnable()
    {
        // 골드 풍선은 GoldBalloonMover가 움직이고 만료도 없다. 두 트윈이 같은 Transform을 다투지 않게 여기서 빠진다
        if (balloonType == BalloonType.Gold) return;

        // DOMoveY는 "목표 월드 높이"를 받으므로, 스폰 높이를 기준으로 계산한다
        float spawnY = transform.position.y;
        float hoverY = spawnY + riseHeight;

        // Yoyo는 한 번 = 한 방향. 짝수여야 hoverY로 돌아온 뒤 하강이 시작돼 반복시에 범위를 벗어나지 않는다.
        int bobLoops = Mathf.RoundToInt(hoverTime / bobDuration);
        if (bobLoops % 2 == 1) bobLoops++;
        if (bobLoops < 2) bobLoops = 2;

        Sequence seq = DOTween.Sequence();
        seq.Append(transform.DOMoveY(hoverY, riseDuration).SetEase(Ease.OutSine));
        seq.Append(transform.DOMoveY(hoverY + bobAmount, bobDuration)
            .SetEase(Ease.InOutSine)
            .SetLoops(bobLoops, LoopType.Yoyo));
        seq.Append(transform.DOMoveY(spawnY - fallBelow, fallDuration).SetEase(Ease.InQuad));
        seq.OnComplete(Expire);
        // 다트에 맞아 Destroy되면 시퀀스도 같이 정리 (Expire도 호출되지 않음)
        seq.SetLink(gameObject);
    }

    // 끝까지 안 맞고 스폰 높이 아래로 내려간 경우: 점수 없이 삭제
    void Expire()
    {
        OnBalloonExpired?.Invoke();
        Destroy(gameObject);
    }
    // 게임이 끝나서 모든 풍선을 삭제할 때: 점수 없이 삭제
    public void GameOver()
    {
        OnBalloonExpired?.Invoke();
        for (int i = 0; i < PopsVFXPrefab.Length; i++)
        {
            Instantiate(PopsVFXPrefab[i], transform.position, Quaternion.identity);
        }
        Destroy(gameObject);
    }

    void Pops()
    {
        gameManager.IncreaseScore(BalloonScore, balloonType);
        OnBalloonPops?.Invoke(BalloonScore);

        for (int i = 0; i < PopsVFXPrefab.Length; i++)
        {
            Instantiate(PopsVFXPrefab[i], transform.position, Quaternion.identity);
        }
        Destroy(gameObject);
        
    }
    private void OnDestroy()
    {
        OnBalloonPops = null;
        OnBalloonExpired = null;
    }
    void OnTriggerEnter(Collider other)
    {
        if (other.gameObject.layer == DartLayer)
        {
            Debug.Log("[WaterBalloon] " +other.gameObject.name + "이 충돌했습니다!");
            Dart dart = other.gameObject.GetComponent<Dart>();
            if(dart?.IsThrown == false) return;
            
            Pops();
        }
    }
}
