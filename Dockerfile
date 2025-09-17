FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

RUN apt-get update && apt-get install --no-install-recommends -y curl ca-certificates

RUN curl -fsSL -o /tmp/install-ollama.sh https://ollama.com/install.sh

RUN for i in $(seq 1 5); do \
    sh /tmp/install-ollama.sh && break || sleep 5; \
done

ARG OLLAMA_MODEL
RUN ollama serve >/dev/null 2>&1 & \
    sleep 5; \
    while ! curl -s http://localhost:11434 >/dev/null; do \
        echo "Waiting for Ollama server..."; \
        sleep 1; \
    done; \
    ollama pull ${OLLAMA_MODEL}; \
    pkill ollama

RUN apt-get update && \
    apt-get install --no-install-recommends -y \
    python3 \
    python3-pip \
    python3-venv \
    x11vnc \
    xvfb \
    xterm \
    xserver-xorg-video-dummy \
    tini \
    xdotool \
    chromium-browser \
    openbox \
    dbus \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

ARG VNC_PASSWORD
RUN x11vnc -storepasswd $VNC_PASSWORD /etc/x11vnc.pass

WORKDIR /app

COPY requirements.txt .

RUN python3 -m venv venv && \
    ./venv/bin/pip install --no-cache-dir -r requirements.txt

RUN ./venv/bin/playwright install-deps && \
    ./venv/bin/playwright install chromium

RUN pip install pyxdg

COPY entrypoint.sh /usr/local/bin/entrypoint.sh
COPY openbox/rc.xml /etc/xdg/openbox/rc.xml
COPY openbox/autostart /etc/xdg/openbox/autostart

RUN chmod +x /usr/local/bin/entrypoint.sh

COPY . .

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/entrypoint.sh"]

EXPOSE 5900
