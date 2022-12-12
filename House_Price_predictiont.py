import plotly.graph_objects as go
import kaleido
import os
import plotly.express as px
import plotly.io as pio
from reportlab.platypus import SimpleDocTemplate,Paragraph
from reportlab.lib.styles import getSampleStyleSheet
import plotly.figure_factory as ff
import plotly
import numpy as np
import pandas as pd
import torch
import torch.nn as nn
import sys
import time
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
import torch.utils.data as Data
import tkinter as tk
from tkinter import ttk
from PIL import Image, ImageTk
from tkinter import messagebox
from PyPDF2 import PdfFileMerger

# Import the data of Lianjia and Anjuke
lianjia_df = pd.read_csv('lianjia.csv')
anjuke_df = pd.read_csv('anjuke.csv')
# Drop some useless data columns
lianjia_drop = ['Id','Direction','Elevator','Renovation']
# clean data
lianjia_df_clean = lianjia_df.drop(lianjia_drop,axis=1)
# Reposition the columns
lianjia_df_clean = pd.DataFrame(lianjia_df_clean, columns=['Region','District','Garden','Layout','Floor','Year','Size','Price'])
# Rearrange the data location of Anjuke, and split the data region of Anjuke
anjuke_df['District'] = anjuke_df['Region'].str.extract(r'.+?-(.+?)-.+?', expand=False)
anjuke_df['Region'] = anjuke_df['Region'].str.extract(r'(.+?)-.+?', expand = False)
anjuke_df = pd.DataFrame(anjuke_df, columns = ['Region', 'District', 'Garden', 'Layout',
                                               'Floor', 'Year', 'Size', 'Price'])

# Summarize data
housedata_df = pd.merge(lianjia_df_clean,anjuke_df,how='outer')
housedata_df['PricePm'] = housedata_df['Price']/housedata_df['Size']
# Clear some blank data
housedata_df.dropna(how='any')
# Clear some duplicate data
housedata_df.drop_duplicates(keep='first',inplace=True)

# Remove meaningless features and digitize features
drop_out = ['Garden', 'Id', 'District', 'Direction']
data = lianjia_df.drop(drop_out, axis=1)
# Chinese character to number mapping dictionary
loc_map = {'东城':1, '西城':2, '朝阳':3, '海淀':4, '丰台':5, '石景山':6, '通州':7, '昌平':8, '大兴':9, '亦庄开发区':10,
           '顺义':11, '房山':12, '门头沟':13, '平谷':14, '怀柔':15, '密云':16, '延庆':17, '燕郊':18, '香河':19}
#1: Doncheng, 2: Xicheng, 3: Chaoyang, 4: Haidian, 5: Fengtai, 6: Shijingshan,
#7: Tong Zhou, 8: Changping, 9: Daxing, 10: Yizhuang, 11: Shunyi, 12: Fangshan,
#13: Mentougou, 14: Pinggu, 15: HuaiRou, 16: Miyun, 17: Yanqing, 18: Yanjiao, 19: Xianghe.

renovation_map = {'简装':0, '精装':1, '其它':2}
elevator_map = {'有电梯':1, '无电梯':0}# Dataset mapping and cleaning
data['Region'] = data['Region'].map(loc_map)
data['Renovation'] = data['Renovation'].map(renovation_map)
data['Elevator'] = data['Elevator'].map(elevator_map)
data['Layout'] = data['Layout'].str.extract('(^\d).*', expand=False)
data = data.dropna(how='any').astype('float') # Convert all data into float

# root window
root = tk.Tk()
root.geometry("1050x950")
root.title('Beijing House Price Visualization')

text1 = tk.Label(text="   House Price Visualization  ", bg="blue", fg="orange",
                 font=('Times', 28, 'bold italic')).grid(row=0, column=2, sticky="e")
text2 = tk.Label(text="\n").grid(row=1, column=2, sticky="e")
# configure the grid
# root.columnconfigure(0, weight=1)
# root.columnconfigure(1, weight=3)


# region-------------------------------------------------------------------------
region_label = ttk.Label(root, text="The region you are looking for:\n", font=('Times', 12, 'bold italic'))
region_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

