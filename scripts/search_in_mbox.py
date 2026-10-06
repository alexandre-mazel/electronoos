#!/usr/bin/env python3

import argparse


def search_file(filename, keywords, chars_after=30, block_size=1024 * 1024):
    """
    Recherche keyword dans un gros fichier sans le charger entierement en RAM.
    Affiche keywords + les chars_after caracteres qui suivent.
    keywords: list of word to file in the chars after
    """

    keyword = keywords[0].encode("utf-8")
    overlap = len(keyword) + chars_after

    with open(filename, "rb") as f:
        previous = b""

        while True:
            block = f.read(block_size)

            if not block:
                # Traiter le dernier morceau
                data = previous
                pos = 0

                while True:
                    pos = data.lower().find(keyword.lower(), pos)
                    if pos == -1:
                        break

                    result = data[pos:pos + len(keyword) + chars_after]
                    for kw in keyword[1:]:
                        result.lower().find(kw.lower(), pos)
                        if result == -1:
                            break
                        print("\nblock(1):" + result.decode("utf-8", errors="replace"))
                    pos += 1

                break

            data = previous + block

            pos = 0
            while True:
                pos = data.lower().find(keyword.lower(), pos)

                if pos == -1:
                    break

                # Si l'occurrence est suffisamment loin de la fin,
                # on peut afficher les 30 caracteres demandes.
                if pos + len(keyword) + chars_after <= len(data):
                    result = data[pos:pos + len(keyword) + chars_after]
                    print("\nblock(2):" + result.decode("utf-8", errors="replace"))
                    pos += 1
                else:
                    # L'occurrence est trop proche de la fin du bloc.
                    # On la traitera au prochain passage.
                    break

            # Garder seulement la fin du bloc pour gerer
            # les mots coupes entre deux blocs.
            previous = data[-overlap:]


def main():

    parser = argparse.ArgumentParser(
        description="Recherche un mot dans un tres gros fichier sans le charger en RAM."
    )

    parser.add_argument("fichier", help="Fichier a analyser")
    parser.add_argument("mot", help="Mot ou texte a rechercher")
    parser.add_argument(
        "-n",
        "--chars",
        type=int,
        default=30,
        help="Nombre de caracteres a afficher apres le mot (defaut: 30)"
    )
    parser.add_argument(
        "-b",
        "--block-size",
        type=int,
        default=1024 * 1024,
        help="Taille des blocs en octets (defaut: 1 MiB)"
    )

    args = parser.parse_args()

    search_file(
        args.fichier,
        args.mot,
        args.chars,
        args.block_size
    )
if __name__ == "__main__":
    #~ main()
    filename  = "d:/takeout_sbre/Tous les messages, y compris ceux du dossier Spam -003.mbox"
    mots = ["choregraphe"]
    mots = ["serial"]
    #~ mots = ["canope"]
    #~ mots = ["canope","serial"]
    search_file( filename, mots, 100, 1024*1024 )
