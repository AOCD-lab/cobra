echo "compiling....."
gfortran -o MLR.x MLR.f normalization*f dnormal*f -lblas -llapack
