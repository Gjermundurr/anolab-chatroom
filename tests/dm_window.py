import tkinter as tk

root = tk.Tk()
root.title('Direct Message')
top_frame = tk.Frame(root, bg='grey', padx=5, pady=5)
user_label = tk.Label(top_frame, text='To: <user>')
chat_frame = tk.Frame(root)
chat = tk.Text(chat_frame, width=10, height=1, state='disabled')
chat_scroll = tk.Scrollbar(chat_frame, command=chat.yview)
chat['yscrollcommand'] = chat_scroll.set

top_frame.pack(anchor='nw')
user_label.pack(side='left')

chat_frame.pack(anchor='nw', fill='both', expand=1)
chat.pack(side='left', fill='both', expand=1)
chat_scroll.pack(side='right', fill='y')

btm_frame = tk.Frame(root, padx=5, pady=5)
msg_field = tk.Text(btm_frame, width=10, height=2)
msg_btn = tk.Button(btm_frame, padx=5, text='Send', height=2, font='fixedsys 10', command=None)

btm_frame.pack(anchor='sw', fill='x')
msg_field.pack(side='left', fill='x', expand=1)
msg_btn.pack(side='left')

root.mainloop()
