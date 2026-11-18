using System;
using UnityEngine;

// 콤보 수 · 남은 콤보 시간 · 배율만 담당한다. 점수는 GameManager가 더한다.
// GameManager와 같은 오브젝트에 붙이고, GameManager가 참조로 들고 있게 한다.
public class ComboCounter : MonoBehaviour
{
    [SerializeField] private float comboWindow = 1.5f;   // 이 시간 안에 다음 풍선을 터트려야 콤보 유지
    [SerializeField] private float maxMultiplier = 3f;   // 배율 상한

    public int CurrentCombo { get; private set; } = 0;
    private float comboTimer = 0f;   // 콤보가 끊기기까지 남은 시간

    public Action<int> OnComboChanged;   // ComboUI가 구독 (0이면 콤보 끊김)

    private void Update()
    {
        // 콤보가 없으면(0) 아무것도 하지 않는다
        if (CurrentCombo == 0) return;

        // comboTimer를 Time.deltaTime만큼 깎는다
        comboTimer -= Time.deltaTime;

        // 0 이하가 되면 ResetCombo()
        if (comboTimer <= 0f)
        {
            ResetCombo();
        }
    }

    // 풍선이 터질 때마다 GameManager가 부른다. 금빛 풍선도 콤보는 올린다
    public void AddCombo()
    {
        CurrentCombo++;
        comboTimer = comboWindow;
        OnComboChanged?.Invoke(CurrentCombo);
    }

    // 공식: min(1 + 0.5 × (콤보 − 1), 최대 배율)
    public float GetMultiplier()
    {
        // 콤보가 0이거나 1이면 ×1
        if (CurrentCombo <= 1) return 1f;

        // 공식대로 계산하고 maxMultiplier를 넘지 않게 자른다
        float multiplier = 1f + 0.5f * (CurrentCombo - 1);
        return Mathf.Min(multiplier, maxMultiplier);
    }

    // 시간이 지나 끊길 때, 새 게임을 시작할 때 부른다
    public void ResetCombo()
    {
        CurrentCombo = 0;
        comboTimer = 0f;
        OnComboChanged?.Invoke(CurrentCombo);
    }
}