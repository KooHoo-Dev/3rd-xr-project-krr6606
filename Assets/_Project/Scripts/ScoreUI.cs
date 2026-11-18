using System;
using TMPro;
using UnityEngine;


    public class ScoreUI : MonoBehaviour
    {
        GameManager gameManager;
        public TMP_Text scoreText;
        private int currentScore;
        private void Start()
        {
            gameManager = GameManager._instance;
            if(gameManager == null) return;
            
                gameManager.OnScoreChanged += ScoreUpdate;
        }

        private void OnEnable()
        {
            if(gameManager == null) return;
            gameManager.OnScoreChanged += ScoreUpdate;
        }

        private void OnDisable()
        {
            gameManager.OnScoreChanged -= ScoreUpdate;
        }
        private void ScoreUpdate(int newScore)
        {
            currentScore = newScore;
            scoreText.text = $"{currentScore.ToString()} / {gameManager.goalScore}" ;
        }
    }
