import os
import telebot
from telebot.apihelper import ApiTelegramException
import time

# 配置信息
BOT_TOKEN = '' # Bot Token
CHANNEL_ID = '@'  # 频道ID
DISCUSSION_GROUP_ID = '@'  # 讨论群组ID

# 支持的图片格式
IMAGE_EXTENSIONS = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp']

# 初始化机器人
bot = telebot.TeleBot(BOT_TOKEN)

# 用于存储最新消息ID的变量
new_message_id = None


# 获取讨论群组中最新消息的ID
def get_latest_message_id():
    global new_message_id
    try:
        # 发送一个临时消息到讨论群组
        temp_message = bot.send_message(DISCUSSION_GROUP_ID, "获取最新消息ID...")
        # 获取该消息的ID
        new_message_id = temp_message.message_id
        # 删除临时消息
        bot.delete_message(DISCUSSION_GROUP_ID, new_message_id)
        print(f"获取到最新消息ID: {new_message_id}")
        return new_message_id
    except Exception as e:
        print(f"获取最新消息ID时出错: {e}")
        return None


def is_image(filename):
    """检查文件是否为图片"""
    ext = os.path.splitext(filename)[1].lower()
    return ext in IMAGE_EXTENSIONS


def process_folders(root_folder):
    """处理根文件夹中的所有子文件夹"""
    # 检查根文件夹是否存在
    if not os.path.isdir(root_folder):
        print(f"错误: '{root_folder}' 不是一个有效的文件夹")
        return

    print(f"开始处理文件夹: {root_folder}")

    # 遍历根文件夹中的所有子文件夹
    for folder_name in os.listdir(root_folder):
        folder_path = os.path.join(root_folder, folder_name)

        # 确保这是一个文件夹
        if not os.path.isdir(folder_path):
            continue

        # 获取文件夹中的所有图片
        images = [f for f in os.listdir(folder_path) if is_image(f)]

        if not images:
            print(f"文件夹 '{folder_name}' 中没有图片,跳过")
            continue

        # 排序图片以确保顺序一致
        images.sort()

        # 获取第一张图片的完整路径
        first_image_path = os.path.join(folder_path, images[0])

        # 发送第一张图片到频道,并附上文件夹名称
        try:
            with open(first_image_path, 'rb') as photo:
                sent_message = bot.send_photo(
                    CHANNEL_ID,
                    photo,
                    caption=f"{folder_name}"
                )
                print(f"已发送 '{folder_name}' 的第一张图片到频道")

            time.sleep(10)
            # 获取讨论群组中最新消息的ID
            get_latest_message_id()

            print(f"频道消息ID: {sent_message.message_id}")
            print(f"讨论群最新消息ID: {new_message_id}")

            # 发送剩余图片到讨论群,作为回复
            for image in images[1:]:
                image_path = os.path.join(folder_path, image)
                with open(image_path, 'rb') as photo:
                    bot.send_photo(
                        DISCUSSION_GROUP_ID,
                        photo,
                        reply_to_message_id=(new_message_id - 1)
                    )
                    print(f"已发送 '{image}' 到讨论群作为回复")
                    time.sleep(6)


            time.sleep(40)
        except ApiTelegramException as e:
            print(f"发送图片时出错: {e}")
        except Exception as e:
            print(f"处理文件夹 '{folder_name}' 时出错: {e}")

        # 删除文件夹
        try:
            delete_path = root_folder + "/" + folder_name
            delete_path = delete_path.replace("\\", "/")
            os.rmdir(delete_path)
            print(f"已删除文件夹: {delete_path}")
        except Exception as e:
            print(f"删除文件夹 '{delete_path}' 时出错: {e}")

    print("处理完成")



if __name__ == "__main__":
    # 直接调用函数处理指定的根文件夹
    user_input = input("请输入文件夹路径:")
    ROOT_FOLDER = user_input.replace("\\", "/")
    process_folders(ROOT_FOLDER)
