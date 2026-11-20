// 손 추적 테스트 씬 만들기 (에디터 전용) — AI-Assist: generated
// 메뉴: Tools > Dart Challenge > Build Hands Test Scene
//
// 하는 일 (docs/decisions/006)
//   1) DartDemo.unity 를 DartDemo_Hands.unity 로 복제한다 (원본 씬은 건드리지 않음)
//   2) 복제본의 XR Origin (XR Rig) 을 XR Origin Hands (XR Rig) 로 교체한다 (같은 위치 · 회전)
//      - 손 리그 안에 컨트롤러 리그가 들어 있어서, 컨트롤러를 내려놓으면 손으로 자동 전환된다
//   3) 옛 리그 카메라를 쓰던 Canvas(Event Camera)를 새 리그 카메라로 다시 연결한다
//   4) 새 리그의 모든 Near-Far Interactor 가 다트를 잡을 수 있게 맞춘다
//      - Interaction Layers 에 다트 프리팹의 Interaction Layers 를 더함
//      - 근거리(Sphere) · 원거리(Curve) 캐스터의 Physics Layer Mask 에 Dart 레이어를 더함
//   5) 손으로 잡을 때만 다트 끝이 앞을 향하도록 회전 오프셋을 준다 (docs/decisions/007)
//      - 손의 Pinch Grab Pose 아래에 "Dart Grip Offset" 자식을 만들고,
//        Interaction Attach Controller 가 그 자식을 따라가게 바꾼다 (컨트롤러는 그대로)
//      - Play 중 Dart Grip Offset 의 Rotation 을 바꿔 보며 각도를 찾고, 찾은 값을 GripOffsetEuler 에 적는다
//   (손 던지기 위쪽 보정 HandThrowAssist 는 사용자 판단으로 삭제함 — docs/decisions/007)
using System.Collections.Generic;
using Unity.XR.CoreUtils;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.XR.Interaction.Toolkit.Attachment;
using UnityEngine.XR.Interaction.Toolkit.Interactables;
using UnityEngine.XR.Interaction.Toolkit.Interactors;
using UnityEngine.XR.Interaction.Toolkit.Interactors.Casters;

public static class HandsTestSceneBuilder
{
    const string SourceScene = "Assets/_Project/Scenes/DartDemo.unity";
    const string TargetScene = "Assets/_Project/Scenes/DartDemo_Hands.unity";
    const string HandsRigPath = "Assets/Samples/XR Interaction Toolkit/3.5.1/Hands Interaction Demo/Prefabs/XR Origin Hands (XR Rig).prefab";
    const string DartPrefabPath = "Assets/_Project/Prefabs/Dart_01.prefab";

    // 사용자가 Link Play 중 직접 맞춘 값 (2026-11-20, 양손 동일)
    static readonly Vector3 GripOffsetEuler = new Vector3(45f, -45f, 0f);

    [MenuItem("Tools/Dart Challenge/Build Hands Test Scene")]
    public static void Build()
    {
        var handsRig = AssetDatabase.LoadAssetAtPath<GameObject>(HandsRigPath);
        var dartPrefab = AssetDatabase.LoadAssetAtPath<GameObject>(DartPrefabPath);
        int dartLayer = LayerMask.NameToLayer("Dart");
        if (handsRig == null || dartPrefab == null || dartLayer < 0)
        {
            Debug.LogError($"[HandsTest] 준비물 없음 — 손 리그:{handsRig != null}, 다트 프리팹:{dartPrefab != null}, Dart 레이어:{dartLayer}");
            return;
        }

        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;

        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(TargetScene) != null &&
            !EditorUtility.DisplayDialog("Hands Test Scene", TargetScene + " 가 이미 있습니다. DartDemo 에서 다시 만들까요?", "다시 만들기", "취소"))
            return;

        AssetDatabase.DeleteAsset(TargetScene);
        if (!AssetDatabase.CopyAsset(SourceScene, TargetScene))
        {
            Debug.LogError("[HandsTest] 씬 복제 실패: " + SourceScene);
            return;
        }
        var scene = EditorSceneManager.OpenScene(TargetScene, OpenSceneMode.Single);

