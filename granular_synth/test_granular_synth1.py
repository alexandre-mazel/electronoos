import numpy as np
import soundfile as sf
from scipy.signal import resample


def voix_moteur_granulaire(
    voix_wav,
    moteur_wav,
    sortie_wav,
    grain_ms=45,
    grains_par_seconde=35,
    pitch_min=0.65,
    pitch_max=1.8,
    metallicite=0.45,
    jitter=0.25,
    seed=42
):
    """
    Transforme une voix en texture/voix métallique
    constituée de fragments d'un son de moteur.

    voix_wav       : voix humaine
    moteur_wav     : enregistrement du moteur
    sortie_wav     : fichier résultat
    """

    rng = np.random.default_rng(seed)

    # ---------------------------------------------------------
    # Chargement
    # ---------------------------------------------------------

    voix, sr = sf.read(voix_wav)
    moteur, sr_m = sf.read(moteur_wav)

    # mono
    if voix.ndim > 1:
        voix = np.mean(voix, axis=1)

    if moteur.ndim > 1:
        moteur = np.mean(moteur, axis=1)

    voix = voix.astype(np.float32)
    moteur = moteur.astype(np.float32)

    # ---------------------------------------------------------
    # Même fréquence d'échantillonnage
    # ---------------------------------------------------------

    if sr_m != sr:

        new_len = int(len(moteur) * sr / sr_m)

        moteur = resample(
            moteur,
            new_len
        ).astype(np.float32)

    # ---------------------------------------------------------
    # Normalisation
    # ---------------------------------------------------------

    voix /= max(
        np.max(np.abs(voix)),
        1e-9
    )

    moteur /= max(
        np.max(np.abs(moteur)),
        1e-9
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

    # sortie = même durée que la voix

    output = np.zeros(
        len(voix) + grain_size,
        dtype=np.float32
    )

    # fenêtre douce
    window = np.hanning(
        grain_size
    ).astype(np.float32)

    # ---------------------------------------------------------
    # Parcours de la voix
    # ---------------------------------------------------------

    for pos in range(
        0,
        len(voix),
        hop
    ):

        # -----------------------------------------------------
        # Amplitude de la voix
        # -----------------------------------------------------

        end = min(
            pos + hop,
            len(voix)
        )

        segment = voix[pos:end]

        if len(segment) == 0:
            continue

        amplitude = np.sqrt(
            np.mean(segment ** 2)
        )

        # silence
        if amplitude < 0.015:
            continue

        # -----------------------------------------------------
        # Hauteur approximative locale
        #
        # Ici on utilise une estimation très simple.
        # On pourra ensuite remplacer ça par YIN/pyin.
        # -----------------------------------------------------

        spectrum = np.abs(
            np.fft.rfft(segment)
        )

        freqs = np.fft.rfftfreq(
            len(segment),
            1 / sr
        )

        valid = (
            (freqs > 80) &
            (freqs < 1200)
        )

        if np.any(valid):

            idx = np.argmax(
                spectrum[valid]
            )

            freq = freqs[valid][idx]

        else:

            freq = 180

        # -----------------------------------------------------
        # Fréquence -> pitch
        #
        # On convertit la hauteur de la voix
        # en facteur de lecture du moteur.
        # -----------------------------------------------------

        pitch_norm = np.clip(
            (freq - 80) / (1200 - 80),
            0,
            1
        )

        pitch = (
            pitch_min
            +
            pitch_norm *
            (pitch_max - pitch_min)
        )

        # -----------------------------------------------------
        # Choix aléatoire dans le moteur
        # -----------------------------------------------------

        if len(moteur) <= grain_size:
            continue

        src_pos = rng.integers(
            0,
            len(moteur) - grain_size
        )

        grain = moteur[
            src_pos:src_pos + grain_size
        ].copy()

        # -----------------------------------------------------
        # Variation de pitch
        # -----------------------------------------------------

        new_len = max(
            16,
            int(len(grain) / pitch)
        )

        grain = resample(
            grain,
            new_len
        ).astype(np.float32)

        # -----------------------------------------------------
        # Fenêtrage
        # -----------------------------------------------------

        grain *= np.hanning(
            len(grain)
        )

        # -----------------------------------------------------
        # Métallisation
        # -----------------------------------------------------

        if metallicite > 0:

            t = np.arange(
                len(grain)
            ) / sr

            # fréquence porteuse
            carrier_freq = (
                freq * 2
                +
                rng.uniform(200, 1800)
            )

            carrier = np.sin(
                2 * np.pi *
                carrier_freq *
                t
            )

            metallic_grain = (
                grain * carrier
            )

            grain = (
                grain * (1 - metallicite)
                +
                metallic_grain * metallicite
            )

        # -----------------------------------------------------
        # Amplitude contrôlée par la voix
        # -----------------------------------------------------

        grain *= amplitude * 2.5

        # -----------------------------------------------------
        # Position temporelle
        # -----------------------------------------------------

        jitter_samples = int(
            rng.normal(
                0,
                jitter * hop
            )
        )

        out_pos = (
            pos +
            jitter_samples
        )

        if out_pos < 0:
            continue

        end = min(
            out_pos + len(grain),
            len(output)
        )

        output[
            out_pos:end
        ] += grain[
            :end-out_pos
        ]

    # ---------------------------------------------------------
    # Normalisation
    # ---------------------------------------------------------

    peak = np.max(
        np.abs(output)
    )

    if peak > 0:
        output *= (
            0.95 / peak
        )

    # ---------------------------------------------------------
    # Export
    # ---------------------------------------------------------

    sf.write(
        sortie_wav,
        output,
        sr
    )

    print( f"Created: {sortie_wav}" )


source = "voice_fr_ref5_torche.wav"
source = "qwen3_test_fr_ref4_majordome.wav"
motorfile = "485355__inspectorj__motor-small-fast-front-04-01-loop.wav"
motorfile = "345348__iut_paris8__gendron_clement_2015_2016_mecanicsound.wav"


voix_moteur_granulaire(
    source, # voix.wav
    motorfile,  # moteur.wav"
    "voix_metal_out.wav",

    grain_ms=45,
    grains_par_seconde=35,

    pitch_min=0.65,
    pitch_max=1.8,

    metallicite=0.45,
    jitter=0.20
)