region_entry = ttk.Combobox(root)
region_entry.grid(column=3, row=2, sticky=tk.E, padx=5, pady=5)
region_entry['value'] = ('Chao Yang', 'Hai Dian', 'Dong Cheng', 'Xi Cheng')

# house layout-------------------------------------------------------------------
layout_label = ttk.Label(root, text="How many bedrooms do you want:\n", font=('Times', 12, 'bold italic'))
layout_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)

layout_entry = ttk.Combobox(root)
layout_entry.grid(column=3, row=3, sticky=tk.E, padx=5, pady=5)
layout_entry['value'] = ('1', '2', '3', '4', '5', '6', '7', '8')

# floor?---------------------------------------------------------------------------
floor_label = ttk.Label(root, text="Which floor do you like:\n", font=('Times', 12, 'bold italic'))
floor_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)

floor_label2 = ttk.Label(root, text="Minimun: \n", font=('Times', 12))
floor_label2.grid(column=2, row=4, sticky=tk.W, padx=5, pady=5)
floor_entry = tk.Scale(root,
                       from_=1,
                       to=57,
                       orient=tk.HORIZONTAL,
                       length=300,
                       tickinterval=10)

floor_entry.grid(column=3, row=4, sticky=tk.E, padx=5, pady=5)

floor_label3 = ttk.Label(root, text="Maximun: \n", font=('Times', 12))
floor_label3.grid(column=2, row=5, sticky=tk.W, padx=5, pady=5)
floor_entry2 = tk.Scale(root,
                        from_=1,
                        to=57,
                        orient=tk.HORIZONTAL,
                        length=300,
                        tickinterval=10)
floor_entry2.grid(column=3, row=5, sticky=tk.E, padx=5, pady=5)

# elevator?------------------------------------------------------------------------
elevator_label = ttk.Label(root, text="Do you want elevator:\n", font=('Times', 12, 'bold italic'))
elevator_label.grid(column=0, row=6, sticky=tk.W, padx=5, pady=5)

elevator_entry = ttk.Combobox(root)
elevator_entry.grid(column=3, row=6, sticky=tk.E, padx=5, pady=5)
elevator_entry['value'] = ('YES', 'NO')

# renovation?----------------------------------------------------------------------
renovation_label = ttk.Label(root, text="Do you want renovation:\n", font=('Times', 12, 'bold italic'))
renovation_label.grid(column=0, row=7, sticky=tk.W, padx=5, pady=5)

renovation_entry = ttk.Combobox(root)
renovation_entry.grid(column=3, row=7, sticky=tk.E, padx=5, pady=5)
renovation_entry['value'] = ('YES', 'NO')

# Build year?----------------------------------------------------------------------
Build_label = ttk.Label(root, text="Which Build year do you like:\n", font=('Times', 12, 'bold italic'))
Build_label.grid(column=0, row=8, sticky=tk.W, padx=5, pady=5)

Build_label2 = ttk.Label(root, text="Minimun: \n", font=('Times', 12))
Build_label2.grid(column=2, row=8, sticky=tk.W, padx=5, pady=5)
Build_entry = tk.Scale(root,
                       from_=1950,
                       to=2016,
                       orient=tk.HORIZONTAL,
                       length=300,
                       tickinterval=20)
Build_entry.grid(column=3, row=8, sticky=tk.E, padx=5, pady=5)

Build_label3 = ttk.Label(root, text="Maximun: \n", font=('Times', 12))
Build_label3.grid(column=2, row=9, sticky=tk.W, padx=5, pady=5)
Build_entry2 = tk.Scale(root,
                        from_=1950,
                        to=2016,
                        orient=tk.HORIZONTAL,
                        length=300,
                        tickinterval=20)
Build_entry2.grid(column=3, row=9, sticky=tk.E, padx=5, pady=5)

# Size?---------------------------------------------------------------------------
Size_label = ttk.Label(root, text="What size range do you like:\n", font=('Times', 12, 'bold italic'))
Size_label.grid(column=0, row=10, sticky=tk.W, padx=5, pady=5)

