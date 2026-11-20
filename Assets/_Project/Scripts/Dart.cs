using Cysharp.Threading.Tasks;
using Unity.Mathematics;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.Interactables;
public class Dart : MonoBehaviour
{
    XRGrabInteractable interactable;

    [SerializeField] private float CorrectionSpeed = 1f;
    private Vector3 originPos;
    private quaternion originRot;
    public Rigidbody rb { get; private set; }

    private object dartlock = new object();

    private bool isThrown = false;
    public bool IsThrown
    {

        get { lock (dartlock) return isThrown; }
        set
        {
            lock (dartlock)   isThrown = value;  }
        }

    private bool isThrownSuccess = false;
    public bool IsThrownSuccess
    {
        get { lock (dartlock) return isThrownSuccess; }
        set
        {
            lock (dartlock)  isThrownSuccess = value;  }
        }
    private void Awake()
    {
        rb = GetComponent<Rigidbody>();
        interactable = GetComponent<XRGrabInteractable>();
    }
    void Start()
    {
        originPos = transform.position;
        originRot = transform.rotation;
        interactable.selectEntered.AddListener(Pickup);
        interactable.selectExited.AddListener(Throw);
    }

    public void Throw(BaseInteractionEventArgs eventArgs)
    {
        rb.isKinematic = false;
        if(rb.linearVelocity.magnitude < 0.001) return;
        float speed =  rb.linearVelocity.magnitude < 0.001 ? rb.linearVelocity.magnitude : 0.01f ;
        rb.AddForce(eventArgs.interactableObject.transform.forward * ( Mathf.Clamp(CorrectionSpeed - (CorrectionSpeed / rb.linearVelocity.magnitude * CorrectionSpeed),1,CorrectionSpeed)), ForceMode.Impulse);
        
        IsThrown = true;
    }
    public void Stop()
    {
        if(rb.isKinematic) return;

        rb.linearVelocity = Vector3.zero;
        rb.angularVelocity = Vector3.zero;

        rb.isKinematic = true;

    }
    public void Pickup(BaseInteractionEventArgs eventArgs)
    {

        Debug.Log($"Pickup:{eventArgs.interactorObject.transform.name}");
    }
    public void ResetTransform()
    {
        lock (dartlock)
        {
            Stop();
            transform.SetPositionAndRotation(originPos, originRot);
        }
         IsThrown = false;
         IsThrownSuccess = false;
        
    }
   private async UniTask DelayReset(float delay)
   {
       await UniTask.Delay((int)(delay * 1000));
       ResetTransform();
   }
    void OnCollisionEnter(Collision collision)
    {

            Stop();
            DelayReset(2f).Forget();

    }
}
