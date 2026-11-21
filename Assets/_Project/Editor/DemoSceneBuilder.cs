// 데모 씬 자동 조립 도구 (에디터 전용) — AI-Assist: generated
// 메뉴: Tools > Stone Challenge > Build Demo Scene
//
// 하는 일
//   1) 생성된 텍스처/FBX의 임포트 설정 (docs/assets/import-guide.md 1~3번을 자동으로)
//   2) M_Palette 머티리얼 생성 후 FBX에 연결
//   3) 새 씬에 게임 준비 배치 + XR Origin + UI(모양만) 배치, 조명/반사 설정
// 하지 않는 일 (직접 구현할 부분)
//   - 새총 세트(SlingshotSceneBuilder), 풍선 판정, 버튼 동작(onClick)
//
// 환경 = 야외 여름 계곡(Valley.fbx), 새총 받침 = 통나무(LogStand.fbx), 물풍선 4종은 예시 배치만 (docs/decisions/003, 008).
// 실내 방 · 다트판 · 바 테이블은 기획 전환으로 삭제했다.
//
// 배치 수치는 Tools/AssetGen/layout.py 와 같게 유지한다.
using System.Collections.Generic;
using System.IO;
using TMPro;
using UnityEditor;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.EventSystems;
using UnityEngine.Rendering;
using UnityEngine.UI;
using UnityEngine.XR.Interaction.Toolkit;
using UnityEngine.XR.Interaction.Toolkit.UI;

public static class DemoSceneBuilder
{
    const string Art = "Assets/_Project/Art";
    const string SceneDir = "Assets/_Project/Scenes";
    const string ScenePath = SceneDir + "/StoneDemo.unity";
    const string RigPath = "Assets/Samples/XR Interaction Toolkit/3.5.1/Starter Assets/Prefabs/XR Origin (XR Rig).prefab";
    const string FontPath = "Assets/99. External Assets/Font/Noto_Sans_KR/NotoSansKR-Regular SDF.asset";

    static readonly Vector3 PlayerPos = new Vector3(0f, 0f, -0.25f);
    static readonly Color Sun = new Color(1f, 0.95f, 0.85f);
    static readonly Color Chalk = new Color(0.92f, 0.91f, 0.87f);
    static readonly Color Pink = new Color(1f, 0.25f, 0.55f);

    // (모델, 위치, Y 회전, 부모 그룹, 정적 여부)
    struct Item
    {
        public string model; public Vector3 pos; public float rotY; public string group; public bool isStatic;
        public Item(string m, Vector3 p, float r, string g, bool s) { model = m; pos = p; rotY = r; group = g; isStatic = s; }
    }

    static readonly Item[] Layout =
    {
        new Item("Valley",         Vector3.zero,                      0, "Environment", true),
        new Item("ShootingLine",   Vector3.zero,                      0, "Game", true),
        new Item("LogStand",       new Vector3(0.55f, 0f, -0.1f),     0, "Game", true),
    };

    // 물풍선 예시 배치 (일렬 대형 하나 + 금빛 하나). 게임에서는 코드가 띄우므로 정적이 아니다
    static readonly Item[] Balloons =
    {
        new Item("Balloon_Red",    new Vector3(-0.25f, 1.45f, 1.30f), 0, "Game", false),
        new Item("Balloon_Blue",   new Vector3(-0.25f, 1.50f, 1.65f), 0, "Game", false),
        new Item("Balloon_Green",  new Vector3(-0.25f, 1.55f, 1.95f), 0, "Game", false),
        new Item("Balloon_Gold",   new Vector3(0.60f, 1.85f, 1.75f),  0, "Game", false),
    };

    [MenuItem("Tools/Stone Challenge/Build Demo Scene")]
    public static void Build()
    {
        if (File.Exists(ScenePath) &&
            !EditorUtility.DisplayDialog("데모 씬 다시 만들기", ScenePath + " 를 덮어씁니다.", "덮어쓰기", "취소"))
            return;
        if (!EditorSceneManager.SaveCurrentModifiedScenesIfUserWantsTo())
            return;

        SetupTextures();
        var palette = SetupMaterials();
        SetupModels(palette);

        var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
        var groups = new Dictionary<string, Transform>();
        foreach (var g in new[] { "Environment", "Game", "Lighting", "XR", "UI" })
            groups[g] = new GameObject(g).transform;

        GameObject valley = null;
        foreach (var it in Layout)
        {
            var go = Spawn(it.model, it.pos, it.rotY, groups[it.group]);
            if (it.isStatic) SetStatic(go);
            if (it.model == "Valley") valley = go;
        }
        PlaceBalloons(groups["Game"]);
        AddGroundCollider(valley);
        SetupLighting(groups["Lighting"]);
        var cam = SetupXR(groups["XR"]);
        SetupUI(groups["UI"], cam);

        Directory.CreateDirectory(SceneDir);
        EditorSceneManager.SaveScene(scene, ScenePath);
        BakeReflectionProbe();
        EditorSceneManager.SaveScene(scene);

        LogSizeCheck();
        Debug.Log("[DemoSceneBuilder] 완료: " + ScenePath + "  (빌드에 넣으려면 File > Build Profiles 에서 씬 추가)");
    }

