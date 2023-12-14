import os
import requests
import tkinter as tk
import tkinter.font as tk_font

from tkinter import messagebox
from tkinter.filedialog import askopenfile


class App(tk.Tk):
    def __init__(self):
        tk.Tk.__init__(self)
        self.font = tk_font.Font(size=18)
        self._frame = None
        self.switch_frame(LoginPage)

    def switch_frame(self, frame_class):
        """Destroys current frame and replaces it with a new one."""
        new_frame = frame_class(self)
        if self._frame is not None:
            self._frame.destroy()
        self._frame = new_frame
        self._frame.pack()


class LoginPage(tk.Frame):
    def __init__(self, master):
        self.master = master

        tk.Frame.__init__(self, master)

        tk.Label(self, text="Username", font=master.font).pack(
            side="top", fill="x", pady=10)
        self.entry_username = tk.Entry(self, font=master.font, width=50)
        self.entry_username.pack()

        tk.Label(self, text="Password", font=master.font).pack(
            side="top", fill="x", pady=10)
        self.entry_password = tk.Entry(self, font=master.font, width=50)
        self.entry_password.pack()

        self.button = tk.Button(self, text="Log in",
                                font=master.font, command=self.login_handler)
        self.button.pack()

    def login_handler(self):
        username = self.entry_username.get()
        password = self.entry_password.get()
        if not username or not password:
            messagebox.showerror("ERROR", "Provide the username and password")
            return

        response = requests.post("http://192.168.18.3:6969/api/email/auth", json={
            "sender": username,
            "password": password,
        })
        if not response or response.status_code != 200:
            messagebox.showerror("ERROR", "Wrong credentials")
            return

        self.master.switch_frame(EmailForm)


class EmailForm(tk.Frame):
    def __init__(self, master):
        self.master = master

        tk.Frame.__init__(self, master)

        tk.Label(self, text="Sender", font=master.font).pack(
            side="top", fill="x", pady=10)
        self.entry_sender = tk.Entry(self, font=master.font, width=50)
        self.entry_sender.pack()

        tk.Label(self, text="Receiver", font=master.font).pack(
            side="top", fill="x", pady=10)
        self.entry_receiver = tk.Entry(self, font=master.font, width=50)
        self.entry_receiver.pack()

        tk.Label(self, text="Subject", font=master.font).pack(
            side="top", fill="x", pady=10)
        self.entry_subject = tk.Entry(self, font=master.font, width=50)
        self.entry_subject.pack()

        tk.Label(self, text="Content", font=master.font).pack(
            side="top", fill="x", pady=10)
        self.entry_content = tk.Text(
            self, font=master.font, width=150, height=15)
        self.entry_content.pack()

        self.upload_file_button = tk.Button(
            self, text="Choose file", font=master.font, command=self.upload_file_handler)
        self.upload_file_button.pack()

        self.button = tk.Button(
            self, text="Send", font=master.font, command=self.email_form_handler)
        self.button.pack()

    def upload_file_handler(self):
        file_path = askopenfile(mode="r", filetypes=[("All files", "*txt")])
        if not file_path:
            messagebox.showerror("ERROR", "could not load the chosen file")
            return

        filename = os.path.basename(file_path.name)
        filecontent = open(file_path.name, "r").read()
        if not filename or not filecontent:
            messagebox.showerror("ERROR", "could not read the chosen file")

        response = requests.post("http://192.168.18.3:6969/api/ftp/upload", json={
            "filename": filename,
            "filecontent": filecontent,
        })
        if not response or response.status_code != 200:
            messagebox.showerror(
                "ERROR", "could upload the file to FTP server")
            return
        else:
            messagebox.showinfo(
                "INFO", f"file {filename} uploaded to FTP server")

        tk.Label(self, text=filename).pack(side="right")

    def email_form_handler(self):
        try:
            sender = self.entry_sender.get()
            receiver = self.entry_receiver.get()
            subject = self.entry_subject.get()
            content = self.entry_content.get("1.0", "end-1c")
            if not sender or not receiver or not subject or not content:
                messagebox.showerror("ERROR", "wrong field value")
                return

            response = requests.post("http://192.168.18.3:6969/api/email", json={
                "sender": sender,
                "receiver": receiver,
                "subject": subject,
                "content": content,
            })
            if not response or response.status_code != 200:
                messagebox.showerror("ERROR", "could not send e-mail")
                return
            else:
                messagebox.showinfo("INFO", "e-mail send")
        except Exception as e:
            messagebox.showerror("ERROR", f"unhandled error occured: {e}")


if __name__ == "__main__":
    app = App()
    app.mainloop()
