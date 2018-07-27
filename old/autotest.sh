echo "testing $1..."
py -3 classify.py $1 $2 > ./result/$1_res.txt
