import tkinter
import subprocess
import json
from functools import partial
from tkinter import simpledialog, ttk, messagebox 
import socket
import os
import requests
"""
Add close button to reports
pip3 download support
"""
scriptdir = os.path.dirname(os.path.abspath(__file__))+"/"
pmmgui = None
fmod = {}

class CreateToolTip(object):
    """
    create a tooltip for a given widget
    """
    def __init__(self, widget, text='widget info'):
        self.waittime = 500     #miliseconds
        self.wraplength = 180   #pixels
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.leave)
        self.widget.bind("<ButtonPress>", self.leave)
        self.id = None
        self.tw = None
		
    def enter(self, event=None):
        self.schedule()

    def leave(self, event=None):
        self.unschedule()
        self.hidetip()

    def schedule(self):
        self.unschedule()
        self.id = self.widget.after(self.waittime, self.showtip)

    def unschedule(self):
        id = self.id
        self.id = None
        if id:
            self.widget.after_cancel(id)

    def showtip(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20
        # creates a toplevel window
        self.tw = tkinter.Toplevel(self.widget)
        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = tkinter.Label(self.tw, text=self.text, justify='left',
                       background="#ffffff", relief='solid', borderwidth=1,
                       wraplength = self.wraplength)
        label.pack(ipadx=1)

    def hidetip(self):
        tw = self.tw
        self.tw= None
        if tw:
            tw.destroy()
     
    def __str__(self):
        return "CreateToolTip"
	
def internet(host="8.8.8.8", port=53, timeout=3):
	try:
		socket.setdefaulttimeout(timeout)
		socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
		return True
	except Exception as ex:
		print( ex)
		return False

def build_package_dict(output):
	global fmod
	lines = output.split("\n")
	modules_outdated = lines[2:]
	fmod = {}
	i = 0
	for item in modules_outdated:
		f = item.split(" ")
		m = []
		i += 1
		for fi in f:
			if fi:
				m.append(fi)
		if len(m) > 0:
			fmod[i] = m
	return fmod

def get_modules(host):
	debug = False
	if debug:
		output = """ Package    Version
								---------- ---------
								certifi    2018.4.16
								psutil     5.4.6
								pycairo    1.17.0
								PyQt5-sip  4.19.11
								setuptools 39.2.0
						 """
	else:
		res = subprocess.run([host.pip, "list"], stdout=subprocess.PIPE)
		output = str(res.stdout,"latin-1")
	data = build_package_dict(output)
	host.modules.delete(0, tkinter.END)
	for item in data:
		host.modules.insert(tkinter.END, data[item][0])
	print(data)
	host.b_update.config(state="disabled")
	host.b_uninstall.config(state="normal")
	
def get_updates(host):
	debug = False
	if debug:
		output = """Package    Version   Latest    Type 
								---------- --------- --------- -----
								certifi    2018.4.16 2018.8.24 wheel
								psutil     5.4.6     5.4.7     sdist
								pycairo    1.17.0    1.17.1    sdist
								PyQt5-sip  4.19.11   4.19.12   wheel
								setuptools 39.2.0    40.2.0    wheel
						 """
	else:
		res = subprocess.run([host.pip, "list", "--outdated"], stdout=subprocess.PIPE)
		output = str(res.stdout,"latin-1")
	data = build_package_dict(output)
	host.modules.delete(0, tkinter.END)
	if len(data) > 0:
		for item in data:
			host.modules.insert(tkinter.END, data[item][0])
		print(data)
		host.b_update.config(state="normal")
		host.b_uninstall.config(state="normal")
		tkinter.messagebox.showinfo(title="Result", message=f"{len(data)} updates found!")
	else:
		pmmgui.infolab.config(text="No updates found!")
		tkinter.messagebox.showinfo(title="Result", message=f"No updates found!")
	
def getConfig():
	with open("config.json") as f:
		return json.load(f)

def setConfig(key:str, value):
	data = getConfig()
	data[key] = value
	with open('config.json', "w") as s:
		json.dump(data, s, indent=4, sort_keys=True)

def dumpConfig(data):
	with open('config.json', "w") as s:
		json.dump(data, s, indent=4, sort_keys=True)

def boolinate(string):
	try:
		truth = ['true', '1', 'yes', 'on']
		if string.lower() in truth:
			return True
		else:
			return False
	except:
		return string

def install_module(module):
    modules = module.get().split(",")  # Split the input into individual module names
    
    results = []  # List to store installation results for each module
    
    for mod in modules:
        print("will install " + mod.strip())  # Strip any leading or trailing whitespace
        
        if pmmgui.usermode:
            res = subprocess.run([pmmgui.pip, "install", "--user", mod.strip()], stdout=subprocess.PIPE)
        else:
            res = subprocess.run([pmmgui.pip, "install", mod.strip()], stdout=subprocess.PIPE)
        
        output = str(res.stdout, "latin-1")
        results.append((mod.strip(), output))  # Append the result for each module
    
    # Generate a message with installation results for all modules
    message = "\n\n".join([f"Module: {mod}\nResult: {output}" for mod, output in results])
    
    tkinter.messagebox.showinfo(title="Batch Installation Result", message=message)


def search_module(module):
    print("will search " + module.get())
    
    search_url = f"https://pypi.org/pypi/{module.get()}/json"
    try:
        response = requests.get(search_url)
        response.raise_for_status()
        data = response.json()
        
        if "info" in data:
            info = data["info"]
            result_text = f"Author: {info['author']}\n"
            result_text += f"Description: {info['description']}\n"
            result_text += "Classifiers:\n"
            result_text += "\n".join(info['classifiers']) + "\n"
            
            display_search_result(result_text, module)
        else:
            display_search_result("No information found for the specified module.")
    except Exception as e:
        display_search_result(f"Error: {str(e)}")

def display_search_result(result_text, module):
    def on_configure(event):
        # Update the size of the list box to match the window size
        list_result.configure(width=event.width // 10, height=event.height // 20)
    
    root = tkinter.Tk()
    root.title(f"Search Result for {module.get()}")
    root.geometry("1250x560")  # Set the main window size to 1250x560

    scrollbar = tkinter.Scrollbar(root, orient=tkinter.VERTICAL)
    list_result = tkinter.Listbox(root, yscrollcommand=scrollbar.set, bg="#272A37", fg="#FFFFFF", selectbackground="#525561", selectforeground="#FFFFFF", font=("Courier", 12), relief="flat")
    scrollbar.config(command=list_result.yview)
    scrollbar.pack(side=tkinter.RIGHT, fill=tkinter.Y)
    list_result.pack(side=tkinter.LEFT, fill=tkinter.BOTH, expand=True)

    # Bind the <Configure> event of the root window to the on_configure function
    root.bind("<Configure>", on_configure)

    # Insert the result_text into the list box
    lines = result_text.split("\n")
    for line in lines:
        list_result.insert(tkinter.END, line)
    
    root.mainloop()

def install():
    w = tkinter.Tk()
    w.geometry("300x200+200+200")  # Set window geometry
    w.configure(bg="#272A37")  # Set background color
    w.resizable(False, False)  # Make window unresizable
    en = tkinter.Entry(w)
    run_inst = partial(install_module, en)
    run_srch = partial(search_module, en)
    
    label_text = "Python Package Installer"
    label = ttk.Label(w, text=label_text, background="#272A37", foreground="#FFFFFF", font=("Courier", 12))  # Set label text color and background color
    
    b = ttk.Button(w, text="Install", command=run_inst, cursor="hand1")
    sr = ttk.Button(w, text="Search", command=run_srch, cursor="hand1")
    
    en.place(relx=0.5, rely=0.3, anchor="center")  # Place the entry widget at the center horizontally and 30% from the top vertically
    label.place(relx=0.5, rely=0.1, anchor="center")  # Place the label at the center horizontally and 10% from the top vertically
    b.place(relx=0.3, rely=0.7, anchor="center")  # Place the Install button at 30% from the left horizontally and 70% from the top vertically
    sr.place(relx=0.7, rely=0.7, anchor="center")  # Place the Search button at 70% from the left horizontally and 70% from the top vertically
    
    w.title("Installer")
    w.mainloop()

def uninstall():
    selected_indices = pmmgui.modules.curselection()  # Get indices of selected items
    if not selected_indices:  # If no item is selected
        return

    modules_to_uninstall = []  # List to store modules to be uninstalled

    # Iterate over selected indices to get module names
    for index in selected_indices:
        module_info = fmod[index + 1]  # Assuming fmod is a list of module information
        modules_to_uninstall.append(module_info)

    # Confirmation message for batch uninstallation
    confirmation_message = "\n".join([f"{module[0]} {module[1]} will be COMPLETELY uninstalled." for module in modules_to_uninstall])
    if tkinter.messagebox.askokcancel(title="Batch Uninstall", message=confirmation_message):
        for module_info in modules_to_uninstall:
            module_name = module_info[0]
            res = subprocess.run([pmmgui.pip, "uninstall", "-y", module_name], stdout=subprocess.PIPE)
            output = str(res.stdout, "latin-1")
            # Update GUI to reflect uninstallation
            pmmgui.modules.delete(pmmgui.modules.get(0, "end").index(module_name))
            # Display result in a separate window
            r = tkinter.Tk()
            lb = tkinter.Label(r, text=output)
            lb.grid()
            r.title("Result")
            r.mainloop()

def update():
    selected_index = pmmgui.modules.curselection()
    if selected_index:  # Check if any item is selected
        mod = selected_index[0]  # Get the index of the selected item
        mod += 1
        print(fmod[mod][0])
        if tkinter.messagebox.askokcancel(title=f"Update {fmod[mod][0]}", message=f"{fmod[mod][0]} will be updated from {fmod[mod][1]} to {fmod[mod][2]}"):
            if pmmgui.usermode:
                res = subprocess.run([pmmgui.pip, "install", "--upgrade", fmod[mod][0]], stdout=subprocess.PIPE)
            else:
                res = subprocess.run([pmmgui.pip, "install", "--upgrade", "--user", fmod[mod][0]], stdout=subprocess.PIPE)
            output = str(res.stdout,"latin-1")
            pmmgui.modules.delete(mod-1)
            r = tkinter.Tk()
            lb = tkinter.Label(r, text=output, justify="left")
            lb.grid()
            r.title("Result")
            r.mainloop()
    else:
        tkinter.messagebox.showwarning("No Selection", "Please select a module to update.")
		
def onselect(evt):
	w = evt.widget
	try:
		index = int(w.curselection()[0])
	except IndexError:
		return
	index += 1
	# value = w.get(index)
	try:
		pmmgui.infolab.config(text=fmod[index][0]+" - Current Version: "+fmod[index][1]+" - PIP Version: "+fmod[index][2])
	except:
		pmmgui.infolab.config(text=fmod[index][0]+" "+fmod[index][1])		

def reconnect():
	if internet():
		pmmgui.b_updatecheck.config(state="normal")
		pmmgui.b_install.config(state="normal")
		pmmgui.b_rec.destroy()
		pmmgui.online = True
		pmmgui.infolab.config(text="Reconnected to network!")
	else:
		tkinter.messagebox.showerror(title="No network connection", message="No internet connection was found.\nPMM will run in offline mode. (No update checking.)")	

def pipcheck():
	res = subprocess.run([pmmgui.pip, "check"], stdout=subprocess.PIPE)
	output = str(res.stdout,"latin-1")	
	r = tkinter.Tk()
	r.resizable(False, False)
	lb = tkinter.Label(r, text=output, justify="left", background="#272A37", foreground="#FFFFFF", font=("Courier", 12))
	lb.grid()
	r.title("Result")
	r.mainloop()
	
def pipshow():
	try:
		mod = pmmgui.modules.curselection()[0]
	except IndexError:
		tkinter.messagebox.showerror(title="Error", message="No package selected.")
		return
	mod += 1
	res = subprocess.run([pmmgui.pip, "show", fmod[mod][0]], stdout=subprocess.PIPE)
	output = str(res.stdout,"latin-1")
	r = tkinter.Tk()
	r.resizable(False, False)
	lb = tkinter.Label(r, text=output, justify="left", background="#272A37", foreground="#FFFFFF", font=("Courier", 12))
	lb.grid()
	r.title("Result")
	r.mainloop()
		
def about():
	tkinter.messagebox.showinfo(title="About PMM", message="PMM (Python Module Manager) is a versatile tool designed to simplify the management of Python modules. With PMM, users can effortlessly install, uninstall, update, and search for Python packages with ease. PMM offers a user-friendly interface and provides convenient features such as batch operations and dependency resolution.\n\nSource Code: https://github.com/Rudransh0110/Python-Module-Manager\n\nVersion: 1.0.0\n\nLicensed under the MIT License.")

def package_statistics():
	total_packages = "N/A"
	total_outdated_packages = "N/A"

	# Calculate total number of Python packages
	try:
		res = subprocess.run(["pip", "list"], stdout=subprocess.PIPE, text=True)
		output = res.stdout
		packages = output.strip().split("\n")[2:]  # Skip the first two lines which contain headers
		total_packages = len(packages)
	except Exception as e:
		print("Error:", e)

	# Calculate total number of outdated packages
	try:
		res = subprocess.run(["pip", "list", "--outdated"], stdout=subprocess.PIPE, text=True)
		output = res.stdout
		outdated_packages = output.strip().split("\n")[2:]  # Skip the first two lines which contain headers
		total_outdated_packages = len(outdated_packages)
	except Exception as e:
		print("Error:", e)

	root = tkinter.Tk()
	root.title("Package Statistics")
	root.configure(bg="#272A37")
	root.grid_location(0, 0)

	label_total_packages = tkinter.Label(root, text=f"Total Packages: {total_packages}", font=("Courier", 12), bg="#272A37", fg="#FFFFFF")
	label_total_packages.grid(row=1, column=1,padx=30, pady=10)

	label_total_outdated_packages = tkinter.Label(root, text=f"Total Outdated Packages: {total_outdated_packages}", font=("Courier", 12), bg="#272A37", fg="#FFFFFF")
	label_total_outdated_packages.grid(row=2, column=1, padx=30, pady=10)
	root.mainloop()

class pipGuiMain:
	def __init__(self):
		self.online = internet()
		self.config = getConfig()
		self.pip = self.config['pip_command']
		self.update_check_on_start = boolinate(self.config['auto_update_check'])
		self.usermode = boolinate(self.config['add_user_flag'])
		self.mainwin = tkinter.Tk()
		self.mainwin.resizable(False, False)
		self.mainwin.title("Python Module Manager")
		self.mainwin.geometry("800x400+200+200")
		self.mainwin.configure(bg="#272A37")
		self.modules = tkinter.Listbox(self.mainwin, justify="left", takefocus=20, height=15, bg="#272A37", fg="#FFFFFF", selectbackground="#525561", selectforeground="#FFFFFF", width=30, font=("Courier", 12), relief="flat", selectmode=tkinter.MULTIPLE)
		self.modules.grid(rowspan=6, columnspan=4,  padx=50, pady=25, sticky="nsew")

		self.modules.bind('<<ListboxSelect>>', onselect)
		ub = partial(get_updates, self)
		ubi = partial(get_modules, self)
		self.infolab = tkinter.Label(self.mainwin, text="Selected info will appear here.")
		self.infolab.grid(row=6, columnspan=4, padx=50, pady=5, sticky="nsew")
		self.chicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'assets\\py.png'))
		self.listicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'assets\\list.png'))
		self.dlicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'assets\\dl.png'))
		self.unicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'assets\\uni.png'))
		self.upicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'assets\\upg.png'))
		self.b_updatecheck = tkinter.Button(self.mainwin, image=self.chicon, compound="left", text="Check for updates", command=ub, cursor="hand1", width=140, anchor="w")
		self.b_listall = tkinter.Button(self.mainwin, text="Show list", image=self.listicon, compound="left", command=ubi, cursor="hand1", width=140, anchor="w")
		self.b_install = tkinter.Button(self.mainwin, image=self.dlicon, compound="left", text="Install...", command=install, cursor="hand1", width=140, anchor="w")
		self.b_uninstall = tkinter.Button(self.mainwin, image=self.unicon, compound="left", text="Uninstall", command=uninstall, state="disabled", cursor="hand1", width=140, anchor="w")
		self.b_update = tkinter.Button(self.mainwin, image=self.upicon, compound="left", text="Update", command=update, state="disabled", cursor="hand1", width=140, anchor="w")
		
		self.b_updatecheck.grid(column=4, row=0)
		CreateToolTip(self.b_updatecheck, "Gets outdated modules list.\nNOTE: Will take a few moments.")
		self.b_listall.grid(column=4, row=1)
		CreateToolTip(self.b_listall, "Gets installed modules list.\nNOTE: Will take a few moments.")
		self.b_install.grid(column=4, row=2)
		CreateToolTip(self.b_install, "Opens the Installer window. Enter a module name to download and install using pip.")
		self.b_uninstall.grid(column=4, row=3)
		CreateToolTip(self.b_uninstall, "Completely uninstalls the module selected in the list.")
		self.b_update.grid(column=4, row=4)
		CreateToolTip(self.b_update, "Updates the selected module in the list.")
		self.mainwin.title("Python Module Manager")
		imgicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'assets\\icon.png'))
		self.mainwin.tk.call('wm', 'iconphoto', self.mainwin, imgicon)  
		self.menu = tkinter.Menu(self.mainwin)
		self.mainwin.config(menu=self.menu)

		self.about_icon = tkinter.PhotoImage(file=os.path.join(scriptdir,"assets\\About-24x24.png"))
		self.check_icon = tkinter.PhotoImage(file=os.path.join(scriptdir,"assets\\Check-24x24.png"))
		self.info_icon = tkinter.PhotoImage(file=os.path.join(scriptdir,"assets\\Info-24x24.png"))
		self.exit_icon = tkinter.PhotoImage(file=os.path.join(scriptdir,"assets\\Exit-24x24.png"))
		self.filemenu = tkinter.Menu(self.mainwin, tearoff=0, bg="#272A37", fg="white",  font=("Courier", 10, "bold"))

		self.menu.add_cascade(label="PMM", menu=self.filemenu)
		self.filemenu.add_command(label="About", image=self.about_icon, compound=tkinter.LEFT, command=about)
		self.filemenu.add_command(label="Check Libraries integrity", image=self.check_icon, compound=tkinter.LEFT, command=pipcheck)
		self.filemenu.add_command(label="Show info on selected package", image=self.info_icon, compound=tkinter.LEFT, command=pipshow)
		self.filemenu.add_command(label="Total packages installed", image=self.listicon, compound=tkinter.LEFT, command=package_statistics)
		self.filemenu.add_separator()
		self.filemenu.add_command(label="Exit", image=self.exit_icon, compound=tkinter.LEFT, command=self.mainwin.destroy)
		#self.filemenu.config(bg="#272A37", fg="#FFFFFF", activebackground="#525561", activeforeground="#FFFFFF", font=("Arial", 10))

		
		if not self.online:
			self.b_updatecheck.config(state="disabled")
			self.b_install.config(state="disabled")
			self.bicon = tkinter.PhotoImage(file=os.path.join(scriptdir,'reset.png'))
			self.b_rec = tkinter.Button(self.mainwin, image=self.bicon, command=reconnect)
			self.b_rec.grid(row=0, column=5)
			CreateToolTip(self.b_rec, "Reconnect to network.")
			self.infolab.config(text="No internet connection was found.\nPMM will run in offline mode. (No update checking.)")
			
		if self.update_check_on_start and self.online:
			get_updates(self)
			
pmmgui = pipGuiMain()	
pmmgui.mainwin.mainloop()
print(pmmgui.pip)