Size_label2 = ttk.Label(root, text="Minimun: (m^2)\n", font=('Times', 12))
Size_label2.grid(column=2, row=10, sticky=tk.W, padx=5, pady=5)
Size_entry = tk.Scale(root,
                      from_=16,
                      to=1019,
                      orient=tk.HORIZONTAL,
                      length=300,
                      tickinterval=200)
Size_entry.grid(column=3, row=10, sticky=tk.E, padx=5, pady=5)

Size_label3 = ttk.Label(root, text="Maximun: （m^2）\n", font=('Times', 12))
Size_label3.grid(column=2, row=11, sticky=tk.W, padx=5, pady=5)
Size_entry2 = tk.Scale(root,
                       from_=16,
                       to=1019,
                       orient=tk.HORIZONTAL,
                       length=300,
                       tickinterval=200)
Size_entry2.grid(column=3, row=11, sticky=tk.E, padx=5, pady=5)

# Price?---------------------------------------------------------------------------------------
Price_label = ttk.Label(root, text="What price range do you like:\n", font=('Times', 12, 'bold italic'))
Price_label.grid(column=0, row=12, sticky=tk.W, padx=5, pady=5)

Price_label2 = ttk.Label(root, text="Minimun: (in 100K)\n", font=('Times', 12))
Price_label2.grid(column=2, row=12, sticky=tk.W, padx=5, pady=5)
Price_entry = tk.Scale(root,
                       from_=6.9,
                       to=550,
                       orient=tk.HORIZONTAL,
                       length=300,
                       tickinterval=100)
Price_entry.grid(column=3, row=12, sticky=tk.E, padx=5, pady=5)

Price_label3 = ttk.Label(root, text="Maximun: （in 100K）\n", font=('Times', 12))
Price_label3.grid(column=2, row=13, sticky=tk.W, padx=5, pady=5)
Price_entry2 = tk.Scale(root,
                        from_=6.9,
                        to=550,
                        orient=tk.HORIZONTAL,
                        length=300,
                        tickinterval=100)
Price_entry2.grid(column=3, row=13, sticky=tk.E, padx=5, pady=5)


# Define funtions===============================================================================
# ====== Rigion
def rigion():
    if region_entry.get() == "":
        messagebox.showinfo("Nothing to show!", "You have to be choose something for Rigion")


# ====== Layout
def layout():
    global layout_value
    layout_value = float(layout_entry.get())
    # print(layout_value)

    if layout_entry.get() == "":
        messagebox.showinfo("Nothing to show!", "You have to be choose something for layout")


# ====== Floor
def floor():
    global floor_value_min
    global floor_value_max
    floor_value_min = floor_entry.get()
    floor_value_max = floor_entry2.get()


# ====== elevator
def elevator():
    global elevator_value
    if elevator_entry.get() == "YES":
        messagebox.showinfo("What user choose", "You choose YES for elevator")
        elevator_value = 1
        # print(elevator_value)

    elif elevator_entry.get() == "NO":
        messagebox.showinfo("What user choose", "You choose NO for elevator")
        elevator_value = 0
        # print(elevator_value)

    elif elevator_entry.get() == "":
        messagebox.showinfo("Nothing to show!", "You have to be choose something for elevator")

    # ====== renovation


def reno():
    global reno_value
    if renovation_entry.get() == "YES":
        messagebox.showinfo("What user choose", "You choose YES for renovation")
        reno_value = 1

    elif renovation_entry.get() == "NO":
        messagebox.showinfo("What user choose", "You choose NO for renovation")
        reno_value = 0

    elif renovation_entry.get() == "":
        messagebox.showinfo("Nothing to show!", "You have to be choose something for renovation")

    # ====== Build Year


def Build():
    global Build_value_min
    global Build_value_max
    Build_value_min = Build_entry.get()
    Build_value_max = Build_entry2.get()


# ====== Size range
def size():
    global size_value_min
    global size_value_max
    size_value_min = Size_entry.get()
    size_value_max = Size_entry2.get()


# ====== Price range
def price():
    global price_value_min
    global price_value_max
    price_value_min = Price_entry.get()
    price_value_max = Price_entry2.get()


