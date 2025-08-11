#!/bin/bash

current_dir=$(pwd)
python_dir="$current_dir/python"
ffmpeg_dir="$current_dir/ffmpeg"

# Скачивание Python (для Linux, пример amd64)
python_url="https://www.python.org/ftp/python/3.12.5/Python-3.12.5.tgz"
python_tgz="$current_dir/python.tgz"
wget $python_url -O $python_tgz
mkdir -p $python_dir
tar -xzvf $python_tgz -C $python_dir --strip-components=1
cd $python_dir
./configure --prefix=$python_dir/local
make
make install
cd $current_dir
rm $python_tgz

# Скачивание FFmpeg (для Linux amd64)
ffmpeg_url="https://johnvansickle.com/ffmpeg/builds/ffmpeg-git-amd64-static.tar.xz"
ffmpeg_tar="$current_dir/ffmpeg.tar.xz"
wget $ffmpeg_url -O $ffmpeg_tar
mkdir -p $ffmpeg_dir
tar -xvf $ffmpeg_tar -C $ffmpeg_dir --strip-components=1
rm $ffmpeg_tar

# Скачивание main.py
script_url="https://raw.githubusercontent.com/your-username/MVC/main/main.py"  # Замени
wget $script_url -O "$current_dir/main.py"

# Создание run.sh
run_sh="$current_dir/run.sh"
echo "#!/bin/bash" > $run_sh
echo "$current_dir/python/local/bin/python3 $current_dir/main.py \$@" >> $run_sh
chmod +x $run_sh

echo "Установка завершена. Запускайте ./run.sh с параметрами, например: ./run.sh"
