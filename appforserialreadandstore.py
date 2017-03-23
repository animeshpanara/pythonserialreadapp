import serial
import serial.tools.list_ports
import threading
import queue
import tkinter as tk
from string import * 

global txt
class SerialThread(threading.Thread):
    def __init__(self,queue,serial):
        threading.Thread.__init__(self)
        self.queue = queue
        self.ser=serial
    def run(self):
        while True:       
                if self.ser.inWaiting():
                    global txt
                    txt = self.ser.readline(self.ser.inWaiting())
                    self.queue.put(txt)

class App(tk.Tk):
    def __init__(self):
        self.txt2=""
        self.txt1=0
        self.txt1=bytes(self.txt1)
       
        tk.Tk.__init__(self)
        self.geometry("1360x750")
        self.poleparam=[[0 for x in range(0,3)]for j in range(0,7)]
        self.ports=list(serial.tools.list_ports.comports())
        self.currentport=tk.StringVar()
        self.baud=tk.IntVar()
        self.baud.set(38400)
        self.currentport.set("COM3")
        self.option=tk.OptionMenu(self,self.currentport,*self.ports)
        self.option.place(x=30,y=10)
        self.option1=tk.OptionMenu(self,self.baud,1200,2400,4800,9600,19200,38400,)
        self.option1.place(x=30,y=40)
        self.runButton = tk.Button(self, text ="Start", command = self.start,font=("Times",11,"bold italic"),height=1,width=20,bg='red',
                                     foreground='black',padx=0,pady=0,bd=6,relief=tk.SOLID)
        self.runButton.place(x=120,y=40)
        #self.poleparam=bytes(self.poleparam)
        self.var = tk.IntVar()
        self.POLES=[("Pole 1",1,'violet'),("Pole 2",2,'indigo'),("Pole 3",3,'blue'),("Pole 4",4,'green'),("Pole 5",5,'yellow'),("Pole 6",6,'orange'),("Pole 7",7,'red')]
        self.text = tk.Text(self, wrap='word',fg='red', font='TimesNewRoman 25', relief='flat',height=12,width=50)
        self.vsb = tk.Scrollbar(self, orient="vertical", command=self.text.yview)
        self.vsb.pack(side="left", fill="y")
        self.text.configure(yscrollcommand=self.vsb.set)
        self.text.place(x=20,y=100)    
        for txt,pole,color in self.POLES :
            self.radio=tk.Radiobutton(self,text=txt,font=("Times",17,"bold italic"),variable=self.var, value=pole,command=self.sel,height=3,width=30,indicatoron = 0,
                                  selectcolor=color,foreground='white',activeforeground='black',background='black',pady=0)
            self.radio.place(x=950,y=100*(pole-1))
            
        self.storeButton = tk.Button(self, text ="Store", command = self.store,font=("Times",21,"bold italic"),height=2,width=25,bg='yellow',
                                     foreground='red',padx=0,pady=0,bd=6,relief=tk.SOLID)
        self.storeButton.place(x=450,y=600)
        self.label = tk.Label(self,font=("Times",20,"bold italic"),height=3,width=20)
        self.label.place(x=350,y=0)
        self.queue = queue.Queue()
    def start(self) :
        temp=self.currentport.get()
        try:
            curserial = serial.Serial(temp[0:temp.find('-')],self.baud.get(),timeout=0)
            if curserial.isOpen() :
                self.text.delete('1.0','end')
                self.text.insert('insert','Serial port open \n')
                self.runButton.config(state= 'disabled')
        except IOError:
            self.text.insert('insert','Unable to open Serial port')
        thread = SerialThread(self.queue,curserial)
        thread.start()
        self.process_serial()
    def sel(self):
        selection = ("You have selected pole :"+str(self.var.get()))
        self.label.config(text = selection)

    def store(self):
        self.text.insert('end',b'values stored are'+self.txt2+b'\n')
        y=self.txt2.split(b';')
        for x in range(0,3):
            self.poleparam[self.var.get()-1][x]=y[x]
        files=[('rpm',0),('planeangle',1),('throwangle',2)]
        for i,x in files  :
            fo = open(i+".txt","ab")
            fo.write(b'\r\n')
            for j in range(0,7):
                if(self.poleparam[j][x]==0) :
                    fo.write(b'0')
                fo.write(bytes(self.poleparam[j][x]))
                if(j!=6) :fo.write(b',')
                  
            fo.close()
        selection = ("values stored for pole:"+str(self.var.get()))
        self.label.config(text = selection)
    

    def process_serial(self):
        while self.queue.qsize():
            try :
                x=self.queue.get()
                self.text.insert('end',x)
                self.text.see(tk.END)
                start=x.find(b'[')
                self.txt1+=x[start+1:]
                end=self.txt1.find(b'\n')
                self.txt2=self.txt1[:end]
                self.txt1 = self.txt1[end+1:]
            except queue.Empty:
                pass
        self.after(100, self.process_serial)

app = App()
app.mainloop()
