using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.XR.ARFoundation;

public class ARReset : MonoBehaviour
{
    public ARSession session;

    void OnApplicationPause(bool pauseStatus)
    {
        if (!pauseStatus)
        {
            session.Reset();
        }
    }
}
