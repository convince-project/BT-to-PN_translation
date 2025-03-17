docker build -t pnml_docker .
docker run --rm -it --network=host pnml_docker