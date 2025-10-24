import tkinter as tk
from tkinter import ttk, messagebox
import threading
import pymem.exception
from scanner import MegaBonkScanner


class ModernShopScannerGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("MegaBonk Shop Scanner")
        self.root.geometry("900x600")
        self.root.resizable(True, True)
        
        # Modern color scheme
        self.colors = {
            'bg': '#1e1e1e',
            'fg': '#ffffff',
            'accent': '#007acc',
            'secondary': '#2d2d30',
            'success': '#4ec9b0',
            'warning': '#ce9178',
            'error': '#f48771',
            'common': '#9e9e9e',
            'rare': '#4169E1',
            'epic': '#9370DB',
            'legendary': '#FFD700'
        }
        
        self.scanner = None
        self.shops_data = []
        self.initialized = False
        
        self.setup_modern_ui()
        
        # Start initialization immediately
        self.root.after(100, self.check_or_initialize)
    
    def setup_modern_ui(self):
        # Configure root background
        self.root.configure(bg=self.colors['bg'])
        
        # Custom style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure styles
        style.configure('Modern.TFrame', background=self.colors['bg'])
        style.configure('Card.TFrame', background=self.colors['secondary'], relief='flat')
        
        # Main container
        main_frame = ttk.Frame(self.root, style='Modern.TFrame', padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(2, weight=1)
        
        # Header - Compact
        header_frame = ttk.Frame(main_frame, style='Modern.TFrame')
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        
        title = tk.Label(header_frame, text="⚡ MegaBonk Shop Scanner", 
                        bg=self.colors['bg'], fg=self.colors['accent'],
                        font=('Segoe UI', 14, 'bold'))
        title.pack(side=tk.LEFT)
        
        self.stats_label = tk.Label(header_frame, text="Shops: 0", 
                                    bg=self.colors['bg'], fg=self.colors['success'],
                                    font=('Segoe UI', 11, 'bold'))
        self.stats_label.pack(side=tk.RIGHT)
        
        # Control panel - Compact
        control_frame = ttk.Frame(main_frame, style='Card.TFrame', padding="10")
        control_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), pady=(0, 10))
        control_frame.columnconfigure(1, weight=1)
        
        # Buttons side by side
        button_container = tk.Frame(control_frame, bg=self.colors['secondary'])
        button_container.grid(row=0, column=0, sticky=tk.W, padx=(0, 15))
        
        self.quick_scan_button = tk.Button(button_container, text="⚡ QUICK SCAN", 
                                           command=self.start_quick_scan,
                                           bg=self.colors['accent'], fg=self.colors['fg'],
                                           font=('Segoe UI', 9, 'bold'), 
                                           relief='flat', cursor='hand2',
                                           padx=15, pady=8, borderwidth=0,
                                           state='disabled')
        self.quick_scan_button.pack(side=tk.LEFT, padx=(0, 5))
        
        self.full_scan_button = tk.Button(button_container, text="🔍 FULL SCAN", 
                                          command=self.start_full_scan,
                                          bg='#555555', fg=self.colors['fg'],
                                          font=('Segoe UI', 9, 'bold'), 
                                          relief='flat', cursor='hand2',
                                          padx=15, pady=8, borderwidth=0,
                                          state='disabled')
        self.full_scan_button.pack(side=tk.LEFT)
        
        # Progress and status
        progress_frame = ttk.Frame(control_frame, style='Card.TFrame')
        progress_frame.grid(row=0, column=1, sticky=(tk.W, tk.E))
        progress_frame.columnconfigure(0, weight=1)
        
        self.progress = ttk.Progressbar(progress_frame, mode='determinate')
        self.progress.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 3))
        
        self.status_label = tk.Label(progress_frame, text="Initializing...", 
                                     bg=self.colors['secondary'], fg=self.colors['fg'],
                                     font=('Segoe UI', 8), anchor='w')
        self.status_label.grid(row=1, column=0, sticky=(tk.W, tk.E))
        
        # Shops display - Compact table-like view
        shops_container = ttk.Frame(main_frame, style='Modern.TFrame')
        shops_container.grid(row=2, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        shops_container.columnconfigure(0, weight=1)
        shops_container.rowconfigure(0, weight=1)
        
        self.canvas = tk.Canvas(shops_container, bg=self.colors['bg'], 
                               highlightthickness=0, borderwidth=0)
        scrollbar = ttk.Scrollbar(shops_container, orient="vertical", command=self.canvas.yview)
        self.scrollable_frame = tk.Frame(self.canvas, bg=self.colors['bg'])
        
        self.scrollable_frame.bind("<Configure>", 
                                  lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        
        self.canvas.create_window((0, 0), window=self.scrollable_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scrollbar.set)
        
        self.canvas.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        self.canvas.bind_all("<MouseWheel>", self._on_mousewheel)
    
    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1*(event.delta/120)), "units")
    
    def update_progress(self, value, maximum):
        self.progress['maximum'] = maximum
        self.progress['value'] = value
        self.root.update_idletasks()
    
    def log_message(self, message):
        self.status_label['text'] = message
        self.root.update_idletasks()
    
    def check_or_initialize(self):
        """Initialize scanner object"""
        try:
            self.log_message("Initializing scanner...")
            
            self.scanner = MegaBonkScanner(
                progress_callback=self.update_progress,
                log_callback=self.log_message
            )
            
            self.initialized = True
            self.log_message("✅ Ready to scan!")
            self.quick_scan_button['state'] = 'normal'
            self.full_scan_button['state'] = 'normal'
            self.quick_scan_button['bg'] = self.colors['accent']
            self.full_scan_button['bg'] = '#555555'
            
        except pymem.exception.ProcessNotFound:
            self.log_message("❌ MegaBonk.exe not running! Start the game first.")
            self.quick_scan_button['state'] = 'disabled'
            self.full_scan_button['state'] = 'disabled'
        except Exception as e:
            self.log_message(f"❌ Error: {str(e)[:50]}")
            self.quick_scan_button['state'] = 'disabled'
            self.full_scan_button['state'] = 'disabled'
    
    def start_quick_scan(self):
        self.start_scan(use_learned=True)
    
    def start_full_scan(self):
        self.start_scan(use_learned=False)
    
    def start_scan(self, use_learned=True):
        if not self.initialized or not self.scanner:
            messagebox.showwarning("Not Initialized", "Scanner not initialized!")
            return
        
        self.quick_scan_button['state'] = 'disabled'
        self.full_scan_button['state'] = 'disabled'
        self.quick_scan_button['bg'] = '#666666'
        self.full_scan_button['bg'] = '#333333'
        
        # Clear previous results
        for widget in self.scrollable_frame.winfo_children():
            widget.destroy()
        
        self.shops_data = []
        
        thread = threading.Thread(target=self.scan_shops, args=(use_learned,), daemon=True)
        thread.start()
    
    def scan_shops(self, use_learned):
        try:
            shops = self.scanner.find_all_shops(
                shop_found_callback=self.add_shop_to_display,
                use_learned=use_learned
            )
            
            if not self.shops_data:
                self.log_message("No shops found")
            else:
                self.log_message(f"✅ Found {len(self.shops_data)} shop(s)!")
            
            self.quick_scan_button['state'] = 'normal'
            self.full_scan_button['state'] = 'normal'
            self.quick_scan_button['bg'] = self.colors['accent']
            self.full_scan_button['bg'] = '#555555'
            
        except Exception as e:
            self.log_message(f"❌ Error: {e}")
            self.quick_scan_button['state'] = 'normal'
            self.full_scan_button['state'] = 'normal'
            self.quick_scan_button['bg'] = self.colors['accent']
            self.full_scan_button['bg'] = '#555555'
    
    def add_shop_to_display(self, shop_data):
        """Add a single shop to display immediately when found"""
        self.shops_data.append(shop_data)
        self.root.after(0, lambda: self.display_single_shop(shop_data, len(self.shops_data) - 1))
    
    def get_rarity_color(self, rarity):
        """Get color for rarity level"""
        colors = [self.colors['common'], self.colors['rare'], 
                 self.colors['epic'], self.colors['legendary']]
        return colors[rarity] if 0 <= rarity <= 3 else '#ffffff'
    
    def get_rarity_symbol(self, rarity):
        """Get symbol for rarity level"""
        symbols = ['●', '●●', '●●●', '★']
        return symbols[rarity] if 0 <= rarity <= 3 else '?'
    
    def display_single_shop(self, shop, idx):
        """Display a single shop in compact format"""
        self.stats_label['text'] = f"Shops: {len(self.shops_data)}"
        
        # Shop container - more compact
        shop_frame = tk.Frame(self.scrollable_frame, bg=self.colors['secondary'], 
                             relief='flat', borderwidth=1)
        shop_frame.grid(row=idx, column=0, sticky=(tk.W, tk.E), pady=3, padx=3)
        shop_frame.columnconfigure(0, weight=1)
        
        # Shop header - single line
        header_frame = tk.Frame(shop_frame, bg=self.colors['accent'], height=2)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E))
        
        # Shop info - compact
        info_frame = tk.Frame(shop_frame, bg=self.colors['secondary'])
        info_frame.grid(row=1, column=0, sticky=(tk.W, tk.E), padx=8, pady=4)
        
        rarity_color = self.get_rarity_color(shop['rarity'])
        rarity_symbol = self.get_rarity_symbol(shop['rarity'])
        status = "✓" if shop['done'] else "○"
        
        shop_label = tk.Label(info_frame, 
                             text=f"{status} Shop #{idx + 1}  {rarity_symbol}",
                             bg=self.colors['secondary'], fg=rarity_color,
                             font=('Segoe UI', 9, 'bold'))
        shop_label.pack(side=tk.LEFT)
        
        # Items in a compact grid
        items_frame = tk.Frame(shop_frame, bg=self.colors['secondary'])
        items_frame.grid(row=2, column=0, sticky=(tk.W, tk.E), padx=8, pady=(0, 6))
        
        for i, item in enumerate(shop['items']):
            self.create_compact_item(items_frame, item, shop['prices'][i] if i < len(shop['prices']) else 0, i)
        
        self.canvas.update_idletasks()
    
    def create_compact_item(self, parent, item, price, index):
        """Create a compact item row"""
        item_frame = tk.Frame(parent, bg=self.colors['bg'], relief='flat')
        item_frame.pack(fill=tk.X, pady=1)
        item_frame.columnconfigure(1, weight=1)
        
        # Index badge - smaller
        badge = tk.Label(item_frame, text=str(index + 1), 
                        bg=self.colors['accent'], fg=self.colors['fg'],
                        font=('Segoe UI', 8, 'bold'), width=2)
        badge.grid(row=0, column=0, padx=(4, 6), pady=3)
        
        # Item info - single line
        info_container = tk.Frame(item_frame, bg=self.colors['bg'])
        info_container.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=3)
        
        # Name and price on same line
        rarity_color = self.get_rarity_color(item['rarity']) if item['rarity'] is not None else '#ffffff'
        rarity_symbol = self.get_rarity_symbol(item['rarity']) if item['rarity'] is not None else ''
        
        name_text = f"{item['name']} {rarity_symbol}"
        name_label = tk.Label(info_container, text=name_text,
                             bg=self.colors['bg'], fg=rarity_color,
                             font=('Segoe UI', 9, 'bold'), anchor='w')
        name_label.pack(side=tk.LEFT)
        
        price_label = tk.Label(info_container, text=f"💰 {price}", 
                              bg=self.colors['bg'], fg=self.colors['success'],
                              font=('Segoe UI', 9), anchor='w')
        price_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Description on second line - smaller font
        if item['description'] and len(item['description']) > 0:
            desc_label = tk.Label(info_container, text=item['description'][:80] + ('...' if len(item['description']) > 80 else ''),
                                 bg=self.colors['bg'], fg='#888888',
                                 font=('Segoe UI', 7), anchor='w')
            desc_label.pack(side=tk.LEFT, padx=(5, 0))


if __name__ == "__main__":
    root = tk.Tk()
    app = ModernShopScannerGUI(root)
    root.mainloop()