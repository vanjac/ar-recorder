using System.Collections;
using System.Collections.Generic;
using UnityEngine;
using UnityEngine.UI;
using System;
using System.Net;
using System.Net.Sockets;
using System.Text;

public class ARStream : MonoBehaviour
{
    public Text filenameText, buttonText;
    public Transform arCam;

    private UdpClient receiveSocket, sendSocket;
    private IPEndPoint connectedClient;
    private bool streaming;

    void Start()
    {
        // acts as a UDP server
        sendSocket = new UdpClient(new IPEndPoint(IPAddress.Any, 7300));
        receiveSocket = new UdpClient(new IPEndPoint(IPAddress.Any, 7299));
        receiveSocket.BeginReceive(new AsyncCallback(ReceiveCallback), null);
    }

    public void StartStopButton()
    {
        if (streaming)
        {
            buttonText.text = "Stream";
            streaming = false;
        }
        else
        {
            buttonText.text = "STOP";
            streaming = true;

            IPHostEntry ipEntry = Dns.GetHostEntry(Dns.GetHostName());
            IPAddress[] addressList = ipEntry.AddressList;

            string ipString = "";
            foreach (IPAddress addr in addressList)
            {
                if (addr.AddressFamily == AddressFamily.InterNetwork)
                    ipString += addr.ToString() + "\n";
            }
            Debug.Log(ipString);
            filenameText.text = ipString;
        }
    }

    void Update()
    {
        if (streaming && connectedClient != null)
        {
            Vector3 camPos = arCam.position;
            Quaternion camRot = arCam.rotation;
            string message = $"c {camPos.x} {camPos.y} {camPos.z} {camRot.x} {camRot.y} {camRot.z} {camRot.w}";
            byte[] send = Encoding.ASCII.GetBytes(message);
            sendSocket.Send(send, send.Length, connectedClient);
        }
    }

    private void ReceiveCallback(IAsyncResult asyncResult)
    {
        receiveSocket.EndReceive(asyncResult, ref connectedClient);
        receiveSocket.BeginReceive(new AsyncCallback(ReceiveCallback), null);
        Debug.Log("Connected to " + connectedClient);
    }
}
