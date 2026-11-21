// 새총 테스트 씬 만들기 (에디터 전용) — AI-Assist: generated
// 메뉴: Tools > Stone Challenge > Build Slingshot Test Scene
//
// 하는 일 (docs/decisions/008)
//   1) StoneDemo_Hands.unity 를 StoneDemo_Slingshot.unity 로 복제한다 (원본 씬은 건드리지 않음)
//   2) 새총 · 주머니 · 고무줄 · 돌멩이 FBX의 재질을 M_Palette 로 연결한다
//   3) 돌멩이 10종 프리팹을 만든다 (Stone + Rigidbody + 구 콜라이더, Stone 레이어 → 풍선이 터지는 레이어)
//      - 돌멩이마다 가장 얇은 축이 앞(+Z)을 향하게 눕히고, 피벗을 '뒷면'에 둔다
//        → 주머니의 StoneSeat 에 두면 넓은 면이 주머니 면에 맞닿는다
//   4) 통나무 받침대 위에 새총을 세운다. 주머니 · 고무줄은 새총의 '자식'이다
//      - 자식이라 새총과 같은 프레임에 움직인다 (따로 두면 XRI 가 새총을 렌더 직전에 한 번 더 옮겨서 한 박자 늦게 흔들렸다)
//      - 새총의 잡기 콜라이더는 손잡이만 쓰도록 지정한다 (안 하면 자식인 주머니 콜라이더까지 새총 것이 된다)
//      - 새총을 쥔 동안 XRI 위치 · 회전 스무딩을 켠다 (손 추적 떨림 완화)
//   5) 손으로 잡는 기준을 '집는 점(Pinch Grab Pose)'에서 '손바닥 쥐기 자세(Grip Pose)'로 바꾸고,
//      손마다 따로 각도를 맞추는 Hold Offset 을 둔다 (왼손 · 오른손 축이 거울처럼 달라서 새총 쪽 하나로는 둘 다 못 맞춘다)
//   6) 소리: 주머니 잡기 '끼익' · 발사 '팅-슉' · 돌 착지 '툭' · 받침대 복귀 '톡' (Tools/AssetGen/make_sfx.py 로 만든 wav)
//      새총은 놓으면 받침대 위 처음 자리로 돌아간다 (SlingshotReturn)
//   7) 결과 UI · 금빛 풍선 팡파르 연결 (GameFeedbackBuilder, 열린 씬에만 따로 적용하는 메뉴도 있음)
using System.Collections.Generic;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.InputSystem;
using UnityEngine.InputSystem.XR;
using UnityEngine.XR.Interaction.Toolkit.Attachment;
using UnityEngine.XR.Interaction.Toolkit.Interactables;

public static class SlingshotSceneBuilder
{
    const string SourceScene = "Assets/_Project/Scenes/StoneDemo_Hands.unity";
    const string TargetScene = "Assets/_Project/Scenes/StoneDemo_Slingshot.unity";
    const string Models = "Assets/_Project/Art/Models";
    const string StonePrefabDir = "Assets/_Project/Prefabs/Stones";
    const string AudioDir = "Assets/_Project/Audio";
    const string InputActions = "Assets/Samples/XR Interaction Toolkit/3.5.1/Starter Assets/XRI Default Input Actions.inputactions";

    // 손마다 새총을 쥐는 위치 · 각도. 사용자가 Quest에서 Grip Pose > Hold Offset 을 직접 맞춘 값 (2026-11-21)
    // 왼손 · 오른손이 거울처럼 부호만 반대다
    static readonly Vector3 HoldPositionLeft = new Vector3(0f, -0.02f, 0.02f);
    static readonly Vector3 HoldOffsetLeft = new Vector3(0f, 18.5f, -90f);
    static readonly Vector3 HoldPositionRight = new Vector3(0f, 0.02f, -0.02f);
    static readonly Vector3 HoldOffsetRight = new Vector3(0f, -18.5f, 90f);
    const float GrabSmoothing = 12f;   // XRI 스무딩 양. 클수록 손을 빨리 따라가고(덜 부드러움), 작을수록 부드럽지만 늦다

    [MenuItem("Tools/Stone Challenge/Build Slingshot Test Scene")]
    public static void Build()
    {
        int stoneLayer = LayerMask.NameToLayer("Stone");
        var palette = AssetDatabase.LoadAssetAtPath<Material>("Assets/_Project/Art/Materials/M_Palette.mat");
        if (stoneLayer < 0 || palette == null || AssetDatabase.LoadAssetAtPath<SceneAsset>(SourceScene) == null)
        {
            Debug.LogError($"[Slingshot] 준비물 없음 — Stone 레이어:{stoneLayer}, M_Palette:{palette != null}, {SourceScene}");
            return;
        }
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo()) return;
        if (AssetDatabase.LoadAssetAtPath<SceneAsset>(TargetScene) != null &&
            !EditorUtility.DisplayDialog("Slingshot Test Scene", TargetScene + " 가 이미 있습니다. StoneDemo_Hands 에서 다시 만들까요?", "다시 만들기", "취소"))
            return;

