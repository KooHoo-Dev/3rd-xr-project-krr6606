using UnityEngine;

public class GameManager : MonoBehaviour
{
   public static GameManager _instance;

    private void Awake()
    {
         if (_instance == null)
         {
              _instance = this;
              DontDestroyOnLoad(gameObject);
         }
         else
         {
              Destroy(gameObject);
         }
    }


}
