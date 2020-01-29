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

    public Text timeText, filenameText;
    private float startTime;
    private StreamWriter file;
    private bool updatePointClouds;

    private List<ARPlane> planesUpdated = new List<ARPlane>();
    private List<ARPlane> planesRemoved = new List<ARPlane>();

    public GameObject arOrigin;
    public Transform arCam;
    public ARPlaneManager planeManager;

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

    public void StartRecording()
    {
        if (file != null)
            StopRecording();
        string fileName = DateTime.Now.Ticks.ToString();
        filenameText.text = fileName;
        file = new StreamWriter(Application.persistentDataPath + "/" + fileName);
        
        startTime = Time.time;

        planesUpdated.Clear();
        planesRemoved.Clear();
        planesUpdated.AddRange(arOrigin.GetComponentsInChildren<ARPlane>());
        updatePointClouds = true;
    }

    public void StopRecording()
    {
        if (file == null)
            return;
        file.Close();
        file = null;
    }

    public void PointCloudChanged()
    {
        updatePointClouds = true;
    }

    public void PlaneChanged(ARPlanesChangedEventArgs args)
    {
        if (file != null)
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
        string t = (Time.time - startTime).ToString();
        timeText.text = t;
        file.WriteLine("t " + t);

        Vector3 camPos = arCam.position;
        Quaternion camRot = arCam.rotation;
        file.WriteLine(String.Format("c {0} {1} {2} {3} {4} {5} {6}",
            camPos.x, camPos.y, camPos.z, camRot.x, camRot.y, camRot.z, camRot.w));
        
        foreach (ARReferencePoint refPoint in arOrigin.GetComponentsInChildren<ARReferencePoint>())
        {
            Vector3 pos = refPoint.transform.position;
            Quaternion rot = refPoint.transform.rotation;
            file.WriteLine(String.Format("r {0} {1} {2} {3} {4} {5} {6} {7}",
                refPoint.trackableId.ToString(), pos.x, pos.y, pos.z, rot.x, rot.y, rot.z, rot.w));
        }
        if (updatePointClouds)
        {
            foreach (ARPointCloud pointCloud in arOrigin.GetComponentsInChildren<ARPointCloud>())
            {
                int numPoints = pointCloud.positions.Length;
                for (int i = 0; i < numPoints; i++)
                {
                    Vector3 pos = pointCloud.positions[i];
                    ulong id = pointCloud.identifiers[i];
                    file.WriteLine(String.Format("d {0} {1} {2} {3}", id, pos.x, pos.y, pos.z));
                }
            }
            updatePointClouds = false;
        }
        foreach (ARPlane plane in planesUpdated)
        {
            if (plane.subsumedBy != null)
                continue;
            Vector3 pos = plane.transform.position;
            Quaternion rot = plane.transform.rotation;
            file.WriteLine(String.Format("p {0} {1} {2} {3} {4} {5} {6} {7}",
                plane.trackableId.ToString(), pos.x, pos.y, pos.z, rot.x, rot.y, rot.z, rot.w));
            foreach (Vector2 point in plane.boundary)
            {
                file.WriteLine(String.Format("b {0} {1}", point.x, point.y));
            }
        }
        planesUpdated.Clear();
        foreach (ARPlane plane in planesRemoved)
        {
            file.WriteLine("pd " + plane.trackableId.ToString());
        }
        planesRemoved.Clear();
    }
}
