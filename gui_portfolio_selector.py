import tkinter as tk
from tkinter import ttk, messagebox
import yfinance as yf


class PortfolioSelectorGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Portfolio Selector")
        self.root.geometry("800x500")
        
        # Configure style for better appearance
        self.style = ttk.Style()
        self.style.configure('TButton', padding=5, font=('Arial', 10))
        self.style.configure('TLabel', font=('Arial', 10))
        self.style.configure('TEntry', font=('Arial', 10))

        self.selected_tickers = []
        self.selected_weights = []

        # Create main frames for horizontal layout
        main_container = ttk.Frame(self.root, padding="10")
        main_container.pack(fill=tk.BOTH, expand=True)

        # Left frame for search and results
        left_frame = ttk.LabelFrame(main_container, text="Ticker Selection", padding="10")
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 5))

        # Right frame for portfolio
        right_frame = ttk.LabelFrame(main_container, text="Your Portfolio", padding="10")
        right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True, padx=(5, 0))

        # ------ Search Section ------
        search_frame = ttk.Frame(left_frame)
        search_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(search_frame, text="Search Ticker:").pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry = ttk.Entry(search_frame, width=20)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.search_entry.bind('<Return>', lambda e: self.search_ticker())
        
        ttk.Button(search_frame, text="Search", command=self.search_ticker).pack(side=tk.LEFT)

        # ------ Search Results ------
        results_frame = ttk.Frame(left_frame)
        results_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.results_list = tk.Listbox(results_frame, width=30, height=15)
        self.results_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        results_scrollbar = ttk.Scrollbar(results_frame, orient=tk.VERTICAL, command=self.results_list.yview)
        results_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.results_list.config(yscrollcommand=results_scrollbar.set)

        # Add button frame
        add_button_frame = ttk.Frame(left_frame)
        add_button_frame.pack(fill=tk.X)
        
        ttk.Button(add_button_frame, text="Add Selected Ticker", command=self.add_ticker).pack(pady=5)

        # ------ Portfolio List ------
        portfolio_list_frame = ttk.Frame(right_frame)
        portfolio_list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 10))

        self.portfolio_list = tk.Listbox(portfolio_list_frame, width=35, height=15)
        self.portfolio_list.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        portfolio_scrollbar = ttk.Scrollbar(portfolio_list_frame, orient=tk.VERTICAL, command=self.portfolio_list.yview)
        portfolio_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.portfolio_list.config(yscrollcommand=portfolio_scrollbar.set)

        # ------ Weight Entry ------
        weight_frame = ttk.Frame(right_frame)
        weight_frame.pack(fill=tk.X, pady=(0, 10))

        ttk.Label(weight_frame, text="Weight for last ticker:").pack(side=tk.LEFT, padx=(0, 5))
        self.weight_entry = ttk.Entry(weight_frame, width=10)
        self.weight_entry.pack(side=tk.LEFT, padx=(0, 5))
        self.weight_entry.bind('<Return>', lambda e: self.set_weight())
        
        ttk.Button(weight_frame, text="Set Weight", command=self.set_weight).pack(side=tk.LEFT)

        # ------ Control Buttons ------
        control_frame = ttk.Frame(right_frame)
        control_frame.pack(fill=tk.X)

        ttk.Button(control_frame, text="Remove Selected", command=self.remove_ticker).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Clear All", command=self.clear_portfolio).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(control_frame, text="Confirm Portfolio", command=self.confirm).pack(side=tk.RIGHT)

        # To block program until user closes
        self.root.mainloop()

    def search_ticker(self):
        query = self.search_entry.get().upper().strip()
        if not query:
            messagebox.showwarning("Warning", "Please enter a ticker symbol.")
            return

        try:
            ticker = yf.Ticker(query)
            info = ticker.info
            # If "longName" exists, it's a valid ticker
            name = info.get("longName", "Unknown Company")
            sector = info.get("sector", "N/A")
            self.results_list.delete(0, tk.END)
            self.results_list.insert(tk.END, f"{query} — {name}")
            self.results_list.insert(tk.END, f"Sector: {sector}")
            self.results_list.insert(tk.END, "---")
        except Exception as e:
            messagebox.showerror("Error", f"Ticker not found or error: {str(e)}")

    def add_ticker(self):
        selection = self.results_list.get(0)  # Get first item which should be the ticker line
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
            self.portfolio_list.delete(idx)
            self.selected_tickers.pop(idx)
            self.selected_weights.pop(idx)
        else:
            messagebox.showwarning("Warning", "Please select a ticker to remove.")

    def clear_portfolio(self):
        if messagebox.askyesno("Confirm", "Are you sure you want to clear the entire portfolio?"):
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
            
        # Normalize weights to sum to 1
        self.selected_weights = [w / total for w in self.selected_weights]

        # Show confirmation
        portfolio_summary = "Portfolio confirmed:\n"
        for i, (ticker, weight) in enumerate(zip(self.selected_tickers, self.selected_weights)):
            portfolio_summary += f"{ticker}: {weight:.2%}\n"
        
        messagebox.showinfo("Portfolio Confirmed", portfolio_summary)
        self.root.destroy()


def select_portfolio_gui():
    gui = PortfolioSelectorGUI()
    return gui.selected_tickers, gui.selected_weights