import tkinter as tk
from tkinter import ttk, messagebox, font
from tkinter import scrolledtext
from datetime import datetime
import csv
import os
import sqlite3
import sys
import shutil
import time

class CollegeEventManager:
    def __init__(self, root):
        self.root = root
        self.root.title("🎓 College Event Management System")
        self.root.geometry("950x750")
        self.root.configure(bg="#1a1a2e")
        self.db_file = "college_events.db"
        self.init_database()
        self.current_view = "all_events"
        self.event_name_var = tk.StringVar()
        self.event_date_var = tk.StringVar()
        self.event_time_var = tk.StringVar()
        self.event_venue_var = tk.StringVar()
        self.event_organizer_var = tk.StringVar()
        main_container = tk.Frame(self.root, bg='#1a1a2e')
        main_container.pack(fill=tk.BOTH, expand=True)
        self.create_sidebar(main_container)
        self.content_area = tk.Frame(main_container, bg='#162447')
        self.content_area.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        self.init_all_views()
        self.show_view("all_events")
    
    def create_sidebar(self, parent):
        """Create navigation sidebar"""
        sidebar = tk.Frame(parent, bg='#0f3460', width=200)
        sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar.pack_propagate(False)
        logo_frame = tk.Frame(sidebar, bg='#0f3460', height=100)
        logo_frame.pack(fill=tk.X, pady=10)
        logo_frame.pack_propagate(False)   
        logo_label = tk.Label(logo_frame,
                             text="🎓\nEVENT\nMANAGER",
                             font=("Arial", 14, "bold"),
                             bg='#0f3460',
                             fg='#e94560')
        logo_label.pack(expand=True)
        nav_buttons = [
            ("📋 All Events", "all_events", "#1f4068"),
            ("➕ Add Event", "add_event", "#1f4068"),
            ("📄 Event Details", "event_details", "#1f4068"),
            ("🗄️ Database", "database", "#1f4068"),
            ("📊 Statistics", "statistics", "#1f4068")
        ]
        for text, view, color in nav_buttons:
            btn = tk.Button(sidebar,
                           text=text,
                           font=("Arial", 11),
                           bg=color,
                           fg='white',
                           activebackground='#e94560',
                           activeforeground='white',
                           relief=tk.FLAT,
                           anchor='w',
                           padx=20,
                           pady=12,
                           cursor="hand2",
                           command=lambda v=view: self.show_view(v))
            btn.pack(fill=tk.X, pady=2)  
        tk.Frame(sidebar, bg='#1f4068', height=2).pack(fill=tk.X, pady=20)
        status_frame = tk.Frame(sidebar, bg='#0f3460')
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=10)
        
        self.status_label = tk.Label(status_frame,
                                    text="Events: 0",
                                    font=("Arial", 9),
                                    bg='#1f4068',
                                    fg='white',
                                    pady=5)
        self.status_label.pack(fill=tk.X)
        refresh_btn = tk.Button(status_frame,
                               text="🔄 Refresh All",
                               font=("Arial", 9),
                               bg='#e94560',
                               fg='white',
                               relief=tk.FLAT,
                               command=self.refresh_all)
        refresh_btn.pack(pady=5)
    def init_all_views(self):
        """Initialize all views"""
        self.views = {}
        
        self.views["all_events"] = self.create_all_events_view()
        
        self.views["add_event"] = self.create_add_event_view()
   
        self.views["event_details"] = self.create_event_details_view()
     
        self.views["database"] = self.create_database_view()
        

        self.views["statistics"] = self.create_statistics_view()
    
    def create_all_events_view(self):
        """Create All Events view"""
        frame = tk.Frame(self.content_area, bg='#162447')
        
  
        header = tk.Frame(frame, bg='#1f4068', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header,
                        text="📋 ALL EVENTS",
                        font=("Arial", 16, "bold"),
                        bg='#1f4068',
                        fg='white')
        title.pack(pady=18)
        
        
        search_frame = tk.Frame(frame, bg='#162447', pady=10)
        search_frame.pack(fill=tk.X, padx=20)
        
        tk.Label(search_frame,
                text="Search:",
                font=("Arial", 10),
                bg='#162447',
                fg='white').pack(side=tk.LEFT, padx=5)
        
        self.search_entry = tk.Entry(search_frame,
                                    font=("Arial", 10),
                                    width=30,
                                    bg='white')
        self.search_entry.pack(side=tk.LEFT, padx=5)
        
        self.search_type = ttk.Combobox(search_frame,
                                       values=["Name", "Date", "Organizer", "Venue"],
                                       width=12,
                                       state="readonly",
                                       font=("Arial", 10))
        self.search_type.set("Name")
        self.search_type.pack(side=tk.LEFT, padx=5)
        
        search_btn = tk.Button(search_frame,
                              text="🔍 Search",
                              bg='#e94560',
                              fg='white',
                              command=self.search_events)
        search_btn.pack(side=tk.LEFT, padx=5)
        
        clear_btn = tk.Button(search_frame,
                             text="🔄 Clear",
                             bg='#1f4068',
                             fg='white',
                             command=self.load_all_events)
        clear_btn.pack(side=tk.LEFT, padx=5)
        
      
        table_frame = tk.Frame(frame, bg='#162447')
        table_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=10)
       
        columns = ("ID", "Event Name", "Date", "Time", "Venue", "Organizer")
        self.events_tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=15)
        
      
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("Treeview",
                       background="#ffffff",
                       foreground="black",
                       fieldbackground="#ffffff",
                       rowheight=25)
        style.configure("Treeview.Heading",
                       background="#1f4068",
                       foreground="white",
                       font=('Arial', 10, 'bold'),
                       relief='flat')
        style.map("Treeview.Heading",
                 background=[('active', '#e94560')])
        
     
        headings = [("ID", 50), ("Event Name", 200), ("Date", 100), 
                   ("Time", 80), ("Venue", 150), ("Organizer", 150)]
        
        for col, width in headings:
            self.events_tree.heading(col, text=col)
            self.events_tree.column(col, width=width, anchor="center")
       
        v_scroll = ttk.Scrollbar(table_frame, orient=tk.VERTICAL, command=self.events_tree.yview)
        h_scroll = ttk.Scrollbar(table_frame, orient=tk.HORIZONTAL, command=self.events_tree.xview)
        self.events_tree.configure(yscrollcommand=v_scroll.set, xscrollcommand=h_scroll.set)
        
        self.events_tree.grid(row=0, column=0, sticky="nsew")
        v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")
        
     
        table_frame.grid_rowconfigure(0, weight=1)
        table_frame.grid_columnconfigure(0, weight=1)
        
    
        action_frame = tk.Frame(frame, bg='#162447', pady=10)
        action_frame.pack(fill=tk.X, padx=20)
        
        btn_delete = tk.Button(action_frame,
                              text="🗑️ Delete Selected",
                              bg='#ff4d4d',
                              fg='white',
                              padx=15,
                              pady=8,
                              command=self.delete_selected_event)
        btn_delete.pack(side=tk.LEFT, padx=5)
        
        btn_export = tk.Button(action_frame,
                              text="📥 Export to CSV",
                              bg='#4CAF50',
                              fg='white',
                              padx=15,
                              pady=8,
                              command=self.export_to_csv)
        btn_export.pack(side=tk.LEFT, padx=5)
        
        btn_refresh = tk.Button(action_frame,
                               text="🔄 Refresh",
                               bg='#2196F3',
                               fg='white',
                               padx=15,
                               pady=8,
                               command=self.load_all_events)
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
        btn_view_details = tk.Button(action_frame,
                                    text="📄 View Details",
                                    bg='#9C27B0',
                                    fg='white',
                                    padx=15,
                                    pady=8,
                                    command=self.view_selected_details)
        btn_view_details.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def create_add_event_view(self):
        """Create Add Event view"""
        frame = tk.Frame(self.content_area, bg='#162447')
        
   
        header = tk.Frame(frame, bg='#1f4068', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header,
                        text="➕ ADD NEW EVENT",
                        font=("Arial", 16, "bold"),
                        bg='#1f4068',
                        fg='white')
        title.pack(pady=18)
        
       
        form_container = tk.Frame(frame, bg='#1f4068')
        form_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        
        canvas = tk.Canvas(form_container, bg='#1f4068', highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_container, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas, bg='#1f4068')
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
       
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        form_content = tk.Frame(scrollable_frame, bg='#1f4068', padx=20, pady=20)
        form_content.pack(fill=tk.BOTH, expand=True)
        
        
        current_date = datetime.now().strftime("%Y-%m-%d")
        
      
        fields = [
            ("Event Name:*", self.event_name_var, 40, "e.g., Annual Cultural Fest"),
            ("Date (YYYY-MM-DD):*", self.event_date_var, 20, current_date),
            ("Time (HH:MM):", self.event_time_var, 15, "e.g., 14:30"),
            ("Venue:*", self.event_venue_var, 40, "e.g., Main Auditorium"),
            ("Organizer:*", self.event_organizer_var, 40, "e.g., Student Council")
        ]
        
        for i, (label_text, var, width, placeholder) in enumerate(fields):
            
            label = tk.Label(form_content,
                            text=label_text,
                            font=("Arial", 11, "bold"),
                            bg='#1f4068',
                            fg='white',
                            anchor="w")
            label.grid(row=i, column=0, sticky="w", pady=12)
            
          
            entry = tk.Entry(form_content,
                            font=("Arial", 11),
                            bg='white',
                            fg='#333333',
                            width=width,
                            textvariable=var,
                            insertbackground='black')
            entry.grid(row=i, column=1, pady=12, padx=(15, 0), sticky="w")
            
            if placeholder:
                var.set(placeholder)
                entry.config(fg='grey')
                
                def on_entry_click(event, var=var, entry=entry, placeholder=placeholder):
                    if var.get() == placeholder:
                        entry.delete(0, tk.END)
                        entry.config(fg='black')
                
                def on_focusout(event, var=var, entry=entry, placeholder=placeholder):
                    if var.get() == '':
                        var.set(placeholder)
                        entry.config(fg='grey')
                
                entry.bind('<FocusIn>', on_entry_click)
                entry.bind('<FocusOut>', on_focusout)
        
      
        desc_label = tk.Label(form_content,
                             text="Description:",
                             font=("Arial", 11, "bold"),
                             bg='#1f4068',
                             fg='white',
                             anchor="w")
        desc_label.grid(row=5, column=0, sticky="nw", pady=12)
        
        
        self.desc_text = scrolledtext.ScrolledText(form_content,
                                                  font=("Arial", 11),
                                                  bg='white',
                                                  fg='#333333',
                                                  width=40,
                                                  height=10,
                                                  wrap=tk.WORD)
        self.desc_text.grid(row=5, column=1, pady=12, padx=(15, 0), sticky="nsew")
        
     
        self.desc_text.insert(1.0, "Enter event description here...")
        self.desc_text.config(fg='grey')
        
        def on_desc_click(event):
            if self.desc_text.get(1.0, tk.END).strip() == "Enter event description here...":
                self.desc_text.delete(1.0, tk.END)
                self.desc_text.config(fg='black')
        
        def on_desc_focusout(event):
            if not self.desc_text.get(1.0, tk.END).strip():
                self.desc_text.insert(1.0, "Enter event description here...")
                self.desc_text.config(fg='grey')
        
        self.desc_text.bind('<FocusIn>', on_desc_click)
        self.desc_text.bind('<FocusOut>', on_desc_focusout)
        
   
        button_frame = tk.Frame(form_content, bg='#1f4068')
        button_frame.grid(row=6, column=0, columnspan=2, pady=30)
        
     
        btn_add = tk.Button(button_frame,
                           text="➕ ADD EVENT",
                           font=("Arial", 12, "bold"),
                           bg='#4CAF50',
                           fg='white',
                           activebackground='#45a049',
                           activeforeground='white',
                           relief=tk.RAISED,
                           padx=30,
                           pady=12,
                           cursor="hand2",
                           command=self.add_event)
        btn_add.pack(side=tk.LEFT, padx=10)
       
        btn_clear = tk.Button(button_frame,
                             text="🧹 CLEAR FORM",
                             font=("Arial", 12),
                             bg='#f44336',
                             fg='white',
                             activebackground='#d32f2f',
                             activeforeground='white',
                             relief=tk.RAISED,
                             padx=30,
                             pady=12,
                             cursor="hand2",
                             command=self.clear_form)
        btn_clear.pack(side=tk.LEFT, padx=10)
        
        
        btn_sample = tk.Button(button_frame,
                              text="📋 SAMPLE DATA",
                              font=("Arial", 10),
                              bg='#FF9800',
                              fg='white',
                              padx=20,
                              pady=8,
                              cursor="hand2",
                              command=self.add_sample_data)
        btn_sample.pack(side=tk.LEFT, padx=10)
        
        tips_frame = tk.Frame(form_content, bg='#1f4068')
        tips_frame.grid(row=7, column=0, columnspan=2, pady=10)
        
        tips = [
            "💡 All fields marked with * are required",
            "💡 Date format: YYYY-MM-DD (e.g., 2025-12-25)",
            "💡 Time format: HH:MM (e.g., 14:30 for 2:30 PM)",
            "💡 Click 'SAMPLE DATA' to test the form"
        ]
        
        for tip in tips:
            tip_label = tk.Label(tips_frame,
                                text=tip,
                                font=("Arial", 9, "italic"),
                                bg='#1f4068',
                                fg='#FFD700',
                                anchor="w")
            tip_label.pack(anchor="w", pady=2)
        
        return frame
    
    def create_event_details_view(self):
        """Create Event Details view"""
        frame = tk.Frame(self.content_area, bg='#162447')
        
       
        header = tk.Frame(frame, bg='#1f4068', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header,
                        text="📄 EVENT DETAILS",
                        font=("Arial", 16, "bold"),
                        bg='#1f4068',
                        fg='white')
        title.pack(pady=18)
        
     
        details_container = tk.Frame(frame, bg='#1f4068', padx=20, pady=20)
        details_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
       
        selector_frame = tk.Frame(details_container, bg='#1f4068')
        selector_frame.pack(fill=tk.X, pady=(0, 20))
        
        tk.Label(selector_frame,
                text="Select Event:",
                font=("Arial", 11, "bold"),
                bg='#1f4068',
                fg='white').pack(side=tk.LEFT, padx=5)
        
        self.event_selector = ttk.Combobox(selector_frame,
                                          state="readonly",
                                          width=50,
                                          font=("Arial", 10))
        self.event_selector.pack(side=tk.LEFT, padx=10, fill=tk.X, expand=True)
        self.event_selector.bind('<<ComboboxSelected>>', self.display_event_details)
        
        btn_refresh = tk.Button(selector_frame,
                               text="🔄 Refresh",
                               bg='#e94560',
                               fg='white',
                               padx=15,
                               command=self.load_event_selector)
        btn_refresh.pack(side=tk.LEFT, padx=5)
        
      
        display_frame = tk.Frame(details_container, bg='white', relief=tk.SUNKEN, borderwidth=2)
        display_frame.pack(fill=tk.BOTH, expand=True)
        
     
        self.details_display = scrolledtext.ScrolledText(display_frame,
                                                        font=("Courier New", 10),
                                                        bg='#f8f9fa',
                                                        fg='#2c3e50',
                                                        width=70,
                                                        height=20,
                                                        state='disabled',
                                                        wrap=tk.WORD)
        self.details_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        self.details_display.config(state='normal')
        self.details_display.insert(1.0, "👈 Select an event from the dropdown to view its complete details")
        self.details_display.config(state='disabled')
        
       
        action_frame = tk.Frame(details_container, bg='#1f4068', pady=10)
        action_frame.pack(fill=tk.X)
        
        btn_print = tk.Button(action_frame,
                             text="🖨️ Print Details",
                             bg='#2196F3',
                             fg='white',
                             padx=15,
                             pady=8)
        btn_print.pack(side=tk.LEFT, padx=5)
        
        btn_copy = tk.Button(action_frame,
                            text="📋 Copy Details",
                            bg='#4CAF50',
                            fg='white',
                            padx=15,
                            pady=8)
        btn_copy.pack(side=tk.LEFT, padx=5)
        
        return frame
    
    def create_database_view(self):
        """Create Database management view"""
        frame = tk.Frame(self.content_area, bg='#162447')
        
     
        header = tk.Frame(frame, bg='#1f4068', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header,
                        text="🗄️ DATABASE MANAGEMENT",
                        font=("Arial", 16, "bold"),
                        bg='#1f4068',
                        fg='white')
        title.pack(pady=18)
        
     
        info_frame = tk.Frame(frame, bg='#1f4068', padx=30, pady=30)
        info_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        

        db_info = tk.Label(info_frame,
                          text=f"📁 Database File: {os.path.abspath(self.db_file)}",
                          font=("Arial", 11, "bold"),
                          bg='#1f4068',
                          fg='white',
                          anchor="w")
        db_info.pack(anchor='w', pady=5)
        
  
        self.db_stats_label = tk.Label(info_frame,
                                       text="Loading statistics...",
                                       font=("Arial", 10),
                                       bg='#1f4068',
                                       fg='#bdc3c7',
                                       justify='left',
                                       anchor='w')
        self.db_stats_label.pack(anchor='w', pady=10)
        
   
        action_frame = tk.Frame(info_frame, bg='#1f4068')
        action_frame.pack(fill=tk.X, pady=20)
        
        actions = [
            ("📊 Update Stats", "#4CAF50", self.update_db_stats),
            ("🗃️ Backup DB", "#2196F3", self.backup_database),
            ("🔄 Reset DB", "#f44336", self.reset_database),
            ("📁 Open Folder", "#FF9800", self.open_db_folder)
        ]
        
        for text, color, command in actions:
            btn = tk.Button(action_frame,
                           text=text,
                           bg=color,
                           fg='white',
                           padx=15,
                           pady=10,
                           command=command)
            btn.pack(side=tk.LEFT, padx=10)
        
       
        preview_label = tk.Label(info_frame,
                                text="📋 Recent Events (Preview):",
                                font=("Arial", 11, "bold"),
                                bg='#1f4068',
                                fg='white')
        preview_label.pack(anchor='w', pady=(20, 10))
        
        preview_frame = tk.Frame(info_frame, bg='white', relief=tk.SUNKEN, borderwidth=1)
        preview_frame.pack(fill=tk.BOTH, expand=True)
        
        self.db_preview = scrolledtext.ScrolledText(preview_frame,
                                                   font=("Courier New", 9),
                                                   bg='#f8f9fa',
                                                   fg='#2c3e50',
                                                   width=70,
                                                   height=10,
                                                   state='disabled')
        self.db_preview.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        return frame
    
    def create_statistics_view(self):
        """Create Statistics view"""
        frame = tk.Frame(self.content_area, bg='#162447')
      
        header = tk.Frame(frame, bg='#1f4068', height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)
        
        title = tk.Label(header,
                        text="📊 EVENT STATISTICS",
                        font=("Arial", 16, "bold"),
                        bg='#1f4068',
                        fg='white')
        title.pack(pady=18)
       
        stats_container = tk.Frame(frame, bg='#1f4068', padx=30, pady=30)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
       
        stats_display_frame = tk.Frame(stats_container, bg='white', relief=tk.SUNKEN, borderwidth=2)
        stats_display_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_display = scrolledtext.ScrolledText(stats_display_frame,
                                                      font=("Courier New", 10),
                                                      bg='#f8f9fa',
                                                      fg='#2c3e50',
                                                      width=70,
                                                      height=20,
                                                      state='disabled',
                                                      wrap=tk.WORD)
        self.stats_display.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        

        refresh_frame = tk.Frame(stats_container, bg='#1f4068')
        refresh_frame.pack(fill=tk.X, pady=10)
        
        btn_refresh = tk.Button(refresh_frame,
                               text="🔄 Refresh Statistics",
                               bg='#e94560',
                               fg='white',
                               padx=20,
                               pady=8,
                               command=self.update_statistics)
        btn_refresh.pack()
        
        return frame
    
 
    
    def init_database(self):
        """Initialize SQLite database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS events (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                date TEXT NOT NULL,
                time TEXT,
                venue TEXT NOT NULL,
                organizer TEXT NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
       
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_name ON events(name)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_date ON events(date)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_organizer ON events(organizer)')
        
        conn.commit()
        conn.close()
    
    def add_event(self):
        """Add new event to database"""
 
        name = self.event_name_var.get().strip()
        date = self.event_date_var.get().strip()
        time = self.event_time_var.get().strip()
        venue = self.event_venue_var.get().strip()
        organizer = self.event_organizer_var.get().strip()
        description = self.desc_text.get("1.0", tk.END).strip()
        
        placeholders = [
            "e.g., Annual Cultural Fest",
            datetime.now().strftime("%Y-%m-%d"),
            "e.g., 14:30",
            "e.g., Main Auditorium",
            "e.g., Student Council",
            "Enter event description here..."
        ]
        
        if name in placeholders:
            name = ""
        if date in placeholders:
            date = ""
        if time in placeholders:
            time = ""
        if venue in placeholders:
            venue = ""
        if organizer in placeholders:
            organizer = ""
        if description in placeholders:
            description = ""
        
      
        if not time:
            time = "TBA"
        
    
        if not name:
            messagebox.showerror("Error", "❌ Event name is required!")
            self.event_name_var.set("")
            return
        
        if not date:
            messagebox.showerror("Error", "❌ Date is required!")
            self.event_date_var.set("")
            return
        
        
        try:
            datetime.strptime(date, "%Y-%m-%d")
        except ValueError:
            messagebox.showerror("Error", "❌ Date must be in YYYY-MM-DD format\nExample: 2025-12-25")
            self.event_date_var.set("")
            return
        
        if not venue:
            messagebox.showerror("Error", "❌ Venue is required!")
            self.event_venue_var.set("")
            return
        
        if not organizer:
            messagebox.showerror("Error", "❌ Organizer is required!")
            self.event_organizer_var.set("")
            return

        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO events (name, date, time, venue, organizer, description)
                VALUES (?, ?, ?, ?, ?, ?)
            ''', (name, date, time, venue, organizer, description))
            
            conn.commit()
            event_id = cursor.lastrowid
            conn.close()
            
           
            messagebox.showinfo("✅ Success", 
                               f"Event added successfully!\n\n"
                               f"📌 Event ID: {event_id}\n"
                               f"📛 Name: {name}\n"
                               f"📅 Date: {date}\n"
                               f"⏰ Time: {time}\n"
                               f"🏛️ Venue: {venue}\n"
                               f"👤 Organizer: {organizer}")
           
            self.clear_form()
            
           
            self.refresh_all()
            
           
            self.show_view("all_events")
            
        except Exception as e:
            messagebox.showerror("❌ Database Error", f"Failed to add event:\n{str(e)}")
    
    def add_sample_data(self):
        """Add sample event data for testing"""
        sample_events = [
            ("Traditional Day", "2025-11-26", "10:00", "College Ground", "Rohan Patil Sir", 
             "Traditional day where everyone needs to wear traditional wear"),
            ("Annual Cultural Fest", "2025-12-15", "09:00", "Main Auditorium", "Cultural Committee", 
             "Annual cultural festival with various performances and competitions"),
            ("Tech Symposium", "2025-12-10", "14:30", "Computer Lab", "Computer Department", 
             "Technical symposium with coding competition and workshops"),
            ("Sports Day", "2025-12-20", "08:00", "Sports Ground", "Sports Committee", 
             "Annual sports day with various games and competitions"),
            ("Alumni Meet", "2025-12-25", "18:00", "Conference Hall", "Alumni Association", 
             "Annual alumni meet and networking event")
        ]
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            added_count = 0
            for event in sample_events:
                cursor.execute('''
                    INSERT INTO events (name, date, time, venue, organizer, description)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', event)
                added_count += 1
            
            conn.commit()
            conn.close()
            
            messagebox.showinfo("✅ Sample Data Added", 
                               f"Added {added_count} sample events to database!")
            
           
            self.refresh_all()

            self.show_view("all_events")
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to add sample data:\n{str(e)}")
    
    def load_all_events(self):
        """Load all events from database"""
       
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
  
        self.search_entry.delete(0, tk.END)
        
 
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, date, time, venue, organizer FROM events ORDER BY date DESC")
            events = cursor.fetchall()
            
            conn.close()
            
       
            for event in events:
                self.events_tree.insert("", tk.END, values=event)
            
         
            self.status_label.config(text=f"📊 Events: {len(events)}")
            
        except Exception as e:
            messagebox.showerror("❌ Database Error", f"Failed to load events:\n{str(e)}")
    
    def delete_selected_event(self):
        """Delete selected event from database"""
        selected = self.events_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ No Selection", "Please select an event to delete")
            return
        
        item = self.events_tree.item(selected[0])
        event_id = item['values'][0]
        event_name = item['values'][1]
        
        confirm = messagebox.askyesno("⚠️ Confirm Delete", 
                                      f"Are you sure you want to delete:\n\n"
                                      f"Event: {event_name}\n"
                                      f"ID: {event_id}\n\n"
                                      f"This action cannot be undone!")
        
        if confirm:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM events WHERE id = ?", (event_id,))
                conn.commit()
                conn.close()
                
                self.events_tree.delete(selected[0])
                
                messagebox.showinfo("✅ Deleted", "Event deleted successfully")
                
              
                self.refresh_all()
                
            except Exception as e:
                messagebox.showerror("❌ Delete Error", f"Failed to delete event:\n{str(e)}")
    
    def view_selected_details(self):
        """View details of selected event"""
        selected = self.events_tree.selection()
        if not selected:
            messagebox.showwarning("⚠️ No Selection", "Please select an event to view details")
            return
        
        item = self.events_tree.item(selected[0])
        event_id = item['values'][0]
        
    
        self.show_view("event_details")
        
        
        self.load_event_selector()
        
       
        for i, value in enumerate(self.event_selector['values']):
            if value.startswith(f"{event_id} - "):
                self.event_selector.current(i)
                self.display_event_details()
                break
    
    def search_events(self):
        """Search events in database"""
        search_term = self.search_entry.get().strip()
        search_type = self.search_type.get()
        
        if not search_term:
            self.load_all_events()
            return
        
       
        for item in self.events_tree.get_children():
            self.events_tree.delete(item)
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            if search_type == "Name":
                cursor.execute('''
                    SELECT id, name, date, time, venue, organizer 
                    FROM events 
                    WHERE name LIKE ? 
                    ORDER BY date DESC
                ''', (f"%{search_term}%",))
            elif search_type == "Date":
                cursor.execute('''
                    SELECT id, name, date, time, venue, organizer 
                    FROM events 
                    WHERE date LIKE ? 
                    ORDER BY date DESC
                ''', (f"%{search_term}%",))
            elif search_type == "Organizer":
                cursor.execute('''
                    SELECT id, name, date, time, venue, organizer 
                    FROM events 
                    WHERE organizer LIKE ? 
                    ORDER BY date DESC
                ''', (f"%{search_term}%",))
            elif search_type == "Venue":
                cursor.execute('''
                    SELECT id, name, date, time, venue, organizer 
                    FROM events 
                    WHERE venue LIKE ? 
                    ORDER BY date DESC
                ''', (f"%{search_term}%",))
            
            events = cursor.fetchall()
            conn.close()
            
         
            for event in events:
                self.events_tree.insert("", tk.END, values=event)
            
            self.status_label.config(text=f"🔍 Search Results: {len(events)} events found")
            
            if len(events) == 0:
                messagebox.showinfo("🔍 No Results", f"No events found for: '{search_term}'")
                
        except Exception as e:
            messagebox.showerror("❌ Search Error", f"Failed to search events:\n{str(e)}")
    
    def load_event_selector(self):
        """Load events into combobox for event details view"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT id, name, date FROM events ORDER BY date DESC")
            events = cursor.fetchall()
            
            conn.close()
            
            
            event_list = [f"{e[0]} - {e[1]} ({e[2]})" for e in events]
            
            self.event_selector['values'] = event_list
            if event_list:
                self.event_selector.set(event_list[0])
                self.display_event_details()
            else:
                self.event_selector.set("")
                self.details_display.config(state='normal')
                self.details_display.delete(1.0, tk.END)
                self.details_display.insert(1.0, "No events in database. Add some events first!")
                self.details_display.config(state='disabled')
                
        except Exception as e:
            messagebox.showerror("❌ Load Error", f"Failed to load events:\n{str(e)}")
    
    def display_event_details(self, event=None):
        """Display complete event details"""
        selection = self.event_selector.get()
        if not selection:
            return
        
        try:
            
            event_id = int(selection.split(" - ")[0])
            
          
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM events WHERE id = ?", (event_id,))
            event = cursor.fetchone()
            
            conn.close()
            
            if not event:
                return
            
          
            details = f"""
{'═'*70}
{'EVENT DETAILS':^70}
{'═'*70}

📌 Event ID: {event[0]}
📛 Event Name: {event[1]}
📅 Date: {event[2]}
⏰ Time: {event[3]}
🏛️ Venue: {event[4]}
👤 Organizer: {event[5]}
📅 Created: {event[7]}

{'═'*70}

📝 DESCRIPTION:
{'─'*70}
{event[6] if event[6] else 'No description provided'}

{'═'*70}
"""
            
          
            self.details_display.config(state='normal')
            self.details_display.delete(1.0, tk.END)
            self.details_display.insert(1.0, details)
            self.details_display.config(state='disabled')
            
        except Exception as e:
            messagebox.showerror("❌ Error", f"Failed to display event details:\n{str(e)}")
    
    def update_db_stats(self):
        """Update database statistics"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
           
            cursor.execute("SELECT COUNT(*) FROM events")
            total_events = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT date) FROM events")
            total_dates = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT organizer) FROM events")
            total_organizers = cursor.fetchone()[0]
            
            cursor.execute("SELECT COUNT(DISTINCT venue) FROM events")
            total_venues = cursor.fetchone()[0]
            
            cursor.execute("SELECT MIN(date), MAX(date) FROM events")
            date_range = cursor.fetchone()
            
            cursor.execute("SELECT * FROM events ORDER BY id DESC LIMIT 5")
            recent_events = cursor.fetchall()
            
         
            file_size = os.path.getsize(self.db_file) if os.path.exists(self.db_file) else 0
            file_size_kb = file_size / 1024
            
            conn.close()
          
            stats_text = f"""📊 DATABASE STATISTICS:
