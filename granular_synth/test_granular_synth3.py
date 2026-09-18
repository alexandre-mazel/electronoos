import numpy as np
import librosa
import soundfile as sf
from scipy.signal import lfilter


def lpc_formant_filter(grain, voice_frame, order=16):
    """
    Applique l'enveloppe spectrale LPC de la voix au grain.
    Le résultat a exactement la même longueur que grain.
    """

    grain_len = len(grain)

    if len(voice_frame) < order + 2:
        return grain.copy()

    # Pré-emphasis
    voice_frame = np.asarray(
        voice_frame,
        dtype=np.float32
    )

    voice_frame = np.append(
        voice_frame[0],
        voice_frame[1:] -
        0.97 * voice_frame[:-1]
    )

    # LPC
    try:
        a = librosa.lpc(
            voice_frame,
            order=order
        )
    except Exception:
        return grain.copy()

    if len(a) != order + 1:
        return grain.copy()

    # ---------------------------------------------------------
    # Enveloppe spectrale LPC
    # ---------------------------------------------------------

    n_fft = max(
        2048,
        2 ** int(np.ceil(np.log2(grain_len)))
    )

    from scipy.signal import freqz

    _, h = freqz(
        [1.0],
        a,
        worN=n_fft // 2 + 1
    )

    envelope = np.abs(h)

    # Éviter les valeurs aberrantes
    envelope /= (
        np.max(envelope) + 1e-9
    )

    # ---------------------------------------------------------
    # FFT du grain
    # ---------------------------------------------------------

    grain_spectrum = np.fft.rfft(
        grain,
        n=n_fft
    )

    # ---------------------------------------------------------
    # Adapter l'enveloppe à la taille FFT du grain
    # ---------------------------------------------------------

    env = np.interp(
        np.linspace(
            0,
            1,
            len(grain_spectrum)
        ),

        np.linspace(
            0,
            1,
            len(envelope)
        ),

        envelope
    )

    # ---------------------------------------------------------
    # Éviter de complètement supprimer le moteur
    # ---------------------------------------------------------

    env = (
        0.15 +
        0.85 * env
    )

    # ---------------------------------------------------------
    # Appliquer l'enveloppe
    # ---------------------------------------------------------

    grain_spectrum *= env

    result = np.fft.irfft(
        grain_spectrum,
        n=n_fft
    )

    # IMPORTANT :
    # exactement la taille originale du grain

    result = result[:grain_len]

    return result.astype(
        np.float32
    )


