using System;
using UnityEngine;

public class GameManager : MonoBehaviour
{
   public static GameManager _instance;

   public int Score { get; private set; }
   public Action<int> OnScoreChanged;
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

    public void IncreaseScore(int amount)
    {
         Score += amount;
         OnScoreChanged?.Invoke(Score);
    }

}