• Total Events: {total_events}
• Event Dates: {total_dates}
• Organizers: {total_organizers}
• Venues: {total_venues}
• Date Range: {date_range[0] or 'N/A'} to {date_range[1] or 'N/A'}
• Database File: {self.db_file}
• File Size: {file_size_kb:.2f} KB ({file_size} bytes)
"""
            
            self.db_stats_label.config(text=stats_text)
            
           
            preview_text = "Recent Events:\n" + "─"*50 + "\n"
            if recent_events:
                for event in recent_events:
                    preview_text += f"ID {event[0]}: {event[1]} - {event[2]}\n"
            else:
                preview_text += "No events in database\n"
            
            self.db_preview.config(state='normal')
            self.db_preview.delete(1.0, tk.END)
            self.db_preview.insert(1.0, preview_text)
            self.db_preview.config(state='disabled')
            
        except Exception as e:
            self.db_stats_label.config(text=f"Error loading stats: {str(e)}")
    
    def update_statistics(self):
        """Update statistics view"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
           
            cursor.execute("SELECT COUNT(*) FROM events")
            total = cursor.fetchone()[0]
            
            cursor.execute('''
                SELECT strftime('%Y-%m', date) as month, COUNT(*) 
                FROM events 
                GROUP BY month 
                ORDER BY month DESC
            ''')
            monthly_stats = cursor.fetchall()
            
            cursor.execute('''
                SELECT organizer, COUNT(*) 
                FROM events 
                GROUP BY organizer 
                ORDER BY COUNT(*) DESC
            ''')
            organizer_stats = cursor.fetchall()
            
            cursor.execute('''
                SELECT venue, COUNT(*) 
                FROM events 
                GROUP BY venue 
                ORDER BY COUNT(*) DESC
            ''')
            venue_stats = cursor.fetchall()
            
            
            cursor.execute('''
                SELECT CASE 
                    WHEN time LIKE '%AM%' OR (CAST(substr(time, 1, 2) AS INTEGER) < 12) THEN 'Morning'
                    WHEN time LIKE '%PM%' OR (CAST(substr(time, 1, 2) AS INTEGER) BETWEEN 12 AND 17) THEN 'Afternoon'
                    ELSE 'Evening/Night'
                END as time_of_day, COUNT(*)
                FROM events 
                WHERE time != 'TBA'
                GROUP BY time_of_day
            ''')
            time_stats = cursor.fetchall()
            
            conn.close()
            
        
            stats_text = f"""
{'═'*70}
{'EVENT STATISTICS':^70}
{'═'*70}

📈 OVERVIEW
{'─'*70}
• Total Events: {total}

📅 MONTHLY BREAKDOWN
{'─'*70}
"""
            
            if monthly_stats:
                for month, count in monthly_stats:
                    stats_text += f"  • {month}: {count} events\n"
            else:
                stats_text += "  No monthly data available\n"
            
            stats_text += f"\n👥 TOP ORGANIZERS\n{'─'*70}\n"
            if organizer_stats:
                for organizer, count in organizer_stats[:5]:
                    stats_text += f"  • {organizer}: {count} events\n"
            else:
                stats_text += "  No organizer data available\n"
            
            stats_text += f"\n🏛️ TOP VENUES\n{'─'*70}\n"
            if venue_stats:
                for venue, count in venue_stats[:5]:
                    stats_text += f"  • {venue}: {count} events\n"
            else:
                stats_text += "  No venue data available\n"
            
            stats_text += f"\n⏰ EVENT TIMING\n{'─'*70}\n"
            if time_stats:
                for time_of_day, count in time_stats:
                    stats_text += f"  • {time_of_day}: {count} events\n"
            else:
                stats_text += "  No timing data available\n"
            
            stats_text += f"\n{'═'*70}"
            
           
            self.stats_display.config(state='normal')
            self.stats_display.delete(1.0, tk.END)
            self.stats_display.insert(1.0, stats_text)
            self.stats_display.config(state='disabled')
            
        except Exception as e:
            self.stats_display.config(state='normal')
            self.stats_display.delete(1.0, tk.END)
            self.stats_display.insert(1.0, f"Error loading statistics: {str(e)}")
            self.stats_display.config(state='disabled')
    
    def backup_database(self):
        """Create a backup of the database"""
        try:
            timestamp = time.strftime("%Y%m%d_%H%M%S")
            backup_file = f"college_events_backup_{timestamp}.db"
            
            shutil.copy2(self.db_file, backup_file)
            
            messagebox.showinfo("✅ Backup Created", 
                               f"Database backed up to:\n{os.path.abspath(backup_file)}")
        except Exception as e:
            messagebox.showerror("❌ Backup Failed", f"Error: {str(e)}")
    
    def reset_database(self):
        """Reset/clear the database"""
        confirm = messagebox.askyesno("⚠️ Confirm Reset", 
                                      "WARNING: This will delete ALL events from the database.\n\n"
                                      "This action cannot be undone!\n\n"
                                      "Are you absolutely sure?")
        
        if confirm:
            try:
                conn = sqlite3.connect(self.db_file)
                cursor = conn.cursor()
                
                cursor.execute("DELETE FROM events")
                cursor.execute("DELETE FROM sqlite_sequence WHERE name='events'")
                
                conn.commit()
                conn.close()
                
                messagebox.showinfo("✅ Database Reset", "All events have been deleted from the database.")
                self.refresh_all()
                
            except Exception as e:
                messagebox.showerror("❌ Reset Failed", f"Error: {str(e)}")
    
    def open_db_folder(self):
        """Open the folder containing database file"""
        try:
            folder_path = os.path.dirname(os.path.abspath(self.db_file))
            if not folder_path:
                folder_path = "."
            
            if os.name == 'nt': 
                os.startfile(folder_path)
            elif sys.platform == 'darwin': 
                os.system(f'open "{folder_path}"')
            else:  # Linux
                os.system(f'xdg-open "{folder_path}"')
                
        except Exception as e:
            messagebox.showerror("❌ Error", f"Cannot open folder: {str(e)}")
    
    def export_to_csv(self):
        """Export events to CSV file"""
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM events ORDER BY date DESC")
            events = cursor.fetchall()
            
            conn.close()
            
            if not events:
                messagebox.showwarning("⚠️ No Data", "No events to export")
                return
            
            csv_file = "college_events_export.csv"
            
            with open(csv_file, 'w', newline='', encoding='utf-8') as file:
                writer = csv.writer(file)
                
               
                writer.writerow(['ID', 'Name', 'Date', 'Time', 'Venue', 'Organizer', 'Description', 'Created At'])
                
          
                for event in events:
                    writer.writerow(event)
            
            messagebox.showinfo("✅ Export Successful", 
                               f"Events exported to:\n{os.path.abspath(csv_file)}\n\n"
                               f"Total events exported: {len(events)}")
        except Exception as e:
            messagebox.showerror("❌ Export Failed", f"Error: {str(e)}")
    
    def clear_form(self):
        """Clear the add event form"""
     
        self.event_name_var.set("e.g., Annual Cultural Fest")
        self.event_date_var.set(datetime.now().strftime("%Y-%m-%d"))
        self.event_time_var.set("e.g., 14:30")
        self.event_venue_var.set("e.g., Main Auditorium")
        self.event_organizer_var.set("e.g., Student Council")
        

        for child in self.views["add_event"].winfo_children():
            if isinstance(child, tk.Frame):
                for grandchild in child.winfo_children():
                    if isinstance(grandchild, tk.Canvas):
                        for greatgrandchild in grandchild.winfo_children():
                            if isinstance(greatgrandchild, tk.Frame):
                                for widget in greatgrandchild.winfo_children():
                                    if isinstance(widget, tk.Entry):
                                        widget.config(fg='grey')
        
       
        self.desc_text.delete(1.0, tk.END)
        self.desc_text.insert(1.0, "Enter event description here...")
        self.desc_text.config(fg='grey')
    
    def show_view(self, view_name):
        """Show the selected view"""
       
        for view in self.views.values():
            view.pack_forget()
        
       
        self.views[view_name].pack(fill=tk.BOTH, expand=True)
        self.current_view = view_name
        
      
        if view_name == "all_events":
            self.load_all_events()
        elif view_name == "add_event":
            pass 
        elif view_name == "event_details":
            self.load_event_selector()
        elif view_name == "database":
            self.update_db_stats()
        elif view_name == "statistics":
            self.update_statistics()
    
    def refresh_all(self):
        """Refresh all views and update status"""
        
        try:
            conn = sqlite3.connect(self.db_file)
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM events")
            count = cursor.fetchone()[0]
            conn.close()
            
            self.status_label.config(text=f"📊 Events: {count}")
        except:
            self.status_label.config(text="📊 Events: 0")
        
      
        if self.current_view == "all_events":
            self.load_all_events()
        elif self.current_view == "event_details":
            self.load_event_selector()
        elif self.current_view == "database":
            self.update_db_stats()
        elif self.current_view == "statistics":
            self.update_statistics()

def main():
    root = tk.Tk()
    
   
    try:
        root.iconbitmap('event_icon.ico')
    except:
        pass
    
   
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_width = 950
    window_height = 750
    x = (screen_width // 2) - (window_width // 2)
    y = (screen_height // 2) - (window_height // 2)
    root.geometry(f"{window_width}x{window_height}+{x}+{y}")
    
    
    root.minsize(850, 600)
    
    app = CollegeEventManager(root)
    root.mainloop()

if __name__ == "__main__":
    main()