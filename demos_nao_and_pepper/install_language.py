#ip = "192.168.0.14"
# le plus simple:
# Jarc [0] ~ $ qicli call PackageManager.install /home/nao/robot-language-arabic-1-4-8.pkg
# true
# Jarc [0] ~ $ qicli call PackageManager.install /home/nao/robot-language-arabic-1-4-8.pkg
# false
# Jarc [0] ~ $ qicli call ALTextToSpeech.getAvailableLanguages
ls ./.local/share/PackageManager/apps/

"""
Jarc [0] ~ $ qicli call PackageManager.remove robot-language-arabic
0
Jarc [0] ~ $ qicli call PackageManager.remove robot-language-arabic
1

"""
qicli call PackageManager.install /home/nao/robot-language-arabic-1-4-5_pepper_2_5.pkg