# Continue button--------------------------------------------------------------------
Continue_button = ttk.Button(root, text="Confirm", width=16, command=lambda: [rigion(), reno(), elevator(),
                                                                              layout(), Build(), floor(),
                                                                              size(), price()])
Continue_button.grid(column=3, row=15, sticky=tk.E, padx=5, pady=5)

# Quit Botton--------------------------------------------------------------------
quit_botton = ttk.Button(root, text="Continue", width=16, command=root.destroy)
quit_botton.grid(column=3, row=16, sticky=tk.E, padx=5, pady=5)

root.mainloop()

# Modify data based on user input
data_user = data[(data['Size'] >= size_value_min) & (data['Size'] <= size_value_max)]
data_user = data_user[(data['Price'] >= price_value_min) & (data['Price'] <= price_value_max)]
data_user = data_user[(data['Floor'] >= floor_value_min) & (data['Floor'] <= floor_value_max)]
data_user = data_user[(data['Year'] >= Build_value_min) & (data['Year'] <= Build_value_max)]
data_user = data_user[data['Layout'] == layout_value]
data_user = data_user[data['Elevator'] == elevator_value]
data_user = data_user[data['Renovation'] == reno_value]

# Scatter plot
fig1 = px.scatter(data_user, x = 'Year', y = 'Price',
                size='Size', size_max=10, color='Region',
                 hover_name='Region', title = 'Price vs. Year')

# fig.show()
# print('Regions are corresponding to: ')
# print('1: Doncheng, 2: Xicheng, 3: Chaoyang, 4: Haidian, 5: Fengtai, 6: Shijingshan,' )
# print('7: Tong Zhou, 8: Changping, 9: Daxing, 10: Yizhuang, 11: Shunyi, 12: Fangshan, ')
# print('13: Mentougou, 14: Pinggu, 15: HuaiRou, 16: Miyun, 17: Yanqing, 18: Yanjiao, 19: Xianghe. \n\n')

# Pie chart
fig2 = px.pie(data_user, names='Region', title='Percentage of Houses in Every Region',  hole=.3)
fig2.update_traces(textposition='outside')
fig2.update_layout(uniformtext_minsize=12, uniformtext_mode='hide')

# Bar chart
fig3 = px.bar(data_user, x="Year", y="Region", color="Floor", title="Region vs. Year")

# Histogram for price
hist = go.Histogram(x = data_user['Price'], xbins={'size': 5})
fig4 = go.Figure(hist)
fig4.update_layout(bargap=0.1, title = "Count for House Price", xaxis_title = "Price (10k)",
    yaxis_title = "Count")

# Histogram for region
hist = go.Histogram(x = data_user['Region'], xbins={'size': 1})
fig5 = go.Figure(hist)
fig5.update_layout(bargap=0.1, title = "Count for Region", xaxis_title = "Region",
    yaxis_title = "Count")

# 3D plot
fig6 = px.scatter_3d(data_user, x='Year', y='Size', z='Price', color='Region')

# root window
root = tk.Tk()
root.geometry("1030x800")
root.title('Beijing House Price')

text1 = tk.Label(text="   Find Your House Now !  ", bg="blue", fg="orange",
                 font=('Times', 28, 'bold italic')).grid(row=0, column=2, sticky="e")
text2 = tk.Label(text="\n").grid(row=1, column=2, sticky="e")
# configure the grid
# root.columnconfigure(0, weight=1)
# root.columnconfigure(1, weight=3)


# region-------------------------------------------------------------------------
region_label = ttk.Label(root, text="The region you are looking for:\n", font=('Times', 12, 'bold italic'))
region_label.grid(column=0, row=2, sticky=tk.W, padx=5, pady=5)

region_entry = ttk.Combobox(root)
region_entry.grid(column=3, row=2, sticky=tk.E, padx=5, pady=5)
region_entry['value'] = ('Dong Cheng', 'Xi Cheng', 'Chao Yang', 'Hai Dian', 'Feng Tai',
                         'Shi Jing Shan', 'Tong Zhou', 'Chang Pin', 'Da Xin', 'Yi Zhuang',
                         'Shun Yi', 'Fang Shan', 'Men Tou Gou', 'Pin Gu', 'Huai Rou',
                         'Mi Yun', 'Yan Qing', 'Yan Jiao', 'Xiang He')

