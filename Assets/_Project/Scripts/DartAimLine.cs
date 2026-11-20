using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.Interactables;

// 다트를 들고 있는 동안, 다트가 똑바로 날아갈 때의 경로를 선으로 보여준다.
// 다트 FBX는 피벗 = 촉 끝, 촉 방향 = +Z 라서 transform.position / forward 를 그대로 쓴다. (Tools/AssetGen/make_dart.py)
[RequireComponent(typeof(LineRenderer))]
public class DartAimLine : MonoBehaviour
{
    [SerializeField] float maxDistance = 15f;   // 아무것도 안 맞으면 이 길이까지 그림
    [SerializeField] LayerMask hitMask = ~0;     // 선이 멈출 대상. 다트 자신은 아래에서 뺀다
    [SerializeField] Material lineMaterial;      // 비우면 Sprites/Default 사용

    LineRenderer line;
    XRGrabInteractable interactable;

    void Awake()
    {
        line = GetComponent<LineRenderer>();
        interactable = GetComponent<XRGrabInteractable>();

        // 다트 레이어를 빼지 않으면 선이 다트 자신의 콜라이더에 맞아 바로 끊긴다
        hitMask &= ~(1 << gameObject.layer);

        line.positionCount = 2;
        line.useWorldSpace = true;
        line.widthMultiplier = 0.004f;
        line.material = lineMaterial != null ? lineMaterial : new Material(Shader.Find("Sprites/Default"));
        line.startColor = new Color(1f, 1f, 1f, 0.8f);
        line.endColor = new Color(1f, 1f, 1f, 0f);   // 끝으로 갈수록 흐려져서 화면이 덜 지저분함
        line.enabled = false;

        interactable.selectEntered.AddListener(OnGrab);
        interactable.selectExited.AddListener(OnRelease);
    }

    void OnGrab(SelectEnterEventArgs args) { line.enabled = true; }
    void OnRelease(SelectExitEventArgs args) { line.enabled = false; }

    // 손이 움직인 뒤의 위치로 그려야 선이 다트보다 한 박자 늦게 따라오지 않는다
    void LateUpdate()
    {
        if (!line.enabled) return;

        Vector3 start = transform.position;
        Vector3 dir = transform.forward;
        Vector3 end = start + dir * maxDistance;
        if (Physics.Raycast(start, dir, out RaycastHit hit, maxDistance, hitMask, QueryTriggerInteraction.Collide))
            end = hit.point;

        line.SetPosition(0, start);
        line.SetPosition(1, end);
    }
}
