from utility.util import MenuResponses
import pygame
import ctypes
from ConvertToPython import PythonConvertMenu
from mainmenu import MainMenu
from executeMenu import ExecuteMenu


# pygame yahoo
def main():
    myappid = u'alterra.software.simplehotkey.testing'  # arbitrary string
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

    pygame.init()

    RES = (1080, 720)  # idek what resolution this is
    pygame.display.set_caption("Simple Hotkey (SHK)")
    window = pygame.display.set_mode(RES)
    fpsClock = pygame.time.Clock()
    fps = 60
    pcm = PythonConvertMenu(window, fpsClock, fps, RES)
    mm = MainMenu(window, fpsClock, fps, RES)
    em = ExecuteMenu(window, fpsClock, fps, RES)
    response = mm.run()
    while True:
        if response == MenuResponses.QUIT:
            return
        elif response == MenuResponses.EnterPCMMenu:
            pcm.reset()
            response = pcm.run()
        elif response == MenuResponses.EnterMainMenu:
            mm.reset()
            response = mm.run()
        elif response == MenuResponses.EnterExecuteMenu:
            em.reset()
            response = em.run()


if __name__ == "__main__":
    main()

    # since the pygame interface is currently not working, please just uncomment the code below when actually using SHK.
    # directoryToFile = input("What's the exact directory to the file you are converting? ")
    #
    # with open(directoryToFile) as f:
    #     pyhk = parse(f.read())
    #
    # print(pyhk)