    [MenuItem("Tools/Stone Challenge/Bake Lighting (optional)")]
    public static void Bake()
    {
        Lightmapping.BakeAsync();
    }

    // ------------------------------------------------------------------ 임포트 설정
    static void SetupTextures()
    {
        foreach (var n in new[] { "T_Palette_Albedo", "T_Palette_MS", "T_Palette_Emission" })
        {
            var ti = (TextureImporter)AssetImporter.GetAtPath($"{Art}/Textures/{n}.png");
            // 팔레트는 16px 색 칸이 붙어 있어 보간·밉맵을 끄면 옆 칸 색이 번지지 않는다
            ti.sRGBTexture = n != "T_Palette_MS";
            ti.filterMode = FilterMode.Point;
            ti.mipmapEnabled = false;
            ti.textureCompression = TextureImporterCompression.Uncompressed;
            ti.SaveAndReimport();
        }
        foreach (var n in new[] { "UI_RoundedRect", "UI_Circle" })
        {
            var ti = (TextureImporter)AssetImporter.GetAtPath($"{Art}/UI/{n}.png");
            ti.textureType = TextureImporterType.Sprite;
            ti.spriteImportMode = SpriteImportMode.Single;
            ti.alphaIsTransparency = true;
            ti.mipmapEnabled = false;
            ti.spriteBorder = n == "UI_RoundedRect" ? new Vector4(64, 64, 64, 64) : Vector4.zero;
            ti.SaveAndReimport();
        }
    }

    static Material SetupMaterials()
    {
        var dir = Art + "/Materials";
        Directory.CreateDirectory(dir);
        var lit = Shader.Find("Universal Render Pipeline/Lit");

        var palette = LoadOrCreate(dir + "/M_Palette.mat", lit);
        palette.SetTexture("_BaseMap", Tex("T_Palette_Albedo"));
        palette.SetColor("_BaseColor", Color.white);
        palette.SetTexture("_MetallicGlossMap", Tex("T_Palette_MS"));
        palette.SetFloat("_Smoothness", 1f);              // MS 텍스처 알파 × 1
        palette.SetFloat("_SmoothnessTextureChannel", 0);  // 0 = Metallic Alpha
        palette.EnableKeyword("_METALLICSPECGLOSSMAP");
        palette.SetTexture("_EmissionMap", Tex("T_Palette_Emission"));
        palette.SetColor("_EmissionColor", Color.white * 1.6f);
        palette.EnableKeyword("_EMISSION");
        palette.globalIlluminationFlags = MaterialGlobalIlluminationFlags.BakedEmissive;
        EditorUtility.SetDirty(palette);
        AssetDatabase.SaveAssets();
        return palette;
    }

    static void SetupModels(Material palette)
    {
        foreach (var path in AssetDatabase.FindAssets("t:Model", new[] { Art + "/Models" }))
        {
            var p = AssetDatabase.GUIDToAssetPath(path);
            var mi = (ModelImporter)AssetImporter.GetAtPath(p);
            mi.animationType = ModelImporterAnimationType.None;
            mi.importAnimation = false;
            mi.importCameras = false;
            mi.importLights = false;
            mi.generateSecondaryUV = true;   // 라이트맵 굽기용 UV2
            mi.AddRemap(new AssetImporter.SourceAssetIdentifier(typeof(Material), "M_Palette"), palette);
            mi.SaveAndReimport();
        }
    }

    // ------------------------------------------------------------------ 배치
    static GameObject Spawn(string model, Vector3 pos, float rotY, Transform parent)
    {
        var asset = AssetDatabase.LoadAssetAtPath<GameObject>($"{Art}/Models/{model}.fbx");
        var go = (GameObject)PrefabUtility.InstantiatePrefab(asset, parent);
        go.transform.SetPositionAndRotation(pos, Quaternion.Euler(0f, rotY, 0f));
        return go;
    }

