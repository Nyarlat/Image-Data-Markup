import cv2
import os
import re


def transliterate(text):
    translit_dict = {
        'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'е': 'e', 'ё': 'yo',
        'ж': 'zh', 'з': 'z', 'и': 'i', 'й': 'y', 'к': 'k', 'л': 'l', 'м': 'm',
        'н': 'n', 'о': 'o', 'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
        'ф': 'f', 'х': 'kh', 'ц': 'ts', 'ч': 'ch', 'ш': 'sh', 'щ': 'shch',
        'ъ': '', 'ы': 'y', 'ь': '', 'э': 'e', 'ю': 'yu', 'я': 'ya',
        'А': 'A', 'Б': 'B', 'В': 'V', 'Г': 'G', 'Д': 'D', 'Е': 'E', 'Ё': 'Yo',
        'Ж': 'Zh', 'З': 'Z', 'И': 'I', 'Й': 'Y', 'К': 'K', 'Л': 'L', 'М': 'M',
        'Н': 'N', 'О': 'O', 'П': 'P', 'Р': 'R', 'С': 'S', 'Т': 'T', 'У': 'U',
        'Ф': 'F', 'Х': 'Kh', 'Ц': 'Ts', 'Ч': 'Ch', 'Ш': 'Sh', 'Щ': 'Shch',
        'Ъ': '', 'Ы': 'Y', 'Ь': '', 'Э': 'E', 'Ю': 'Yu', 'Я': 'Ya'
    }

    result = []
    for char in text:
        if char in translit_dict:
            result.append(translit_dict[char])
        else:
            result.append(char)
    return ''.join(result)


def sanitize_filename(filename):
    filename = transliterate(filename)
    filename = filename.replace(' ', '_')
    filename = re.sub(r'[^\w\.-]', '', filename)
    return filename


def process_video(video_path, output_folder, frame_interval=1):
    original_name = os.path.splitext(os.path.basename(video_path))[0]
    safe_name = sanitize_filename(original_name)

    video_output_folder = os.path.join(output_folder, safe_name)
    if not os.path.exists(video_output_folder):
        os.makedirs(video_output_folder)

    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        print(f"Ошибка: Не удалось открыть видео {video_path}")
        return

    frame_count = 0
    saved_count = 0

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        if frame_count % frame_interval == 0:
            frame_filename = os.path.join(
                video_output_folder,
                f"{safe_name}_{saved_count:04d}.jpg"
            )
            cv2.imwrite(frame_filename, frame)
            saved_count += 1

        frame_count += 1

    cap.release()
    print(f"Обработано: {video_path} | Кадров: {frame_count} | Сохранено: {saved_count}")


def process_videos_in_folder(input_folder, output_folder, frame_interval=1):
    if not os.path.exists(input_folder):
        print(f"Ошибка: папка {input_folder} не существует!")
        return

    video_extensions = ('.mp4', '.avi', '.mov', '.mkv', '.flv')

    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    for filename in os.listdir(input_folder):
        if filename.lower().endswith(video_extensions):
            video_path = os.path.join(input_folder, filename)
            process_video(video_path, output_folder, frame_interval)

    print("\nВсе видео обработаны.")


if __name__ == "__main__":
    input_folder = "videos"
    output_folder = "images"
    frame_interval = 5

    process_videos_in_folder(input_folder, output_folder, frame_interval)