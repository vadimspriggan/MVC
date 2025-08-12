import math

def compare_results(ssim, predicted_size_mb, original_size_mb, threshold_ssim=0.95):
    """
    Сравнивает SSIM и предсказанный размер с оригинальным.
    
    Параметры:
    - ssim: SSIM значение из модуля ssim.py (float).
    - predicted_size_mb: Предсказанный размер полного видео (float).
    - original_size_mb: Размер оригинального видео (float).
    - threshold_ssim: Минимальный SSIM для приемлемости (default: 0.95).

    Возвращает:
    - is_acceptable: True, если SSIM >= threshold_ssim и predicted_size_mb <= original_size_mb.
    - quality_score: Оценка качества (например, SSIM * (original_size_mb / predicted_size_mb) если size ok, иначе 0).
    """
    if ssim >= threshold_ssim and predicted_size_mb <= original_size_mb:
        is_acceptable = True
        quality_score = ssim * (original_size_mb / predicted_size_mb if predicted_size_mb > 0 else 1)
    else:
        is_acceptable = False
        quality_score = 0.0

    print(f"Сравнение: SSIM {ssim:.3f} (>= {threshold_ssim}? {ssim >= threshold_ssim}), Размер {predicted_size_mb:.3f} MB (<= {original_size_mb:.3f} MB? {predicted_size_mb <= original_size_mb})")
    return is_acceptable, quality_score

def find_best_crf(results, original_size_mb, threshold_ssim=0.95):
    """
    Находит лучший CRF из результатов (dict с 'SSIM' и 'PredictedSize').

    Параметры:
    - results: Dict {crf: {'SSIM': float, 'PredictedSize': float}}.
    - original_size_mb: Размер оригинального видео.
    - threshold_ssim: Минимальный SSIM.

    Возвращает:
    - best_crf, best_ssim, best_size.
    """
    acceptable = {k: v for k, v in results.items() if v['SSIM'] >= threshold_ssim and v['PredictedSize'] <= original_size_mb}
    if acceptable:
        # Выбираем среди приемлемых тот, с минимальным размером
        best_crf = min(acceptable, key=lambda k: acceptable[k]['PredictedSize'])
        best_ssim = acceptable[best_crf]['SSIM']
        best_size = acceptable[best_crf]['PredictedSize']
    else:
        # Fallback на CRF с минимальным размером, если нет приемлемых
        if results:
            best_crf = min(results, key=lambda k: results[k]['PredictedSize'])
            best_ssim = results[best_crf]['SSIM']
            best_size = results[best_crf]['PredictedSize']
        else:
            best_crf = 30
            best_ssim = 0.0
            best_size = 0.0
            print("WARNING: Нет результатов. Fallback на CRF=30.")

    return best_crf, best_ssim, best_size
