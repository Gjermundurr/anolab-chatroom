import tkinter as tk

root = tk.Tk()
root.geometry('600x350')
top_frame = tk.Frame(root)

top_frame.pack(side='top', expand=1, fill='both')


# Left frame!
chat_frame = tk.Frame(top_frame)
chat = tk.Text(chat_frame, width=10, height=1)
chat_scroll = tk.Scrollbar(chat_frame)

chat_frame.pack(side='left', expand=1, fill='both', padx=5, pady=5)
chat.pack(side='left', expand=1, fill='both')
chat_scroll.pack(side='right', fill='y')


# Right frame!
users_frame = tk.Frame(top_frame)
users_box = tk.Listbox(users_frame)
users_scroll = tk.Scrollbar(users_frame)

users_frame.pack(side='right', anchor='ne', padx=5, pady=5)
users_box.pack(side='left')
users_scroll.pack(side='right', fill='y')

# Bottom frame!
msg_frame = tk.Frame(root, height=50, padx=5, pady=5)
msg_text = tk.Text(msg_frame, height=2, width=10)
msg_btn = tk.Button(msg_frame, text='<-Enter>', height=2)
# msg_btn.bind('<Return>', my_func)

msg_frame.pack(anchor='sw', side='bottom', fill='x')
msg_text.pack(side='left', fill='x', expand=1)
msg_btn.pack(padx=10, ipadx=20)

msg = 'yyoyooyoyoyoy'
chat.insert('end', msg)

root.mainloop()


