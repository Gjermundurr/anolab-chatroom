import tkinter as tk
from PIL import ImageTk, Image
root = tk.Tk()
img_path = r'../img/Green-icon.png'
online_img = ImageTk.PhotoImage(Image.open(img_path))
label = tk.Label(root, text=' myname', image=online_img, compound='left')

label.pack()

root.mainloop()