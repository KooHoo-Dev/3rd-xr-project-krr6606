using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.Interactables;

// 새총을 놓으면 통나무 받침대 위 처음 자리로 부드럽게 돌아간다 (결정 008).
// - 처음 자리 = 씬 시작 때 위치 · 회전 (빌더가 받침대 위에 세워 둔 자리)
// - 돌아가는 움직임은 SlingshotPouch와 같은 '지수 감쇠' 방식: 멀면 빠르게, 가까우면 천천히 다가간다
// - 다 돌아오면 딱 맞춰 놓고 '톡' 소리를 낸다
[RequireComponent(typeof(XRGrabInteractable), typeof(AudioSource))]
public class SlingshotReturn : MonoBehaviour
{
    [SerializeField] float returnSharpness = 6f;   // 클수록 빨리 돌아온다
    [SerializeField] float arriveDistance = 0.005f; // 이 거리(m) 안이면 도착으로 본다
    [SerializeField] AudioClip arriveClip;          // 받침대에 놓이는 '톡'

    XRGrabInteractable grab;
    AudioSource audioSource;
    Vector3 homePosition;
    Quaternion homeRotation;
    bool returning;

    void Awake()
    {
        grab = GetComponent<XRGrabInteractable>();
        audioSource = GetComponent<AudioSource>();
        homePosition = transform.position;
        homeRotation = transform.rotation;
        grab.selectEntered.AddListener(OnGrab);
        grab.selectExited.AddListener(OnRelease);
    }

    void OnGrab(SelectEnterEventArgs args)
    {
        returning = false;   // 돌아오는 중에 다시 잡으면 그 자리에서 멈추고 손을 따른다
    }

    void OnRelease(SelectExitEventArgs args)
    {
        returning = true;
    }

    void Update()
    {
        if (!returning) return;
        float t = 1f - Mathf.Exp(-returnSharpness * Time.deltaTime);
        transform.SetPositionAndRotation(
            Vector3.Lerp(transform.position, homePosition, t),
            Quaternion.Slerp(transform.rotation, homeRotation, t));

        if (Vector3.Distance(transform.position, homePosition) < arriveDistance)
        {
            transform.SetPositionAndRotation(homePosition, homeRotation);
            returning = false;
            audioSource.PlayOneShot(arriveClip);
        }
    }
}
