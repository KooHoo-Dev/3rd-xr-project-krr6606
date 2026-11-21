// VFX 프리팹 자동 생성 도구 (에디터 전용) — AI-Assist: generated
// 메뉴: Tools > Stone Challenge > Build VFX Prefabs
//
// 하는 일
//   1) T_FX_* 텍스처 임포트 설정, 파티클 머티리얼 4개 생성 (Art/Materials/M_FX_*)
//   2) 파티클 프리팹 생성 (Prefabs/VFX/)
//        VFX_BalloonPop_Red / Blue / Green / Gold  풍선 터짐 (물 튐 + 쏟아지는 물 + 풍선 조각 + 고리)
//        VFX_GoldSparkle                           금빛 반짝이 (Gold 터짐에는 이미 들어 있음)
//        VFX_WaterSpill                            큰 물 쏟아짐 (올 클리어 연출용)
// 하지 않는 일 (직접 구현할 부분)
//   - 풍선이 맞았을 때 프리팹을 생성(Instantiate)하고 소리를 재생하는 게임 로직
//
// 모든 프리팹은 생성되면 스스로 재생되고(Play On Awake), 끝나면 스스로 사라진다(Stop Action = Destroy).
// 텍스처는 Tools/AssetGen/make_fx_textures.py 가 만든다. 다시 실행하면 같은 경로에 덮어쓴다.
using System.IO;
using UnityEditor;
using UnityEngine;
using UnityEngine.Rendering;

public static class VfxBuilder
{
    const string TexDir = "Assets/_Project/Art/Textures";
    const string MatDir = "Assets/_Project/Art/Materials";
    const string OutDir = "Assets/_Project/Prefabs/VFX";

    static readonly Color Water = new Color(0.78f, 0.92f, 1f, 0.85f);
    static readonly Color WaterLight = new Color(1f, 1f, 1f, 0.9f);
    static readonly Color GoldA = new Color(1f, 0.80f, 0.25f, 1f);
    static readonly Color GoldB = new Color(1f, 0.97f, 0.80f, 1f);

    static Material matWater, matShred, matRing, matSparkle;

    [MenuItem("Tools/Stone Challenge/Build VFX Prefabs")]
    public static void Build()
    {
        AssetDatabase.Refresh();
        SetupTextures();
        matWater = FxMaterial("M_FX_Water", "T_FX_Droplet", false);
        matShred = FxMaterial("M_FX_Shred", "T_FX_Shred", false);
        matRing = FxMaterial("M_FX_Ring", "T_FX_Ring", false);
        matSparkle = FxMaterial("M_FX_Sparkle", "T_FX_Sparkle", true);
        AssetDatabase.SaveAssets();

        Directory.CreateDirectory(OutDir);
        // 색 · 지름은 Tools/AssetGen/common.py, make_balloons.py 와 같은 값
        Save(BalloonPop("VFX_BalloonPop_Red", Hex("E8323C"), 0.35f, false));
        Save(BalloonPop("VFX_BalloonPop_Blue", Hex("2F7DE1"), 0.28f, false));
        Save(BalloonPop("VFX_BalloonPop_Green", Hex("3DBE4E"), 0.22f, false));
        Save(BalloonPop("VFX_BalloonPop_Gold", Hex("F2B630"), 0.12f, true));
        Save(GoldSparkle("VFX_GoldSparkle", null, 0.12f, true));
        Save(WaterSpill("VFX_WaterSpill"));

        AssetDatabase.SaveAssets();
        AssetDatabase.Refresh();
        Debug.Log("[VfxBuilder] 완료: " + OutDir + " 에 프리팹 6개");
    }

    // ------------------------------------------------------------------ 텍스처 · 머티리얼
    static void SetupTextures()
    {
        foreach (var n in new[] { "T_FX_Droplet", "T_FX_Sparkle", "T_FX_Ring", "T_FX_Shred" })
        {
            var ti = AssetImporter.GetAtPath($"{TexDir}/{n}.png") as TextureImporter;
            if (ti == null) { Debug.LogError($"{n}.png 없음. python Tools/AssetGen/make_fx_textures.py 를 먼저 실행"); continue; }
            ti.textureType = TextureImporterType.Default;
            ti.alphaIsTransparency = true;
            ti.wrapMode = TextureWrapMode.Clamp;
            ti.mipmapEnabled = true;
            ti.SaveAndReimport();
        }
    }

