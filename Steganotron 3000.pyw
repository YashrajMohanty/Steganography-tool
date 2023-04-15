from tkinter import Tk, Button, Label, filedialog, Text, WORD, LabelFrame
from PIL import Image, ImageTk
import numpy as np
from os.path import isfile
import cv2
from math import ceil

img_savepath = 'Encrypted images\\'

class rdh():
    img_path = ''
    img = None
    validation_text = 'spur' # acts as a password embedded in the message

def open_img():
    print('Open img')
    rdh.img_path = filedialog.askopenfilename() #get image path through dialog box
    print(rdh.img_path)
    load_image = cv2.imread(rdh.img_path) #open image
    rdh.img = load_image
    return

def display_thumbnail():
    img = rdh.img
    img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    img = Image.fromarray(np.uint8(img))
    img.thumbnail((250,250), Image.ANTIALIAS) #downscale image
    img = ImageTk.PhotoImage(img) #store image in render variable
    img_label.configure(image=img)
    img_label.image = img
    return

def namechecker():
    print('namechecker')
    print(rdh.img_path)

    if rdh.img_path == '':
        print('No image selected')
        temp_label = Label(encrypt_lf, text=("No image selected"), bg=bgcolor, font=("Roboto", 15)) #print label
        temp_label.place(x=210, y=410)
        temp_label.after(3000, temp_label.destroy)
        return False

    #read input from textbox
    picname = nametxt.get(1.0, "end-1c") # 1->Line 1, 0->Character 0, end->read till end of textbox, -1c->deletes one char (to avoid newline)
    pictext = txt.get(1.0, "end-1c")

    if len(picname) == 0:
        print('No name entered')
        temp_label = Label(encrypt_lf, text=("No name entered"), bg=bgcolor, font=("Roboto", 15)) #print label
        temp_label.place(x=210, y=410)
        temp_label.after(3000, temp_label.destroy)
        return False

    if len(pictext) == 0:
        temp_label = Label(encrypt_lf, text=("No text entered"), bg=bgcolor, font=("Roboto", 15)) #print label
        temp_label.place(x=210, y=410)
        temp_label.after(3000, temp_label.destroy)
        return False

    if isfile(img_savepath + picname + '.png'):
        print('Duplicate')
        encrypt_lf.pack_forget()
        confirm_label.configure(text='File name already exists. Overwrite?')
        confirm_lf.pack(expand='yes', fill='both')
        return False
    return True

def encrypt_check():
    if (namechecker()):
        run_encryptor()
        return

def run_encryptor():
    print('Run encryptor')
    img = rdh.img
    img = np.asarray(img)
    _, width, _ = img.shape #obtain width of image

    picname = nametxt.get(1.0, "end-1c") # 1->Line 1, 0->Character 0, end->read till end of textbox, -1c->deletes one char (to avoid newline)
    data = txt.get(1.0, "end-1c") # 1->Line 1, 0->Character 0, end->read till end of textbox, -1c->deletes one char (to avoid newline)
    data = rdh.validation_text + data # adds validation text before the message
    data = [format(ord(i), '08b') for i in data] #breakdown image data and convert to ASCII, ord->returns integer representing unicode character, format->formats specified values and insert them inside the string's placeholder
    #image encryption algorithm
    PixReq = len(data) * 3 #compute no. of pixels required (Length of ASCII array * 3)

    RowReq = PixReq/width #obtain rows required
    RowReq = ceil(RowReq) #rounds up to nearest integer

    count = 0 #initialize count
    charCount = 0 #initialize charcount
    for i in range(RowReq + 1): #traversing image row-wise
        while(count < width and charCount < len(data)):
            char = data[charCount] #for each ASCII character
            charCount += 1
            for index_k, k in enumerate(char):
                if((k == '1' and img[i][count][index_k % 3] % 2 == 0) or (k == '0' and img[i][count][index_k % 3] % 2 == 1)): #if bit=1 and pixel=even or bit=0 and pixel=odd
                    img[i][count][index_k % 3] -= 1 #make pixel value even or odd
                if(index_k % 3 == 2): 
                    count += 1 #number of letters
                if(index_k == 7):
                    if(charCount*3 < PixReq and img[i][count][2] % 2 == 1): #if next character exists and pixel value is odd
                        img[i][count][2] -= 1 #make pixel value even
                    if(charCount*3 >= PixReq and img[i][count][2] % 2 == 0): #if next character doesn't exist and pixel value is even
                        img[i][count][2] -= 1 #make pixel value odd
                    count += 1
        count = 0 #reset count to 0

    write_location = img_savepath + picname + '.png'
    cv2.imwrite(write_location, img) #write encrypted image to new file
    success_label = Label(encrypt_lf, text=("Encryption complete!"), bg=bgcolor, font=("Roboto", 15)) #print label
    success_label.place(x=195, y=420)
    success_label.after(3000, success_label.destroy)


