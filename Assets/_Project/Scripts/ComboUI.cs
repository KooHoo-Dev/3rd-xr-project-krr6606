using System;
using TMPro;
using UnityEngine;
using DG.Tweening;


    // ScoreUI · TimerUI와 같은 구조. 콤보 텍스트가 붙은 오브젝트(또는 그 부모)에 붙인다
    public class ComboUI : MonoBehaviour
    {
        ComboCounter comboCounter;
        public TMP_Text comboText;

        [Header("콤보 연출")]
        [SerializeField] private Color lowComboColor = new Color(1f, 0.9f, 0.4f);   // 2콤보: 연한 노랑
        [SerializeField] private Color highComboColor = new Color(1f, 0.25f, 0.1f); // maxStep콤보: 진한 주황빨강
        [SerializeField] private int maxStep = 8;            // 이 콤보에서 색 · 크기가 최대
        [SerializeField] private float maxScale = 1.6f;      // 최대 콤보일 때 기본 크기의 몇 배
        [SerializeField] private float punchAmount = 0.3f;   // 콤보가 오를 때 튀는 정도
        private void Start()
        {
            if(GameManager._instance == null) return;
            comboCounter = GameManager._instance.comboCounter;
            if(comboCounter == null) return;
            comboCounter.OnComboChanged += ComboUpdate;
            ComboUpdate(0);
        }

        private void OnEnable()
        {
            if(comboCounter == null) return;
            comboCounter.OnComboChanged += ComboUpdate;
        }

        private void OnDisable()
        {
            if(comboCounter == null) return;
            comboCounter.OnComboChanged -= ComboUpdate;
        }
        private void ComboUpdate(int combo)
        {
            // 1콤보는 그냥 첫 터짐이라 보여줄 필요 없음
            if (combo < 2)
            {
                comboText.text = "";
                return;
            }
            comboText.text = $"{combo.ToString()} Combo!";

            // 2콤보 → 0, maxStep콤보 이상 → 1. 이 비율로 색과 크기를 함께 키운다
            float t = Mathf.Clamp01((combo - 2) / (float)(maxStep - 2));
            comboText.color = Color.Lerp(lowComboColor, highComboColor, t);

            // 이전 펀치가 끝나기 전에 또 오르면 크기가 어긋나므로, 먼저 끊고 목표 크기로 맞춘 뒤 튀긴다
            comboText.transform.DOKill();
            float scale = Mathf.Lerp(1f, maxScale, t);
            comboText.transform.localScale = Vector3.one * scale;
            comboText.transform.DOPunchScale(Vector3.one * punchAmount, 0.25f, 6, 0.5f)
                .SetLink(comboText.gameObject);
        }
    }