    // URP 파티클 Unlit 셰이더를 투명으로 설정. additive = 겹칠수록 밝아지는 가산 혼합 (빛 표현용)
    static Material FxMaterial(string name, string tex, bool additive)
    {
        var path = $"{MatDir}/{name}.mat";
        var shader = Shader.Find("Universal Render Pipeline/Particles/Unlit");
        var m = AssetDatabase.LoadAssetAtPath<Material>(path);
        if (m == null)
        {
            m = new Material(shader);
            AssetDatabase.CreateAsset(m, path);
        }
        m.shader = shader;
        m.SetTexture("_BaseMap", AssetDatabase.LoadAssetAtPath<Texture2D>($"{TexDir}/{tex}.png"));
        m.SetColor("_BaseColor", Color.white);
        m.SetFloat("_Surface", 1f);                    // 1 = Transparent
        m.SetFloat("_Blend", additive ? 2f : 0f);      // 0 = Alpha, 2 = Additive
        var dst = additive ? BlendMode.One : BlendMode.OneMinusSrcAlpha;
        m.SetFloat("_SrcBlend", (float)BlendMode.SrcAlpha);
        m.SetFloat("_DstBlend", (float)dst);
        m.SetFloat("_SrcBlendAlpha", (float)BlendMode.One);
        m.SetFloat("_DstBlendAlpha", (float)dst);
        m.SetFloat("_ZWrite", 0f);
        m.EnableKeyword("_SURFACE_TYPE_TRANSPARENT");
        m.DisableKeyword("_ALPHATEST_ON");
        m.SetOverrideTag("RenderType", "Transparent");
        m.renderQueue = (int)RenderQueue.Transparent;
        m.SetShaderPassEnabled("ShadowCaster", false);
        EditorUtility.SetDirty(m);
        return m;
    }

    // ------------------------------------------------------------------ 프리팹
    // 풍선 터짐. diameter = 풍선 지름(m). 모든 크기 · 개수가 지름에 비례한다
    static GameObject BalloonPop(string name, Color skin, float diameter, bool gold)
    {
        float r = diameter * 0.5f;
        float k = diameter / 0.35f;                    // 가장 큰 풍선(빨강)을 1로 본 비율

        // 1) Spray (루트): 사방으로 빠르게 튀는 작은 물방울. 속도 방향으로 길게 늘어남
        var spray = NewSystem(name, null, matWater, true);
        Main(spray, 0.35f, 0.75f, 1.5f * k + 0.8f, 4.0f * k + 1.2f, 0.012f, 0.035f, Water, WaterLight, 1.0f);
        Burst(spray, Count(46, k));
        Sphere(spray, r * 0.8f);
        Fade(spray, 1f, 1f, 0f);
        Stretch(spray, 0.06f, 1.6f);

        // 2) Spill: 풍선 안에 있던 물 덩어리. 풍선 모양으로 생겨서 거의 제자리에서 아래로 쏟아진다
        var spill = NewSystem("Spill", spray.transform, matWater, false);
        Main(spill, 1.2f, 1.6f, 0.0f, 0.5f, 0.05f * k + 0.02f, 0.10f * k + 0.03f, Water, WaterLight, 1.25f);
        Burst(spill, Count(70, k));
        Sphere(spill, r * 0.75f);
        Fade(spill, 0.9f, 0.9f, 0.6f);
        Shrink(spill, 0.45f);
        HitGround(spill, GroundSplash(spray.transform, k));

        // 3) Shreds: 풍선 색 고무 조각. 빠르게 튀었다가 공기 저항으로 금방 느려져 팔랑팔랑 떨어짐
        var shreds = NewSystem("Shreds", spray.transform, matShred, false);
        Main(shreds, 0.5f, 0.9f, 2.5f, 5.5f, 0.03f * k + 0.015f, 0.07f * k + 0.02f, skin, skin * 0.8f + Color.black * 0.2f, 0.7f);
        Burst(shreds, Count(12, k));
        Sphere(shreds, r * 0.9f);
        Fade(shreds, 1f, 1f, 1f, 0f);
        Spin(shreds, 9f);
        Drag(shreds, 5f);

        // 4) Flash: 터지는 순간 한 번 퍼지는 흰 고리
        var flash = NewSystem("Flash", spray.transform, matRing, false);
        Main(flash, 0.16f, 0.16f, 0f, 0f, diameter * 2.4f, diameter * 2.4f, Color.white, Color.white, 0f);
        Burst(flash, 1);
        NoShape(flash);
        Fade(flash, 0.9f, 0.5f, 0f);
        Grow(flash, 0.4f);

        if (gold) GoldSparkle("Sparkle", spray.transform, diameter, false);
        return spray.gameObject;
    }