# house layout-------------------------------------------------------------------
layout_label = ttk.Label(root, text="How many bedrooms do you want:\n", font=('Times', 12, 'bold italic'))
layout_label.grid(column=0, row=3, sticky=tk.W, padx=5, pady=5)

layout_entry = ttk.Combobox(root)
layout_entry.grid(column=3, row=3, sticky=tk.E, padx=5, pady=5)
layout_entry['value'] = ('1', '2', '3', '4', '5', '6', '7', '8')

# floor?---------------------------------------------------------------------------
floor_label = ttk.Label(root, text="Which floor do you like:\n", font=('Times', 12, 'bold italic'))
floor_label.grid(column=0, row=4, sticky=tk.W, padx=5, pady=5)

floor_entry = tk.Scale(root,
                       from_=1,
                       to=57,
                       orient=tk.HORIZONTAL,
                       length=300,
                       tickinterval=10)

floor_entry.grid(column=3, row=4, sticky=tk.E, padx=5, pady=5)

# elevator?------------------------------------------------------------------------
elevator_label = ttk.Label(root, text="Do you want elevator:\n", font=('Times', 12, 'bold italic'))
elevator_label.grid(column=0, row=6, sticky=tk.W, padx=5, pady=5)

elevator_entry = ttk.Combobox(root)
elevator_entry.grid(column=3, row=6, sticky=tk.E, padx=5, pady=5)
elevator_entry['value'] = ('YES', 'NO')

# renovation?----------------------------------------------------------------------
renovation_label = ttk.Label(root, text="Do you want renovation:\n", font=('Times', 12, 'bold italic'))
renovation_label.grid(column=0, row=7, sticky=tk.W, padx=5, pady=5)

renovation_entry = ttk.Combobox(root)
renovation_entry.grid(column=3, row=7, sticky=tk.E, padx=5, pady=5)
renovation_entry['value'] = ('YES', 'NO')

# Build year?----------------------------------------------------------------------
Build_label = ttk.Label(root, text="Which Build year do you like:\n", font=('Times', 12, 'bold italic'))
Build_label.grid(column=0, row=8, sticky=tk.W, padx=5, pady=5)

Build_entry = tk.Scale(root,
                       from_=1980,
                       to=2016,
                       orient=tk.HORIZONTAL,
                       length=300,
                       tickinterval=20)
Build_entry.grid(column=3, row=8, sticky=tk.E, padx=5, pady=5)

# Size?---------------------------------------------------------------------------
Size_label = ttk.Label(root, text="What size do you like:\n", font=('Times', 12, 'bold italic'))
Size_label.grid(column=0, row=9, sticky=tk.W, padx=5, pady=5)

Size_label2 = ttk.Label(root, text="in m^2\n", font=('Times', 12))
Size_label2.grid(column=2, row=9, sticky=tk.W, padx=5, pady=5)
Size_entry = tk.Scale(root,
                      from_=16,
                      to=500,
                      orient=tk.HORIZONTAL,
                      length=300,
                      tickinterval=200)
Size_entry.grid(column=3, row=9, sticky=tk.E, padx=5, pady=5)

# # Price?---------------------------------------------------------------------------------------
# Price_label = ttk.Label(root, text="What price range do you like:\n", font=('Times', 12, 'bold italic'))
# Price_label.grid(column=0, row=11, sticky=tk.W, padx=5, pady=5)
#
# Price_label2 = ttk.Label(root, text="Price in 100K\n", font=('Times', 12))
# Price_label2.grid(column=2, row=11, sticky=tk.W, padx=5, pady=5)
# Price_entry = tk.Scale(root,
#                        from_=6.9,
#                        to=550,
#                        orient=tk.HORIZONTAL,
#                        length=300,
#                        tickinterval=100)
# Price_entry.grid(column=3, row=11, sticky=tk.E, padx=5, pady=5)


#      'Yan Qing','Yan Jiao','Xiang He'

