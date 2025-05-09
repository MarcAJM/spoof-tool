import tkinter as tk

class SessionView:

    def __init__(self, model):
        self.model = model

        root = tk.Tk()
        root.title("Spoof Session")
        root.focus_force()
        frame = tk.Frame(root, padx=10, pady=10)
        frame.pack(fill="both", expand=True)
        output_box = tk.Text(frame, state=tk.DISABLED)
        output_box.pack(fill="both", expand=True)
        tk.mainloop()


class SessionModel:

    def __init__(self):
        print("TODO")


model = SessionModel()
SessionView(model)

