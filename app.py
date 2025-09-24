# --- Импорты ---
# os: для работы с файловой системой (например, для удаления временных файлов)
import os 
# Flask: наш веб-фреймворк, как Express.js
from flask import Flask, request, jsonify 
# essentia.standard: импортируем стандартный набор функций Essentia
import essentia.standard as es 
# numpy: для математических операций, например, вычисления среднего значения
import numpy as np

# --- Инициализация приложения ---
# Создаем экземпляр нашего веб-приложения
app = Flask(__name__)

# --- Роут (Endpoint) для анализа ---
# Объявляем роут, который будет принимать POST-запросы по адресу /analyze
@app.route('/analyze', methods=['POST'])
def analyze_audio():
    # --- Валидация запроса ---
    # Проверяем, был ли в запросе отправлен файл с ключом 'file'
    if 'file' not in request.files:
        # Если файла нет, возвращаем ошибку 400
        return jsonify({"error": "File part is missing"}), 400

    file = request.files['file']

    # Проверяем, что имя файла не пустое
    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    # --- Сохранение и обработка файла ---
    # Создаем безопасный путь для временного файла в системной папке /tmp
    temp_audio_path = f"/tmp/{file.filename}"
    
    # Используем 'try...finally', чтобы гарантировать удаление временного файла,
    # даже если во время анализа произойдет ошибка.
    try:
        # Сохраняем загруженный файл по временному пути
        file.save(temp_audio_path)

        # --- "Магия" анализа аудио с помощью Essentia ---
        
        # 1. Загружаем аудиофайл. Essentia автоматически его декодирует.
        # MonoLoader преобразует стерео в моно, что достаточно для анализа.
        loader = es.MonoLoader(filename=temp_audio_path)
        audio = loader()

        # 2. Извлекаем BPM (темп)
        # RhythmExtractor2013 - это мощный алгоритм для определения темпа.
        rhythm_extractor = es.RhythmExtractor2013(method="multifeature")
        bpm, _, _, _, _ = rhythm_extractor(audio)

        # 3. Извлекаем тональность (Key) и лад (Scale)
        key_extractor = es.KeyExtractor()
        key, scale, strength = key_extractor(audio) # Например: "C#", "minor", 0.8

        # 4. Извлекаем "танцевальность"
        # Этот алгоритм анализирует ритмическую структуру трека.
        danceability_extractor = es.Danceability()
        danceability_result, _ = danceability_extractor(audio)

        # 5. Извлекаем энергию/громкость
        # Мы можем оценить общую энергию трека по его средней громкости (RMS).
        energy_extractor = es.Energy()
        energy = energy_extractor(audio)
        
        # --- Формируем ответ ---
        # Собираем все полученные данные в словарь Python
        analysis_data = {
            "bpm": round(bpm, 2),
            "key": key,
            "scale": scale,
            "danceability": round(danceability_result, 3),
            # np.mean вычисляет среднее значение энергии по всему треку
            "energy": round(float(np.mean(energy)), 5) 
        }

        # Возвращаем JSON с результатами анализа и статусом 200 (OK)
        return jsonify(analysis_data), 200

    except Exception as e:
        # Если что-то пошло не так во время анализа, возвращаем ошибку сервера
        return jsonify({"error": f"Failed to analyze audio: {str(e)}"}), 500
    
    finally:
        # Этот блок выполнится в любом случае: и после успешного анализа, и после ошибки.
        # Проверяем, существует ли еще временный файл, и удаляем его.
        if os.path.exists(temp_audio_path):
            os.remove(temp_audio_path)


# --- Точка входа для запуска сервера ---
# Эта конструкция позволяет запустить сервер командой `python app.py`
# Flask-сервер для разработки будет работать на порту 5001.
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5001, debug=True)

