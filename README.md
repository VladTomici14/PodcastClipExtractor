# Podcast 16x9 clip extractor 

## 1) Install 

1. Requirements for the install (```datetime``` and ```timeit``` should be installed already with python)
```shell
cv2==4.6.0
argparse=1.1
moviepy==1.0.3
numpy=1.26.0
datetime
timeit
```

2. If you don't have install some of the packages, you can use the next commands: 
```shell
pip install opencv-python 
pip install argparse
pip install moviepy
pip install numpy
```

## 2) Run 

Before running, you need to know the project structure. All the input videos will be in the ```input``` directory. After running the ```main.py``` script, the cropped video will be saved in the ```results``` directory.

1. First, you need to run the ```main.py``` script. For this command, you need to the video path as an argument. You can do this like this:
```shell
python3 main.py --input input/joe-rogan-1.mp4
```

For this scenario, I am using the ```joe-rogan-1.mp4``` video. You can change it with whatever file you want. 

2. After that, the script will launch. It will take a while to run, especially if the video is high-quality or is long. 
3. When the script finishes running, the cropped video will be saved in the ```results``` directory. The name format is the date and hour when the script was ran. 
4. If you want to add the audio, you will need to execute the ```audio.py``` script. You can do that like this:
```shell
python3 audio.py --input results/cropped_file.mp4 --audio input/joe-rogan-1.mp4
```

After you have cropped the video, you can add the audio from the original file by running the script ```audio.py```. 

\n
Basically, this script takes the audio from the original video and sticks it up to the cropped video. After the ```--input``` argument, you need to add the path of the cropped video. After the ```--audio```, you need to add the input file with the audio. 

\n
The output file with sound, will be saved in the project directory, and will be named ```output.mp4```.

\n
And there you go ! Everything should be ok ! :) 

