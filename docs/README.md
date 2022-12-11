# AR Recorder

AR Recorder lets you animate an object's position/rotation in Blender by moving your phone. It uses AR frameworks (ARCore or ARKit) to track the motion of your phone camera and recreate it in Blender.

There are two ways to record animation data:

- **Save to file**: Record the motion of your phone to a file, which can be "played back" on an object in Blender. You can use this method to recreate camera motion of recorded video, for compositing 3D effects.
- **Stream**: Send tracking data over WiFi to allow controlling objects in real time. With Auto Keying enabled you can record animation keyframes by moving your phone.

The [import-blender.py](https://github.com/vanjac/ar-recorder/blob/master/import-blender.py) addon script adds both of these control methods to Blender.

[Download for Android.](https://github.com/vanjac/ar-recorder/releases) Built with Unity 2019.2.19.

It also works on iOS, but you'll have to build it yourself.
