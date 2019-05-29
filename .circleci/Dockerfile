# sudo docker build --build-arg python_version="3.7"  --coverage="coverage coveralls" --build-arg cdat_channel="cdat/label/nightly" -t cdoutrix/cdat:cdms-base-3 .
# docker push cdoutrix/cdat:cdms-base-3

FROM ubuntu:18.04
ARG cdat_channel="cdat/label/nightly"
ARG python_version="3.7"
ARG coverage="coverage coveralls"
RUN apt-get update && apt-get install -y curl bash git && apt-get clean && apt-get autoclean && apt-get autoremove && chsh -s /bin/bash
RUN curl https://repo.continuum.io/miniconda/Miniconda3-latest-Linux-x86_64.sh -o miniconda3.sh
RUN /bin/bash ./miniconda3.sh -b -p ${HOME}/miniconda && rm miniconda3.sh && ${HOME}/miniconda/bin/conda update --all -y -n base && ${HOME}/miniconda/bin/conda create -y -n cdat -c ${cdat_channel} -c conda-forge "python=${python_version}" esmpy libcf distarray cdtime libcdms cdat_info testsrunner pyopenssl flake8 myproxyclient lazy-object-proxy gcc_linux-64 ${coverage} && ${HOME}/miniconda/bin/conda clean --all -y
CMD ["/bin/bash"]