def voix_moteur_formants(
    voix_wav,
    moteur_wav,
    sortie_wav,

    grain_ms=60,
    grains_par_seconde=35,

    metallicite=0.30,

    formants=0.85,

    jitter=0.10,

    seed=42
):
    """
    Synthèse granulaire voix -> moteur.

    F0 de la voix :
        contrôle le pitch des grains.

    Formants :
        contrôlent l'enveloppe spectrale.

    metallicite :
        ajoute une modulation métallique.

    formants :
        0 = moteur original
        1 = formants de la voix très présents.
    """

    rng = np.random.default_rng(seed)

    # =========================================================
    # CHARGEMENT
    # =========================================================

    voix, sr = librosa.load(
        voix_wav,
        sr=None,
        mono=True
    )

    moteur, sr_m = librosa.load(
        moteur_wav,
        sr=sr,
        mono=True
    )

    voix = voix.astype(
        np.float32
    )

    moteur = moteur.astype(
        np.float32
    )

    # =========================================================
    # NORMALISATION
    # =========================================================

    voix /= max(
        np.max(np.abs(voix)),
        1e-9
    )

    moteur /= max(
        np.max(np.abs(moteur)),
        1e-9
    )

    # =========================================================
    # PARAMÈTRES
    # =========================================================

    grain_size = int(
        sr *
        grain_ms /
        1000
    )

    hop = int(
        sr /
        grains_par_seconde
    )

    # =========================================================
    # ANALYSE F0
    # =========================================================

    print(
        "Analyse F0 avec PYIN..."
    )

    f0, voiced, confidence = librosa.pyin(
        voix,

        fmin=librosa.note_to_hz(
            "C2"
        ),

        fmax=librosa.note_to_hz(
            "C6"
        ),

        sr=sr,

        frame_length=2048,
        hop_length=256,

        fill_na=None
    )

    # =========================================================
    # RMS
    # =========================================================

    rms = librosa.feature.rms(
        y=voix,
        frame_length=2048,
        hop_length=256
    )[0]

    # =========================================================
    # SORTIE
    # =========================================================

    output = np.zeros(
        len(voix) +
        grain_size * 2,

        dtype=np.float32
    )

    # =========================================================
    # GRAINS
    # =========================================================

    print(
        "Synthèse granulaire..."
    )

    for pos in range(
        0,
        len(voix),
        hop
    ):

        frame_idx = int(
            pos / 256
        )

        if frame_idx >= len(f0):
            break

        current_f0 = f0[
            frame_idx
        ]

        is_voiced = voiced[
            frame_idx
        ]

        conf = confidence[
            frame_idx
        ]

        # -----------------------------------------------------
        # RMS
        # -----------------------------------------------------

        rms_idx = min(
            frame_idx,
            len(rms) - 1
        )

        amplitude = rms[
            rms_idx
        ]

        # -----------------------------------------------------
        # Silence
        # -----------------------------------------------------

        if (
            not is_voiced
            or np.isnan(current_f0)
            or conf < 0.50
            or amplitude < 0.008
        ):
            continue

        # -----------------------------------------------------
        # FRAME VOIX POUR LPC
        # -----------------------------------------------------

        frame_start = max(
            0,
            pos - 1024
        )

        frame_end = min(
            len(voix),
            pos + 1024
        )

        voice_frame = voix[
            frame_start:
            frame_end
        ]

        if len(voice_frame) < 512:
            continue

        # -----------------------------------------------------
        # CHOIX DU GRAIN MOTEUR
        # -----------------------------------------------------

        if len(moteur) <= grain_size:
            continue

        source_pos = rng.integers(
            0,
            len(moteur) -
            grain_size
        )

        grain = moteur[
            source_pos:
            source_pos +
            grain_size
        ].copy()

        # -----------------------------------------------------
        # PITCH DU GRAIN
        # -----------------------------------------------------

        try:

            grain_f0 = librosa.yin(
                grain,

                fmin=50,
                fmax=5000,

                sr=sr,

                frame_length=1024
            )

            grain_f0 = grain_f0[
                np.isfinite(grain_f0)
            ]

            if len(grain_f0):

                source_pitch = np.median(
                    grain_f0
                )

            else:

                source_pitch = 200

        except Exception:

            source_pitch = 200

        if (
            not np.isfinite(
                source_pitch
            )
            or source_pitch <= 0
        ):
            source_pitch = 200

        # -----------------------------------------------------
        # TRANSPOSITION
        # -----------------------------------------------------

        ratio = (
            current_f0 /
            source_pitch
        )

        ratio = np.clip(
            ratio,
            0.25,
            4.0
        )

        new_sr = int(
            sr * ratio
        )

        try:

            grain = librosa.resample(
                grain,

                orig_sr=sr,

                target_sr=new_sr
            )

        except Exception:

            continue

        # remettre taille
        if len(grain) > grain_size:

            grain = grain[
                :grain_size
            ]

        else:

            grain = np.pad(
                grain,

                (
                    0,
                    grain_size -
                    len(grain)
                )
            )

        # -----------------------------------------------------
        # FORMANTS
        # -----------------------------------------------------

        filtered = lpc_formant_filter(
            grain,
            voice_frame,
            order=16
        )

        grain = (
            grain *
            (1 - formants)
            +
            filtered *
            formants
        )

        # -----------------------------------------------------
        # FENÊTRE
        # -----------------------------------------------------

        grain *= np.hanning(
            len(grain)
        )

        # -----------------------------------------------------
        # MÉTALLISATION
        # -----------------------------------------------------

        if metallicite > 0:

            t = (
                np.arange(
                    len(grain)
                )
                /
                sr
            )

            carrier1 = np.sin(
                2 *
                np.pi *
                current_f0 *
                2 *
                t
            )

            carrier2 = np.sin(
                2 *
                np.pi *
                current_f0 *
                3.01 *
                t
            )

            metal = grain * (
                0.5 * carrier1
                +
                0.5 * carrier2
            )

            grain = (
                grain *
                (1 - metallicite)
                +
                metal *
                metallicite
            )

        # -----------------------------------------------------
        # DYNAMIQUE VOIX
        # -----------------------------------------------------

        grain *= (
            amplitude *
            5.0
        )

        # -----------------------------------------------------
        # JITTER
        # -----------------------------------------------------

        offset = int(
            rng.normal(
                0,
                jitter * hop
            )
        )

        out_pos = (
            pos +
            offset
        )

        if out_pos < 0:
            continue

        # -----------------------------------------------------
        # MIX
        # -----------------------------------------------------

        end = min(
            out_pos +
            len(grain),

            len(output)
        )

        output[
            out_pos:end
        ] += grain[
            :end - out_pos
        ]

    # =========================================================
    # NORMALISATION
    # =========================================================

    peak = np.max(
        np.abs(output)
    )

    if peak > 0:

        output *= (
            0.95 /
            peak
        )

    # =========================================================
    # EXPORT
    # =========================================================

    sf.write(
        sortie_wav,
        output,
        sr
    )

    print(
        "Créé :",
        sortie_wav
    )


source = "voice_fr_ref5_torche.wav"
source = "qwen3_test_fr_ref4_majordome.wav"
motorfile = "485355__inspectorj__motor-small-fast-front-04-01-loop.wav"
#~ motorfile = "345348__iut_paris8__gendron_clement_2015_2016_mecanicsound.wav"


voix_moteur_formants(
    source, # voix.wav
    motorfile,  # moteur.wav"
    "voix_metal_out_formant.wav",

    grain_ms=55,
    grains_par_seconde=40,
    metallicite=0.25,
    formants=0.85,
    jitter=0.08
    
# voix métallique mais encore compréhensible :
#~ grain_ms=70,
#~ grains_par_seconde=30,
#~ formants=0.9,
#~ metallicite=0.15,
#~ jitter=0.05,

# beaucoup plus robotique / machine
#~ grain_ms=30,
#~ grains_par_seconde=70,
#~ formants=1.0,
#~ metallicite=0.6,
#~ jitter=0.20,

# nappe mécanique
#~ grain_ms=180,
#~ grains_par_seconde=15,
#~ formants=0.7,
#~ metallicite=0.4,
#~ jitter=0.5,



)
