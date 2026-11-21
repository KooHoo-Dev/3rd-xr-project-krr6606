using UnityEngine;

// 주머니를 당기는 동안, 놓으면 돌멩이가 날아갈 포물선을 그린다.
// 발사 속도(SlingshotPouch.LaunchVelocity)를 놓기 전에 이미 알 수 있으므로, 실제 궤적과 같은 선을 그릴 수 있다.
[RequireComponent(typeof(LineRenderer))]
[DefaultExecutionOrder(100)]   // 주머니가 움직인 다음에 그린다
public class SlingshotTrajectory : MonoBehaviour
{
    [SerializeField] SlingshotPouch pouch;
    [SerializeField] int points = 40;
    [SerializeField] float timeStep = 0.04f;      // 점 사이 시간 간격 (초). 40점이면 1.6초 앞까지
    [SerializeField] LayerMask hitMask = ~0;      // 선이 멈출 대상 (지형 등)

    LineRenderer line;

    void Awake()
    {
        line = GetComponent<LineRenderer>();
        line.useWorldSpace = true;
        if (line.sharedMaterial == null)   // 비워 두면 기본 스프라이트 재질
            line.material = new Material(Shader.Find("Sprites/Default"));
        line.enabled = false;
    }

    void LateUpdate()
    {
        line.enabled = pouch.IsPulling;
        if (!line.enabled) return;

        Vector3 pos = pouch.LaunchPoint;
        Vector3 vel = pouch.LaunchVelocity;
        line.positionCount = points;
        line.SetPosition(0, pos);
        for (int i = 1; i < points; i++)
        {
            // 한 칸씩 물리처럼 전진: 속도에 중력을 더하고, 위치에 속도를 더한다
            Vector3 next = pos + vel * timeStep + 0.5f * Physics.gravity * timeStep * timeStep;
            vel += Physics.gravity * timeStep;
            if (Physics.Linecast(pos, next, out RaycastHit hit, hitMask, QueryTriggerInteraction.Ignore))
            {
                line.SetPosition(i, hit.point);           // 땅 등에 닿으면 거기서 선을 끝낸다
                line.positionCount = i + 1;
                return;
            }
            line.SetPosition(i, next);
            pos = next;
        }
    }
}
