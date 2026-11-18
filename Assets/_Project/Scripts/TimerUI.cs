using System;
using TMPro;
using UnityEngine;


    public class TimerUI : MonoBehaviour
    {
        GameManager gameManager;
        public TMP_Text timerText;
        private void Start()
        {
            gameManager = GameManager._instance;
            if(gameManager == null) return;
            // OnEnable은 Start보다 먼저 불려서 그때는 gameManager가 비어 있다. 첫 구독은 여기서 한다
            gameManager.OnTimeChanged += TimeUpdate;
            TimeUpdate(gameManager.GameTime);
        }

        private void OnEnable()
        {
            if(gameManager == null) return;
            gameManager.OnTimeChanged += TimeUpdate;
        }

        private void OnDisable()
        {
            if(gameManager == null) return;
            gameManager.OnTimeChanged -= TimeUpdate;
        }
        private void TimeUpdate(float remainingTime)
        {
            // 내림이면 시작하자마자 59가 보이고, 0.9초 남았을 때 이미 0이 된다. 올림이라야 "0"이 곧 끝이다
            int seconds = Mathf.CeilToInt(remainingTime);
            timerText.text = $"{seconds.ToString()}";
        }
    }
