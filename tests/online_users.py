import tkinter as tk

online = ['Gjermund F. Haugen', 'Tomas Valen', 'BV', 'testboi123', '123', '1245', '532', '43663', '564', '56546', '546']
offline = ['Jorgen Norstelien']
data1 = {'head': 'meta', 'body': {'online': online}}
data2 = {'head': 'meta', 'body': {'offline': offline}}
users_index = []


def is_online(meta, frame):
    global users_index
    ((key, value),) = meta.items()
    if key == 'online':
        users_index += [user for user in value]
        for user in value:
            user_lbl = tk.Label(frame, text=user, bg='lightgrey')
            user_lbl.pack(anchor='w')
            user_lbl.bind('<Enter>', lambda event, h=user_lbl: h.configure(bg='lightblue'))
            user_lbl.bind('<Leave>', lambda event, h=user_lbl: h.configure(bg='lightgrey'))
            user_lbl.bind('<Button-3>', popup)


def popup(event):
    try:
        popup_menu.tk_popup(event.x_root, event.y_root, 0)
    finally:
        popup_menu.grab_release()


def directmessage():
    print('Executing DM window ...')


root = tk.Tk()
# root.title('online feature')
# user_frame = tk.Frame(root).pack(fill='both')
# left_frame = tk.Frame(root).pack(side='left')
# right_frame = tk.Frame(user_frame).pack(side='right', fill='y')
# user_scroll = tk.Scrollbar(right_frame, command=mycanvas.yview).pack(side='right', fill='y')
# mycanvas.configure(yscrollcommand=user_scroll.set)
popup_menu = tk.Menu(tearoff=0)
popup_menu.add_command(label='Direct Message', command=directmessage)

is_online(data1['body'], left_frame)


container = tk.Frame(root)
canvas = tk.Canvas(container)
scrollbar = tk.Scrollbar(container, orient='vertical', command=canvas.yview)
scrollable_frame = tk.Frame(canvas)

scrollable_frame.bind('<Configure>', lambda e: canvas.configure(scrollregion=canvas.bbox('all')))

canvas.create_window((0, 0), window=scrollable_frame, anchor='nw')
canvas.configure(yscrollcommand=scrollbar.set)

for i in range(50):
    tk.Label(scrollable_frame, text=f'sample users {i}').pack()

container.pack()
canvas.pack(side='left', fill='both', expand=True)
scrollbar.pack(side='right', fill='y')

root.mainloop()
