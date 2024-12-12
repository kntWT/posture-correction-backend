FROM nvidia/cuda:12.1.1-cudnn8-devel-ubuntu22.04

WORKDIR /app

RUN apt update && \
    apt install -y \
    build-essential \
    cmake>=3.28 \
    libgl1-mesa-dev \
    clinfo \
    opencl-headers \
    libboost-all-dev \
    libopenblas-dev \
    git \
    python3 \
    python3-pip \
    python3-venv && \
    apt clean && rm -rf /var/lib/apt/lists/*

RUN python3 -m venv /app/.venv
ENV PATH /app/.venv/bin:$PATH
RUN pip install -U pip

# RUN git clone --recursive https://github.com/microsoft/LightGBM.git && \
#     cd LightGBM && \
#     mkdir build && cd build && \
#     cmake -DUSE_GPU=1 -DOpenCL_LIBRARY=/usr/lib/x86_64-linux-gnu/libOpenCL.so.1 -DOpenCL_INCLUDE_DIR=/usr/local/cuda/include/ .. && \
#     make OPENCL_HEADERS=/usr/local/cuda-12.6/targets/x86_64-linux/include LIBOPENCL=/usr/local/cuda-12.6/targets/x86_64-linux/lib
# cd ../python-package && \
# python3 setup.py install && \
# cd ../.. && rm -rf LightGBM

# RUN /bin/bash -c "source activate python3 && cd /app/LightGBM && sh ./build-python.sh install --precompile && deactivate"

COPY . .

# RUN pip install -r requirements.txt
# CMD ["gunicorn", "--config", "gunicorn_config_prod.py", "app:app"]

CMD ["/bin/bash", "-c", "python3 -m venv .venv && . .venv/bin/activate && pip install -r prod.requirements.txt && python3 main.py"]
