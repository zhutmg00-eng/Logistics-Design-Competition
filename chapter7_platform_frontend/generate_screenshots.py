# -*- coding: utf-8 -*-
import os
import sys
import subprocess
import shutil
import zipfile

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
if not os.path.exists(chrome_path):
    chrome_path = r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe"

base_dir = r"d:\物流设计大赛\chapter7_platform_frontend"
output_dir = os.path.join(base_dir, "screenshots")
os.makedirs(output_dir, exist_ok=True)

targets = [
    {
        "name": "Fig7_0_Master_Showcase_Portal.png",
        "file": "index.html",
        "width": 1920,
        "height": 1080,
        "cn_copies": [
            "图7-0_多模型共同配送平台展示门户.png"
        ]
    },
    {
        "name": "Fig7_1_Platform_Architecture_And_Model_Cascade.png",
        "file": "platform_architecture.html",
        "width": 1920,
        "height": 1080,
        "cn_copies": [
            "图7-1_多模型驱动的社区末端共同配送平台总体架构.png",
            "图7-2_多模型协同调用关系图.png"
        ]
    },
    {
        "name": "Fig7_2_CoDelivery_Operation_Management_Cockpit.png",
        "file": "terminal_operation.html",
        "width": 1920,
        "height": 1080,
        "cn_copies": [
            "图7-2_共同配送运营管理端_数字孪生驾驶舱.png",
            "图7-3_共同配送运营管理端_数字孪生驾驶舱.png"
        ]
    },
    {
        "name": "Fig7_3_Logistics_Enterprise_Portal_FullChain_Tracking.png",
        "file": "terminal_enterprise.html",
        "width": 1920,
        "height": 1080,
        "cn_copies": [
            "图7-3_物流企业与分拨中心协同端_全链路追踪.png",
            "图7-4_物流企业与分拨中心协同端_全链路追踪.png"
        ]
    },
    {
        "name": "Fig7_4_Courier_Mobile_App_Triptych_Showcase.png",
        "file": "terminal_courier.html",
        "width": 1920,
        "height": 1080,
        "cn_copies": [
            "Fig7_4_Courier_Mobile_App_Radar_Handoff_And_Tasks.png",
            "图7-4_配送执行移动端_人车交接雷达与上门工单.png",
            "图7-5_配送执行移动端_人车交接雷达与上门工单.png"
        ]
    },
    {
        "name": "Fig7_5_Resident_WeChat_MiniProgram_Triptych_Showcase.png",
        "file": "terminal_resident.html",
        "width": 1920,
        "height": 1080,
        "cn_copies": [
            "Fig7_5_Resident_WeChat_MiniProgram_Mode_And_Time_Window.png",
            "图7-5_社区居民服务小程序_多方式与时间窗预约.png",
            "图7-6_社区居民服务小程序_多方式与时间窗预约.png"
        ]
    },
    {
        "name": "Fig7_6_Cross_Role_Dynamic_Exception_Closed_Loop.png",
        "file": "terminal_closed_loop.html",
        "width": 1920,
        "height": 1080,
        "cn_copies": [
            "图7-6_跨主体异常协同与闭环反馈联动系统.png",
            "图7-7_跨主体异常协同与闭环反馈联动系统.png"
        ]
    },
    {
        "name": "Fig7_8_Four_Terminals_Collaborative_Matrix.png",
        "file": "overview_matrix.html",
        "width": 1920,
        "height": 1080,
        "cn_copies": [
            "Fig7_1_Four_Terminals_Collaborative_Matrix.png",
            "图7-1_四端协同全景矩阵大屏.png",
            "图7-8_四端协同全景矩阵大屏.png"
        ]
    }
]

print("Starting headless browser screenshot generation with updated high-res layout...")
for item in targets:
    html_path = os.path.join(base_dir, item["file"])
    out_png = os.path.join(output_dir, item["name"])
    file_url = f"file:///{html_path.replace(os.sep, '/')}"
    
    cmd = [
        chrome_path,
        "--headless",
        "--disable-gpu",
        "--hide-scrollbars",
        "--virtual-time-budget=4500",
        "--force-device-scale-factor=2.0",
        f"--window-size={item['width']},{item['height']}",
        f"--screenshot={out_png}",
        file_url
    ]
    
    print(f"Capturing: {item['name']} from {item['file']} ({item['width']}x{item['height']})...")
    res = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    if os.path.exists(out_png):
        size_kb = os.path.getsize(out_png) / 1024
        print(f"[OK] Generated: {item['name']} ({size_kb:.1f} KB)")
        for cn_name in item.get("cn_copies", []):
            cn_path = os.path.join(output_dir, cn_name)
            shutil.copyfile(out_png, cn_path)
            print(f"     -> Copied to: {cn_name}")
    else:
        print(f"[ERROR] Failed to generate: {item['name']}")

# Also update 前端截图.zip
zip_path = os.path.join(output_dir, "前端截图.zip")
with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zf:
    for root, _, files in os.walk(output_dir):
        for f in files:
            if f.endswith('.png'):
                full_p = os.path.join(root, f)
                arc_p = os.path.relpath(full_p, output_dir)
                zf.write(full_p, arc_p)
print(f"[OK] Updated zip archive: {zip_path}")

print("All screenshots generated and archived successfully!")
