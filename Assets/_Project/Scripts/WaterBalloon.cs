using System;
using UnityEngine;

public class WaterBalloon : MonoBehaviour
{
    
    GameManager gameManager;
    Renderer rend;
    private Collider col;
    LayerMask DartLayer;
    public GameObject[] PopsVFXPrefab;
    public int BalloonScore = 1;
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

    void Pops()
    {
        gameManager.IncreaseScore(BalloonScore);
        for (int i = 0; i < PopsVFXPrefab.Length; i++)
        {
            Instantiate(PopsVFXPrefab[i], transform.position, Quaternion.identity);
        }
        Destroy(gameObject);
        
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
