# House Price Prediction

The purpose this project is to show user the house price range in different plots and predict the house price for varies requirements.


## Description

First of all, this project uses a crawler program to collect nearly 30,000 pieces of housing price information in Beijing. 
The raw data came from China's well-known real estate transaction information website Lianjia and Anjuke (similar to the apartments website). 
In the data cleaning part, blank data and extreme data are removed to get better data visualization and house price prediction.
For the convenience of users, we use the tkinter package to create a graphic user interface (GUI) for user interaction. 
Users can choose the housing data they want to know in our interface, such as the built year, floor, size, area of the house and other factors. 
After the user selects the data, a series of visual data will be provided to let the user understand the distribution and trend of housing prices in Beijing.


## Getting Started

### Dependencies

Windows 10 or greater, Python 3.7 or greater, Numpy, Plotly, PyTorch, Pandas, tkinter, PIL, Kaleido, Pypdf2, os

### Installing

* Go to the following link to download PyTorch.
  https://pytorch.org/get-started/locally/
* Follow the steps on tha same link to complete the installation.
* Install kaleido using CMD.exe Prompt, copy (pip install kaleido) and hit enter for installation.
* Install reportlab using CMD.exe Prompt, copy (pip install reportlab) and hit enter for installation.
* Install Pypdf2 using CMD.exe Prompt, copy (pip install PyPDF2) and hit enter for installation.

### Executing program

* Open Project.py

Before running the code:

In the following command change the path to your own path

```
path = '# Enter your path here'  (ex. /Users/Username/###/###)
```


* Run the Code


### GUI Instruction

For the Visualization:

* Select the data on GUI and click "Confirm" botton
* Review the massage shown in massage box 
* If no error massage shown, click "Get Plots" botton and the results will save as pdf in assigned folder
* Open pdf file saved in assigned folder to see the results

For the Prediction:

* Select the data on GUI and click "Confirm" botton
* Review the massage shown in massage box 
* If no error massage shown, click "Get Predicts" botton and the results will save as pdf in assigned folder
* Open pdf file saved in assigned folder to see the results


## Help

Any Error massage shown, Restart Kernel and Run All Cells.

## Authors

* Yuhang Li
* Zhide Wang
* Yujie Yi


## Version History

0.1


## License

N/A


## Acknowledgments

N/A
