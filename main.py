import tkinter as tk
from tkinter import ttk, filedialog, messagebox, simpledialog
import markdown
import webbrowser
import tempfile
import os
import re
from tkinter.scrolledtext import ScrolledText
from datetime import datetime

class ReadmeGenerator:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Driizzyys README Generator & Viewer")
        self.root.geometry("1400x800")
        self.root.configure(bg='#2b2b2b')
        
        # Current project info
        self.project_info = {
            'title': 'README Generator & Viewer',
            'description': 'A professional, feature-rich GUI application for creating, editing, and previewing README.md files with real-time markdown rendering and advanced customization options.',
            'author': 'driizzyy',
            'license': 'MIT',
            'version': '1.0.0',
            'language': 'Python',
            'repo_url': 'https://github.com/driizzyy/readme-generator/',
            'contact': 'drakko5.56 on Discord'
        }
        
        self.setup_ui()
        self.load_default_template()
        
    def setup_ui(self):
        # Configure styles
        style = ttk.Style()
        style.theme_use('clam')
        style.configure('Dark.TFrame', background='#2b2b2b')
        style.configure('Dark.TLabel', background='#2b2b2b', foreground='white')
        style.configure('Dark.TButton', background='#404040', foreground='white')
        
        # Main container
        main_frame = ttk.Frame(self.root, style='Dark.TFrame')
        main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Top toolbar
        self.create_toolbar(main_frame)
        
        # Main split view
        paned_window = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        paned_window.pack(fill=tk.BOTH, expand=True, pady=(10, 0))
        
        # Left panel - Editor
        self.create_editor_panel(paned_window)
        
        # Right panel - Preview
        self.create_preview_panel(paned_window)
        
        # Status bar
        self.create_status_bar(main_frame)
        
    def create_toolbar(self, parent):
        toolbar = ttk.Frame(parent, style='Dark.TFrame')
        toolbar.pack(fill=tk.X, pady=(0, 10))
        
        # File operations
        ttk.Button(toolbar, text="New README", command=self.new_readme, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Import README", command=self.import_readme, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Export README", command=self.export_readme, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Templates
        ttk.Button(toolbar, text="Basic Template", command=lambda: self.load_template('basic'), style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Advanced Template", command=lambda: self.load_template('advanced'), style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Project Info", command=self.edit_project_info, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        
        ttk.Separator(toolbar, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)
        
        # Quick inserts
        ttk.Button(toolbar, text="Add Badge", command=self.insert_badge, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Table", command=self.insert_table, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        ttk.Button(toolbar, text="Add Code Block", command=self.insert_code_block, style='Dark.TButton').pack(side=tk.LEFT, padx=2)
        
    def create_editor_panel(self, parent):
        # Editor frame
        editor_frame = ttk.Frame(parent, style='Dark.TFrame')
        parent.add(editor_frame, weight=1)
        
        # Editor label
        ttk.Label(editor_frame, text="Markdown Editor", style='Dark.TLabel', font=('Arial', 12, 'bold')).pack(anchor='w', pady=(0, 5))
        
        # Text editor with scrollbar
        self.editor = ScrolledText(
            editor_frame,
            wrap=tk.WORD,
            font=('Consolas', 11),
            bg='#1e1e1e',
            fg='white',
            insertbackground='white',
            selectbackground='#404040'
        )
        self.editor.pack(fill=tk.BOTH, expand=True)
        
        # Bind text change event for live preview
        self.editor.bind('<KeyRelease>', self.on_text_change)
        self.editor.bind('<Button-1>', self.on_text_change)
        
    def create_preview_panel(self, parent):
        # Preview frame
        preview_frame = ttk.Frame(parent, style='Dark.TFrame')
        parent.add(preview_frame, weight=1)
        
        # Preview label with refresh button
        preview_header = ttk.Frame(preview_frame, style='Dark.TFrame')
        preview_header.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Label(preview_header, text="Live Preview", style='Dark.TLabel', font=('Arial', 12, 'bold')).pack(side=tk.LEFT)
        ttk.Button(preview_header, text="Refresh", command=self.update_preview, style='Dark.TButton').pack(side=tk.RIGHT)
        ttk.Button(preview_header, text="Open in Browser", command=self.open_in_browser, style='Dark.TButton').pack(side=tk.RIGHT, padx=(0, 5))
        
        # Preview text widget with GitHub-style colors and padding
        self.preview = ScrolledText(
            preview_frame,
            wrap=tk.WORD,
            font=('Segoe UI', 10),
            bg='#ffffff',
            fg='#24292f',
            state=tk.DISABLED,
            selectbackground='#0969da',
            relief='flat',
            borderwidth=1,
            padx=20,
            pady=15
        )
        self.preview.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)
        
    def create_status_bar(self, parent):
        self.status_bar = ttk.Label(parent, text="Ready", style='Dark.TLabel')
        self.status_bar.pack(side=tk.BOTTOM, fill=tk.X, pady=(10, 0))
        
    def on_text_change(self, event=None):
        # Update preview in real-time
        self.root.after_idle(self.update_preview)
        
    def update_preview(self):
        try:
            # Get markdown content
            markdown_content = self.editor.get(1.0, tk.END)
            
            # Convert to HTML with GitHub-style rendering
            html = self.render_github_markdown(markdown_content)
            
            # Update preview with formatted content
            self.preview.config(state=tk.NORMAL)
            self.preview.delete(1.0, tk.END)
            
            # Apply GitHub-style formatting to the text widget
            self.apply_github_formatting(markdown_content)
            
            self.preview.config(state=tk.DISABLED)
            
            self.status_bar.config(text=f"Preview updated - {len(markdown_content.strip())} characters")
            
        except Exception as e:
            self.status_bar.config(text=f"Preview error: {str(e)}")
            
    def render_github_markdown(self, markdown_content):
        # Convert markdown to HTML with GitHub extensions
        html = markdown.markdown(
            markdown_content,
            extensions=[
                'fenced_code',
                'tables', 
                'toc',
                'codehilite',
                'nl2br',
                'attr_list'
            ],
            extension_configs={
                'codehilite': {
                    'css_class': 'highlight',
                    'use_pygments': False
                }
            }
        )
        return html
        
    def apply_github_formatting(self, markdown_content):
        lines = markdown_content.split('\n')
        current_line = 1
        
        # Configure text tags for GitHub-style formatting
        self.configure_github_tags()
        
        for line in lines:
            line_start = f"{current_line}.0"
            line_end = f"{current_line}.end"
            
            # Insert the line
            self.preview.insert(tk.END, line + '\n')
            
            # Apply formatting based on markdown syntax
            if line.strip():
                self.format_line(line, current_line)
            
            current_line += 1
            
    def configure_github_tags(self):
        # Configure text tags for GitHub styling
        self.preview.tag_configure("h1", font=('Segoe UI', 20, 'bold'), spacing1=15, spacing3=12,
                                 underline=True, underlinefg='#d0d7de')
        self.preview.tag_configure("h2", font=('Segoe UI', 16, 'bold'), spacing1=12, spacing3=10,
                                 underline=True, underlinefg='#d0d7de')
        self.preview.tag_configure("h3", font=('Segoe UI', 14, 'bold'), spacing1=10, spacing3=8)
        self.preview.tag_configure("h4", font=('Segoe UI', 12, 'bold'), spacing1=8, spacing3=6)
        self.preview.tag_configure("h5", font=('Segoe UI', 11, 'bold'), spacing1=6, spacing3=4)
        self.preview.tag_configure("h6", font=('Segoe UI', 10, 'bold'), spacing1=4, spacing3=2, foreground='#656d76')
        
        self.preview.tag_configure("bold", font=('Segoe UI', 10, 'bold'))
        self.preview.tag_configure("italic", font=('Segoe UI', 10, 'italic'))
        self.preview.tag_configure("code", font=('Consolas', 10), background='#f6f8fa', 
                                 relief="solid", borderwidth=1)
        self.preview.tag_configure("code_block", font=('Consolas', 9), background='#f6f8fa',
                                 relief="solid", borderwidth=1, spacing1=8, spacing3=8,
                                 lmargin1=16, lmargin2=16)
        self.preview.tag_configure("blockquote", foreground='#656d76', lmargin1=16, lmargin2=16,
                                 background='#f6f8fa', relief="solid", borderwidth=1)
        self.preview.tag_configure("link", foreground='#0969da', underline=True)
        self.preview.tag_configure("list_item", lmargin1=20, lmargin2=20)
        self.preview.tag_configure("badge", background='#0969da', foreground='white', 
                                 relief="solid", borderwidth=1)
        
    def format_line(self, line, line_num):
        line_start = f"{line_num}.0"
        line_end = f"{line_num}.end"
        
        # Headers
        if line.startswith('# '):
            self.preview.tag_add("h1", line_start, line_end)
        elif line.startswith('## '):
            self.preview.tag_add("h2", line_start, line_end)
        elif line.startswith('### '):
            self.preview.tag_add("h3", line_start, line_end)
        elif line.startswith('#### '):
            self.preview.tag_add("h4", line_start, line_end)
        elif line.startswith('##### '):
            self.preview.tag_add("h5", line_start, line_end)
        elif line.startswith('###### '):
            self.preview.tag_add("h6", line_start, line_end)
            
        # Code blocks
        elif line.startswith('```'):
            self.preview.tag_add("code_block", line_start, line_end)
            
        # Blockquotes
        elif line.startswith('> '):
            self.preview.tag_add("blockquote", line_start, line_end)
            
        # List items
        elif line.strip().startswith('- ') or line.strip().startswith('* ') or re.match(r'^\s*\d+\.', line):
            self.preview.tag_add("list_item", line_start, line_end)
            
        # Badges (shields.io pattern)
        elif '![' in line and 'shields.io' in line:
            self.preview.tag_add("badge", line_start, line_end)
            
        # Apply inline formatting
        self.apply_inline_formatting(line, line_num)
        
    def apply_inline_formatting(self, line, line_num):
        # Bold text **text** or __text__
        bold_pattern = r'\*\*(.*?)\*\*|__(.*?)__'
        for match in re.finditer(bold_pattern, line):
            start_pos = f"{line_num}.{match.start()}"
            end_pos = f"{line_num}.{match.end()}"
            self.preview.tag_add("bold", start_pos, end_pos)
            
        # Italic text *text* or _text_
        italic_pattern = r'(?<!\*)\*(?!\*)([^*]+?)\*(?!\*)|(?<!_)_(?!_)([^_]+?)_(?!_)'
        for match in re.finditer(italic_pattern, line):
            start_pos = f"{line_num}.{match.start()}"
            end_pos = f"{line_num}.{match.end()}"
            self.preview.tag_add("italic", start_pos, end_pos)
            
        # Inline code `code`
        code_pattern = r'`([^`]+)`'
        for match in re.finditer(code_pattern, line):
            start_pos = f"{line_num}.{match.start()}"
            end_pos = f"{line_num}.{match.end()}"
            self.preview.tag_add("code", start_pos, end_pos)
            
        # Links [text](url)
        link_pattern = r'\[([^\]]+)\]\([^)]+\)'
        for match in re.finditer(link_pattern, line):
            start_pos = f"{line_num}.{match.start()}"
            end_pos = f"{line_num}.{match.end()}"
            self.preview.tag_add("link", start_pos, end_pos)
        
    def new_readme(self):
        if messagebox.askyesno("New README", "Create a new README? This will clear the current content."):
            self.editor.delete(1.0, tk.END)
            self.load_default_template()
            self.status_bar.config(text="New README created")
            
    def import_readme(self):
        file_path = filedialog.askopenfilename(
            title="Import README",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                self.editor.delete(1.0, tk.END)
                self.editor.insert(1.0, content)
                self.update_preview()
                self.status_bar.config(text=f"Imported: {os.path.basename(file_path)}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to import file: {str(e)}")
                
    def export_readme(self):
        file_path = filedialog.asksaveasfilename(
            title="Export README",
            defaultextension=".md",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                content = self.editor.get(1.0, tk.END)
                
                with open(file_path, 'w', encoding='utf-8') as file:
                    file.write(content)
                    
                self.status_bar.config(text=f"Exported: {os.path.basename(file_path)}")
                messagebox.showinfo("Success", f"README exported successfully to:\n{file_path}")
                
            except Exception as e:
                messagebox.showerror("Error", f"Failed to export file: {str(e)}")
                
    def open_in_browser(self):
        try:
            # Get markdown content
            markdown_content = self.editor.get(1.0, tk.END)
            
            # Convert to HTML with styling
            html = markdown.markdown(
                markdown_content,
                extensions=['fenced_code', 'tables', 'toc', 'codehilite']
            )
            
            # Add GitHub-style CSS styling
            styled_html = f"""
            <!DOCTYPE html>
            <html>
            <head>
                <meta charset="UTF-8">
                <title>README Preview</title>
                <style>
                    body {{
                        font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans", Helvetica, Arial, sans-serif;
                        font-size: 16px;
                        line-height: 1.5;
                        color: #24292f;
                        background-color: #ffffff;
                        max-width: 1012px;
                        margin: 0 auto;
                        padding: 45px;
                        box-sizing: border-box;
                    }}
                    
                    h1, h2, h3, h4, h5, h6 {{
                        margin-top: 24px;
                        margin-bottom: 16px;
                        font-weight: 600;
                        line-height: 1.25;
                    }}
                    
                    h1 {{
                        font-size: 2em;
                        border-bottom: 1px solid #d0d7de;
                        padding-bottom: 0.3em;
                        margin-top: 0;
                    }}
                    
                    h2 {{
                        font-size: 1.5em;
                        border-bottom: 1px solid #d0d7de;
                        padding-bottom: 0.3em;
                    }}
                    
                    h3 {{ font-size: 1.25em; }}
                    h4 {{ font-size: 1em; }}
                    h5 {{ font-size: 0.875em; }}
                    h6 {{ 
                        font-size: 0.85em; 
                        color: #656d76;
                    }}
                    
                    p {{ margin-top: 0; margin-bottom: 16px; }}
                    
                    code {{
                        background-color: #f6f8fa;
                        border-radius: 6px;
                        font-size: 85%;
                        margin: 0;
                        padding: 0.2em 0.4em;
                        font-family: ui-monospace, SFMono-Regular, "SF Mono", Consolas, "Liberation Mono", Menlo, monospace;
                    }}
                    
                    pre {{
                        background-color: #f6f8fa;
                        border-radius: 6px;
                        font-size: 85%;
                        line-height: 1.45;
                        overflow: auto;
                        padding: 16px;
                        margin-top: 0;
                        margin-bottom: 16px;
                    }}
                    
                    pre code {{
                        background-color: transparent;
                        border: 0;
                        display: inline;
                        line-height: inherit;
                        margin: 0;
                        overflow: visible;
                        padding: 0;
                        word-wrap: normal;
                    }}
                    
                    blockquote {{
                        border-left: 0.25em solid #d0d7de;
                        color: #656d76;
                        margin: 0;
                        padding: 0 1em;
                    }}
                    
                    ul, ol {{
                        margin-top: 0;
                        margin-bottom: 16px;
                        padding-left: 2em;
                    }}
                    
                    li + li {{ margin-top: 0.25em; }}
                    
                    table {{
                        border-spacing: 0;
                        border-collapse: collapse;
                        display: block;
                        width: max-content;
                        max-width: 100%;
                        overflow: auto;
                        margin-top: 0;
                        margin-bottom: 16px;
                    }}
                    
                    th, td {{
                        padding: 6px 13px;
                        border: 1px solid #d0d7de;
                    }}
                    
                    th {{
                        background-color: #f6f8fa;
                        font-weight: 600;
                    }}
                    
                    tr:nth-child(2n) {{
                        background-color: #f6f8fa;
                    }}
                    
                    img {{
                        max-width: 100%;
                        height: auto;
                        box-sizing: content-box;
                        background-color: #ffffff;
                    }}
                    
                    a {{
                        color: #0969da;
                        text-decoration: none;
                    }}
                    
                    a:hover {{
                        text-decoration: underline;
                    }}
                    
                    strong {{ font-weight: 600; }}
                    
                    hr {{
                        height: 0.25em;
                        padding: 0;
                        margin: 24px 0;
                        background-color: #d0d7de;
                        border: 0;
                    }}
                    
                    /* Badge styling */
                    img[src*="shields.io"] {{
                        display: inline-block;
                        margin: 2px;
                    }}
                </style>
            </head>
            <body>
                {html}
            </body>
            </html>
            """
            
            # Save to temporary file and open
            with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False, encoding='utf-8') as f:
                f.write(styled_html)
                temp_path = f.name
                
            webbrowser.open(f'file://{temp_path}')
            self.status_bar.config(text="Opened in browser")
            
        except Exception as e:
            messagebox.showerror("Error", f"Failed to open in browser: {str(e)}")
            
    def edit_project_info(self):
        # Create project info dialog
        dialog = ProjectInfoDialog(self.root, self.project_info)
        self.root.wait_window(dialog.dialog)
        
        if dialog.result:
            self.project_info = dialog.result
            self.status_bar.config(text="Project info updated")
            
    def load_template(self, template_type):
        if template_type == 'basic':
            self.load_basic_template()
        elif template_type == 'advanced':
            self.load_advanced_template()
            
    def load_default_template(self):
        self.load_basic_template()
        
    def load_basic_template(self):
        template = f"""# {self.project_info['title']}

{self.project_info['description']}

## Installation

```bash
git clone https://github.com/{self.project_info['author']}/{self.project_info['title'].lower().replace(' ', '-')}.git
cd {self.project_info['title'].lower().replace(' ', '-')}
```

## Usage

Describe how to use your project here.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the {self.project_info['license']} License.

## Author

**{self.project_info['author']}**
"""
        
        self.editor.delete(1.0, tk.END)
        self.editor.insert(1.0, template)
        self.update_preview()
        
    def load_advanced_template(self):
        template = f"""# {self.project_info['title']}

![Version](https://img.shields.io/badge/version-{self.project_info['version']}-blue.svg)
![License](https://img.shields.io/badge/license-{self.project_info['license']}-green.svg)
![Language](https://img.shields.io/badge/language-{self.project_info['language']}-orange.svg)

{self.project_info['description']}

## 🚀 Features

- Feature 1
- Feature 2
- Feature 3

## 📋 Table of Contents

- [Installation](#installation)
- [Usage](#usage)
- [API Reference](#api-reference)
- [Examples](#examples)
- [Contributing](#contributing)
- [License](#license)
- [Contact](#contact)

## 💻 Installation

### Prerequisites

- List any prerequisites here

### Install

```bash
git clone https://github.com/{self.project_info['author']}/{self.project_info['title'].lower().replace(' ', '-')}.git
cd {self.project_info['title'].lower().replace(' ', '-')}
# Add installation commands here
```

## 🔧 Usage

### Basic Usage

```python
# Add code examples here
```

### Advanced Usage

```python
# Add more complex examples here
```

## 📚 API Reference

### Class/Function Name

Description of what it does.

**Parameters:**
- `param1` (type): Description
- `param2` (type): Description

**Returns:**
- `type`: Description

**Example:**
```python
# Example usage
```

## 🎯 Examples

### Example 1: Basic Example

```python
# Code example
```

### Example 2: Advanced Example

```python
# Advanced code example
```

## 🤝 Contributing

Contributions, issues, and feature requests are welcome!

1. Fork the Project
2. Create your Feature Branch (`git checkout -b feature/AmazingFeature`)
3. Commit your Changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the Branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

This project is licensed under the {self.project_info['license']} License - see the [LICENSE](LICENSE) file for details.

## 👤 Author

**{self.project_info['author']}**

- GitHub: [@{self.project_info['author']}](https://github.com/{self.project_info['author']})

## 📞 Contact

{self.project_info['contact'] if self.project_info['contact'] else 'Add your contact information here'}

## ⭐ Show your support

Give a ⭐ if this project helped you!
"""
        
        self.editor.delete(1.0, tk.END)
        self.editor.insert(1.0, template)
        self.update_preview()
        
    def insert_badge(self):
        badge_dialog = BadgeDialog(self.root)
        self.root.wait_window(badge_dialog.dialog)
        
        if badge_dialog.result:
            badge_md = badge_dialog.result
            # Insert at current cursor position
            current_pos = self.editor.index(tk.INSERT)
            self.editor.insert(current_pos, badge_md)
            self.update_preview()
            
    def insert_table(self):
        table_md = """
| Column 1 | Column 2 | Column 3 |
|----------|----------|----------|
| Row 1    | Data     | Data     |
| Row 2    | Data     | Data     |
"""
        current_pos = self.editor.index(tk.INSERT)
        self.editor.insert(current_pos, table_md)
        self.update_preview()
        
    def insert_code_block(self):
        language = simpledialog.askstring("Code Block", "Enter programming language (optional):") or ""
        
        code_block = f"""
```{language}
# Your code here
```
"""
        current_pos = self.editor.index(tk.INSERT)
        self.editor.insert(current_pos, code_block)
        self.update_preview()
        
    def run(self):
        self.root.mainloop()


class ProjectInfoDialog:
    def __init__(self, parent, current_info):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Project Information")
        self.dialog.geometry("400x500")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.fields = {}
        self.create_widgets(current_info)
        
    def create_widgets(self, current_info):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Project Information", 
                              font=('Arial', 14, 'bold'), 
                              bg='#2b2b2b', fg='white')
        title_label.pack(pady=(0, 20))
        
        # Form fields
        fields_info = [
            ('title', 'Project Title:'),
            ('description', 'Description:'),
            ('author', 'Author:'),
            ('version', 'Version:'),
            ('license', 'License:'),
            ('language', 'Main Language:'),
            ('repo_url', 'Repository URL:'),
            ('demo_url', 'Demo URL:'),
            ('contact', 'Contact Info:')
        ]
        
        for key, label in fields_info:
            # Label
            lbl = tk.Label(main_frame, text=label, bg='#2b2b2b', fg='white', anchor='w')
            lbl.pack(fill=tk.X, pady=(5, 2))
            
            # Entry
            if key == 'description':
                entry = tk.Text(main_frame, height=3, font=('Arial', 10), bg='#404040', fg='white')
                entry.insert(1.0, current_info.get(key, ''))
            else:
                entry = tk.Entry(main_frame, font=('Arial', 10), bg='#404040', fg='white')
                entry.insert(0, current_info.get(key, ''))
                
            entry.pack(fill=tk.X, pady=(0, 10))
            self.fields[key] = entry
            
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(20, 0))
        
        ttk.Button(button_frame, text="Save", command=self.save).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
    def save(self):
        result = {}
        for key, widget in self.fields.items():
            if key == 'description':
                result[key] = widget.get(1.0, tk.END).strip()
            else:
                result[key] = widget.get().strip()
                
        self.result = result
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()


class BadgeDialog:
    def __init__(self, parent):
        self.result = None
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Insert Badge")
        self.dialog.geometry("400x300")
        self.dialog.configure(bg='#2b2b2b')
        self.dialog.resizable(False, False)
        
        # Make dialog modal
        self.dialog.transient(parent)
        self.dialog.grab_set()
        
        # Center the dialog
        self.dialog.geometry("+%d+%d" % (parent.winfo_rootx() + 50, parent.winfo_rooty() + 50))
        
        self.create_widgets()
        
    def create_widgets(self):
        main_frame = ttk.Frame(self.dialog)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = tk.Label(main_frame, text="Create Badge", 
                              font=('Arial', 14, 'bold'), 
                              bg='#2b2b2b', fg='white')
        title_label.pack(pady=(0, 20))
        
        # Badge type
        tk.Label(main_frame, text="Badge Type:", bg='#2b2b2b', fg='white', anchor='w').pack(fill=tk.X)
        self.badge_type = ttk.Combobox(main_frame, values=[
            "Version", "License", "Build Status", "Coverage", "Downloads", "Language", "Custom"
        ])
        self.badge_type.pack(fill=tk.X, pady=(5, 15))
        self.badge_type.set("Version")
        
        # Label
        tk.Label(main_frame, text="Label:", bg='#2b2b2b', fg='white', anchor='w').pack(fill=tk.X)
        self.label_entry = tk.Entry(main_frame, font=('Arial', 10), bg='#404040', fg='white')
        self.label_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Message
        tk.Label(main_frame, text="Message:", bg='#2b2b2b', fg='white', anchor='w').pack(fill=tk.X)
        self.message_entry = tk.Entry(main_frame, font=('Arial', 10), bg='#404040', fg='white')
        self.message_entry.pack(fill=tk.X, pady=(5, 15))
        
        # Color
        tk.Label(main_frame, text="Color:", bg='#2b2b2b', fg='white', anchor='w').pack(fill=tk.X)
        self.color_combo = ttk.Combobox(main_frame, values=[
            "blue", "green", "red", "orange", "yellow", "brightgreen", "lightgrey"
        ])
        self.color_combo.pack(fill=tk.X, pady=(5, 20))
        self.color_combo.set("blue")
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X)
        
        ttk.Button(button_frame, text="Insert", command=self.insert).pack(side=tk.RIGHT, padx=(5, 0))
        ttk.Button(button_frame, text="Cancel", command=self.cancel).pack(side=tk.RIGHT)
        
    def insert(self):
        label = self.label_entry.get().strip() or "label"
        message = self.message_entry.get().strip() or "message"
        color = self.color_combo.get() or "blue"
        
        # Create shields.io badge
        badge_url = f"https://img.shields.io/badge/{label}-{message}-{color}.svg"
        badge_md = f"![{label}]({badge_url})"
        
        self.result = badge_md
        self.dialog.destroy()
        
    def cancel(self):
        self.dialog.destroy()


if __name__ == "__main__":
    app = ReadmeGenerator()
    app.run()