xhost +local:docker

docker build --no-cache -t bt_translation . 

docker run -it -e DISPLAY=$DISPLAY -v /tmp/.X11-unix:/tmp/.X11-unix --name bt_translation --net=host bt_translation:latest