#if UNITY_IOS

using System.Collections;
using System.Collections.Generic;
using System.IO;
using UnityEngine;
using UnityEditor;
using UnityEditor.iOS.Xcode;
using UnityEditor.Callbacks;


public static class IOSPostBuild
{
    [PostProcessBuild]
    public static void ChangeXcodePlist(BuildTarget buildTarget, string pathToBuiltProject)
    {
        if (buildTarget == BuildTarget.iOS)
        {
            Debug.Log("iOS post build");
            string plistPath = pathToBuiltProject + "/Info.plist";
            PlistDocument plist = new PlistDocument();
            plist.ReadFromFile(plistPath);

            PlistElementDict rootDict = plist.root;

            rootDict.SetBoolean("UIFileSharingEnabled", true);
            rootDict.SetBoolean("LSSupportsOpeningDocumentsInPlace", true);

            var capabilities = rootDict["UIRequiredDeviceCapabilities"].AsArray();
            capabilities.AddString("wifi");

            plist.WriteToFile(plistPath);
        }
    }
}

#endif
