运行条件，首先在本地下载ollama，模型是deepseek-r1:1.5b和llama3.2:latest。
第二步再本地下载anything llm 使用deepseek作为思考端，llm作为回答端根据项目中的execl文件训练模型。参考官方的api调用文档进行模型调用。
第三步下载liv2d的web包（项目中已有了），可以自行改变数字人-但需要改包
运行教程：
首先再终端打开china-3d-map1目录，再这个目录下cmd。输入npm run dev
然后再进入下层的server目录，再这个目录下cmd。输入node index.js
然后使用vs code（pycharm也行）运行china-3d-map1下的app.py；再运行server文件夹下的route_planning_server.py;再运行flask——可视化\flask——可视化目录下的app1.py;然后在运行mcp_baidu文件夹下的baidu_map.py；再运行ai面试(语音)\视频和语音文件夹下的app.py。
完成上述的操作就可以使用完整的项目功能。语言识别和语言播报api到期后需要自行更换语言识别的api是科大讯飞的那个实时语音转录；
## 打赏和联系
3560791768
