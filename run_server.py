"""
Logistics Design Platform Launcher
(超大城市末端配送协同网络数智化与绿色化决策平台 启动入口)
"""

import os
import sys
import uvicorn

if __name__ == "__main__":
    current_dir = os.path.dirname(os.path.abspath(__file__))
    demo_dir = os.path.join(current_dir, "demo")
    if demo_dir not in sys.path:
        sys.path.insert(0, demo_dir)

    from demo.server import app

    print("=" * 60)
    print("超大城市末端配送协同网络数智化与绿色化决策平台")
    print("第九届北京市大学生物流设计大赛 · 主题二 原型系统")
    print("服务地址: http://127.0.0.1:8000")
    print("=" * 60)

    uvicorn.run(app, host="127.0.0.1", port=8000)