    static void PlaceBalloons(Transform game)
    {
        var parent = new GameObject("Balloons_Example").transform;
        parent.SetParent(game, false);
        foreach (var it in Balloons)
            Spawn(it.model, it.pos, it.rotY, parent);
    }

    // 지면에만 MeshCollider (떨어진 다트가 땅에 멈추게). 바위 · 나무 · 산은 충돌 없음
    static void AddGroundCollider(GameObject valley)
    {
        var ground = FindDeep(valley.transform, "Ground");
        if (ground == null) { Debug.LogWarning("Valley 안에 Ground 없음"); return; }
        ground.gameObject.AddComponent<MeshCollider>();

        // 먼 산은 너무 커서 라이트맵을 크게 키우므로 굽기에서 뺀다 (환경광만 받음)
        var mountains = FindDeep(valley.transform, "Mountains");
        if (mountains != null)
        {
            var flags = GameObjectUtility.GetStaticEditorFlags(mountains.gameObject) & ~StaticEditorFlags.ContributeGI;
            GameObjectUtility.SetStaticEditorFlags(mountains.gameObject, flags);
        }
    }

    // ------------------------------------------------------------------ 조명
    static void SetupLighting(Transform root)
    {
        // 야외: 해(Directional) 하나 + 하늘색 환경광 + Unity 기본 하늘(Skybox)
        RenderSettings.skybox = AssetDatabase.GetBuiltinExtraResource<Material>("Default-Skybox.mat");
        RenderSettings.ambientMode = AmbientMode.Trilight;
        RenderSettings.ambientSkyColor = new Color(0.62f, 0.74f, 0.90f);
        RenderSettings.ambientEquatorColor = new Color(0.50f, 0.56f, 0.52f);
        RenderSettings.ambientGroundColor = new Color(0.28f, 0.26f, 0.22f);
        RenderSettings.fog = false;

        var sun = AddLight(root, "Sun", LightType.Directional, new Vector3(0f, 5f, 0f), Sun, 1.3f, 0f, LightmapBakeType.Mixed);
        sun.transform.rotation = Quaternion.Euler(50f, -30f, 0f);   // 플레이어 오른쪽 뒤 위에서 앞쪽으로 비춤
        sun.shadows = LightShadows.Soft;
        RenderSettings.sun = sun;

        var probeGo = new GameObject("ReflectionProbe");
        probeGo.transform.SetParent(root, false);
        probeGo.transform.position = new Vector3(0f, 1.5f, 1.0f);
        var probe = probeGo.AddComponent<ReflectionProbe>();
        probe.mode = ReflectionProbeMode.Custom;
        probe.size = new Vector3(30f, 15f, 30f);     // 야외라 넓게, 상자 투영은 끔
        probe.center = new Vector3(0f, 0f, 0f);
        probe.boxProjection = false;
        probe.resolution = 128;

        var ls = new LightingSettings { name = "StoneDemo_Lighting" };
        ls.bakedGI = true;
        ls.realtimeGI = false;
        ls.mixedBakeMode = MixedLightingMode.IndirectOnly;
        ls.lightmapResolution = 6;                   // 계곡 지형이 넓어서 실내 때(12)보다 낮춤
        ls.lightmapMaxSize = 1024;
        var lsPath = SceneDir + "/StoneDemo_Lighting.lighting";
        Directory.CreateDirectory(SceneDir);
        AssetDatabase.DeleteAsset(lsPath);
        AssetDatabase.CreateAsset(ls, lsPath);
        Lightmapping.lightingSettings = ls;
    }

    static Light AddLight(Transform root, string name, LightType type, Vector3 pos, Color color,
                          float intensity, float range, LightmapBakeType bake)
    {
        var go = new GameObject(name);
        go.transform.SetParent(root, false);
        go.transform.position = pos;
        var l = go.AddComponent<Light>();
        l.type = type;
        l.color = color;
        l.intensity = intensity;
        l.range = range;
        l.lightmapBakeType = bake;
        l.shadows = LightShadows.None;
        return l;
    }

    static void BakeReflectionProbe()
    {
        var probe = Object.FindFirstObjectByType<ReflectionProbe>();
        var path = SceneDir + "/StoneDemo_ReflectionProbe.exr";
        if (probe != null && Lightmapping.BakeReflectionProbe(probe, path))
        {
            AssetDatabase.ImportAsset(path);
            probe.customBakedTexture = AssetDatabase.LoadAssetAtPath<Texture>(path);
        }
    }

