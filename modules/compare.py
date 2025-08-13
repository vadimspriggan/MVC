import math

def compare_results(ssim, predicted_size_mb, original_size_mb, threshold_ssim=0.95, size_tolerance=1.05):
    """
    Сравнивает SSIM и предсказанный размер с оригинальным.
    
    Параметры:
    - ssim: SSIM значение из модуля ssim.py (float).
    - predicted_size_mb: Предсказанный размер полного видео (float).
    - original_size_mb: Размер оригинального видео (float).
    - threshold_ssim: Минимальный SSIM для приемлемости (default: 0.95).
    - size_tolerance: Допуск превышения размера (default: 1.05, т.е. 5%).

    Возвращает:
    - is_acceptable: True, если SSIM >= threshold_ssim и predicted_size_mb <= original_size_mb * size_tolerance.
    - quality_score: Оценка качества (SSIM * (original_size_mb / predicted_size_mb) если size ok, иначе 0).
    """
    max_size = original_size_mb * size_tolerance
    is_acceptable = ssim >= threshold_ssim and predicted_size_mb <= max_size
    quality_score = ssim * (original_size_mb / predicted_size_mb) if is_acceptable and predicted_size_mb > 0 else 0.0

    print(f"Сравнение: SSIM {ssim:.3f} (>= {threshold_ssim}? {ssim >= threshold_ssim}), Размер {predicted_size_mb:.3f} MB (<= {max_size:.3f} MB? {predicted_size_mb <= max_size})")
    return is_acceptable, quality_score

def find_best_crf(results, original_size_mb, threshold_ssim=0.95, size_tolerance=1.05):
    """
    Находит лучший CRF из результатов (dict с 'SSIM' и 'PredictedSize').

    Параметры:
    - results: Dict {crf: {'SSIM': float, 'PredictedSize': float}}.
    - original_size_mb: Размер оригинального видео.
    - threshold_ssim: Минимальный SSIM.
    - size_tolerance: Допуск превышения размера (1.05 = 5%).

    Возвращает:
    - best_crf, best_ssim, best_size.
    """
    max_size = original_size_mb * size_tolerance
    acceptable = {k: v for k, v in results.items() if v['SSIM'] >= threshold_ssim and v['PredictedSize'] <= max_size}
    if acceptable:
        # Выбираем среди приемлемых тот, с минимальным размером
        best_crf = min(acceptable, key=lambda k: acceptable[k]['PredictedSize'])
        best_ssim = acceptable[best_crf]['SSIM']
        best_size = acceptable[best_crf]['PredictedSize']
    else:
        print("WARNING: Нет приемлемых CRF по SSIM (>= {threshold_ssim}) и размеру (<= {max_size:.3f} MB). Выбор по размеру с 5% допуском.")
        # Fallback на выбор по размеру с допуском
        fallback_candidates = {k: v for k, v in results.items() if v['PredictedSize'] <= max_size}
        if fallback_candidates:
            best_crf = min(fallback_candidates, key=lambda k: fallback_candidates[k]['PredictedSize'])
            best_ssim = fallback_candidates[best_crf]['SSIM']
            best_size = fallback_candidates[best_crf]['PredictedSize']
            print(f"Выбран CRF {best_crf} по минимальному размеру ({best_size:.3f} MB), SSIM: {best_ssim:.3f}")
        else:
            print("WARNING: Нет результатов даже по размеру. Fallback на CRF=30.")
            best_crf = 30
            best_ssim = 0.0
            best_size = 0.0

    return best_crf, best_ssim, best_size