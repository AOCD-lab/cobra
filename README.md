# pcs
Full tests for PCS calculations <br>

# How to install
Download the full package <br>

edit Utilities/set_variables.py to match your enviornment <br>
<br>

cd Fortran<br>
modify link.sh to adapt it to your fortran environment <br>
sh ./linka.sh <br>
cd .. <br>
<br>

Usage:  <br>
python runtests.py -m/--matrix file.matrix <br>
&emsp; &emsp; &emsp;  -n/--no_of_cycles  No of randomizaiton/bootstrap/optimization cycles  <br>
&emsp; &emsp; &emsp;  -t/--precentage_top_preds fraction of top/bottom systems to predict: 0.1 = 10% predicted <br>
&emsp; &emsp; &emsp;  -b/--precentage_bootstrap fraction of systems out of the bags:  0.2 = 20% held out <br>
&emsp; &emsp; &emsp;  -o/--precentage_cycles fraction of systems out in the optimization cycles:  0.3 = 30% held out <br>
&emsp; &emsp; &emsp;  -d/--direction up or down: keywords up/dw <br>
&emsp; &emsp; &emsp;  -c/--cutoff cutoff to define TP/TN: 0.8 = Max experimental performance * 0.8 <br>
<br>

# Run an example
cd Examples <br>

<br>
Run first all tests<br>
python $PATH_TO_PCS/runtests.py -m test.matrix -d up -n 10 -t .2 -b .2 -o .3 -d up -c 0.8 <br>
<br>

Then make plots analyzing tests<br>
python $PATH_TO_PCS/runplots.py -m test.matrix <br>
<br>

Note:  $PATH_TO_PCS is the path to the pcs location <br>