        // 2) 재질 연결
        var modelNames = new List<string> { "Slingshot", "Pouch", "Band" };
        foreach (var path in Directory.GetFiles(Models, "Stone_*.fbx")) modelNames.Add(Path.GetFileNameWithoutExtension(path));
        foreach (var name in modelNames) RemapToPalette($"{Models}/{name}.fbx", palette);

        // 3) 돌멩이 프리팹
        var stonePaths = BuildStonePrefabs(modelNames, stoneLayer);

        // 1) 씬 복제
        AssetDatabase.DeleteAsset(TargetScene);
        AssetDatabase.CopyAsset(SourceScene, TargetScene);
        var scene = EditorSceneManager.OpenScene(TargetScene, OpenSceneMode.Single);

        // 프리팹은 씬을 연 '뒤에' 경로로 다시 불러온다.
        // 저장 직후 쥐고 있던 참조는 씬 복제 · 열기 중 에셋을 다시 읽으면서 무효가 되어, 씬에 빈 값으로 저장됐었다
        var stones = stonePaths.Select(p => AssetDatabase.LoadAssetAtPath<Stone>(p)).ToArray();

        // 4) 새총 세트 배치 (통나무 받침대 윗면 위)
        Vector3 pos = GameObject.Find("LogStand").transform.position + new Vector3(0f, 1.08f, 0f);
        BuildSlingshotSet(pos, stones, stoneLayer);

        // 5) 손 잡기 기준을 Grip Pose + 손별 Hold Offset 으로
        int hands = SetupGripPose();

        // 7) 결과 UI · 금빛 풍선 팡파르
        GameFeedbackBuilder.Setup(scene);

