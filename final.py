from __future__ import division, print_function, unicode_literals
import sys
import random
import argparse
import logging
from tkinter import Tk, Button, filedialog, messagebox, simpledialog
import os
from PIL import Image
import numpy as np
from Crypto.Cipher import AES
import hashlib

global password

def load_image(name):
    return Image.open(name)

def prepare_message_image(image, size=(256, 256)):
    if size != image.size:
        image = image.resize(size, Image.Resampling.LANCZOS)
    return image

def generate_secret(size):
    width, height = size
    new_secret_image = Image.new(mode="RGB", size=(width * 2, height * 2))

    for x in range(0, 2 * width, 2):
        for y in range(0, 2 * height, 2):
            color1 = np.random.randint(255)
            color2 = np.random.randint(255)
            color3 = np.random.randint(255)
            new_secret_image.putpixel((x, y), (color1, color2, color3))
            new_secret_image.putpixel((x + 1, y), (255 - color1, 255 - color2, 255 - color3))
            new_secret_image.putpixel((x, y + 1), (255 - color1, 255 - color2, 255 - color3))
            new_secret_image.putpixel((x + 1, y + 1), (color1, color2, color3))
    
    return new_secret_image

def pad(data):
    # Pad data to be a multiple of AES block size (16 bytes)
    while len(data) % 16 != 0:
        data += ' '  # Using space for padding
    return data

def unpad(data):
    # Remove padding
    return data.rstrip(b' ')

def encrypt(imagename, password):
    plaintextstr = ""
    im = Image.open(imagename)
    im = prepare_message_image(im)
    pix = im.load()
    width, height = im.size
    
    # Constructing the plaintext string
    plaintextstr += "w" + str(width) + "w"  # Adding width info
    plaintextstr += "h" + str(height) + "h"  # Adding height info
    
    print("Encrypting image:", imagename, "with given password.")
    
    for x in range(width):
        for y in range(height):
            r, g, b = pix[x, y]
            plaintextstr += str(r).zfill(3) + str(g).zfill(3) + str(b).zfill(3)  # Ensure RGB values are 3 digits
            
            # Print the pixel values to the terminal
            print(f"Pixel ({x}, {y}): R={r}, G={g}, B={b}")

    # Encrypting the plaintext
    key = hashlib.sha256(password.encode()).digest()
    cipher = AES.new(key, AES.MODE_CBC, b'This is an IV456')  # Use bytes for the IV.
    
    plaintextstr = pad(plaintextstr)  # Pad plaintext
    
    ciphertext = cipher.encrypt(plaintextstr.encode())
    enc_image_name = "encrypted.jpeg"
    with open(enc_image_name, 'wb') as f:
        f.write(ciphertext)
    
    messagebox.showinfo("Success", f"Image encrypted and saved as {enc_image_name}")

def decrypt(ciphername, password):
    with open(ciphername, 'rb') as cipher:
        ciphertext = cipher.read()
    
    # Decrypting ciphertext with password
    key = hashlib.sha256(password.encode()).digest()
    obj2 = AES.new(key, AES.MODE_CBC, b'This is an IV456')  # Use bytes for the IV.
    decrypted = obj2.decrypt(ciphertext)

    # Unpad the decrypted data
    decrypted = unpad(decrypted)
    
    # Extract dimensions of images.
    decrypted_str = decrypted.decode('latin1')  # Decode using 'latin1' to preserve binary data.
    newwidth = int(decrypted_str.split("w")[1].split("h")[0])
    newheight = int(decrypted_str.split("h")[1].split("h")[0])  # Adjusted parsing to avoid issues

    # Reconstructing the image from the decrypted string.
    newim = Image.new("RGB", (newwidth, newheight))
    pix = newim.load()

    # Rebuild the image from the decrypted string.
    index = decrypted_str.index("h") + len(str(newheight)) + 1  # Skip past dimensions.
    
    for x in range(newwidth):
        for y in range(newheight):
            # Extract RGB values as 3-character sequences.
            r = int(decrypted_str[index:index + 3])
            g = int(decrypted_str[index + 3:index + 6])
            b = int(decrypted_str[index + 6:index + 9])
            pix[x, y] = (r, g, b)
            index += 9
    
    newim.save("decrypted.jpeg")
    messagebox.showinfo("Success", "Image decrypted and saved as decrypted.jpeg")

def load_image_for_encryption():
    filename = filedialog.askopenfilename()
    if filename:
        password = simpledialog.askstring("Password", "Enter password for encryption:")
        encrypt(filename, password)

def load_image_for_decryption():
    filename = filedialog.askopenfilename()
    if filename:
        password = simpledialog.askstring("Password", "Enter password for decryption:")
        decrypt(filename, password)

# Initialize the Tkinter GUI
root = Tk()
root.title("Image Encryption/Decryption Tool")
root.geometry("400x300")

# Add buttons for loading images
load_encrypt_button = Button(root, text="Load Image for Encryption", command=load_image_for_encryption)
load_encrypt_button.pack(pady=10)

load_decrypt_button = Button(root, text="Load Image for Decryption", command=load_image_for_decryption)
load_decrypt_button.pack(pady=10)

# Start the Tkinter event loop
root.mainloop()