    // ------------------------------------------------------------------ XR
    static Camera SetupXR(Transform root)
    {
        new GameObject("XR Interaction Manager", typeof(XRInteractionManager)).transform.SetParent(root, false);

        var rigAsset = AssetDatabase.LoadAssetAtPath<GameObject>(RigPath);
        if (rigAsset == null) { Debug.LogError("XR Origin 프리팹 없음: " + RigPath); return null; }
        var rig = (GameObject)PrefabUtility.InstantiatePrefab(rigAsset, root);
        rig.transform.SetPositionAndRotation(PlayerPos, Quaternion.identity);

        // 기획서: 제자리 플레이 (이동·텔레포트·회전 없음)
        var loco = FindDeep(rig.transform, "Locomotion");
        if (loco != null) loco.gameObject.SetActive(false);

        var cam = rig.GetComponentInChildren<Camera>(true);
        if (cam != null) cam.nearClipPlane = 0.03f;   // 얼굴 가까이 든 다트가 잘리지 않게

        var es = new GameObject("EventSystem", typeof(EventSystem), typeof(XRUIInputModule));
        es.transform.SetParent(root, false);
        return cam;
    }

    // ------------------------------------------------------------------ UI (모양만, 동작은 직접 연결)
    static void SetupUI(Transform root, Camera cam)
    {
        var font = AssetDatabase.LoadAssetAtPath<TMP_FontAsset>(FontPath);
        var rounded = AssetDatabase.LoadAssetAtPath<Sprite>($"{Art}/UI/UI_RoundedRect.png");

        // 점수판: 풍선 구역 왼쪽 위 (0.8 x 0.5 m). 계곡용 간판 모델이 생기면 그 면 앞으로 옮긴다
        var score = MakeCanvas(root, "UI_ScoreBoard", new Vector3(-1.15f, 1.62f, 2.072f), 0f, new Vector2(800, 500), cam);
        Panel(score.transform, rounded);
        Label(score, font, "점수", 46, new Vector2(0, 170), Chalk);
        Label(score, font, "0 / 300", 120, new Vector2(0, 60), Chalk).name = "ScoreText";
        Label(score, font, "남은 시간", 40, new Vector2(0, -70), Chalk);
        Label(score, font, "60", 72, new Vector2(0, -150), Chalk).name = "TimeText";

        // 시작 패널: 플레이어 앞 1.15 m, 눈보다 조금 아래, 위쪽으로 살짝 기울임
        var start = MakeCanvas(root, "UI_StartPanel", new Vector3(0f, 1.35f, 0.9f), 12f, new Vector2(640, 400), cam);
        Panel(start.transform, rounded);
        Label(start, font, "물풍선 터트리기", 72, new Vector2(0, 110), Color.white);
        Label(start, font, "60초 안에 물풍선을 터트려 300점을 넘겨라!\n금빛 풍선 = 777점", 34, new Vector2(0, 10), new Color(0.85f, 0.85f, 0.85f));
        MakeButton(start.transform, font, rounded, "StartButton", "시작", new Vector2(0, -120));

        // 결과 패널: 같은 자리, 처음엔 꺼 둠
        var result = MakeCanvas(root, "UI_ResultPanel", new Vector3(0f, 1.35f, 0.9f), 12f, new Vector2(640, 400), cam);
        Panel(result.transform, rounded);
        Label(result, font, "승리!", 84, new Vector2(0, 105), Pink).name = "ResultTitle";
        Label(result, font, "최종 점수 0점", 44, new Vector2(0, 10), Color.white).name = "FinalScore";
        MakeButton(result.transform, font, rounded, "RestartButton", "다시하기", new Vector2(0, -120));
        result.gameObject.SetActive(false);
    }

    static Canvas MakeCanvas(Transform root, string name, Vector3 pos, float tiltX, Vector2 size, Camera cam)
    {
        var go = new GameObject(name, typeof(RectTransform), typeof(Canvas), typeof(CanvasScaler), typeof(TrackedDeviceGraphicRaycaster));
        go.transform.SetParent(root, false);
        var canvas = go.GetComponent<Canvas>();
        canvas.renderMode = RenderMode.WorldSpace;
        canvas.worldCamera = cam;
        var rt = (RectTransform)go.transform;
        rt.sizeDelta = size;
        rt.position = pos;
        rt.rotation = Quaternion.Euler(tiltX, 0f, 0f);
        rt.localScale = Vector3.one * 0.001f;   // 1 px = 1 mm
        go.GetComponent<CanvasScaler>().dynamicPixelsPerUnit = 4f;
        return canvas;
    }

