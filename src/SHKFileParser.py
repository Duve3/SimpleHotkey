# the script for parsing what the hotkey script turns into

def __find_nth_overlapping(haystack, needle, n):
    start = haystack.find(needle)
    while start >= 0 and n > 1:
        start = haystack.find(needle, start+1)
        n -= 1
    return start


def __createListText(text: str) -> list:
    ListText = []
    for line in text.splitlines():
        ListText.append(line)

    return ListText


def __createTextFromList(ListText: list) -> str:
    newText = ListText.pop(0)
    for line in ListText:
        newText += f"\n{line}"

    return newText


def __clearComments(text: str) -> str:
    # creating a list for each line for easier modification on a per-line basis
    ListText = __createListText(text)

    # for comments that aren't inline
    for i, line in enumerate(ListText):
        if line.startswith("#"):
            ListText[i] = ""

        # for inline comments
        elif "#" in line:
            line = line.split("#")[0]  # only take the non-comment part of the line
            ListText[i] = line

    newText = __createTextFromList(ListText)

    return newText


def __winapiCheck(text: str) -> bool:
    # creating a list for each line for easier modification on a per-line basis
    ListText = __createListText(text)

    if "%WINAPI%" not in ListText[0]:
        print("Warning: WINAPI setting is not defined, defaulting to False (using pyautogui).")
        return False
    elif 'TRUE' in ListText[0]:
        return True
    else:
        return False


def __findTags(text: str, winapi: bool) -> dict:
    """
    Used for finding "tags" inside the script
    :param text: the text from the file
    :param winapi: whether WINAPI setting is enabled
    :return: dictionary that has all the tokens/tags found
    """
    ListText = __createListText(text)
    if winapi is True:
        ListText.pop(0)

    finalDict = {}

    for i, line in enumerate(ListText):
        if line.count("%") % 2 != 0:
            print(ListText)
            raise SyntaxError(f"on line {i} \n\"{line}\"\n\t - Invalid Number of %!")

        symbolList = [z for z in range(0, len(line)) if line[z:].startswith("%")]

        finalDict[i] = symbolList

    for i, entry in enumerate(finalDict):
        if entry is []:
            del finalDict[i]

    return finalDict


def __timeGetter(timeString: str) -> float:
    s = 0
    m = 0
    h = 0

    for char in timeString:
        if char == "s":
            s += 1

        elif char == "m":
            m += 1

        elif char == "h":
            h += 1

    if s + m + h > 1:
        raise SyntaxError(f"Failed timings due to more than one time setter (s, m, h)!")

    try:
        pauseTime = float(timeString.replace("s", "").replace("m", "").replace("h", ""))
    except ValueError:
        raise ValueError("Failed to provide proper timings! Remember only s, m, and h are allowed in EHK scripts.")

    # seconds are skipped since they don't need any change

    if m != 0:
        pauseTime *= 60

    elif h != 0:
        pauseTime *= (60 * 60)

    return pauseTime