    // 떨어진 물이 바닥에 닿을 때 튀는 작은 물보라 (Spill 의 보조 발생기)
    static ParticleSystem GroundSplash(Transform parent, float k)
    {
        var ps = NewSystem("GroundSplash", parent, matWater, false);
        Main(ps, 0.25f, 0.45f, 0.6f, 1.6f, 0.012f, 0.03f, WaterLight, Water, 1.0f);
        Burst(ps, 2);
        Cone(ps, 55f, 0.02f);
        Fade(ps, 0.9f, 0f);
        var main = ps.main;
        main.maxParticles = 200;
        return ps;
    }

    // 금빛 반짝이: 별 모양이 깜빡이며 천천히 흩날린다
    static GameObject GoldSparkle(string name, Transform parent, float diameter, bool isRoot)
    {
        var ps = NewSystem(name, parent, matSparkle, isRoot);
        Main(ps, 0.8f, 1.6f, 0.4f, 1.6f, 0.03f, 0.08f, GoldA, GoldB, 0.12f);
        Burst(ps, 36);
        Sphere(ps, diameter * 0.6f);
        Fade(ps, 0f, 1f, 0.25f, 1f, 0.2f, 0.9f, 0f);    // 알파가 오르내려서 깜빡임
        Spin(ps, 3f);
        Drag(ps, 1.5f);
        var noise = ps.noise;                           // 바람에 날리듯 흔들림
        noise.enabled = true;
        noise.strength = 0.35f;
        noise.frequency = 1.2f;
        noise.scrollSpeed = 0.6f;
        return ps.gameObject;
    }

    // 큰 물 쏟아짐: 폭 1 m 물줄기가 1.2초 동안 떨어진다. 놓는 위치 = 물이 시작되는 높이
    static GameObject WaterSpill(string name)
    {
        var ps = NewSystem(name, null, matWater, true);
        Main(ps, 1.0f, 1.6f, 0.2f, 1.2f, 0.06f, 0.16f, Water, WaterLight, 1.3f);
        var main = ps.main;
        main.duration = 1.2f;
        main.maxParticles = 300;
        var em = ps.emission;
        em.rateOverTime = 140f;
        var shape = ps.shape;
        shape.enabled = true;
        shape.shapeType = ParticleSystemShapeType.Box;
        shape.scale = new Vector3(1.0f, 0.1f, 0.3f);
        shape.rotation = new Vector3(90f, 0f, 0f);      // 상자의 앞(+Z)을 아래로 → 아래쪽으로 뿜음
        Fade(ps, 0.9f, 0.9f, 0.6f);
        Shrink(ps, 0.5f);
        HitGround(ps, GroundSplash(ps.transform, 1f));
        return ps.gameObject;
    }

    static void Save(GameObject go)
    {
        PrefabUtility.SaveAsPrefabAsset(go, $"{OutDir}/{go.name}.prefab");
        Object.DestroyImmediate(go);
    }

    // ------------------------------------------------------------------ 파티클 설정 도우미
    static ParticleSystem NewSystem(string name, Transform parent, Material mat, bool isRoot)
    {
        var go = new GameObject(name);
        if (parent != null) go.transform.SetParent(parent, false);
        var ps = go.AddComponent<ParticleSystem>();
        ps.Stop(true, ParticleSystemStopBehavior.StopEmittingAndClear);

        var main = ps.main;
        main.duration = 1.5f;
        main.loop = false;
        main.playOnAwake = true;
        main.simulationSpace = ParticleSystemSimulationSpace.World;   // 풍선이 사라져도 제자리에 남게
        main.scalingMode = ParticleSystemScalingMode.Hierarchy;
        main.maxParticles = 120;
        // 루트만 Destroy: 루트는 자식 파티클까지 전부 끝난 뒤에 멈춘 것으로 처리된다
        main.stopAction = isRoot ? ParticleSystemStopAction.Destroy : ParticleSystemStopAction.None;

        var em = ps.emission;
        em.enabled = true;
        em.rateOverTime = 0f;

        var r = go.GetComponent<ParticleSystemRenderer>();
        r.sharedMaterial = mat;
        r.renderMode = ParticleSystemRenderMode.Billboard;
        r.shadowCastingMode = ShadowCastingMode.Off;
        r.receiveShadows = false;
        r.lightProbeUsage = LightProbeUsage.Off;
        r.reflectionProbeUsage = ReflectionProbeUsage.Off;
        return ps;
    }

    static void Main(ParticleSystem ps, float lifeMin, float lifeMax, float speedMin, float speedMax,
                     float sizeMin, float sizeMax, Color colorA, Color colorB, float gravity)
    {
        var main = ps.main;
        main.startLifetime = new ParticleSystem.MinMaxCurve(lifeMin, lifeMax);
        main.startSpeed = new ParticleSystem.MinMaxCurve(speedMin, speedMax);
        main.startSize = new ParticleSystem.MinMaxCurve(sizeMin, sizeMax);
        main.startColor = new ParticleSystem.MinMaxGradient(colorA, colorB);
        main.startRotation = new ParticleSystem.MinMaxCurve(0f, Mathf.PI * 2f);
        main.gravityModifier = gravity;
    }

