import cv2
from fer import FER

def webcam_emotion_detection():
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    
    # 初始化FER检测器
    detector = FER()
    
    print("按q键退出")
    
    while True:
        # 捕获帧
        ret, frame = cap.read()
        if not ret:
            print("无法获取视频帧，退出...")
            break
        
        # 水平翻转帧（镜像效果）
        frame = cv2.flip(frame, 1)
        
        # 检测表情
        try:
            emotions = detector.detect_emotions(frame)
            
            # 在每个人脸上绘制边界框和表情
            for face in emotions:
                # 获取人脸位置
                x, y, w, h = face['box']
                
                # 绘制人脸框
                cv2.rectangle(frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                
                # 获取最强烈的情绪
                emotions_dict = face['emotions']
                emotion = max(emotions_dict, key=emotions_dict.get)
                score = emotions_dict[emotion]
                
                # 绘制表情标签
                label = f"{emotion}: {score:.2f}"
                cv2.putText(frame, label, (x, y-10), 
                            cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 0), 2)
        except Exception as e:
            print(f"处理帧时出错: {e}")
        
        # 显示结果
        cv2.imshow("表情识别", frame)
        
        # 按q退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    webcam_emotion_detection() 