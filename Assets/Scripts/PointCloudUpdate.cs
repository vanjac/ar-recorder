using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.ARSubsystems;
using UnityEngine.XR.ARFoundation;

public class PointCloudUpdate : MonoBehaviour
{
    ARPointCloud pointCloud;
    
    void Awake()
    {
        pointCloud = GetComponent<ARPointCloud>();
    }

    void OnEnable()
    {
        pointCloud.updated += OnPointCloudChanged;
    }

    void OnDisable()
    {
        pointCloud.updated -= OnPointCloudChanged;
    }

    void OnPointCloudChanged(ARPointCloudUpdatedEventArgs eventArgs)
    {
        ARRecord.instance.PointCloudChanged();
    }
}
