

for M in LQ-example HQ-example case-01 case-02 case-03 case-04 case-05 case-06 case-07 
do
    cd $M

    python3 ../../runtests.py -m $M.matrix -d up -n 1000 -t .2 -b .1 -o .2 -c 0.8
    python3 ../../runplots.py -m $M.matrix 

    cd ..
done