    static int Count(int atFullSize, float k) => Mathf.Max(6, Mathf.RoundToInt(atFullSize * Mathf.Lerp(0.45f, 1f, k)));

    static void Burst(ParticleSystem ps, int count)
    {
        var em = ps.emission;
        em.SetBursts(new[] { new ParticleSystem.Burst(0f, (short)count) });
    }

    static void Sphere(ParticleSystem ps, float radius)
    {
        var shape = ps.shape;
        shape.enabled = true;
        shape.shapeType = ParticleSystemShapeType.Sphere;
        shape.radius = radius;
        shape.radiusThickness = 1f;                     // 1 = 구 안쪽 전체에서 생성
    }

    static void Cone(ParticleSystem ps, float angle, float radius)
    {
        var shape = ps.shape;
        shape.enabled = true;
        shape.shapeType = ParticleSystemShapeType.Cone;
        shape.angle = angle;
        shape.radius = radius;
        shape.rotation = new Vector3(-90f, 0f, 0f);     // 원뿔을 위쪽으로
    }

    static void NoShape(ParticleSystem ps)
    {
        var shape = ps.shape;
        shape.enabled = false;
    }

    // 수명 동안의 알파 변화. 값들을 같은 간격으로 놓는다 (최대 8개)
    static void Fade(ParticleSystem ps, params float[] alphas)
    {
        var keys = new GradientAlphaKey[alphas.Length];
        for (int i = 0; i < alphas.Length; i++)
            keys[i] = new GradientAlphaKey(alphas[i], i / (float)(alphas.Length - 1));
        var g = new Gradient();
        g.SetKeys(new[] { new GradientColorKey(Color.white, 0f), new GradientColorKey(Color.white, 1f) }, keys);
        var col = ps.colorOverLifetime;
        col.enabled = true;
        col.color = new ParticleSystem.MinMaxGradient(g);
    }

    static void Shrink(ParticleSystem ps, float endScale) => SizeCurve(ps, 1f, endScale);
    static void Grow(ParticleSystem ps, float startScale) => SizeCurve(ps, startScale, 1f);

    static void SizeCurve(ParticleSystem ps, float from, float to)
    {
        var size = ps.sizeOverLifetime;
        size.enabled = true;
        size.size = new ParticleSystem.MinMaxCurve(1f, AnimationCurve.EaseInOut(0f, from, 1f, to));
    }

    static void Stretch(ParticleSystem ps, float velocityScale, float lengthScale)
    {
        var r = ps.GetComponent<ParticleSystemRenderer>();
        r.renderMode = ParticleSystemRenderMode.Stretch;
        r.velocityScale = velocityScale;
        r.lengthScale = lengthScale;
    }

    static void Spin(ParticleSystem ps, float radPerSec)
    {
        var rot = ps.rotationOverLifetime;
        rot.enabled = true;
        rot.z = new ParticleSystem.MinMaxCurve(-radPerSec, radPerSec);
    }

    static void Drag(ParticleSystem ps, float drag)
    {
        var lim = ps.limitVelocityOverLifetime;
        lim.enabled = true;
        lim.limit = 1000f;                              // 속도 제한은 쓰지 않고 공기 저항만 사용
        lim.dampen = 0f;
        lim.drag = drag;
    }

    // 콜라이더(땅)에 닿으면 사라지고, 그 자리에서 보조 발생기(물보라)를 터뜨린다
    static void HitGround(ParticleSystem ps, ParticleSystem splash)
    {
        var col = ps.collision;
        col.enabled = true;
        col.type = ParticleSystemCollisionType.World;
        col.mode = ParticleSystemCollisionMode.Collision3D;
        col.quality = ParticleSystemCollisionQuality.High;
        col.lifetimeLoss = 1f;                          // 닿으면 수명을 전부 잃음 = 사라짐
        col.bounce = 0f;
        col.radiusScale = 0.5f;
        col.sendCollisionMessages = false;

        var sub = ps.subEmitters;
        sub.enabled = true;
        sub.AddSubEmitter(splash, ParticleSystemSubEmitterType.Collision, ParticleSystemSubEmitterProperties.InheritNothing);
    }

    static Color Hex(string hex)
    {
        ColorUtility.TryParseHtmlString("#" + hex, out var c);
        return c;
    }
}
