import sys
import tkinter as tk
from tkinter import Label, StringVar, CENTER, filedialog as fd

import clipboard
import cv2
import easygui
import pandas

# Configurando o file dialog do tkinter
root = tk.Tk()
root.title('Color picker')
root.resizable(False, False)
root.geometry('300x150')

text = StringVar()
text.set('Selecione o seu arquivo')
label = Label(root, textvariable=text, justify=CENTER)
label.pack()

img_path = fd.askopenfilename()

root.destroy()

# Verificando se a imagem e o seu tamanho são compatíveis
img = cv2.imread(img_path)
if img is None:
    sys.exit("Could not read the image. (Não foi possível ler a imagem)")

height = img.shape[0]
width = img.shape[1]

if height > 1500 or width > 800:
    img = cv2.resize(img, (1500, 800))

# Lendo arquivo de imagens
index = ["color", "color_name", "hex", "R", "G", "B"]
csv = pandas.read_csv('colors.csv', names=index, header=None)

# Configurando variáveis globais
clicked = False
r = g = b = xpos = ypos = 0


# Funções de Callback
def draw_function(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDBLCLK:
        global b, g, r, xpos, ypos, clicked
        clicked = True
        xpos = x
        ypos = y
        b, g, r = img[y, x]
        b = int(b)
        g = int(g)
        r = int(r)


def get_color_name(R, G, B):
    min = 10000
    for i in range(len(csv)):
        d = abs(R - int(csv.loc[i, "R"])) + abs(G - int(csv.loc[i, "G"])) + abs(B - int(csv.loc[i, "B"]))
        if d <= min:
            min = d
            cname = csv.loc[i, "color_name"]
    return cname


def rgb_to_hex(R, G, B):
    return '#%02x%02x%02x' % (R, G, B)


cv2.namedWindow('image')
cv2.setMouseCallback('image', draw_function)

# Usando easy GUI para exibir uma simples msgbox
easygui.msgbox("LEIA COM ATENÇÃO\n\nClique duas vezes no pixel que deseja saber a cor\n[ESC] = Sair do programa\nAs "
               "cores vão automaticamente para sua clipboard em hexadecimal", "Python color picker")

while True:
    cv2.imshow("image", img)
    if clicked:
        cv2.rectangle(img, (20, 20), (750, 120), (b, g, r), -1)
        text = "{0} R={1}, G={2}, B={3}, {4}".format(get_color_name(r, g, b), r, g, b, rgb_to_hex(r, g, b))
        clipboard.copy(rgb_to_hex(r, g, b))

        color_text = (0, 0, 0) if r + g + b >= 600 else (255, 255, 255)

        cv2.putText(img, text, (50, 50), 2, 0.8, color_text, 2, cv2.LINE_AA)
        cv2.putText(img, "[ESC] = Exit, {0} copied to clipboard".format(rgb_to_hex(r, g, b)), (50, 100), 2, 0.8, color_text, 2, cv2.LINE_AA)

        clicked = False

    if cv2.waitKey(20) & 0xFF == 27:
        break

cv2.destroyAllWindows()