def run_decryptor():
    print('run decryptor')
    if rdh.img_path == '':
        print('No image selected')
        temp_label = Label(decrypt_lf, text=("No image selected"), bg=bgcolor, font=("Roboto", 15)) #print label
        temp_label.place(x=210, y=420)
        temp_label.after(3000, temp_label.destroy)
        return
    #decryption algorithm
    img = rdh.img
    img = np.asarray(img)
    data = []
    stop = False
    for _, i in enumerate(img):
        i.tolist() #convert array elements to list
        for index_j, j in enumerate(i):
            if((index_j) % 3 == 2): #1 bit of data from every row is added to data variable. bin->binary
                data.append(bin(j[0])[-1]) #1st pixel
                data.append(bin(j[1])[-1]) #2nd pixel
                if(bin(j[2])[-1] == '1'): #3rd pixel
                    stop = True
                    break
            else: #ASCII bits are stored serially in data variable
                data.append(bin(j[0])[-1]) #1st pixel
                data.append(bin(j[1])[-1]) #2nd pixel
                data.append(bin(j[2])[-1]) #3rd pixel
        if(stop): #if EOF character, break from loop else continue
            break

    message = []
    for i in range(int((len(data)+1)/8)): #ASCII bits are grouped into letters in groups of 8   
        message.append(data[i*8:(i*8+8)]) #letters stored in message variable
    message = [chr(int(''.join(i), 2)) for i in message] #join the letters to form message
    message = ''.join(message) #add space after word
    return message

def display_decrypt_message(message):
    if message == None:
        return
    if message[:len(rdh.validation_text)] == rdh.validation_text: # checks if the message starts with validation text
        message = message[len(rdh.validation_text):] # removes validation text from message
        message_label.configure(text=message)
    else:
        message_label.configure(text='Error! Image is not encrypted')
    return

app = Tk()
app.title("Steganotron 3000")
#app.tk.call("source", "Azure-ttk-theme-2.1.0/azure.tcl")
#app.tk.call("set_theme", "light")
app.geometry('600x700')
bgcolor = '#ffbb99'

# Encrypt
encrypt_lf = LabelFrame(app, bg=bgcolor)
encrypt_lf.pack(expand='yes', fill='both')

head_label = Label(encrypt_lf, text="Encryptor", bg=bgcolor, font=("Tahoma", 20))
head_label.place(x=250, y=10)

on_click_button = Button(encrypt_lf, text="Open Image", bg='white', fg='black', command=lambda:[open_img(), display_thumbnail()]) #button for on_click
on_click_button.place(x=210, y=70)

txt = Text(encrypt_lf, wrap=WORD, width=30) #textbox to enter the text to be hidden
txt.place(x=180, y=450, height=120)

nametxt = Text(encrypt_lf, wrap=WORD, width=30) #textbox to enter the filename
nametxt.place(x=180, y=580, height=20)

text_label = Label(encrypt_lf, text="Text:", bg=bgcolor, font=("Calibri", 15))
text_label.place(x=120, y=450)

name_label = Label(encrypt_lf, text="Name:", bg=bgcolor, font=("Calibri", 15))
name_label.place(x=110, y=575)

encrypt_button = Button(encrypt_lf, text="Encrypt", bg='white', fg='black', command=encrypt_check) #button to encrypt text
encrypt_button.place(x=270, y=620)

gotodecrypt_button = Button(encrypt_lf, text="Switch to decryptor", bg='white', fg='black', command=lambda:[encrypt_lf.pack_forget(), decrypt_lf.pack(expand='yes', fill='both')]) #button to go to decryptor
gotodecrypt_button.place(x=310, y=70)

# Decrypt
decrypt_lf = LabelFrame(app, bg=bgcolor)

head_label = Label(decrypt_lf, text="Decryptor", bg=bgcolor, font=("Tahoma", 20))
head_label.place(x=250, y=10)

decrypt_button = Button(decrypt_lf, text="Decrypt", bg='white', fg='black', command=lambda:display_decrypt_message(run_decryptor())) #button for decrypt
decrypt_button.place(x=270, y=620)

openimg_button = Button(decrypt_lf, text="Open Image", bg='white', fg='black', command=lambda:[open_img(), display_thumbnail()]) #button for decrypt
openimg_button.place(x=210, y=70)

gotoencrypt_button = Button(decrypt_lf, text="Switch to encryptor", bg='white', fg='black', command=lambda:[decrypt_lf.pack_forget(), encrypt_lf.pack(expand='yes', fill='both')]) #button to go to decryptor
gotoencrypt_button.place(x=310, y=70)

message_label = Label(decrypt_lf, bg=bgcolor, font=("Roboto", 13))
message_label.place(x=220, y=480)

# Confirmation
confirm_lf = LabelFrame(app, bg=bgcolor)

confirm_label = Label(confirm_lf, bg=bgcolor, font=("Roboto", 15)) #print label
confirm_label.place(x=150, y=30)

confirm_yes_button = Button(confirm_lf, text="Yes", bg='white', fg='black', command=lambda:[print('Confirm yes'), confirm_lf.pack_forget(), encrypt_lf.pack(expand='yes', fill='both'), run_encryptor()])
confirm_yes_button.place(x=270, y=70)

confirm_no_button = Button(confirm_lf, text="No", bg='white', fg='black', command=lambda:[print('Confirm no'), confirm_lf.pack_forget(), encrypt_lf.pack(expand='yes', fill='both')])
confirm_no_button.place(x=310, y=70)

# image thumbnail
img_label = Label(app, background=bgcolor, justify='center') #image placement
img_label.place(x=210, y=140)

app.mainloop()