using UnityEngine;

public class DartGate : MonoBehaviour
{
    private LayerMask dartLayerMask;
    void Start()
    {
        dartLayerMask =  LayerMask.NameToLayer("Dart");
    }
    private void OnTriggerEnter(Collider other)
    {
        if (dartLayerMask == (dartLayerMask | (1 << other.gameObject.layer)))
        {
            Dart dart = other.GetComponent<Dart>();
            if (dart != null && dart.IsThrown)
            {
               dart.IsThrownSuccess = true;
            }
        }
    }
}
