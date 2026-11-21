// 게임 피드백 연결 (에디터 전용) — AI-Assist: generated
// 메뉴: Tools > Stone Challenge > Add Game Feedback (Result UI · Gold Fanfare)
//
// 지금 열린 씬에 바로 적용한다 (씬을 처음부터 다시 만들지 않으므로 직접 바꾼 값이 남는다).
// 여러 번 실행해도 된다: 전에 만든 GameFeedback 오브젝트를 지우고 다시 만든다.
//   1) GameFeedback 오브젝트 (2D AudioSource + GoldFanfare + ResultUI)
//   2) ResultUI 를 씬의 UI_ResultPanel (ResultTitle · FinalScore · RestartButton) 에 연결
//   3) 시작 패널 제목 '다트 챌린지' → '물풍선 터트리기'
using TMPro;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.SceneManagement;
using UnityEngine.UI;

public static class GameFeedbackBuilder
{
    const string AudioDir = "Assets/_Project/Audio";
    const string GameTitle = "물풍선 터트리기";

    [MenuItem("Tools/Stone Challenge/Add Game Feedback (Result UI · Gold Fanfare)")]
    static void Menu()
    {
        Scene scene = SceneManager.GetActiveScene();
        Setup(scene);
        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        Debug.Log($"[Feedback] 완료: {scene.path}");
    }

    // SlingshotSceneBuilder 도 씬을 만든 뒤 이것을 부른다 (저장은 부르는 쪽이 한다)
    public static void Setup(Scene scene)
    {
        Transform resultPanel = FindInScene(scene, "UI_ResultPanel");

        Transform old = FindInScene(scene, "GameFeedback");
        if (old != null) Object.DestroyImmediate(old.gameObject);   // 다시 실행한 경우: 전에 만든 것을 지운다

        var go = new GameObject("GameFeedback");
        SceneManager.MoveGameObjectToScene(go, scene);
        var audio = go.AddComponent<AudioSource>();
        audio.playOnAwake = false;
        audio.spatialBlend = 0f;   // 결과 · 팡파르는 어디서 났는지보다 '잘 들리는 것'이 중요해서 2D

        var gold = go.AddComponent<GoldFanfare>();
        var so = new SerializedObject(gold);
        so.FindProperty("goldPopClip").objectReferenceValue = Clip("SFX_GoldPop");
        so.FindProperty("fanfareClip").objectReferenceValue = Clip("SFX_Fanfare");
        so.ApplyModifiedPropertiesWithoutUndo();

        var result = go.AddComponent<ResultUI>();
        so = new SerializedObject(result);
        so.FindProperty("resultPanel").objectReferenceValue = resultPanel.gameObject;
        so.FindProperty("titleText").objectReferenceValue = resultPanel.Find("ResultTitle").GetComponent<TMP_Text>();
        so.FindProperty("scoreText").objectReferenceValue = resultPanel.Find("FinalScore").GetComponent<TMP_Text>();
        so.FindProperty("restartButton").objectReferenceValue = resultPanel.Find("RestartButton").GetComponent<Button>();
        so.FindProperty("winClip").objectReferenceValue = Clip("SFX_Win");
        so.FindProperty("loseClip").objectReferenceValue = Clip("SFX_Lose");
        so.ApplyModifiedPropertiesWithoutUndo();

        // 시작 패널 제목. 이미 바꾼 씬이면 '다트 챌린지' 글자가 없으니 그냥 지나간다
        foreach (TMP_Text t in FindInScene(scene, "UI_StartPanel").GetComponentsInChildren<TMP_Text>(true))
        {
            if (t.text == "다트 챌린지") t.text = GameTitle;
        }
    }

    static AudioClip Clip(string name) => AssetDatabase.LoadAssetAtPath<AudioClip>($"{AudioDir}/{name}.wav");

    // GameObject.Find 는 꺼진 오브젝트를 못 찾는다. 결과 패널은 처음에 꺼져 있어서 직접 뒤진다
    static Transform FindInScene(Scene scene, string name)
    {
        foreach (GameObject root in scene.GetRootGameObjects())
        {
            foreach (Transform t in root.GetComponentsInChildren<Transform>(true))
            {
                if (t.name == name) return t;
            }
        }
        return null;
    }
}
