"""Extração de **features acústicas** para o classificador de violência no som (Fase 8).

Mesma extração usada no **treino** (``scripts/treino_acustico.py``) e na **inferência**
(``app.audio.classificacao``) — manter num só lugar evita divergência entre o modelo treinado e o
vetor calculado em produção. Usa ``librosa`` (MFCC/log-mel); ``soundfile`` decodifica wav/flac/ogg
sem ffmpeg, como no transcritor da Fase 1.
"""

from __future__ import annotations

from pathlib import Path

# Configuração da extração (mantida estável entre treino e inferência).
SR = 16000
N_MFCC = 20


def carregar_audio(caminho: str | Path):
    """Decodifica um áudio para mono float32 a 16 kHz (librosa; resample embutido)."""
    import librosa

    y, _ = librosa.load(str(caminho), sr=SR, mono=True)
    return y


def extrair_features(caminho: str | Path):
    """Vetor de features de um arquivo de áudio (média + desvio dos MFCC) como ``np.ndarray``."""
    return features_do_sinal(carregar_audio(caminho))


def features_do_sinal(y):
    """Calcula o vetor de features de um sinal já carregado (mono 16 kHz)."""
    import librosa
    import numpy as np

    if y is None or len(y) == 0:
        return np.zeros(N_MFCC * 2, dtype=np.float32)
    mfcc = librosa.feature.mfcc(y=y, sr=SR, n_mfcc=N_MFCC)
    vetor = np.concatenate([mfcc.mean(axis=1), mfcc.std(axis=1)])
    return vetor.astype(np.float32)
