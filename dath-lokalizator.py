import os
import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox, filedialog
import re

versio = "(0.0.2 | 15/III-25)"

# Dragon-and-the-Tower-Lokalizator (arbtttrn6) (0.0.2 | 15/III-25)
# [RU] Локализатор для INSTEAD игры "Дракон и Башня" ("Dragon and the Tower") на Python  
# [EO] Tradukilo por INSTEADa ludo "Дракон и Башня" ("Drako kaj Turo") en Python  
# [ISV] Lokalizator za INSTEAD igru "Дракон и Башня" ("Zmij i Věža") na Python  
# [HY] Թարգմանչական ծրագիր INSTEAD'ի խաղի "Дракон и башня" («Վիշապ և Աշտարակ») համար Python-ում.  

class cLokalizator:
    def __init__(self, master):
        self.master = master
        self.current_index = 0
        self.ru_file = 'ru.lua'
        self.eo_file = 'eo.lua'
        self.ru_data = {}
        self.eo_data = {}
        self.all_keys = []
        
        self.load_data()
        self.create_widgets()
        self.display_entry()

    def load_data(self):
        self.ru_data = self.parse_lua_file(self.ru_file)
        self.eo_data = self.parse_lua_file(self.eo_file)
        self.all_keys = sorted(set(self.ru_data.keys()).union(set(self.eo_data.keys())))

    def parse_lua_file(self, filename):
        data = {}
        current_path = []
        indent_stack = [-1]
        table_stack = []

        with open(filename, 'r', encoding='utf-8') as f:
                lines = f.readlines()

        for line_num, line in enumerate(lines):
                stripped = line.strip()
                if not stripped:
                        continue

                indent = len(line) - len(line.lstrip())

                if stripped.startswith('}'):
                        while indent_stack and indent <= indent_stack[-1]:
                                indent_stack.pop()
                                if current_path:
                                        current_path.pop()
                        continue

                table_match = re.match(r"^(\w+)\s*=\s*{", stripped)
                if table_match:
                        while indent_stack and indent <= indent_stack[-1]:
                                indent_stack.pop()
                                current_path.pop()

                        current_path.append(table_match.group(1))
                        indent_stack.append(indent)
                        continue

                key_match = re.match(r"^\s*(\w+)\s*=\s*'(.*)'\s*,?\s*$", stripped)
                if key_match:
                        while indent_stack and indent <= indent_stack[-1]:
                                indent_stack.pop()
                                current_path.pop()

                        key = key_match.group(1)
                        value = key_match.group(2)
                        full_key = ".".join(current_path + [key])
                        
                        data[full_key] = {
                                'value': value,
                                'line_num': line_num,
                                'indent': indent,
                                'raw_line': line
                        }

        return data

    def create_widgets(self):
        paned = ttk.PanedWindow(self.master, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        list_frame = ttk.Frame(paned)
        paned.add(list_frame, weight=1)
        
        search_frame = ttk.Frame(list_frame)
        search_frame.pack(fill=tk.X, padx=5, pady=5)
        
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=self.search_var)
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)
        search_entry.bind('<KeyRelease>', self.update_search)

        self.count_label = ttk.Label(search_frame, text="0/0")
        self.count_label.pack(side=tk.RIGHT, padx=(5,0))

        list_container = ttk.Frame(list_frame)
        list_container.pack(fill=tk.BOTH, expand=True)
        
        xscroll = ttk.Scrollbar(list_container, orient=tk.HORIZONTAL)
        yscroll = ttk.Scrollbar(list_container, orient=tk.VERTICAL)
        
        self.listbox = tk.Listbox(
            list_container,
            xscrollcommand=xscroll.set,
            yscrollcommand=yscroll.set,
            width=40,
            font=('TkFixedFont', 10))
        
            
        xscroll.config(command=self.listbox.xview)
        yscroll.config(command=self.listbox.yview)

        self.listbox.grid(row=0, column=0, sticky='nsew')
        yscroll.grid(row=0, column=1, sticky='ns')
        xscroll.grid(row=1, column=0, sticky='ew')
        
        list_container.grid_rowconfigure(0, weight=1)
        list_container.grid_columnconfigure(0, weight=1)

        self.update_listbox()
        self.listbox.bind('<<ListboxSelect>>', self.on_key_select)

        editor_frame = ttk.Frame(paned)
        paned.add(editor_frame, weight=3)

        top_frame = ttk.Frame(editor_frame)
        top_frame.pack(fill=tk.BOTH, expand=True)
        
        top_header = ttk.Frame(top_frame)
        top_header.pack(fill=tk.X)
        ttk.Label(top_header, text="Source:").pack(side=tk.LEFT)
        self.ru_label = ttk.Label(top_header, text=f"({os.path.basename(self.ru_file)})")
        self.ru_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(top_header, text="[C]", width=3, 
                 command=self.copy_source_key).pack(side=tk.LEFT)
        ttk.Button(top_header, text="Change", 
                 command=lambda: self.select_file('ru')).pack(side=tk.LEFT)

        self.ru_text = scrolledtext.ScrolledText(top_frame, wrap=tk.WORD, height=5, state=tk.DISABLED)
        self.ru_text.pack(fill=tk.BOTH, expand=True)

        bottom_frame = ttk.Frame(editor_frame)
        bottom_frame.pack(fill=tk.BOTH, expand=True)
        
        bottom_header = ttk.Frame(bottom_frame)
        bottom_header.pack(fill=tk.X)
        ttk.Label(bottom_header, text="Target:").pack(side=tk.LEFT)
        self.eo_label = ttk.Label(bottom_header, text=f"({os.path.basename(self.eo_file)})")
        self.eo_label.pack(side=tk.LEFT, padx=5)
        ttk.Button(bottom_header, text="[C]", width=3,
                 command=self.copy_target_key).pack(side=tk.LEFT)
        ttk.Button(bottom_header, text="Change", 
                 command=lambda: self.select_file('eo')).pack(side=tk.LEFT)

        self.eo_text = scrolledtext.ScrolledText(bottom_frame, wrap=tk.WORD, height=5)
        self.eo_text.pack(fill=tk.BOTH, expand=True)

        button_frame = ttk.Frame(editor_frame)
        button_frame.pack(fill=tk.X)
        ttk.Button(button_frame, text="Previous", command=self.prev_entry).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Next", command=self.next_entry).pack(side=tk.LEFT)
        ttk.Button(button_frame, text="Save", command=self.save_eo_file).pack(side=tk.RIGHT)

    def copy_source_key(self):
        current_key = self.all_keys[self.current_index] if self.all_keys else ""
        key_part = current_key.split('.')[-1] if current_key else ""
        self.master.clipboard_clear()
        self.master.clipboard_append(key_part)

    def copy_target_key(self):
        current_key = self.all_keys[self.current_index] if self.all_keys else ""
        key_part = current_key.split('.')[-1] if current_key else ""
        self.master.clipboard_clear()
        self.master.clipboard_append(key_part)
    
    def select_file(self, panel_type):
        filetypes = (('Lua files', '*.lua'), ('All files', '*.*'))
        filename = filedialog.askopenfilename(
            title=f'Select {panel_type.upper()} file',
            initialdir='.',
            filetypes=filetypes
        )
        
        if filename:
            if panel_type == 'ru':
                self.ru_file = filename
                self.ru_label.config(text=f"({os.path.basename(filename)})")
            else:
                self.eo_file = filename
                self.eo_label.config(text=f"({os.path.basename(filename)})")
            
            self.all_keys = sorted(set(self.ru_data.keys()).union(set(self.eo_data.keys())))
            self.current_index = 0
            self.update_listbox()
            self.display_entry()
    
    def update_listbox(self):
        self.listbox.delete(0, tk.END)
        for key in self.all_keys:
            self.listbox.insert(tk.END, key)
        if self.all_keys:
            self.listbox.selection_set(0)
            self.listbox.see(0)

    def update_search(self, event):
        search_term = self.search_var.get().lower()
        filtered_keys = [key for key in self.all_keys if search_term in key.lower()]
        
        self.listbox.delete(0, tk.END)
        for key in filtered_keys:
            self.listbox.insert(tk.END, key)
            
        total = len(self.all_keys)
        shown = len(filtered_keys)
        self.count_label.config(text=f"{shown}/{total}")
        
        if filtered_keys:
            self.listbox.selection_set(0)
            self.listbox.see(0)
        else:
            self.ru_text.delete(1.0, tk.END)
            self.eo_text.delete(1.0, tk.END)

    def on_key_select(self, event):
        if selection := self.listbox.curselection():
            selected_key = self.listbox.get(selection[0])
            self.current_index = self.all_keys.index(selected_key)
            self.display_entry()

    def display_entry(self):
        if not self.all_keys:
            return
        
        self.current_index = max(0, min(self.current_index, len(self.all_keys)-1))
        current_key = self.all_keys[self.current_index] if self.all_keys else ""
        ru_value = self.ru_data.get(current_key, {}).get('value', '')
        eo_value = self.eo_data.get(current_key, {}).get('value', '')

        self.ru_label.config(
            text=f"({os.path.basename(self.ru_file)}): {current_key}"
        )
        self.eo_label.config(
            text=f"({os.path.basename(self.eo_file)}): {current_key}"
        )

        self.ru_text.config(state=tk.NORMAL)
        self.ru_text.delete(1.0, tk.END)
        self.ru_text.insert(tk.END, ru_value)
        self.ru_text.config(state=tk.DISABLED)

        self.eo_text.delete(1.0, tk.END)
        self.eo_text.insert(tk.END, eo_value)
        
        if self.all_keys:
            self.listbox.selection_clear(0, tk.END)
            self.listbox.selection_set(self.current_index)
            self.listbox.see(self.current_index)

    def prev_entry(self):
        #self.save_current_eo()
        if self.current_index > 0:
            self.current_index -= 1
            self.display_entry()

    def next_entry(self):
        #self.save_current_eo()
        if self.current_index < len(self.all_keys) - 1:
            self.current_index += 1
            self.display_entry()

    def save_current_eo(self):
        current_key = self.all_keys[self.current_index]
        new_value = self.eo_text.get(1.0, tk.END).strip()
        
        if current_key in self.eo_data:
            self.eo_data[current_key]['value'] = new_value
        else:
            self.eo_data[current_key] = {
                'value': new_value,
                'line_num': None,
                'raw_line': None
            }

    def save_eo_file(self):
        self.save_current_eo()
        try:
                with open(self.eo_file, 'r', encoding='utf-8') as f:
                        original_lines = f.readlines()

                new_lines = []
                processed_keys = set()

                for i, line in enumerate(original_lines):
                        modified = False
                        stripped = line.strip()
                        
                        key_match = re.match(r"^\s*(\w+)\s*=\s*'(.*)'\s*,?\s*$", stripped)
                        if key_match:
                                current_key = self.find_full_key(i)
                                if current_key in self.eo_data:
                                        indent = len(line) - len(line.lstrip())
                                        new_line = f"{' '*indent}{key_match.group(1)} = '{self.eo_data[current_key]['value']}',\n"
                                        new_lines.append(new_line)
                                        processed_keys.add(current_key)
                                        modified = True
                        
                        if not modified:
                                new_lines.append(line)

                for key in self.eo_data:
                        if key not in processed_keys:
                                parent_table = '.'.join(key.split('.')[:-1])
                                table_pos = self.find_table_position(original_lines, parent_table)
                                
                                if table_pos is not None:
                                        indent = ' ' * (table_pos['indent'] + 4)
                                        new_line = f"{indent}{key.split('.')[-1]} = '{self.eo_data[key]['value']}',\n"
                                        new_lines.insert(table_pos['insert_pos'], new_line)
                                else:
                                        new_line = f"{key.split('.')[-1]} = '{self.eo_data[key]['value']}',\n"
                                        new_lines.append(new_line)

                with open(self.eo_file, 'w', encoding='utf-8') as f:
                        f.writelines(new_lines)
                
                messagebox.showinfo("Success", "Konservita!")
        except Exception as e:
                messagebox.showerror("Error", f"Eraro: {str(e)}")

    def find_full_key(self, line_num):
        for key, data in self.eo_data.items():
                if data.get('line_num') == line_num:
                        return key
        return None

    def find_table_position(self, lines, table_path):
        current_path = []
        current_indent = 0
        in_target_table = False
        brace_count = 0
        
        for i, line in enumerate(lines):
                stripped = line.strip()
                indent = len(line) - len(line.lstrip())

                if stripped.startswith('}'):
                        if brace_count > 0:
                                brace_count -= 1
                        if brace_count == 0 and in_target_table:
                                return {'insert_pos': i, 'indent': current_indent}
                        continue

                table_match = re.match(r"^(\w+)\s*=\s*{", stripped)
                if table_match:
                        current_path.append(table_match.group(1))
                        current_indent = indent
                        if '.'.join(current_path) == table_path:
                                in_target_table = True
                                brace_count = 1
                        continue

                if in_target_table:
                        if '{' in line:
                                brace_count += 1
                        if '}' in line:
                                brace_count -= 1

        return None

def main():
    root = tk.Tk()
    root.title(f"Dragon-and-the-Tower: Lokalizator (arbtttrn6) {versio}")
    cLokalizator(root)
    root.mainloop()

if __name__ == '__main__':
    main()
