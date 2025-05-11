import requests
import time
from datetime import datetime
import json

# 替换为你自己的 Gitee AI 平台 token
API_KEY = "xxx"

def generate_request(prompt, id):
# 1. 发起异步生成请求
    response = requests.post(
        "https://ai.gitee.com/v1/async/videos/generations",
        headers={
            "Content-Type": "application/json",
            "Authorization": f"Bearer {API_KEY}"  # 添加授权头
        },
        json={
            "model": "Wan2.1-T2V-14B",
            "prompt": prompt,
            "negative_prompt": "色调艳丽，过曝，静态，细节模糊不清，字幕，风格，作品，画作，画面，静止，整体发灰，最差质量，低质量，JPEG压缩残留，丑陋的，残缺的，多余的手指，画得不好的手部，画得不好的脸部，畸形的，毁容的，形态畸形的肢体，手指融合，静止不动的画面，杂乱的背景，三条腿，背景人很多，倒着走"
        }
    )

    # 2. 解析响应
    if response.status_code == 200:
        data = response.json()
        task_id = data.get("task_id")
        get_url = data.get("urls", {}).get("get")
        print(f"任务提交成功，ID：{task_id}")
    else:
        print("提交失败：", response.status_code, response.text)
        exit()

    # 2. 查询任务状态
    while True:
        status_resp = requests.get(
            get_url,
            headers={"Authorization": f"Bearer {API_KEY}"}
        )
        if status_resp.status_code != 200:
            print("状态查询失败：", status_resp.status_code, status_resp.text)
            break

        status_data = status_resp.json()
        print(status_resp)
        status = status_data.get("status")
        print(f"当前任务状态：{status}")

        if status == "success":
            output = status_data.get("output", {})
            started_at = status_data.get("started_at", {})
            completed_at = status_data.get("completed_at", {})
            started_time = datetime.fromtimestamp(started_at / 1000)
            completed_time = datetime.fromtimestamp(completed_at / 1000)
            print("Started at:", started_time)
            print("Completed at:", completed_time)
            # 假设结果视频 URL 存在于 output 中，可能是 output["video_url"]
            video_url = output.get("file_url") or output.get("url")
            if video_url:
                save_path = f"D:/SYSU_myclass/综合实训/wan_results/{id}_{prompt[:50]}.mp4"  # 替换为你希望保存的位置

                response = requests.get(video_url, stream=True)
                if response.status_code == 200:
                    with open(save_path, 'wb') as f:
                        for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB 每块
                            f.write(chunk)
                    print("视频下载完成:", save_path)
                else:
                    print("下载失败，状态码:", response.status_code)
            else:
                print("任务成功，但未找到视频地址，请查看 output 内容：", output)
            break
        elif status == "failure":
            print("任务失败")
            break
        elif status == "cancelled":
            print("任务取消")
            break
        elif status in ["waiting", "in_progress"]:
            time.sleep(1800)
            continue
        else:
            print(f"未知状态：{status}")
            break

if __name__ == "__main__":
    # 假设 JSON 文件叫 prompts.json
    with open("prompt_example.json", "r", encoding="utf-8") as f:
        data = json.load(f)

    # 遍历并过滤
    for item in data:
        if item.get("id") != 8 and item.get("id") != 1:
            generate_request(item["prompt"], item.get("id"))

# while True:
#     time.sleep(5)
#     status_resp = requests.get(
#         "https://ai.gitee.com/api/v1/task/HLSKO9OADSNKTWJC3WPRVNNAE9DSWJ83",
#         headers={"Authorization": f"Bearer {API_KEY}"}
#     )
#     if status_resp.status_code != 200:
#         print("状态查询失败：", status_resp.status_code, status_resp.text)
#         break
#
#     status_data = status_resp.json()
#     print(status_resp)
#     status = status_data.get("status")
#     print(f"当前任务状态：{status}")
#
#     if status == "success":
#         output = status_data.get("output", {})
#         started_at = status_data.get("started_at", {})
#         completed_at = status_data.get("completed_at", {})
#         started_time = datetime.fromtimestamp(started_at / 1000)
#         completed_time = datetime.fromtimestamp(completed_at / 1000)
#         print("Started at:", started_time)
#         print("Completed at:", completed_time)
#         # 假设结果视频 URL 存在于 output 中，可能是 output["video_url"]
#         video_url = output.get("file_url") or output.get("url")
#         if video_url:
#             save_path = f"D:/SYSU_myclass/综合实训/wan_results/{1}.mp4"  # 替换为你希望保存的位置
#
#             response = requests.get(video_url, stream=True)
#             if response.status_code == 200:
#                 with open(save_path, 'wb') as f:
#                     for chunk in response.iter_content(chunk_size=1024 * 1024):  # 1MB 每块
#                         f.write(chunk)
#                 print("视频下载完成:", save_path)
#             else:
#                 print("下载失败，状态码:", response.status_code)
#         else:
#             print("任务成功，但未找到视频地址，请查看 output 内容：", output)
#         break
#     elif status == "failure":
#         print("任务失败")
#         break
#     elif status == "cancelled":
#         print("任务取消")
#         break
#     elif status in ["waiting", "in_progress"]:
#         continue
#     else:
#         print(f"未知状态：{status}")
#         break