using System.Collections;
using System.Collections.Generic;
using System;
using UnityEngine;
using UnityEngine.UI;
using UnityEngine.XR.ARFoundation;
using System.IO;

public class ARRecord : MonoBehaviour
{
    public static ARRecord instance;

    public GameObject uiCanvas;
    public Text timeText, filenameText;
    public Text startStopText;

    public GameObject arOrigin;
    public Transform arCam;
    public ARPlaneManager planeManager;

    public bool recordCamera { get; set; } = true;
    public bool recordPointCloud { get; set; } = true;
    public bool recordPlanes { get; set; } = true;
    public bool hideWhileRecording { get; set; } = false;

    private float startTime;
    private StreamWriter file;
    private bool updatePointClouds;
    private List<ARPlane> planesUpdated = new List<ARPlane>();
    private List<ARPlane> planesRemoved = new List<ARPlane>();

    void Awake()
    {
        instance = this;
    }

    void OnEnable()
    {
        planeManager.planesChanged += PlaneChanged;
    }

    void OnDisable()
    {
        planeManager.planesChanged -= PlaneChanged;
    }

    public void StartStopButton()
    {
        if (file != null)
            StopRecording();
        else
            StartRecording();
    }

    private void StartRecording()
    {
        startStopText.text = "STOP";

        string fileName = DateTime.Now.ToString("yyyyMMdd_HHmmssfff") + ".txt";
        filenameText.text = fileName;
        file = new StreamWriter(Application.persistentDataPath + "/" + fileName);

        planesUpdated.Clear();
        planesRemoved.Clear();
        planesUpdated.AddRange(arOrigin.GetComponentsInChildren<ARPlane>());
        updatePointClouds = true;

        Camera cam = arCam.GetComponent<Camera>();
        file.WriteLine($"m {cam.fieldOfView} {Screen.width} {Screen.height}");

        if (hideWhileRecording)
        {
            uiCanvas.SetActive(false);
            cam.cullingMask = 0;
        }

        startTime = 0;
    }

    private void StopRecording()
    {
        startStopText.text = "START";

        if (file == null)
            return;
        file.Close();
        file = null;

        if (hideWhileRecording)
        {
            uiCanvas.SetActive(true);
            arCam.GetComponent<Camera>().cullingMask = ~0;
        }
    }

    public void PointCloudChanged()
    {
        updatePointClouds = true;
    }

    public void PlaneChanged(ARPlanesChangedEventArgs args)
    {
        if (file != null && recordPlanes)
        {
            planesUpdated.AddRange(args.added);
            planesUpdated.AddRange(args.updated);
            planesRemoved.AddRange(args.removed);
        }
    }

    void Update()
    {
        if (file == null)
        {
            timeText.text = "";
            return;
        }
        if (startTime == 0)
        {
            startTime = Time.time;
            return;
        }

        if (hideWhileRecording && Input.GetMouseButtonDown(0))
        {
            StopRecording();
            return;
        }

        string t = (Time.time - startTime).ToString();
        timeText.text = "Time: " + t;
        file.WriteLine($"t {t}");

        if (recordCamera)
        {
            Vector3 camPos = arCam.position;
            Quaternion camRot = arCam.rotation;
            file.WriteLine($"c {camPos.x} {camPos.y} {camPos.z} {camRot.x} {camRot.y} {camRot.z} {camRot.w}");
        }

        if (recordPointCloud && updatePointClouds)
        {
            foreach (ARPointCloud pointCloud in arOrigin.GetComponentsInChildren<ARPointCloud>())
            {
                int numPoints = pointCloud.positions.Length;
                for (int i = 0; i < numPoints; i++)
                {
                    Vector3 pos = pointCloud.positions[i];
                    ulong id = pointCloud.identifiers[i];
                    float confidence = pointCloud.confidenceValues[i];
                    file.WriteLine($"d {id} {pos.x} {pos.y} {pos.z} {confidence}");
                }
            }
            updatePointClouds = false;
        }

        if (recordPlanes)
        {
            foreach (ARPlane plane in planesUpdated)
            {
                if (plane.subsumedBy != null)
                    continue;
                Vector3 pos = plane.transform.position;
                Quaternion rot = plane.transform.rotation;
                var id = plane.trackableId;
                file.WriteLine($"p {id} {pos.x} {pos.y} {pos.z} {rot.x} {rot.y} {rot.z} {rot.w}");
                foreach (Vector2 point in plane.boundary)
                {
                    file.WriteLine($"b {point.x} {point.y}");
                }
            }
            planesUpdated.Clear();
            foreach (ARPlane plane in planesRemoved)
            {
                file.WriteLine($"pd {plane.trackableId}");
            }
            planesRemoved.Clear();
        }
    }
}