        EditorSceneManager.MarkSceneDirty(scene);
        EditorSceneManager.SaveScene(scene);
        Debug.Log($"[Slingshot] 완료: {TargetScene} / 돌멩이 프리팹 {stones.Length}개 / Grip Pose 로 바꾼 손 {hands}개 (기대값 2)");
    }

    static void RemapToPalette(string fbxPath, Material palette)
    {
        var mi = (ModelImporter)AssetImporter.GetAtPath(fbxPath);
        mi.animationType = ModelImporterAnimationType.None;
        mi.importAnimation = false;
        mi.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), "M_Palette"), palette);
        mi.SaveAndReimport();
    }

    static string[] BuildStonePrefabs(List<string> modelNames, int stoneLayer)
    {
        Directory.CreateDirectory(StonePrefabDir);
        var result = new List<string>();
        foreach (var name in modelNames)
        {
            if (!name.StartsWith("Stone_")) continue;
            var root = new GameObject(name) { layer = stoneLayer };
            var model = (GameObject)PrefabUtility.InstantiatePrefab(AssetDatabase.LoadAssetAtPath<GameObject>($"{Models}/{name}.fbx"), root.transform);
            PrefabUtility.UnpackPrefabInstance(model, PrefabUnpackMode.Completely, InteractionMode.AutomatedAction);
            model.layer = stoneLayer;

            // 가장 얇은 축을 앞(+Z)으로 돌리고, 돌멩이 뒷면이 원점(피벗)에 오게 옮긴다
            var b = model.GetComponent<MeshFilter>().sharedMesh.bounds;
            Vector3 e = b.extents;
            Vector3 thinAxis = (e.x <= e.y && e.x <= e.z) ? Vector3.right : (e.y <= e.z ? Vector3.up : Vector3.forward);
            float halfThick = Vector3.Dot(e, thinAxis);
            var rot = Quaternion.FromToRotation(thinAxis, Vector3.forward);
            model.transform.localRotation = rot;
            model.transform.localPosition = -(rot * b.center) + Vector3.forward * halfThick;

            // 빠르게 날아가는 작은 물체라 구 콜라이더 + 연속 충돌 검사로 풍선을 뚫고 지나가지 않게 한다
            var sphere = root.AddComponent<SphereCollider>();
            sphere.center = Vector3.forward * halfThick;
            sphere.radius = (e.x + e.y + e.z) / 3f;
            var rb = root.AddComponent<Rigidbody>();
            rb.mass = 0.05f;
            rb.interpolation = RigidbodyInterpolation.None;   // 장전 중엔 꺼야 주머니를 따라간다. 날아갈 때 Stone.Launch()가 켠다
            rb.collisionDetectionMode = CollisionDetectionMode.ContinuousDynamic;
            var stone = root.AddComponent<Stone>();
            var stoneSo = new SerializedObject(stone);
            stoneSo.FindProperty("landClip").objectReferenceValue = Clip("SFX_StoneMiss");
            stoneSo.ApplyModifiedPropertiesWithoutUndo();

            string path = $"{StonePrefabDir}/{name}.prefab";
            PrefabUtility.SaveAsPrefabAsset(root, path);
            Object.DestroyImmediate(root);
            result.Add(path);
        }
        return result.ToArray();
    }

    static void BuildSlingshotSet(Vector3 pos, Stone[] stones, int stoneLayer)
    {
        var root = new GameObject("Slingshot Set").transform;

        // 새총 몸체: 손잡이를 쥐면 손에 붙는다. 레이로 잡으면 손으로 끌려온다
        var sling = Spawn("Slingshot", root, stoneLayer);
        sling.transform.position = pos;
        var handle = sling.AddComponent<CapsuleCollider>();
        handle.direction = 1;                     // Y축 (손잡이 방향)
        handle.radius = 0.018f;
        handle.height = 0.14f;
        var slingBody = sling.AddComponent<Rigidbody>();
        slingBody.isKinematic = true;             // 물리로 떨어지지 않게. 놓으면 SlingshotReturn 이 받침대로 옮긴다
        slingBody.useGravity = false;
        var slingGrab = sling.AddComponent<XRGrabInteractable>();
        slingGrab.colliders.Add(handle);          // 잡는 곳은 손잡이뿐. 자식인 주머니 콜라이더는 주머니 것
        slingGrab.attachTransform = sling.transform.Find("GripAttach");
        slingGrab.movementType = XRBaseInteractable.MovementType.Instantaneous;
        slingGrab.throwOnDetach = false;
        slingGrab.farAttachMode = InteractableFarAttachMode.Near;
        slingGrab.smoothPosition = true;
        slingGrab.smoothPositionAmount = GrabSmoothing;
        slingGrab.smoothRotation = true;
        slingGrab.smoothRotationAmount = GrabSmoothing;
        AddAudio(sling);
        var ret = sling.AddComponent<SlingshotReturn>();
        var retSo = new SerializedObject(ret);
        retSo.FindProperty("arriveClip").objectReferenceValue = Clip("SFX_SlingReturn");
        retSo.ApplyModifiedPropertiesWithoutUndo();

        // 주머니: 새총의 자식. 잡아도 부모에서 떼지 않는다 (떼면 다시 한 박자 늦게 따라간다)
        var pouch = Spawn("Pouch", sling.transform, stoneLayer);
        var pouchCol = pouch.AddComponent<SphereCollider>();
        pouchCol.radius = 0.035f;                 // 잡기 쉽게 실제 주머니보다 크게
        var pouchBody = pouch.AddComponent<Rigidbody>();
        pouchBody.isKinematic = true;
        pouchBody.useGravity = false;
        var pouchGrab = pouch.AddComponent<XRGrabInteractable>();
        pouchGrab.trackPosition = false;          // 위치는 SlingshotPouch 가 정한다
        pouchGrab.trackRotation = false;
        pouchGrab.throwOnDetach = false;
        pouchGrab.unparentTransformOnGrab = false;
        AddAudio(pouch);
        var pouchScript = pouch.AddComponent<SlingshotPouch>();
        var so = new SerializedObject(pouchScript);
        so.FindProperty("slingshot").objectReferenceValue = sling.transform;
        so.FindProperty("anchorL").objectReferenceValue = sling.transform.Find("BandAnchor_L");
        so.FindProperty("anchorR").objectReferenceValue = sling.transform.Find("BandAnchor_R");
        so.FindProperty("stoneSeat").objectReferenceValue = pouch.transform.Find("StoneSeat");
        var arr = so.FindProperty("stonePrefabs");
        arr.arraySize = stones.Length;
        for (int i = 0; i < stones.Length; i++) arr.GetArrayElementAtIndex(i).objectReferenceValue = stones[i];
        so.FindProperty("stretchClip").objectReferenceValue = Clip("SFX_SlingStretch");
        so.FindProperty("releaseClip").objectReferenceValue = Clip("SFX_SlingRelease");
        so.ApplyModifiedPropertiesWithoutUndo();

        // 고무줄 두 줄 (새총의 자식)
        var bandL = Spawn("Band", sling.transform, stoneLayer);
        bandL.name = "Band_L";
        var bandR = Spawn("Band", sling.transform, stoneLayer);
        bandR.name = "Band_R";
        var bands = sling.AddComponent<SlingshotBands>();
        so = new SerializedObject(bands);
        so.FindProperty("anchorL").objectReferenceValue = sling.transform.Find("BandAnchor_L");
        so.FindProperty("anchorR").objectReferenceValue = sling.transform.Find("BandAnchor_R");
        so.FindProperty("tieL").objectReferenceValue = pouch.transform.Find("BandTie_L");
        so.FindProperty("tieR").objectReferenceValue = pouch.transform.Find("BandTie_R");
        so.FindProperty("bandL").objectReferenceValue = bandL.transform;
        so.FindProperty("bandR").objectReferenceValue = bandR.transform;
        so.ApplyModifiedPropertiesWithoutUndo();

        // 조준선 (포물선)
        var aim = new GameObject("Trajectory");
        aim.transform.SetParent(root, false);
        var line = aim.AddComponent<LineRenderer>();
        line.widthMultiplier = 0.006f;
        line.startColor = new Color(1f, 1f, 1f, 0.85f);
        line.endColor = new Color(1f, 1f, 1f, 0.05f);   // 끝으로 갈수록 흐리게
        line.shadowCastingMode = UnityEngine.Rendering.ShadowCastingMode.Off;
        var traj = aim.AddComponent<SlingshotTrajectory>();
        so = new SerializedObject(traj);
        so.FindProperty("pouch").objectReferenceValue = pouchScript;
        so.FindProperty("hitMask").intValue = ~(1 << stoneLayer);  // 새총 · 주머니 · 돌멩이(Stone 레이어)에 선이 걸리지 않게
        so.ApplyModifiedPropertiesWithoutUndo();
    }

    // 손의 Interaction Attach Controller 가 따라가는 대상을 Pinch Grab Pose 아래 Grip Offset → Grip Pose > Hold Offset 으로 바꾼다.
    // Grip Pose 는 Pinch Grab Pose 와 같은 부모(같은 추적 좌표계)에 두고, TrackedPoseDriver 로 손바닥 쥐기 자세를 따라가게 한다
    static int SetupGripPose()
    {
        var refs = AssetDatabase.LoadAllAssetsAtPath(InputActions).OfType<InputActionReference>().ToList();
        int count = 0;
        foreach (var attach in Object.FindObjectsByType<InteractionAttachController>(FindObjectsInactive.Include, FindObjectsSortMode.None))
        {
            var follow = attach.transformToFollow;
            if (follow.name != "Grip Offset") continue;          // 손만 (컨트롤러는 다른 대상을 따라간다)
            var pinchPose = follow.parent;
            bool left = IsLeft(pinchPose);
            string side = left ? "Left" : "Right";

            var grip = new GameObject("Grip Pose");
            grip.transform.SetParent(pinchPose.parent, false);
            var driver = grip.AddComponent<TrackedPoseDriver>();
            driver.trackingType = TrackedPoseDriver.TrackingType.RotationAndPosition;
            driver.updateType = TrackedPoseDriver.UpdateType.UpdateAndBeforeRender;
            driver.positionInput = new InputActionProperty(refs.First(r => r.name == $"XRI {side}/Grip Position"));
            driver.rotationInput = new InputActionProperty(refs.First(r => r.name == $"XRI {side}/Grip Rotation"));

            var hold = new GameObject("Hold Offset").transform;
            hold.SetParent(grip.transform, false);
            hold.localPosition = left ? HoldPositionLeft : HoldPositionRight;
            hold.localRotation = Quaternion.Euler(left ? HoldOffsetLeft : HoldOffsetRight);

            attach.transformToFollow = hold;
            Object.DestroyImmediate(follow.gameObject);          // 쓰지 않게 된 다트 시절 오프셋
            PrefabUtility.RecordPrefabInstancePropertyModifications(attach);
            count++;
        }
        return count;
    }

    static bool IsLeft(Transform t)
    {
        for (; t != null; t = t.parent)
        {
            if (t.name.Contains("Left")) return true;
            if (t.name.Contains("Right")) return false;
        }
        throw new System.Exception("[Slingshot] 왼손 · 오른손을 구분할 수 없습니다");
    }

    static GameObject Spawn(string model, Transform parent, int layer)
    {
        var asset = AssetDatabase.LoadAssetAtPath<GameObject>($"{Models}/{model}.fbx");
        var go = (GameObject)PrefabUtility.InstantiatePrefab(asset, parent);
        go.layer = layer;
        foreach (Transform c in go.GetComponentsInChildren<Transform>(true)) c.gameObject.layer = layer;
        return go;
    }

    // 소리 에셋은 쓰는 순간에 경로로 불러온다 (씬을 연 뒤 예전 참조가 무효가 됐던 문제와 같은 이유)
    static AudioClip Clip(string name) => AssetDatabase.LoadAssetAtPath<AudioClip>($"{AudioDir}/{name}.wav");

    // 손 근처에서 나는 소리라 3D(거리 · 방향)로 들리게 한다
    static void AddAudio(GameObject go)
    {
        var src = go.AddComponent<AudioSource>();
        src.playOnAwake = false;
        src.spatialBlend = 1f;
        src.minDistance = 0.5f;
    }
}
