import cv2
import os


def process_video(video_path, output_folder, frame_interval=1):
    video_name = os.path.splitext(os.path.basename(video_path))[0]

    video_output_folder = os.path.join(output_folder, video_name)
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
                f"{video_name}_{saved_count:04d}.jpg"
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

    frame_interval = 20

    process_videos_in_folder(input_folder, output_folder, frame_interval)