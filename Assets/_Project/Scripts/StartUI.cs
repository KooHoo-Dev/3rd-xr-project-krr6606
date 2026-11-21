using System;
using UnityEngine;
using UnityEngine.UI;


    // 이 스크립트는 항상 켜져 있는 Canvas에 붙인다. 패널 자신에 붙이면
    // 패널이 꺼질 때 OnDisable에서 구독이 풀려 게임 오버 때 다시 켤 수 없다
    public class StartUI : MonoBehaviour
    {
        GameManager gameManager;
        public GameObject startPanel;   // 시작 버튼이 들어 있는 패널
        public Button startButton;
        private void Start()
        {
            gameManager = GameManager._instance;
            if(gameManager == null) return;
            gameManager.OnGameStarted += HideStartPanel;
            // 게임이 끝나면 결과 패널(ResultUI)이 같은 자리에 뜨고 다시하기도 거기서 한다. 시작 패널은 처음 한 번만 보인다
            startButton.onClick.AddListener(OnClickStart);
            ShowStartPanel();
        }

        private void OnDestroy()
        {
            if(gameManager == null) return;
            gameManager.OnGameStarted -= HideStartPanel;
        }
        private void OnClickStart()
        {
            // 패널은 여기서 끄지 않는다. 시작이 실제로 됐을 때(OnGameStarted)만 끈다
            gameManager.StartGame();
        }
        private void HideStartPanel()
        {
            startPanel.SetActive(false);
        }
        private void ShowStartPanel()
        {
            startPanel.SetActive(true);
        }
    }
