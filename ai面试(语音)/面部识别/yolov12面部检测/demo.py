#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from pathlib import Path

import click
import cv2
from matplotlib import pyplot as plt

# 修改导入方式
import moviepy.editor
from fer import FER
from fer.utils import draw_annotations

# 替换Video类引用
try:
    from fer.classes import Video
except ImportError:
    # 如果导入失败，创建一个简化版本的Video类
    class Video:
        def __init__(self, video_file):
            self.video_file = video_file
        
        def analyze(self, detector, display=False):
            cap = cv2.VideoCapture(self.video_file)
            data = []
            
            while True:
                ret, frame = cap.read()
                if not ret:
                    break
                
                emotions = detector.detect_emotions(frame)
                data.append(emotions)
                
                if display:
                    frame = draw_annotations(frame, emotions)
                    cv2.imshow('Video Analysis', frame)
                    if cv2.waitKey(1) == ord('q'):
                        break
            
            cap.release()
            cv2.destroyAllWindows()
            return data
        
        def to_pandas(self, data):
            import pandas as pd
            return pd.DataFrame(data)
        
        def get_first_face(self, df):
            # 简化版本
            return df
        
        def get_emotions(self, df):
            # 简化版本
            return df


mtcnn_help = "Use slower but more accurate mtcnn face detector"


@click.group()
def cli():
    pass


@cli.command()
@click.argument("device", default=0, help="webcam device (usually 0 or 1)")
@click.option("--mtcnn", is_flag=True, help=mtcnn_help)
def webcam(device, mtcnn):
    detector = FER(mtcnn=mtcnn)
    cap = cv2.VideoCapture(device)

    if not cap.isOpened():
        print("Cannot open camera")
        exit()

    while True:
        # Capture frame-by-frame
        ret, frame = cap.read()

        if not ret:
            print("Can't receive frame (stream end?). Exiting ...")
            break

        frame = cv2.flip(frame, 1)
        emotions = detector.detect_emotions(frame)
        frame = draw_annotations(frame, emotions)

        # Display the resulting frame
        cv2.imshow("frame", frame)
        if cv2.waitKey(1) == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()


@cli.command()
@click.argument("image_path", default="justin.jpg", type=click.Path(exists=True))
@click.option("--mtcnn", is_flag=True, help=mtcnn_help)
def image(image_path, mtcnn):
    image_path = Path(image_path)
    detector = FER(mtcnn=mtcnn)

    image = cv2.imread(str(image_path.resolve()))
    faces = detector.detect_emotions(image)
    image = draw_annotations(image, faces)

    outpath = f"{image_path.stem}_drawn{image_path.suffix}"
    cv2.imwrite(outpath, image)
    print(f"{faces}\nSaved to {outpath}")


@cli.command()
@click.argument("video-file", default="tests/test.mp4", type=click.Path(exists=True))
@click.option("--mtcnn", is_flag=True, help=mtcnn_help)
def video(video_file, mtcnn):
    video = Video(video_file)
    detector = FER(mtcnn=mtcnn)

    # Output list of dictionaries
    raw_data = video.analyze(detector, display=False)

    # Convert to pandas for analysis
    df = video.to_pandas(raw_data)
    df = video.get_first_face(df)
    df = video.get_emotions(df)

    # Plot emotions
    df.plot()
    plt.show()


if __name__ == "__main__":
    cli() 