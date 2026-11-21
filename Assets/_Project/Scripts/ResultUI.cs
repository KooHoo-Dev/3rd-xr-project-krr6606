using TMPro;
using UnityEngine;
using UnityEngine.UI;

// 게임이 끝나면 결과 패널에 승리/패배와 최종 점수를 보여주고, 결과에 맞는 소리를 낸다.
// 다시하기 버튼을 누르면 새 게임을 시작하고, 시작되면 패널을 숨긴다.
// StartUI와 같은 이유로 항상 켜져 있는 오브젝트에 붙인다 (패널에 붙이면 패널이 꺼질 때 구독이 풀린다)
[RequireComponent(typeof(AudioSource))]
public class ResultUI : MonoBehaviour
{
    [SerializeField] GameObject resultPanel;
    [SerializeField] TMP_Text titleText;
    [SerializeField] TMP_Text scoreText;
    [SerializeField] Button restartButton;
    [SerializeField] AudioClip winClip;
    [SerializeField] AudioClip loseClip;
    [SerializeField] Color winColor = new Color(1f, 0.82f, 0.2f);   // 금빛
    [SerializeField] Color loseColor = new Color(0.55f, 0.7f, 1f);  // 차가운 파랑

    GameManager gameManager;
    AudioSource audioSource;

    // GameManager._instance는 GameManager의 Awake에서 정해지므로 Start에서 가져온다
    void Start()
    {
        gameManager = GameManager._instance;
        audioSource = GetComponent<AudioSource>();
        gameManager.OnGameOver += ShowResult;
        gameManager.OnGameStarted += HideResult;
        restartButton.onClick.AddListener(OnClickRestart);
        HideResult();
    }

    void OnDestroy()
    {
        gameManager.OnGameOver -= ShowResult;
        gameManager.OnGameStarted -= HideResult;
    }

    void ShowResult()
    {
        int score = gameManager.currentScore;
        bool win = score >= gameManager.goalScore;

        titleText.text = win ? "성공!" : "아쉬워요!";
        titleText.color = win ? winColor : loseColor;
        scoreText.text = $"최종 점수 {score}점\n목표 {gameManager.goalScore}점";
        resultPanel.SetActive(true);
        audioSource.PlayOneShot(win ? winClip : loseClip);
    }

    void HideResult()
    {
        resultPanel.SetActive(false);
    }

    void OnClickRestart()
    {
        gameManager.StartGame();   // 시작되면 OnGameStarted → HideResult로 패널이 꺼진다
    }
}