# Define funtions===============================================================================
# ====== region
def region():
    global region_value

    if region_entry.get() == "Dong Cheng":
        messagebox.showinfo("What user choose", "you choose Dong Cheng for region")
        region_value = 1

    elif region_entry.get() == "Xi Cheng":
        messagebox.showinfo("What user choose", "you choose Xi Cheng for region")
        region_value = 2

    elif region_entry.get() == "Chao Yang":
        messagebox.showinfo("What user choose", "you choose Chao Yang for region")
        region_value = 3

    elif region_entry.get() == "Hai Dian":
        messagebox.showinfo("What user choose", "you choose Hai Dian for region")
        region_value = 4

    elif region_entry.get() == "Feng Tai":
        messagebox.showinfo("What user choose", "you choose Feng Tai for region")
        region_value = 5

    elif region_entry.get() == "Shi Jing Shan":
        messagebox.showinfo("What user choose", "you choose Shi Jing Shan for region")
        region_value = 6

    elif region_entry.get() == "Tong Zhou":
        messagebox.showinfo("What user choose", "you choose Feng Tai for region")
        region_value = 7

    elif region_entry.get() == "Chang Pin":
        messagebox.showinfo("What user choose", "you choose Chang Pin for region")
        region_value = 8

    elif region_entry.get() == "Da Xin":
        messagebox.showinfo("What user choose", "you choose Da Xin for region")
        region_value = 9

    elif region_entry.get() == "Yi Zhuang":
        messagebox.showinfo("What user choose", "you choose Yi Zhuang for region")
        region_value = 10

    elif region_entry.get() == "Shun Yi":
        messagebox.showinfo("What user choose", "you choose Shun Yi for region")
        region_value = 11

    elif region_entry.get() == "Fang Shan":
        messagebox.showinfo("What user choose", "you choose Fang Shan for region")
        region_value = 12

    elif region_entry.get() == "Men Tou Gou":
        messagebox.showinfo("What user choose", "you choose Men Tou Gou for region")
        region_value = 13

    elif region_entry.get() == "Pin Gu":
        messagebox.showinfo("What user choose", "you choose Pin Gu for region")
        region_value = 14

    elif region_entry.get() == "Huai Rou":
        messagebox.showinfo("What user choose", "you choose Huai Rou for region")
        region_value = 15

    elif region_entry.get() == "Mi Yun":
        messagebox.showinfo("What user choose", "you choose Mi Yun for region")
        region_value = 16

    elif region_entry.get() == "Yan Qing":
        messagebox.showinfo("What user choose", "you choose Yan Qing for region")
        region_value = 17

    elif region_entry.get() == "Yan Jiao":
        messagebox.showinfo("What user choose", "you choose Yan Jiao for region")
        region_value = 18

    elif region_entry.get() == "Xiang He":
        messagebox.showinfo("What user choose", "you choose Xiang He for region")
        region_value = 19

    elif region_entry.get() == "":
        messagebox.showinfo("nothing to show!", "You have to be choose something for region!")


# ====== Layout
def layout():
    global layout_value

    layout_value = float(layout_entry.get())
    # print(layout_value)

    if layout_entry.get() == "":
        messagebox.showinfo("nothing to show!", "you have to be choose something for layout")


# ====== Floor
def floor():
    global floor_value
    floor_value = floor_entry.get()


# ====== elevator
def elevator():
    global elevator_value
    if elevator_entry.get() == "YES":
        messagebox.showinfo("What user choose", "you choose YES for elevator")
        elevator_value = 1
        # print(elevator_value)

    elif elevator_entry.get() == "NO":
        messagebox.showinfo("What user choose", "you choose NO for elevator")
        elevator_value = 0
        # print(elevator_value)

    elif elevator_entry.get() == "":
        messagebox.showinfo("nothing to show!", "you have to be choose something for elevator")

    # ====== renovation


def reno():
    global reno_value
    if renovation_entry.get() == "YES":
        messagebox.showinfo("What user choose", "you choose YES for renovation")
        reno_value = 1

    elif renovation_entry.get() == "NO":
        messagebox.showinfo("What user choose", "you choose NO for renovation")
        reno_value = 0

    elif renovation_entry.get() == "":
        messagebox.showinfo("nothing to show!", "you have to be choose something for renovation")

    # ====== Build Year


