# Android_Face

## Android Face

This App detect and recognise the face of person.
Using Two Models:
* yolov8n-face_float16.tflite (For Detection)
* facenet_512.tflite (For recognition)

### Installation & Requirements:
* sudo apt update
* sudo apt install -y git zip unzip openjdk-17-jdk
* sudo apt-get update
* sudo apt-get install libssl-dev

**Now create conda environment**
* conda create -n android python=3.11.5
* pip install --user buildozer Cython

then also pip install
* kivy==2.2.1
* pillow
* numpy
* tflite-runtime==2.5.0
* android

now make
* mkdir android_face_app
* cd android_face_app

create app python File such as **main.py** 

* nano main.py

Then

* buildozer init

* nano buildozer.spec or open directly in text editor

In buidozer.spec update this
```
source.include_exts = py,png,jpg,kv,atlas,tflite
requirements = python3,kivy,pillow,numpy,tflite-runtime,android
android.permissions = CAMERA,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.external_storage = true
orientation = portrait
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a, armeabi-v7a

then save and exit

```

After This Run in the same directory
* buildozer -v android debug

if **debug** successfully then it creates **.apk** file in bin folder
if not successfully then clean and run again  
* buildozer android clean
* buildozer -v android debug

After successful debuging ,install **.apk** on android device (real or virtual) **(virtual device means install at Android Studio Emulator(create virutal device))**.

### Working of Android Face:

After successful installation of App, run appliction on the device.

As this app creates box-layout for **camera  and three buttons like (star camera, stop camera and save to database)**.

Now click on **Start Camera** the turns on camera of device.

Now If any face detected, a crop image of face according box, as it shown in the below box layout.

When the face detected, now click on **Save to Database** button, It save the recent face detected box image in a variable **knowing_embedding**.

Now Recognition code is running...

Now If same person face detected, The detection rectangle of box become **Green**, and also showing there similarity score will be greater than **threshold i.e 0.8** above.

And if different person face detected the rectangle of box become **Red** and similarity score will less then **threshold i.e 0.8**.


