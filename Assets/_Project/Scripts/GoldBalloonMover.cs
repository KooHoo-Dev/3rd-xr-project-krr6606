using DG.Tweening;
using UnityEngine;

// 골드 풍선 전용: 스폰 위치 주변 범위 안에서 무작위 지점으로 계속 옮겨 다닌다.
// 맞을 때까지 유지(만료 없음). WaterBalloon은 골드일 때 체공 시퀀스를 건너뛴다.
public class GoldBalloonMover : MonoBehaviour
{
    [SerializeField] private Vector2 moveRange = new Vector2(1.5f, 0.8f); // 스폰 위치 기준 X·Y 최대 거리
    [SerializeField] private float minMoveTime = 0.4f;
    [SerializeField] private float maxMoveTime = 1.2f;

    private Vector3 centerPos;

    private void Start()
    {
        // 범위의 중심은 스폰 위치로 고정. 현재 위치 기준이면 점점 범위 밖으로 흘러간다
        centerPos = transform.position;
        MoveToNextPoint();
    }

    void MoveToNextPoint()
    {
        Vector3 target = centerPos;
        target.x += Random.Range(-moveRange.x, moveRange.x);
        target.y += Random.Range(-moveRange.y, moveRange.y);

        // 이동 시간도 매번 다르게 해서 속도로도 예측하기 어렵게 한다
        float moveTime = Random.Range(minMoveTime, maxMoveTime);

        transform.DOMove(target, moveTime)
            .SetEase(Ease.InOutSine)
            .OnComplete(MoveToNextPoint)   // 도착하면 다음 지점으로 → 끝없이 반복
            .SetLink(gameObject);          // 다트에 맞아 Destroy되면 트윈도 정리
    }
}