    static RectTransform Ui(string name, Transform parent, Vector2 pos, Vector2 size)
    {
        var go = new GameObject(name, typeof(RectTransform));
        go.transform.SetParent(parent, false);
        var rt = (RectTransform)go.transform;
        rt.anchoredPosition = pos;
        rt.sizeDelta = size;
        return rt;
    }

    static void Panel(Transform canvas, Sprite rounded)
    {
        var rt = Ui("Background", canvas, Vector2.zero, Vector2.zero);
        rt.anchorMin = Vector2.zero;
        rt.anchorMax = Vector2.one;
        var img = rt.gameObject.AddComponent<Image>();
        img.sprite = rounded;
        img.type = Image.Type.Sliced;
        img.color = new Color(0.07f, 0.08f, 0.09f, 0.92f);
    }

    static TextMeshProUGUI Label(Canvas c, TMP_FontAsset font, string text, float size, Vector2 pos, Color color)
    {
        var rt = Ui("Label", c.transform, pos, new Vector2(((RectTransform)c.transform).sizeDelta.x - 40, size * 2.4f));
        return Text(rt, font, text, size, color);
    }

    static TextMeshProUGUI Text(RectTransform rt, TMP_FontAsset font, string text, float size, Color color)
    {
        var t = rt.gameObject.AddComponent<TextMeshProUGUI>();
        if (font != null) t.font = font;
        t.text = text;
        t.fontSize = size;
        t.color = color;
        t.alignment = TextAlignmentOptions.Center;
        t.raycastTarget = false;
        return t;
    }

    static void MakeButton(Transform parent, TMP_FontAsset font, Sprite rounded, string name, string label, Vector2 pos)
    {
        var rt = Ui(name, parent, pos, new Vector2(260, 84));
        var img = rt.gameObject.AddComponent<Image>();
        img.sprite = rounded;
        img.type = Image.Type.Sliced;
        img.pixelsPerUnitMultiplier = 2f;      // 작은 버튼은 모서리 반지름을 절반으로
        img.color = Color.white;
        var btn = rt.gameObject.AddComponent<Button>();
        var colors = btn.colors;
        colors.normalColor = Pink;
        colors.highlightedColor = new Color(1f, 0.45f, 0.7f);
        colors.pressedColor = new Color(0.75f, 0.15f, 0.4f);
        colors.selectedColor = Pink;
        btn.colors = colors;
        var lt = Ui("Text", rt, Vector2.zero, Vector2.zero);
        lt.anchorMin = Vector2.zero;
        lt.anchorMax = Vector2.one;
        Text(lt, font, label, 40, Color.white);
    }

    // ------------------------------------------------------------------ 유틸
    static Material LoadOrCreate(string path, Shader shader)
    {
        var m = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (m == null)
        {
            m = new Material(shader);
            AssetDatabase.CreateAsset(m, path);
        }
        m.shader = shader;
        return m;
    }

    static Texture2D Tex(string name) =>
        AssetDatabase.LoadAssetAtPath<Texture2D>($"{Art}/Textures/{name}.png");

    static void SetStatic(GameObject go)
    {
        var flags = StaticEditorFlags.ContributeGI | StaticEditorFlags.BatchingStatic |
                    StaticEditorFlags.OccluderStatic | StaticEditorFlags.OccludeeStatic |
                    StaticEditorFlags.ReflectionProbeStatic;
        foreach (var t in go.GetComponentsInChildren<Transform>(true))
            GameObjectUtility.SetStaticEditorFlags(t.gameObject, flags);
    }

    static Transform FindDeep(Transform root, string name)
    {
        if (root.name == name) return root;
        foreach (Transform c in root)
        {
            var r = FindDeep(c, name);
            if (r != null) return r;
        }
        return null;
    }

    static void LogSizeCheck()
    {
        // 임포트 스케일 확인: 빨강 풍선 가로 ≈ 0.35, 금빛 풍선 가로 ≈ 0.12 이어야 정상
        foreach (var n in new[] { "Balloon_Red", "Balloon_Gold" })
        {
            var go = GameObject.Find(n);
            if (go == null) continue;
            var r = go.GetComponentInChildren<Renderer>();
            Debug.Log($"[DemoSceneBuilder] {n} bounds size = {r.bounds.size.ToString("F3")}");
        }
    }
}
