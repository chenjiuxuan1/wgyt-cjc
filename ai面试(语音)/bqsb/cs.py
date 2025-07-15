from modelscope.pipelines import pipeline
from modelscope.utils.constant import Tasks
from PIL import Image
import os

# 确保模型缓存目录存在
os.makedirs(os.path.expanduser('~/.cache/modelscope/hub'), exist_ok=True)

# 加载模型，不指定版本号
emotion_pipeline = pipeline(
    task=Tasks.image_classification,
    model='LangGPT/facial_emotions_detection'
)

try:
    # 打开并处理图像
    image = Image.open('测试.jpg')
    # 进行预测
    result = emotion_pipeline(image)
    print("情绪识别结果:", result)
except Exception as e:
    print(f"发生错误: {e}")
    print("请确保已安装所有必要的依赖: pip install -U 'modelscope[cv]' torch torchvision")