        // 2) 리그 교체
        var oldOrigin = Object.FindFirstObjectByType<XROrigin>();
        if (oldOrigin == null)
        {
            Debug.LogError("[HandsTest] 씬에 XR Origin 이 없습니다.");
            return;
        }
        var oldRig = oldOrigin.gameObject;
        var oldCam = oldOrigin.Camera;

        var newRig = (GameObject)PrefabUtility.InstantiatePrefab(handsRig, scene);
        newRig.transform.SetParent(oldRig.transform.parent, false);
        newRig.transform.SetPositionAndRotation(oldRig.transform.position, oldRig.transform.rotation);
        newRig.transform.SetSiblingIndex(oldRig.transform.GetSiblingIndex());
        var newCam = newRig.GetComponent<XROrigin>().Camera;

        // 3) Canvas 의 Event Camera 재연결 (옛 카메라가 사라지면 레이로 UI 를 못 누름)
        int canvasCount = 0;
        foreach (var canvas in Object.FindObjectsByType<Canvas>(FindObjectsInactive.Include, FindObjectsSortMode.None))
        {
            if (canvas.worldCamera != null && canvas.worldCamera == oldCam)
            {
                canvas.worldCamera = newCam;
                canvasCount++;
            }
        }
        Object.DestroyImmediate(oldRig);

        // 4) 다트를 잡을 수 있게 레이어 맞추기 (손 · 컨트롤러 모두)
        var dartGrab = dartPrefab.GetComponentInChildren<XRGrabInteractable>(true);
        int dartInteraction = dartGrab != null ? dartGrab.interactionLayers.value : 1;
        int dartPhysics = 1 << dartLayer;

        var changed = new List<string>();
        foreach (var interactor in newRig.GetComponentsInChildren<NearFarInteractor>(true))
        {
            interactor.interactionLayers = interactor.interactionLayers.value | dartInteraction;
            changed.Add(interactor.name);
        }
        foreach (var sphere in newRig.GetComponentsInChildren<SphereInteractionCaster>(true))
            sphere.physicsLayerMask = sphere.physicsLayerMask.value | dartPhysics;
        foreach (var curve in newRig.GetComponentsInChildren<CurveInteractionCaster>(true))
            curve.raycastMask = curve.raycastMask.value | dartPhysics;

        // 5) 손 잡기 회전 오프셋 (Pinch Grab Pose 를 따라가는 것만 = 손만)
        int offsetCount = 0;
        foreach (var attach in newRig.GetComponentsInChildren<InteractionAttachController>(true))
        {
            var follow = attach.transformToFollow;
            if (follow == null || follow.name != "Pinch Grab Pose") continue;

            var offset = new GameObject("Dart Grip Offset").transform;
            offset.SetParent(follow, false);
            offset.localRotation = Quaternion.Euler(GripOffsetEuler);
            attach.transformToFollow = offset;
            PrefabUtility.RecordPrefabInstancePropertyModifications(attach);
            offsetCount++;
        }

        // 프리팹 인스턴스 안의 값을 바꿨으므로 오버라이드로 기록되게 한다
        PrefabUtility.RecordPrefabInstancePropertyModifications(newRig);
        foreach (var c in newRig.GetComponentsInChildren<Component>(true))
            if (c is NearFarInteractor || c is SphereInteractionCaster || c is CurveInteractionCaster)
                PrefabUtility.RecordPrefabInstancePropertyModifications(c);

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        Debug.Log($"[HandsTest] 완료: {TargetScene}\n" +
                  $"- Canvas 카메라 재연결 {canvasCount}개\n" +
                  $"- 다트 잡기 설정한 Near-Far Interactor {changed.Count}개: {string.Join(", ", changed)}\n" +
                  $"- 손 잡기 회전 오프셋 {offsetCount}개 (기대값 2)");
    }
}
