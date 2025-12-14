import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf


class PortfolioSelectorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Portfolio Selector")
        self.root.geometry("900x600")
        
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5, font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))

        self.selected_tickers = []
        self.selected_weights = []

        # Predefined portfolios
        self.predefined_portfolios = {
            "All Weather (Ray Dalio)": {
                "TLT": 0.40,    
                "SPY": 0.30,    
                "IEF": 0.15,    
                "GLD": 0.075,   
                "DBC": 0.075,  
            },
            "60/40 Portfolio": {
                "SPY": 0.60,    
                "AGG": 0.40,    
            },
            "Permanent Portfolio": {
                "SPY": 0.25, 
                "TLT": 0.25,    
                "GLD": 0.25,    
                "SHY": 0.25,    
            },
            "Three Fund Portfolio": {
                "VTI": 0.50,    
                "VXUS": 0.30,   
                "BND": 0.20,    
            }
        }

        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        left_frame = ttk.LabelFrame(main_container, text="Ticker Selection", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        right_frame = ttk.LabelFrame(main_container, text="Your Portfolio", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        predefined_frame = ttk.LabelFrame(left_frame, text="Predefined Portfolios", padding="10")
        predefined_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(predefined_frame, text="Select Portfolio:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.portfolio_var = tk.StringVar()
        portfolio_combo = ttk.Combobox(predefined_frame, textvariable=self.portfolio_var, 
                                      values=list(self.predefined_portfolios.keys()), 
                                      state="readonly", width=20)
        portfolio_combo.pack(side=tk.LEFT, padx=(0, 5))
        portfolio_combo.bind('<<ComboboxSelected>>', self.on_portfolio_select)
        
        ttk.Button(predefined_frame, text="Load Portfolio", 
                  command=self.load_predefined_portfolio).pack(side=tk.LEFT)
        
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search Ticker:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.bind('<Return>', lambda e: self.search_ticker())
        
        ttk.Button(search_frame, text="Search", command=self.search_ticker).pack(side=tk.LEFT, padx=(0, 10))
        
        quick_frame = ttk.Frame(left_frame)
        quick_frame.pack(fill=tk.X, pady=(0, 10))
        
        ttk.Label(quick_frame, text="Quick add:").pack(side=tk.LEFT, padx=(0, 5))
        
        popular_tickers = [
            'AAPL', 'MSFT', 'SPY', 'QQQ',  
            'TLT', 'AGG', 'BND', 'IEF',   
            'GLD', 'SLV', 'DBC'            
        ]
        for ticker in popular_tickers:
            btn = ttk.Button(quick_frame, text=ticker, width=5, 
                           command=lambda t=ticker: self.quick_add_ticker(t))
            btn.pack(side=tk.LEFT, padx=2)

        results_frame = ttk.Frame(left_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.results_list = tk.Listbox(results_frame, width=35, height=10)
        self.results_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_list.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_list.config(yscrollcommand=results_scrollbar.set)
        
        self.results_list.bind('<Double-Button-1>', lambda e: self.add_ticker())

        add_button_frame = ttk.Frame(left_frame)
        add_button_frame.pack(fill=tk.X)
        
        ttk.Button(add_button_frame, text="Add Selected Ticker", command=self.add_ticker).pack(pady=5)

        portfolio_list_frame = ttk.Frame(right_frame)
        portfolio_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.portfolio_list = tk.Listbox(portfolio_list_frame, width=40, height=12)
        self.portfolio_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        portfolio_scrollbar = ttk.Scrollbar(portfolio_list_frame, orient=tk.VERTICAL, command=self.portfolio_list.yview)
        portfolio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.portfolio_list.config(yscrollcommand=portfolio_scrollbar.set)

        weight_frame = ttk.Frame(right_frame)
        weight_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(weight_frame, text="Weight for selected:").pack(side=tk.LEFT, padx=(0, 5))
        self.weight_entry = ttk.Entry(weight_frame, width=10)
        self.weight_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.weight_entry.bind('<Return>', lambda e: self.set_weight())
        
        ttk.Button(weight_frame, text="Set Weight", command=self.set_weight).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(weight_frame, text="Auto Balance", command=self.auto_balance).pack(side=tk.LEFT)

        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="Remove Selected", command=self.remove_ticker).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Clear All", command=self.clear_portfolio).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Confirm Portfolio", command=self.confirm).pack(side=tk.RIGHT)

        tips_frame = ttk.Frame(left_frame)
        tips_frame.pack(fill=tk.X, pady=(10, 0))
        
        tips_text = "Tip: Use predefined portfolios or search for tickers (stocks: AAPL, bonds: TLT, commodities: GLD)"
        tip_label = ttk.Label(tips_frame, text=tips_text, font=('Arial', 9), foreground='gray', wraplength=400)
        tip_label.pack()

        asset_info_frame = ttk.Frame(right_frame)
        asset_info_frame.pack(fill=tk.X, pady=(10, 0))
        
        asset_info = "Asset Types: SPY(Stocks), TLT(Bonds), GLD(Gold), DBC(Commodities)"
        asset_label = ttk.Label(asset_info_frame, text=asset_info, font=('Arial', 9), foreground='blue', wraplength=400)
        asset_label.pack()

        self.root.mainloop()

    def on_portfolio_select(self, event):
        """When a predefined portfolio is selected from dropdown"""
        portfolio_name = self.portfolio_var.get()
        if portfolio_name:
            portfolio = self.predefined_portfolios[portfolio_name]
            composition_text = f"{portfolio_name}:\n"
            for ticker, weight in portfolio.items():
                composition_text += f"  {ticker}: {weight:.1%}\n"

    def load_predefined_portfolio(self):
        """Load the selected predefined portfolio"""
        portfolio_name = self.portfolio_var.get()
        if not portfolio_name:
            messagebox.showwarning("Warning", "Please select a portfolio first.")
            return

        if self.selected_tickers and not messagebox.askyesno("Confirm", "This will replace your current portfolio. Continue?"):
            return

        self.portfolio_list.delete(0, tk.END)
        self.selected_tickers.clear()
        self.selected_weights.clear()

        portfolio = self.predefined_portfolios[portfolio_name]
        for ticker, weight in portfolio.items():
            self.selected_tickers.append(ticker)
            self.selected_weights.append(weight)
            self.portfolio_list.insert(tk.END, f"{ticker} — weight: {weight:.1%}")

        messagebox.showinfo("Success", f"Loaded {portfolio_name} portfolio")

    def auto_balance(self):
        """Automatically balance weights equally"""
        if not self.selected_tickers:
            messagebox.showerror("Error", "No tickers in portfolio.")
            return

        equal_weight = 1.0 / len(self.selected_tickers)
        self.selected_weights = [equal_weight] * len(self.selected_tickers)
        
        self.portfolio_list.delete(0, tk.END)
        for i, ticker in enumerate(self.selected_tickers):
            self.portfolio_list.insert(tk.END, f"{ticker} — weight: {equal_weight:.1%}")

        messagebox.showinfo("Success", f"Balanced portfolio with equal weights")

    def quick_add_ticker(self, ticker):
        """Quickly add a popular ticker without searching"""
        self.search_entry.delete(0, tk.END)
        self.search_entry.insert(0, ticker)
        self.search_ticker()
        self.root.after(100, self.add_ticker)

    def search_ticker(self):
        query = self.search_entry.get().upper().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a ticker symbol.")
            return

        try:
            ticker = yf.Ticker(query)
            info = ticker.info
            name = info.get("longName", "Unknown Company")
            sector = info.get("sector", "N/A")
            current_price = info.get("currentPrice", info.get("regularMarketPrice", "N/A"))
            
            self.results_list.delete(0, tk.END)
            self.results_list.insert(tk.END, f"{query} — {name}")
            self.results_list.insert(tk.END, f"Sector: {sector}")
            if current_price != "N/A":
                self.results_list.insert(tk.END, f"Current Price: ${current_price:.2f}")
            else:
                self.results_list.insert(tk.END, "Current Price: N/A")
            self.results_list.insert(tk.END, "---")
            self.results_list.insert(tk.END, "Double-click or use button to add")
        except Exception as e:
            messagebox.showerror("Error", f"Ticker '{query}' not found or error: {str(e)}")

    def add_ticker(self):
        selection = self.results_list.get(0)
        if selection and "—" in selection:
            ticker = selection.split("—")[0].strip()
            if ticker in self.selected_tickers:
                messagebox.showwarning("Warning", f"Ticker {ticker} is already in your portfolio.")
                return
                
            self.selected_tickers.append(ticker)
            self.selected_weights.append(None)
            self.portfolio_list.insert(tk.END, f"{ticker} — weight: NOT SET")
            self.weight_entry.delete(0, tk.END)
            self.weight_entry.focus()
        else:
            messagebox.showwarning("Warning", "Please search for a valid ticker first.")

    def remove_ticker(self):
        selection = self.portfolio_list.curselection()
        if selection:
            idx = selection[0]
            ticker = self.selected_tickers[idx]
            self.portfolio_list.delete(idx)
            self.selected_tickers.pop(idx)
            self.selected_weights.pop(idx)
        else:
            messagebox.showwarning("Warning", "Please select a ticker to remove.")

    def clear_portfolio(self):
        if self.selected_tickers and messagebox.askyesno("Confirm", "Are you sure you want to clear the entire portfolio?"):
            self.portfolio_list.delete(0, tk.END)
            self.selected_tickers.clear()
            self.selected_weights.clear()

    def set_weight(self):
        if not self.selected_tickers:
            messagebox.showerror("Error", "Add a ticker first.")
            return

        try:
            weight = float(self.weight_entry.get())
            if weight <= 0:
                messagebox.showerror("Error", "Weight must be a positive number.")
                return
        except ValueError:
            messagebox.showerror("Error", "Weight must be a number.")
            return

        selection = self.portfolio_list.curselection()
        if selection:
            idx = selection[0]
        else:
            idx = len(self.selected_weights) - 1

        self.selected_weights[idx] = weight

        t = self.selected_tickers[idx]
        self.portfolio_list.delete(idx)
        self.portfolio_list.insert(idx, f"{t} — weight: {weight:.2f}")

    def confirm(self):
        if not self.selected_tickers:
            messagebox.showerror("Error", "Portfolio is empty. Add at least one ticker.")
            return
            
        if None in self.selected_weights:
            messagebox.showerror("Error", "Set all weights before confirming.")
            return

        total = sum(self.selected_weights)
        if total <= 0:
            messagebox.showerror("Error", "Total weight must be positive.")
            return
            
        self.selected_weights = [w / total for w in self.selected_weights]

        portfolio_summary = "Portfolio confirmed:\n"
        for i, (ticker, weight) in enumerate(zip(self.selected_tickers, self.selected_weights)):
            portfolio_summary += f"{ticker}: {weight:.2%}\n"
        
        messagebox.showinfo("Portfolio Confirmed", portfolio_summary)
        self.root.destroy()


def select_portfolio_gui():
    gui = PortfolioSelectorGUI()
    return gui.selected_tickers, gui.selected_weights