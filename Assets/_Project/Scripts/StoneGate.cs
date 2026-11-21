using UnityEngine;

public class StoneGate : MonoBehaviour
{
    private LayerMask stoneLayerMask;
    void Start()
    {
        stoneLayerMask =  LayerMask.NameToLayer("Stone");
    }
    private void OnTriggerEnter(Collider other)
    {
        if (stoneLayerMask == other.gameObject.layer)
        {
            Stone stone = other.GetComponent<Stone>();
            if (stone != null && stone.IsThrown)
            {
               stone.IsThrownSuccess = true;
            }
        }
    }
}
