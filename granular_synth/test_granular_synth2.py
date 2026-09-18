import numpy as np
import soundfile as sf
import librosa


def voix_moteur_pyin(
    voix_wav,
    moteur_wav,
    sortie_wav,
    grain_ms=60,
    grains_par_seconde=30,
    metallicite=0.35,
    jitter=0.15,
    seed=42
):
    """
    Voix -> synthèse granulaire à partir d'un son de moteur.

    PYIN détecte la hauteur de la voix.
    Chaque grain du moteur est ensuite transposé
    pour suivre la mélodie / intonation de la voix.

    La durée et le rythme de la voix sont conservés.
    """

    rng = np.random.default_rng(seed)

    # ---------------------------------------------------------
    # Chargement
    # ---------------------------------------------------------

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

    voix = voix.astype(np.float32)
    moteur = moteur.astype(np.float32)

    # Normalisation
    voix /= max(
        np.max(np.abs(voix)),
        1e-9
    )

    moteur /= max(
        np.max(np.abs(moteur)),
        1e-9
    )

    # ---------------------------------------------------------
    # PYIN
    # ---------------------------------------------------------

    print("Analyse de hauteur avec PYIN...")

    f0, voiced_flag, voiced_prob = librosa.pyin(
        voix,

        fmin=librosa.note_to_hz("C2"),
        fmax=librosa.note_to_hz("C6"),

        sr=sr,

        frame_length=2048,
        hop_length=256,

        fill_na=None
    )

    # ---------------------------------------------------------
    # Paramètres
    # ---------------------------------------------------------

    grain_size = int(
        sr * grain_ms / 1000
    )

    hop = int(
        sr / grains_par_seconde
    )

    output = np.zeros(
        len(voix) + grain_size * 2,
        dtype=np.float32
    )

    # ---------------------------------------------------------
    # Analyse d'amplitude
    # ---------------------------------------------------------

    rms = librosa.feature.rms(
        y=voix,
        frame_length=2048,
        hop_length=256
    )[0]

    # ---------------------------------------------------------
    # Parcours temporel
    # ---------------------------------------------------------

    for pos in range(
        0,
        len(voix),
        hop
    ):

        # -----------------------------------------------------
        # Frame PYIN correspondant
        # -----------------------------------------------------

        frame_index = int(
            pos / 256
        )

        if frame_index >= len(f0):
            break

        frequency = f0[frame_index]

        voiced = voiced_flag[frame_index]

        probability = voiced_prob[frame_index]

        # -----------------------------------------------------
        # Amplitude de la voix
        # -----------------------------------------------------

        rms_index = min(
            frame_index,
            len(rms) - 1
        )

        amplitude = rms[rms_index]

        # -----------------------------------------------------
        # Silence
        # -----------------------------------------------------

        if (
            not voiced
            or np.isnan(frequency)
            or probability < 0.55
            or amplitude < 0.01
        ):
            continue

        # -----------------------------------------------------
        # Choisir un grain du moteur
        # -----------------------------------------------------

        if len(moteur) <= grain_size:
            continue

        src_pos = rng.integers(
            0,
            len(moteur) - grain_size
        )

        grain = moteur[
            src_pos:
            src_pos + grain_size
        ].copy()

        # -----------------------------------------------------
        # Estimation de la hauteur naturelle du grain
        # -----------------------------------------------------
        #
        # On estime approximativement le pitch du grain
        # avec PYIN.

        try:

            grain_f0 = librosa.yin(
                grain,
                fmin=40,
                fmax=5000,
                sr=sr,
                frame_length=1024
            )

            grain_pitch = np.median(
                grain_f0[
                    np.isfinite(grain_f0)
                ]
            )

        except Exception:

            grain_pitch = 200

        if (
            not np.isfinite(grain_pitch)
            or grain_pitch <= 0
        ):
            grain_pitch = 200

        # -----------------------------------------------------
        # Facteur de transposition
        # -----------------------------------------------------

        pitch_ratio = (
            frequency /
            grain_pitch
        )

        # Limitation pour éviter des transpositions absurdes

        pitch_ratio = np.clip(
            pitch_ratio,
            0.25,
            4.0
        )

        # -----------------------------------------------------
        # Transposition du grain
        # -----------------------------------------------------

        new_length = max(
            32,
            int(
                len(grain) /
                pitch_ratio
            )
        )

        grain = librosa.resample(
            grain,
            orig_sr=sr,
            target_sr=int(
                sr * pitch_ratio
            )
        )

        # On remet à la longueur souhaitée

        if len(grain) > grain_size:

            grain = grain[
                :grain_size
            ]

        else:

            grain = np.pad(
                grain,
                (
                    0,
                    grain_size - len(grain)
                )
            )

        # -----------------------------------------------------
        # Fenêtre Hann
        # -----------------------------------------------------

        grain *= np.hanning(
            len(grain)
        )

        # -----------------------------------------------------
        # Métallisation
        # -----------------------------------------------------

        if metallicite > 0:

            t = (
                np.arange(
                    len(grain)
                ) / sr
            )

            # Harmoniques liées à la voix

            carrier1 = np.sin(
                2 *
                np.pi *
                frequency *
                2 *
                t
            )

            carrier2 = np.sin(
                2 *
                np.pi *
                frequency *
                3.01 *
                t
            )

            metal = (
                grain *
                (
                    0.5 * carrier1 +
                    0.5 * carrier2
                )
            )

            grain = (
                grain *
                (1 - metallicite)
                +
                metal *
                metallicite
            )

        # -----------------------------------------------------
        # Dynamique de la voix
        # -----------------------------------------------------

        grain *= (
            amplitude *
            5.0
        )

        # -----------------------------------------------------
        # Jitter temporel
        # -----------------------------------------------------

        offset = int(
            rng.normal(
                0,
                jitter * hop
            )
        )

        out_pos = pos + offset

        if out_pos < 0:
            continue

        # -----------------------------------------------------
        # Mixage
        # -----------------------------------------------------

        end = min(
            out_pos + len(grain),
            len(output)
        )

        output[
            out_pos:end
        ] += grain[
            :end - out_pos
        ]

    # ---------------------------------------------------------
    # Normalisation
    # ---------------------------------------------------------

    peak = np.max(
        np.abs(output)
    )

    if peak > 0:

        output *= (
            0.95 /
            peak
        )

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    sf.write(
        sortie_wav,
        output,
        sr
    )

    print(
        f"Fichier créé : {sortie_wav}"
    )



source = "voice_fr_ref5_torche.wav"
source = "qwen3_test_fr_ref4_majordome.wav"
motorfile = "485355__inspectorj__motor-small-fast-front-04-01-loop.wav"
motorfile = "345348__iut_paris8__gendron_clement_2015_2016_mecanicsound.wav"


voix_moteur_pyin(
    source, # voix.wav
    motorfile,  # moteur.wav"
    "voix_metal_out_pyin.wav",

    grain_ms=60,
    grains_par_seconde=30,

    metallicite=0.35,
    jitter=0.15
)
