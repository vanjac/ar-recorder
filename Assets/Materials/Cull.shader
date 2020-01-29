Shader "Custom/Cull"
{
    Properties
    {
        _MainTex ("Texture", 2D) = "white" {}
    }
    SubShader
    {
        Tags { "Queue" = "Geometry-1" }
        Lighting Off
        ZWrite On
        ColorMask 0

        CGPROGRAM
        #pragma surface surf Lambert
        struct Input {
            float4 color : COLOR;
        };

        void surf(Input IN, inout SurfaceOutput o) {

        }
        ENDCG
    }
}