def __tokenHandler(text: str, tokens: dict, winapi: bool) -> str:
    TokenKEY_operationOffset = 1
    TokenPAUSE_lengthOffset = 1
    TokenTYPE_stringOffset = 1
    TokenKEY_CustomKeys = {"M1": ["pyautogui.mouseDown(button='left')", "pyautogui.mouseUp(button='left')"], "M2": ["pyautogui.mouseDown(button='right')", "pyautogui.mouseUp(button='right')"], "M3": ["pyautogui.mouseDown(button='middle')", "pyautogui.mouseUp(button='middle')"]}
    validTokens = ["key", "pause", "type", "moveto", "move"]
    varTokens = ["winapi"]
    ListText = __createListText(text)

    codeList = []

    if winapi is False:
        codeList.append("import pyautogui")

    codeList.append("import time")

    for kv in tokens.items():
        key = kv[0]
        values = kv[1]

        line = ListText[key]

        while len(values) > 0:
            p1 = values.pop(0)
            p2 = values.pop(0)

            res = line[p1 + 1:p2]  # + 1 is used because it includes the lower number

            if res.lower() not in validTokens + varTokens:
                raise SyntaxError(f"The token {res} does not exist. Perhaps its a typo?")

            # key
            if res == validTokens[0]:
                spaceList = [z for z in range(0, len(line)) if line[z:].startswith(" ") and z > p2]

                s1 = spaceList.pop(0)
                s2 = spaceList.pop(0)

                key = line[s1:s2].replace(" ", "")  # get the key
                codeKey = ""
                operation = line[s2 + TokenKEY_operationOffset:s2 + TokenKEY_operationOffset + len("PRESS")]

                if operation == "PRESS":
                    codeKey = f"pyautogui.keyDown('{key}')"

                operation = line[s2 + TokenKEY_operationOffset:s2 + TokenKEY_operationOffset + len("RELEASE")]

                if operation == "RELEASE":
                    codeKey = f"pyautogui.keyUp('{key}')"

                if key.upper().replace(" ", "") in TokenKEY_CustomKeys.keys():
                    codeKey = TokenKEY_CustomKeys[key.upper()][0 if operation != "RELEASE" else 1]

                codeList.append(codeKey)

            # pause
            elif res == validTokens[1]:
                amtOfTime = line[p2 + TokenPAUSE_lengthOffset:len(line)]  # from the time given to the end of the line
                pauseTime = __timeGetter(amtOfTime)

                codeList.append(f"time.sleep({pauseTime})")

            # typing
            elif res == validTokens[2]:
                spaceList = [z for z in range(0, len(line)) if line[z:].startswith(" ") and z > p2]

                s1 = spaceList.pop(0)
                s2 = spaceList.pop(0)

                waitTime = __timeGetter(line[s1:s2].replace(" ", ""))

                String = line[s2 + TokenTYPE_stringOffset:len(line)]

                codeList.append(f'pyautogui.write("{String}", interval={waitTime})')

            # moving mouse to exact pos
            elif res == validTokens[3]:
                spaceList = [z for z in range(0, len(line)) if line[z:].startswith(" ") and z > p2]

                s1 = spaceList.pop(0)
                s2 = spaceList.pop(0)

                moveX = line[s1:s2].replace(" ", "")
                moveY = line[s2:len(line)].replace(" ", "")

                codeLine = f"pyautogui.moveTo({moveX}, {moveY})"

                codeList.append(codeLine)

            # moving mouse to relative pos
            elif res == validTokens[4]:
                spaceList = [z for z in range(0, len(line)) if line[z:].startswith(" ") and z > p2]

                s1 = spaceList.pop(0)
                s2 = spaceList.pop(0)

                moveX = line[s1:s2].replace(" ", "")
                moveY = line[s2:len(line)].replace(" ", "")

                codeLine = f"pyautogui.move({moveX}, {moveY})"

                codeList.append(codeLine)

    code = __createTextFromList(codeList)

    return code


def parse(text: str) -> str:
    text = __clearComments(text)
    winapi = __winapiCheck(text)
    tokens = __findTags(text, winapi)
    code = __tokenHandler(text, tokens, winapi)
    print(code)

    return code


# tests
if __name__ == "__main__":
    default = False
    if default:
        with open(r"C:\Users\laksh\PycharmProjects\EasyHotkey\scripts\advancedStarter.ehk", "r") as asf:
            print("-----------------------------------", "RESULT FROM ADVANCED STARTER SCRIPT:", parse(asf.read()), sep="\n")

        with open(r"C:\Users\laksh\PycharmProjects\EasyHotkey\scripts\StarterHotkey.ehk", "r") as sf:
            print("-----------------------------------", "RESULT FROM BASIC STARTER SCRIPT:", parse(sf.read()), sep="\n")

    else:
        with open(input("What is the directory of the script? "), "r") as f:
            exec(parse(f.read()))
