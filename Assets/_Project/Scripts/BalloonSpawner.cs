
using System;
using System.Collections.Generic;
using UnityEngine;

public class BalloonSpawner : MonoBehaviour
{
    [SerializeField] private WaterBalloon[] balloonPrefabList;
    private Dictionary<BalloonType, WaterBalloon> balloonPrefabs;
    [SerializeField] private Transform[] spawnPointList;
    // bool값은 현재 스폰 가능한지의 여부를 나타냅니다. true이면 스폰 가능, false이면 스폰 불가
    private  List<bool> spawnPointStatus;
    [SerializeField] private Transform GoldBalloonSpawnPoint;
    bool isGoldBalloonSpawned = false;
    [SerializeField] private float spawnInterval = 2f; // 스폰 간격

    private float spawnTimer = 0f;
    void Start()
    {
        balloonPrefabs = new Dictionary<BalloonType, WaterBalloon>();
        for(int i = 0; i < balloonPrefabList.Length; i++)
        {
            WaterBalloon balloon = balloonPrefabList[i];
            balloonPrefabs[balloon.balloonType] = balloon;
        }
        
        spawnPointStatus = new List<bool>();
        for (int i = 0; i < spawnPointList.Length; i++)
        {
            spawnPointStatus.Add(true);
        }

    }
    void Update()
    {
        // 시작 버튼을 누르기 전, 게임이 끝난 뒤에는 스폰하지 않는다
        if (GameManager._instance.IsGameRunning == false) return;

        spawnTimer += Time.deltaTime;
        if (spawnTimer >= spawnInterval)
        {
            RandomBalloonSpawn();
            UpdateGoldBalloonSpawn();
            spawnTimer = 0f;
        }
    }
    // 골드 풍선을 제외한 풍선 일정 간격으로 스폰
    void RandomBalloonSpawn()
    {
        // 모든 스폰 포인트가 사용 중이면 반환
        if (spawnPointStatus.TrueForAll(status => status == false))
        {
            Debug.Log("모든 스폰 포인트가 사용 중입니다.");
            return;
        }
        int spawnPointIndex = UnityEngine.Random.Range(0, spawnPointList.Length);
        // 선택된 스폰 포인트가 사용 중이면, 다음 사용 가능한 스폰 포인트를 계속 탐색합니다.
        if (spawnPointStatus[spawnPointIndex] == false)
        {
            int MaxAttempts = spawnPointList.Length; // 최대 시도 횟수를 스폰 포인트 수로 설정
            int attempts = 0;
            bool foundAvailableSpawnPoint = false;
            while (foundAvailableSpawnPoint == false && attempts < MaxAttempts)
            {
                spawnPointIndex = (spawnPointIndex + 1) % spawnPointList.Length;
                if (spawnPointStatus[spawnPointIndex])
                {
                    foundAvailableSpawnPoint = true;
                }
                attempts++;
            }
        }
        
        spawnPointStatus[spawnPointIndex] = false;
        Transform spawnPoint = spawnPointList[spawnPointIndex];
        BalloonType balloonType = (BalloonType)UnityEngine.Random.Range(0, (int)BalloonType.Gold);
        WaterBalloon balloonPrefab = balloonPrefabs[balloonType];
        WaterBalloon spawnedBalloon = Instantiate(balloonPrefab, spawnPoint.position, Quaternion.identity);
        spawnedBalloon.OnBalloonPops += (balloonTypeIndex) => ReSetSpawnSates(spawnPointIndex);
        spawnedBalloon.OnBalloonExpired += () => ReSetSpawnSates(spawnPointIndex);
        GameManager._instance.RegisterBalloon(spawnedBalloon);
    }
    void GoldBalloonSpawn()
    {
        // Invoke로 예약된 사이에 게임이 끝났을 수 있다. 그때는 만들지 않고 다음 판을 위해 상태만 되돌린다
        if (GameManager._instance.IsGameRunning == false)
        {
            isGoldBalloonSpawned = false;
            return;
        }
        WaterBalloon goldBalloonPrefab = balloonPrefabs[BalloonType.Gold];
        WaterBalloon spawnedBalloon = Instantiate(goldBalloonPrefab, GoldBalloonSpawnPoint.position, Quaternion.identity);
        spawnedBalloon.OnBalloonPops += (balloonTypeIndex) => isGoldBalloonSpawned = false;
        spawnedBalloon.OnBalloonExpired += () => isGoldBalloonSpawned = false;
        GameManager._instance.RegisterBalloon(spawnedBalloon);

    }
    void UpdateGoldBalloonSpawn()
    {
        if (isGoldBalloonSpawned == false)
        {
            DelayGoldBalloonSpawn(spawnInterval);
            isGoldBalloonSpawned = true;
        }
    }
    void DelayGoldBalloonSpawn(float delay)
    {
        Invoke(nameof(GoldBalloonSpawn), delay);
    }
    void ReSetSpawnSates(int spawnPointIndex)
    {
        spawnPointStatus[spawnPointIndex] = true;
    }
}