def Build():
    global Build_value
    Build_value = Build_entry.get()


# ====== Size range
def size():
    global size_value
    size_value = Size_entry.get()


# ====== Price range
# def price():
#     global price_value
#     price_value = Price_entry.get()


# Continue button--------------------------------------------------------------------
Continue_button = ttk.Button(root, text="Confirm", width=16, command=lambda: [region(), reno(), elevator(),
                                                                               layout(), Build(), floor(),
                                                                               size()])
Continue_button.grid(column=3, row=14, sticky=tk.E, padx=5, pady=5)

# Quit Botton--------------------------------------------------------------------
quit_botton = ttk.Button(root, text="Continue", width=16, command=root.destroy)
quit_botton.grid(column=3, row=15, sticky=tk.E, padx=5, pady=5)

root.mainloop()
# Get input data
input_data = [region_value,layout_value,floor_value,elevator_value,reno_value,Build_value,size_value]


# Rearrange fields
columns1 = ['Region', 'Layout', 'Floor', 'Elevator', 'Renovation', 'Year', 'Size', 'Price']
columns2 = ['Region', 'Layout', 'Floor', 'Elevator', 'Renovation', 'Year', 'Size']
data = pd.DataFrame(data, columns=columns1)

# Price mean and standard deviation
mean = data.Price.mean()
std = data.Price.std()

# Data standardization
def nor_data(input_data):
    region_nor = (input_data[0]-data.Region.mean())/data.Region.std()
    Layout_nor = (input_data[1] - data.Layout.mean()) / data.Layout.std()
    Floor_nor = (input_data[2] - data.Floor.mean()) / data.Floor.std()
    Elevator_nor = (input_data[3] - data.Elevator.mean()) / data.Elevator.std()
    Renovation_nor = (input_data[4] - data.Renovation.mean()) / data.Renovation.std()
    Year_nor = (input_data[5] - data.Year.mean()) / data.Year.std()
    Size_nor = (input_data[6] - data.Size.mean()) / data.Size.std()
    nor_pred_data = [region_nor,Layout_nor,Floor_nor,Elevator_nor,Renovation_nor,Year_nor,Size_nor]
    return nor_pred_data

# Get prediction parameters
pred_features =pd.DataFrame(columns=columns2)
pred_features.loc[0] = nor_data(input_data)

# Data standardization
data = data.apply(
    lambda x: (x - x.mean()) / (x.std())
    )

n_train = data.shape[0]
train_features = torch.tensor(data.iloc[:,0:7].values,dtype=torch.float)
train_labels = torch.tensor(data.Price.values,dtype=torch.float).view(-1,1)
pred_features = torch.tensor(pred_features.values,dtype=torch.float)



# Train the model using a basic linear regression model and a squared loss function
loss = torch.nn.MSELoss()

# Initialize the network
def get_net(feature_num):
    net = nn.Linear(feature_num,1)
    for param in net.parameters():
        nn.init.normal_(param,mean=0,std=0.01)
        return net


# Training function
def train(net,train_features,train_labels,test_features,test_labels,num_epochs,learning_rate,weight_decay,batch_size):
    train_ls, test_ls = [],[]
    dataset = Data.TensorDataset(train_features,train_labels)
    train_iter = Data.DataLoader(dataset,batch_size,shuffle = True)
    # Using the adam optimization algorithm
    optimizer = torch.optim.Adam(net.parameters(),lr = learning_rate,weight_decay = weight_decay)
    net = net.float()#.to(device='cuda')
    for epoch in range(num_epochs):
        for X,y in train_iter:
            l = loss(net(X),y)
            optimizer.zero_grad()
            l.backward()
            optimizer.step()
        train_ls.append(loss(net(train_features),train_labels).item())
        if test_labels is not None:
            test_ls.append(loss(net(test_features),test_labels).item())

    return train_ls,test_ls

k,num_epochs,lr,weight_decay,batch_size = 5,100,0.0025,0,64

