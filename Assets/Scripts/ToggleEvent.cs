using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.Events;

public class ToggleEvent : MonoBehaviour
{
    public UnityEvent on, off;

    public void Toggle(bool toggle)
    {
        if (toggle)
            on.Invoke();
        else
            off.Invoke();
    }
}
