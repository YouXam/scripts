subdir = (
    odpd
)

for dir in ${subdir[@]}; do
    cd $dir
    ./install.sh
    cd ..
done