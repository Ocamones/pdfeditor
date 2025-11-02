import tkinter as tk
from tkinter import filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter, PdfMerger
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import os
import io
import sys
import ctypes
from ctypes import wintypes

# ============================================================
#              COMBINED PDF TOOLBOX APP
# ============================================================

class PDFToolboxApp:
    def __init__(self, root):
        self.root = root
        self.root.title("📚 PDF Toolbox")
        self.root.geometry("1000x750")
        self.root.resizable(False, False)

        self.container = tk.Frame(root)
        self.container.pack(fill="both", expand=True)

        self.show_home()

    # ============================================================
    #                    HOME MENU
    # ============================================================
    def show_home(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        title = tk.Label(self.container, text="📚 PDF Toolbox", font=("Arial", 22, "bold"))
        title.pack(pady=40)

        merge_btn = tk.Button(
            self.container,
            text="Merge PDFs & Images",
            font=("Arial", 16),
            width=30,
            height=2,
            bg="#185D96",
            fg="white",
            command=self.show_merge_tool,
        )
        merge_btn.pack(pady=20)

        edit_btn = tk.Button(
            self.container,
            text="View / Delete PDF Pages",
            font=("Arial", 16),
            width=30,
            height=2,
            bg="#185D96",
            fg="white",
            command=self.show_edit_tool,
        )
        edit_btn.pack(pady=20)

        split_btn = tk.Button(
            self.container,
            text="Split PDF into Parts",
            font=("Arial", 16),
            width=30,
            height=2,
            bg="#185D96",
            fg="white",
            command=self.show_split_tool,
        )
        split_btn.pack(pady=20)

    # ============================================================
    #                    VIEW / ERASE TOOL
    # ============================================================
    def show_edit_tool(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        app = PDFViewerApp(self.container, self.show_home)
        app.build_ui()

    # ============================================================
    #                    MERGE TOOL (placeholder)
    # ============================================================
    def show_merge_tool(self):
        for widget in self.container.winfo_children():
            widget.destroy()

        app = PDFMergerApp(self.container, self.show_home)
        app.build_ui()

    # ============================================================
    #                    SPLIT TOOL
    # ============================================================
    def show_split_tool(self):
        for widget in self.container.winfo_children():
            widget.destroy()
        app = PDFSplitterApp(self.container, self.show_home)


# ============================================================
#              PDF PAGE VIEWER / ERASER CLASS
# ============================================================

class PDFViewerApp:
    def __init__(self, parent, go_back_callback):
        self.root = parent
        self.go_back_callback = go_back_callback
        self.pdf_path = None
        self.doc = None
        self.total_pages = 0
        self.current_page = 0
        self.page_images = []

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        tk.Button(top_frame, text="🏠 Home", command=self.go_back_callback).grid(row=0, column=0, padx=5)
        tk.Button(top_frame, text="📂 Open PDF", command=self.open_pdf).grid(row=0, column=1, padx=5)
        tk.Button(top_frame, text="❌ Delete Page", command=self.delete_page).grid(row=0, column=2, padx=5)
        tk.Button(top_frame, text="💾 Save As...", command=self.save_pdf).grid(row=0, column=3, padx=5)

        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=5)
        tk.Button(nav_frame, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        self.page_entry = tk.Entry(nav_frame, width=5)
        self.page_entry.grid(row=0, column=1, padx=5)
        self.page_entry.bind("<Return>", lambda event: self.go_to_page())
        tk.Button(nav_frame, text="Next ▶", command=self.next_page).grid(row=0, column=2, padx=5)
        tk.Button(nav_frame, text="Go", command=self.go_to_page).grid(row=0, column=3, padx=5)
        self.page_label = tk.Label(nav_frame, text="Page: 0 / 0")
        self.page_label.grid(row=0, column=4, padx=10)

        self.canvas = tk.Canvas(self.root, bg="#f0f0f0")
        self.canvas.pack(expand=True, fill="both")

    def open_pdf(self):
        file_path = filedialog.askopenfilename(title="Select a PDF file", filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return
        self.pdf_path = file_path
        self.doc = fitz.open(file_path)
        self.total_pages = len(self.doc)
        self.current_page = 0
        self.page_images.clear()
        self.render_all_pages()
        self.show_page(0)

    def render_all_pages(self):
        self.page_images.clear()
        for page_num in range(self.total_pages):
            page = self.doc.load_page(page_num)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = Image.open(io.BytesIO(pix.tobytes("png")))
            self.page_images.append(img_data)

    def show_page(self, page_num):
        if not self.page_images or page_num < 0 or page_num >= self.total_pages:
            return
        self.current_page = page_num
        img = self.page_images[page_num]
        img.thumbnail((800, 600))
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(450, 350, image=self.tk_img)
        self.page_label.config(text=f"Page: {page_num + 1} / {self.total_pages}")

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.show_page(self.current_page + 1)

    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def go_to_page(self):
        try:
            page = int(self.page_entry.get()) - 1
            if 0 <= page < self.total_pages:
                self.show_page(page)
            else:
                messagebox.showwarning("Invalid", "Page out of range.")
        except ValueError:
            messagebox.showwarning("Error", "Please enter a valid page number.")

    def delete_page(self):
        if not self.doc:
            return
        confirm = messagebox.askyesno("Confirm", f"Delete page {self.current_page + 1}?")
        if not confirm:
            return
        self.doc.delete_page(self.current_page)
        self.total_pages -= 1
        if self.current_page >= self.total_pages:
            self.current_page = max(0, self.total_pages - 1)
        self.render_all_pages()
        self.show_page(self.current_page)
        messagebox.showinfo("Success", "Page deleted successfully!")

    def save_pdf(self):
        if not self.doc:
            return
        output_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not output_path:
            return
        if os.path.exists(output_path):
            messagebox.showwarning("Exists", "A file with this name already exists!")
            return
        self.doc.save(output_path)
        messagebox.showinfo("Saved", f"File saved successfully:\n{output_path}")

# ============================================================
#              PDF MERGE PDF
# ============================================================
class PDFMergerApp:
    def __init__(self, parent, go_back_callback):
        self.root = parent
        self.go_back_callback = go_back_callback
        self.files_list = []
        self.output_folder = ""

    def build_ui(self):
        title_label = tk.Label(self.root, text="Merge PDF & Image Files", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)

        back_btn = tk.Button(self.root, text="🏠 Home", command=self.go_back_callback)
        back_btn.pack(pady=5)

        button_frame = tk.Frame(self.root)
        button_frame.pack(pady=5)
        tk.Button(button_frame, text="Add Files", command=self.add_files, width=20).grid(row=0, column=0, padx=5)
        tk.Button(button_frame, text="Merge Files", command=self.merge_files, bg="#4CAF50", fg="white", width=20).grid(row=0, column=1, padx=5)

        folder_frame = tk.Frame(self.root)
        folder_frame.pack(pady=5)
        tk.Button(folder_frame, text="Set Output Folder", command=self.set_output_folder, width=20).grid(row=0, column=0, padx=5)
        self.folder_label = tk.Label(folder_frame, text="Output Folder: Not set", anchor="w")
        self.folder_label.grid(row=0, column=1, padx=5)

        name_frame = tk.Frame(self.root)
        name_frame.pack(pady=5)
        tk.Label(name_frame, text="Merged File Name:").grid(row=0, column=0, padx=5)
        self.output_name_entry = tk.Entry(name_frame, width=40)
        self.output_name_entry.grid(row=0, column=1, padx=5)
        self.output_name_entry.insert(0, "merged_file.pdf")

        list_frame = tk.Frame(self.root)
        list_frame.pack(pady=10)
        scrollbar = tk.Scrollbar(list_frame, orient="vertical")
        self.file_listbox = tk.Listbox(list_frame, width=80, height=15, yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.file_listbox.yview)
        scrollbar.pack(side="right", fill="y")
        self.file_listbox.pack(side="left", fill="both")

        # --- bind click event to update filename ---
        self.file_listbox.bind("<<ListboxSelect>>", self.on_file_select)

        move_frame = tk.Frame(self.root)
        move_frame.pack(pady=10)
        tk.Button(move_frame, text="↑ Move Up", command=self.move_up, width=20).grid(row=0, column=0, padx=5)
        tk.Button(move_frame, text="↓ Move Down", command=self.move_down, width=20).grid(row=0, column=1, padx=5)
        tk.Button(move_frame, text="✖ Remove Selected", command=self.remove_selected, width=20, fg="red").grid(row=0, column=2, padx=5)

        self.total_label = tk.Label(self.root, text="Total pages: 0", font=("Arial", 12))
        self.total_label.pack(pady=5)

    def on_file_select(self, event):
        """Update merged filename when selecting a file."""
        try:
            index = self.file_listbox.curselection()[0]
            file_path, _ = self.files_list[index]
            base_name = os.path.splitext(os.path.basename(file_path))[0]
            self.output_name_entry.delete(0, tk.END)
            self.output_name_entry.insert(0, f"{base_name}.pdf")
        except IndexError:
            pass

    def count_pages(self, file_path):
        ext = os.path.splitext(file_path)[1].lower()
        if ext == ".pdf":
            try:
                reader = PdfReader(file_path)
                return len(reader.pages)
            except:
                return 0
        elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
            return 1
        return 0

    def update_listbox(self):
        self.file_listbox.delete(0, tk.END)
        total_pages = 0
        for path, pages in self.files_list:
            name = os.path.basename(path)
            self.file_listbox.insert(tk.END, f"{name}  ({pages} pages)")
            total_pages += pages
        self.total_label.config(text=f"Total pages: {total_pages}")

    def add_files(self):
        paths = filedialog.askopenfilenames(
            title="Add PDF or Image files",
            filetypes=[("PDF and Images", "*.pdf *.jpg *.jpeg *.png *.bmp *.tiff")]
        )
        if paths:
            for path in paths:
                if path not in [p for p, _ in self.files_list]:
                    pages = self.count_pages(path)
                    self.files_list.append((path, pages))
            # --- Auto-sort alphabetically ---
            self.files_list.sort(key=lambda x: os.path.basename(x[0]).lower())
            self.update_listbox()

    def move_up(self):
        try:
            index = self.file_listbox.curselection()[0]
            if index == 0:
                return
            self.files_list[index - 1], self.files_list[index] = self.files_list[index], self.files_list[index - 1]
            self.update_listbox()
            self.file_listbox.selection_set(index - 1)
        except IndexError:
            pass

    def move_down(self):
        try:
            index = self.file_listbox.curselection()[0]
            if index == len(self.files_list) - 1:
                return
            self.files_list[index + 1], self.files_list[index] = self.files_list[index], self.files_list[index + 1]
            self.update_listbox()
            self.file_listbox.selection_set(index + 1)
        except IndexError:
            pass

    def remove_selected(self):
        try:
            index = self.file_listbox.curselection()[0]
            del self.files_list[index]
            self.update_listbox()
        except IndexError:
            pass

    def set_output_folder(self):
        folder = filedialog.askdirectory(title="Select Output Folder")
        if folder:
            self.output_folder = folder
            self.folder_label.config(text=f"Output Folder: {self.output_folder}")

    def merge_files(self):
        if not self.files_list:
            messagebox.showwarning("Warning", "No files selected.")
            return
        if not self.output_folder:
            messagebox.showwarning("Warning", "Please set an output folder first.")
            return

        filename = self.output_name_entry.get().strip()
        if not filename:
            messagebox.showwarning("Warning", "Please enter a merged file name.")
            return
        if not filename.lower().endswith(".pdf"):
            filename += ".pdf"

        save_path = os.path.join(self.output_folder, filename)

        # ✅ Ask before overwriting
        if os.path.exists(save_path):
            replace = messagebox.askyesno("File Exists", f"The file '{filename}' already exists.\nDo you want to replace it?")
            if not replace:
                messagebox.showinfo("Cancelled", "Merge cancelled. Choose a different name or folder.")
                return

        try:
            merger = PdfMerger()
            total_pages = 0
            for path, _ in self.files_list:
                ext = os.path.splitext(path)[1].lower()
                if ext == ".pdf":
                    reader = PdfReader(path)
                    merger.append(path)
                    total_pages += len(reader.pages)
                elif ext in [".jpg", ".jpeg", ".png", ".bmp", ".tiff"]:
                    image = Image.open(path).convert("RGB")
                    temp_pdf = os.path.join(self.output_folder, "__temp.pdf")
                    image.save(temp_pdf)
                    reader = PdfReader(temp_pdf)
                    merger.append(temp_pdf)
                    total_pages += len(reader.pages)
                    os.remove(temp_pdf)

            merger.write(save_path)
            merger.close()
            messagebox.showinfo("Success", f"Merged file saved as:\n{save_path}\nTotal pages: {total_pages}")
            self.files_list.clear()
            self.update_listbox()
        except Exception as e:
            messagebox.showerror("Error", f"Error merging files:\n{e}")



# ============================================================
#              PDF SPLITTER CLASS (from splitpdf.py)
# ============================================================

class PDFSplitterApp:
    def __init__(self, root, go_back_callback):
        self.root = root
        self.go_back_callback = go_back_callback
        self.pdf_path = None
        self.doc = None
        self.total_pages = 0
        self.page_images = []
        self.current_page = 0
        self.split_frames = []
        self.split_count = tk.IntVar(value=1)
        self.build_ui()

    def build_ui(self):
        top_frame = tk.Frame(self.root)
        top_frame.pack(pady=10)
        tk.Button(top_frame, text="🏠 Home", command=self.go_back_callback).grid(row=0, column=0, padx=5)
        tk.Button(top_frame, text="📂 Open PDF", command=self.open_pdf).grid(row=0, column=1, padx=5)
        tk.Button(top_frame, text="🧹 Erase", command=self.clear_all).grid(row=0, column=2, padx=5)
        tk.Button(top_frame, text="✂ Split PDF", command=self.split_pdf).grid(row=0, column=3, padx=5)
        self.pdf_name_label = tk.Label(top_frame, text="No PDF selected")
        self.pdf_name_label.grid(row=0, column=4, padx=10)

        nav_frame = tk.Frame(self.root)
        nav_frame.pack(pady=5)
        tk.Button(nav_frame, text="◀ Prev", command=self.prev_page).grid(row=0, column=0, padx=5)
        self.page_entry = tk.Entry(nav_frame, width=5)
        self.page_entry.grid(row=0, column=1)
        self.page_entry.bind("<Return>", lambda e: self.go_to_page())
        tk.Button(nav_frame, text="Next ▶", command=self.next_page).grid(row=0, column=2, padx=5)
        tk.Button(nav_frame, text="Go", command=self.go_to_page).grid(row=0, column=3, padx=5)
        self.page_label = tk.Label(nav_frame, text="Page: 0 / 0")
        self.page_label.grid(row=0, column=4, padx=10)

        self.canvas = tk.Canvas(self.root, bg="#f0f0f0")
        self.canvas.pack(expand=True, fill="both", pady=10)

        self.options_frame = tk.LabelFrame(self.root, text="Split Configuration", padx=10, pady=10)
        self.options_frame.pack(fill="x", padx=20, pady=5)
        tk.Label(self.options_frame, text="Number of parts:").grid(row=0, column=0, padx=5)
        tk.Spinbox(self.options_frame, from_=1, to=10, width=5, textvariable=self.split_count).grid(row=0, column=1, padx=5)
        tk.Button(self.options_frame, text="Generate", command=self.generate_split_fields).grid(row=0, column=2, padx=5)
        self.splits_container = tk.Frame(self.options_frame)
        self.splits_container.grid(row=1, column=0, columnspan=5, pady=10)

    def clear_all(self):
        confirm = messagebox.askyesno("Confirm", "Erase everything?")
        if not confirm:
            return
        self.pdf_path = None
        self.doc = None
        self.total_pages = 0
        self.page_images.clear()
        self.current_page = 0
        self.canvas.delete("all")
        self.page_label.config(text="Page: 0 / 0")
        self.pdf_name_label.config(text="No PDF selected")
        for widget in self.splits_container.winfo_children():
            widget.destroy()
        self.split_frames.clear()
        messagebox.showinfo("Cleared", "All data has been erased.")

    def open_pdf(self):
        file_path = filedialog.askopenfilename(title="Select PDF", filetypes=[("PDF Files", "*.pdf")])
        if not file_path:
            return
        self.pdf_path = file_path
        self.doc = fitz.open(file_path)
        self.total_pages = len(self.doc)
        self.page_images.clear()
        self.current_page = 0
        self.pdf_name_label.config(text=os.path.basename(file_path))
        self.render_all_pages()
        self.show_page(0)

    def render_all_pages(self):
        self.page_images.clear()
        for i in range(self.total_pages):
            page = self.doc.load_page(i)
            pix = page.get_pixmap(matrix=fitz.Matrix(1.5, 1.5))
            img_data = Image.open(io.BytesIO(pix.tobytes("png")))
            self.page_images.append(img_data)

    def show_page(self, page_num):
        if not self.page_images or page_num < 0 or page_num >= self.total_pages:
            return
        self.current_page = page_num
        img = self.page_images[page_num].copy()
        img.thumbnail((800, 600))
        self.tk_img = ImageTk.PhotoImage(img)
        self.canvas.delete("all")
        self.canvas.create_image(450, 350, image=self.tk_img)
        self.page_label.config(text=f"Page: {page_num + 1} / {self.total_pages}")

    def next_page(self):
        if self.current_page < self.total_pages - 1:
            self.show_page(self.current_page + 1)

    def prev_page(self):
        if self.current_page > 0:
            self.show_page(self.current_page - 1)

    def go_to_page(self):
        try:
            page = int(self.page_entry.get()) - 1
            if 0 <= page < self.total_pages:
                self.show_page(page)
            else:
                messagebox.showwarning("Invalid", "Page out of range.")
        except ValueError:
            messagebox.showwarning("Error", "Enter a valid page number.")

    def generate_split_fields(self):
        if not self.pdf_path:
            messagebox.showwarning("Warning", "You must open a PDF first.")
            return
        for w in self.splits_container.winfo_children():
            w.destroy()
        self.split_frames.clear()
        count = self.split_count.get()
        for i in range(count):
            frame = tk.Frame(self.splits_container)
            frame.pack(fill="x", pady=3)
            tk.Label(frame, text=f"Part {i+1}:", width=10).pack(side="left")
            tk.Label(frame, text="From").pack(side="left")
            start = tk.Entry(frame, width=5)
            start.pack(side="left", padx=3)
            tk.Label(frame, text="to").pack(side="left")
            end = tk.Entry(frame, width=5)
            end.pack(side="left", padx=3)
            name_var = tk.StringVar(value=f"{os.path.splitext(os.path.basename(self.pdf_path))[0]}_{i+1}.pdf")
            name_entry = tk.Entry(frame, textvariable=name_var, width=40)
            name_entry.pack(side="left", padx=10)
            self.split_frames.append((start, end, name_var))

    def split_pdf(self):
        if not self.doc:
            messagebox.showwarning("Warning", "No PDF selected.")
            return
        output_folder = filedialog.askdirectory(title="Select Output Folder")
        if not output_folder:
            return
        for i, (start_entry, end_entry, name_var) in enumerate(self.split_frames):
            try:
                start_page = int(start_entry.get()) - 1
                end_page = int(end_entry.get())
                if start_page < 0 or end_page > self.total_pages or start_page >= end_page:
                    messagebox.showerror("Error", f"Invalid page range in Part {i+1}")
                    return
                new_pdf = fitz.open()
                for p in range(start_page, end_page):
                    new_pdf.insert_pdf(self.doc, from_page=p, to_page=p)
                output_path = os.path.join(output_folder, name_var.get())
                if os.path.exists(output_path):
                    messagebox.showwarning("Exists", f"File {name_var.get()} already exists!")
                    continue
                new_pdf.save(output_path)
                new_pdf.close()
            except ValueError:
                messagebox.showerror("Error", f"Invalid input in Part {i+1}")
                return
        messagebox.showinfo("Done", "PDF successfully split!")


# ============================================================
#                    RUN APP
# ============================================================
if __name__ == "__main__":
    root = tk.Tk()
    app = PDFToolboxApp(root)
    root.mainloop()
