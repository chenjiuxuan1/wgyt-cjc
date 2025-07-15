import cv2
from deepface import DeepFace

def webcam_emotion_detection():
    # 初始化摄像头
    cap = cv2.VideoCapture(0)
    
    # 检查摄像头是否正确打开
    if not cap.isOpened():
        print("无法打开摄像头")
        return
    
    print("按q键退出")
    
    while True:
        # 捕获帧
        ret, frame = cap.read()
        if not ret:
            print("无法获取视频帧，退出...")
            break
        
        # 水平翻转帧（镜像效果）
        frame = cv2.flip(frame, 1)
        
        # 创建帧的副本用于显示
        display_frame = frame.copy()
        
        try:
            # 使用DeepFace进行表情分析
            analysis = DeepFace.analyze(img_path=frame, 
                                       actions=['emotion'], 
                                       enforce_detection=False)
            
            # 显示结果
            if analysis:
                for face_analysis in analysis:
                    # 获取边界框
                    if 'region' in face_analysis:
                        x, y, w, h = face_analysis['region']['x'], face_analysis['region']['y'], \
                                     face_analysis['region']['w'], face_analysis['region']['h']
                        
                        # 绘制人脸框
                        cv2.rectangle(display_frame, (x, y), (x+w, y+h), (0, 255, 0), 2)
                        
                        # 获取表情结果
                        emotion = face_analysis['dominant_emotion']
                        # 绘制表情标签
                        cv2.putText(display_frame, 
                                    emotion, 
                                    (x, y-10), 
                                    cv2.FONT_HERSHEY_SIMPLEX, 
                                    0.9, 
                                    (0, 255, 0), 
                                    2)
        
        except Exception as e:
            print(f"处理帧时出错: {e}")
        
        # 显示处理后的帧
        cv2.imshow("DeepFace 表情识别", display_frame)
        
        # 按q键退出
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
    
    # 释放资源
    cap.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    webcam_emotion_detection() 