# K folded cross-validation
def get_k_fold_data(k, i, X, y):
    # Returns the training and validation data required for the i-fold cross-validation
    assert k > 1
    fold_size = X.shape[0] // k
    X_train, y_train = None, None
    for j in range(k):
        idx = slice(j * fold_size, (j + 1) * fold_size)
        X_part, y_part = X[idx, :], y[idx]
        if j == i:
            X_valid, y_valid = X_part, y_part
        elif X_train is None:
            X_train, y_train = X_part, y_part
        else:
            X_train = torch.cat((X_train, X_part), dim=0)
            y_train = torch.cat((y_train, y_part), dim=0)
    return X_train, y_train, X_valid, y_valid

# In K-fold cross-validation we train k times and return the average error of training and validation
def k_fold(k,X_train,y_train,num_epochs,learning_rate,weight_decay,batch_size):
    train_l_sum,valid_l_sum = 0,0
    for i in range(k):
        data = get_k_fold_data(k,i,X_train,y_train)
        net = get_net(X_train.shape[1])
        train_ls,valid_ls = train(net,*data,num_epochs,learning_rate,weight_decay,batch_size)
        train_l_sum += train_ls[-1]
        valid_l_sum += valid_ls[-1]
        print('fold %d, train rmse %f, valid rmse %f' % (i+1,float(train_ls[-1]), float(valid_ls[-1])))
    return train_l_sum/k,valid_l_sum/k
# train_l,valid_l = k_fold(k,train_features,train_labels,num_epochs,lr,weight_decay,batch_size)

# Training and prediction
def train_and_pred(train_features,test_features,train_labels,test_data,num_epochs,lr,weight_decay,batch_size):
    net = get_net(train_features.shape[1])
    train_ls,_ = train(net,train_features,train_labels,None,None,num_epochs,lr,weight_decay,batch_size)
    preds = net(test_features).detach().numpy()
    return preds

n = 0
price_pred = 0
start = time.time()
while n < 1:
    start = time.time()
    pred_price_nor = train_and_pred(train_features,pred_features,train_labels,None,num_epochs,lr,weight_decay,batch_size)
    pred_price = (pred_price_nor*std+mean)/0.70
    price_pred +=pred_price
    end = time.time()
    n +=1
end = time.time()


# Delete all PDF files
path = '/Users/cronusli/PycharmProjects/project'
i = 0
for file in os.listdir(path):
    path_to_zip_file = os.path.join(path)

    if file.endswith('.pdf'):
        os.remove(file)
    i += 1

doc = SimpleDocTemplate('7.pdf')
styles = getSampleStyleSheet()
style = styles['Normal']
story = []
price = 1000
story.append(Paragraph(f"Region: {region_value}",style))
story.append(Paragraph(f"Floor: {floor_value}",style))
story.append(Paragraph(f"Layout: {layout_value}",style))
story.append(Paragraph(f"Elevator: {elevator_value}",style))
story.append(Paragraph(f"Build: {Build_value}",style))
story.append(Paragraph(f"Renovation: {reno_value}",style))
story.append(Paragraph(f"Size: {size_value}",style))
story.append(Paragraph(f"The prediction house price is {price_pred}",style))
doc.build(story)

# Create PDF for every figure
pio.write_image(fig1,  "1.pdf", format="pdf", engine="kaleido")
pio.write_image(fig2,  "2.pdf", format="pdf", engine="kaleido")
pio.write_image(fig3,  "3.pdf", format="pdf", engine="kaleido")
pio.write_image(fig4,  "4.pdf", format="pdf", engine="kaleido")
pio.write_image(fig5,  "5.pdf", format="pdf", engine="kaleido")
pio.write_image(fig6,  "6.pdf", format="pdf", engine="kaleido")

# Merge all PDF to have the final report
pdf_list = [f for f in os.listdir(path) if f.endswith('.pdf')]
pdf_list = [os.path.join(path, filename) for filename in pdf_list]
pdf_list.sort()
file_merger = PdfFileMerger()
for pdf in pdf_list:
    file_merger.append(pdf)
file_merger.write("/Users/cronusli/PycharmProjects/project/Project.pdf")




