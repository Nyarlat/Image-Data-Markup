### Как использовать волшебную палочку для разметки
1. Установите cuda версии 12.6 или новее
   https://developer.nvidia.com/cuda-12-6-0-download-archive
2. Установить torch в режиме работы с cuda
    `pip3 install torch torchvision --index-url https://download.pytorch.org/whl/cu126`
3. Убедитесь что torch корректно установился с cuda, для этого в интерпретаторе питона сделать

   `import torch`
   
   `torch.cuda.is_available()`
4. Установить библиотеку segment-anything 
   `pip install git+https://github.com/facebookresearch/segment-anything.git`
5. Скачать веса нужной модели в папку с проектом
   https://github.com/facebookresearch/segment-anything?tab=readme-ov-file#model-checkpoints
6. Запустить проект