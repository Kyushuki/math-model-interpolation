import matplotlib.pyplot as plt
import os
import numpy as np
from sympy import symbols, Eq, solve
from tkinter.messagebox import showerror
from pandas import read_csv as pd
from matplotlib.widgets import TextBox, Button, RadioButtons
from scipy.interpolate import CubicSpline

# расположение всего в окне 
fig, ax = plt.subplots()
fig.subplots_adjust(right=0.85, left= 0.1)
axbox = fig.add_axes([0.1, 0.02, 0.2, 0.04])
axbutton = fig.add_axes([0.82, 0.02, 0.1, 0.04])
axradioMode = fig.add_axes([0.87, 0.65, 0.09, 0.1])
axradioI = fig.add_axes([0.87, 0.78, 0.09, 0.1])

# основы графика
x = [0,1]
y = [1,0]
l = ax.scatter(x,y)
ax.grid()
mode = 0

# экземпляры элементов интерфейса
text = TextBox(axbox, 'csv-file',textalignment="center")
button = Button(axbutton, 'clear')
radioB_mode = RadioButtons(axradioMode, ('one','a lot'))
radioB_Inter = RadioButtons(axradioI, ('к-линейная','к-парабол','Лагранж','Кубик-сплайн'))


# класс графика
class Graph:
    def __init__(self) -> None:
        self.x = []
        self.y = []
    def function_to_ndarray(self,function, x):
        return np.fromiter((function(value) for value in x), dtype=float, count=len(x))
    # метод draw рисует график
    def draw(self, x, y):
        self.x = x
        self.y = y
        self.x, self.y = self.sort(self.x,self.y)
        ax.scatter(self.x,self.y,marker='x')
        ax.grid()
        plt.draw()
    def sort(self, x,y):
        l = []
        for i in range(len(x)):
            l.append((x[i],y[i]))
        l.sort(key=lambda x: x)
        X = []
        Y = []
        for item in l:
            X.append(item[0])
            Y.append(item[1])
        return X,Y
    # кусочно-линейная
    def linar(self):
        x = self.x
        y = self.y

        for i in range(1,len(x)):
            a = ((y[i]-y[i-1])/(x[i]-x[i-1]))
            b = y[i-1] - a*x[i-1]
            X = np.linspace(x[i-1],x[i])
            Y = a * X + b
            ax.plot(X, Y)
    # методом Лагранжа
    def Lagranj(self):
        x = self.x
        y = self.y
        # считает базу 
        def base(x_val,i):
            def basic(x):
                div = 1
                res = 1
                for j in range(len(x_val)):
                    if i != j:
                        res = np.multiply(res, (x - x_val[j]), dtype=object)
                        div = np.multiply(div,(x_val[i]-x_val[j]), dtype=object)
                return np.divide(res,div, dtype=object)
            return basic
        # умножает y на базу
        def Lagr(x_val, y_val):
            polynoms = []
            for i in range(len(x_val)):
                polynoms.append(base(x_val,i))
            def lagr_poly(x):
                r = 0
                for i in range(len(y_val)):
                    r += np.multiply(y_val[i],polynoms[i](x),dtype=object)
                return r
            return lagr_poly
        X =np.linspace(min(x),max(x))
        Y = Lagr(x,y)
        ax.plot(X, Y(X))
    # кусочно-параболическая
    def parabolic(self):
        x = self.x
        y = self.y

        Y = []
        a, b, c = symbols('a b c')
        for i in range(1,len(x)-1):
            system_eq = [Eq(a*x[i-1]**2 + b*x[i-1] + c, y[i-1]), Eq(a*x[i]**2 + b*x[i] + c, y[i]), Eq(a*x[i+1]**2 + b*x[i+1] + c, y[i+1])]
            solution = solve(system_eq)
            X = np.linspace(x[i], x[i+1])
            Y = self.function_to_ndarray(lambda X: solution.get(a)*(X**2) + solution.get(b)*X + solution.get(c), X)
            ax.plot(X, Y)
    # кубическая сплайн
    def Cubic(self):
        x = self.x
        y = self.y

        c = CubicSpline(x,y)
        X = np.linspace(min(x),max(x))
        ax.plot(X, c(X))

# класс для работы с интерфейсом 
class InterFace:
    def __init__(self) -> None:
        self.graph = Graph() # экземпляр класса графика
        self.f = 0 # сюда помещается файлик csv

    # очищает график от всего
    def clear(self, event):
        ax.cla()
        plt.draw()
        

    def RadioB_Mode(self, label):
        global mode
        if label == 'one':
            mode = 0
        else:
            mode = 1
    def RadioB_I(self, label):
        ax.grid()
        if mode == 0:
            ax.cla()
        x = self.f['x']
        y = self.f['y']
        self.graph.draw(x,y)
        match label:
            case 'к-линейная':
                self.graph.linar()
            case 'к-парабол':
                self.graph.parabolic()
            case 'Лагранж':
                self.graph.Lagranj()
            case 'Кубик-сплайн':
                self.graph.Cubic()
                
    # загружает и выводит на экран график из файла
    def sumbit(self, expression):
        global mode
        ax.grid()
        ext = os.path.splitext(expression)[-1]
        if ext == ".csv":
            try:
                self.f = pd(expression)
            except FileNotFoundError:
                showerror('Ошибка', 'Нет такого файла')
            else:
                if mode == 0:
                    ax.cla()
                # сортировка точек от меньшего к большему по оси X 
                x = self.f['x']
                y = self.f['y']
                self.graph.draw(x, y) 
                inter = radioB_Inter.value_selected
                match inter:
                    case 'к-линейная':
                        self.graph.linar()
                    case 'к-парабол':
                        self.graph.parabolic()
                    case 'Лагранж':
                        self.graph.Lagranj()
                    case 'Кубик-сплайн':
                        self.graph.Cubic()
                
        else:
            showerror('Ошибка', 'Не правильное расширение файла')

inter = InterFace() # экземпляр логики интерфейса

#соединение интерфейса с логикой его работы
text.on_submit(inter.sumbit)
button.on_clicked(inter.clear)
radioB_mode.on_clicked(inter.RadioB_Mode)
radioB_Inter.on_clicked(inter.RadioB_I)
plt.show()
