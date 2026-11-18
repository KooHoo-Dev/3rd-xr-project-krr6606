
using System;
using System.Collections.Generic;
using UnityEngine;

public class GameManager : MonoBehaviour
{
   public static GameManager _instance;
   
    public int currentScore { get; private set; }
    [field: SerializeField] public int goalScore { get; private set; } = 300; // 목표 점수
    public Action<int> OnScoreChanged;
    public ComboCounter comboCounter;     // 같은 오브젝트의 ComboCounter (ComboUI도 여기서 가져감)
    public Action<float> OnTimeChanged;   // 남은 시간이 바뀔 때 (TimerUI)
    public Action OnGameStarted;          // 시작 버튼을 눌러 게임이 시작될 때 (StartUI)
    public Action OnGameOver;             // 시간이 다 돼서 게임이 끝날 때 (StartUI)
    public bool IsGameRunning { get; private set; } = false;
    public float GameTime = 60f; // 게임 시간 (초)
    private float remainingTime;
    public bool IsGameOver { get; private set; } = false;
    List<WaterBalloon> activeBalloons = new List<WaterBalloon>();

    public void RegisterBalloon(WaterBalloon balloon)
    {
        if (activeBalloons.Contains(balloon) == false)
        {
            activeBalloons.Add(balloon);
        }
    }
    public void AllBalloonExpire()
    {
        foreach (var balloon in activeBalloons)
        {
            if (balloon != null)
            {
                balloon.GameOver();
            }
        }
        activeBalloons.Clear();
    }
    public void ResetTimer()
    {
        remainingTime = GameTime;
        IsGameOver = false;

    }
    public void StartGame()
    {
        // 버튼을 두 번 눌러도 진행 중인 게임이 처음부터 다시 시작되지 않게 막는다
        if (IsGameRunning) return;

        // 다시하기일 때 지난 판 점수가 남아 있으면 안 된다
        currentScore = 0;
        OnScoreChanged?.Invoke(currentScore);
        comboCounter.ResetCombo();

        ResetTimer();
        OnTimeChanged?.Invoke(remainingTime);

        IsGameRunning = true;
        OnGameStarted?.Invoke();
    }
    public void StopGame()
    {
        IsGameRunning = false;
    }
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
    private void Start()
    {
        ResetTimer();
    }
    private void Update()
    {
        if(IsGameRunning == false) return;
        if(IsGameOver) return;

        remainingTime -= Time.deltaTime;
        if (remainingTime <= 0f)
        {
            remainingTime = 0f;
            IsGameOver = true;
            IsGameRunning = false;
            AllBalloonExpire();
            // 끝난 뒤에도 콤보 글자가 남아 있지 않게 바로 끊는다
            comboCounter.ResetCombo();
        }
        OnTimeChanged?.Invoke(remainingTime);

        // 0초 표시를 먼저 보낸 뒤에 끝났다고 알린다
        if (IsGameOver)
        {
            OnGameOver?.Invoke();
        }

    }
    public void IncreaseScore(int amount, BalloonType balloonType)
    {
         // 콤보를 먼저 올려야 지금 터진 풍선이 자기 콤보의 배율을 받는다
         comboCounter.AddCombo();

         // 금빛 풍선은 배율 없이 고정 점수 (콤보 수는 위에서 올렸다)
         if (balloonType != BalloonType.Gold)
         {
             amount = Mathf.RoundToInt(amount * comboCounter.GetMultiplier());
         }
         currentScore += amount;
         OnScoreChanged?.Invoke(currentScore);
    }

}
