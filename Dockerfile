FROM python

# Install deps, create basedirs
RUN pip install feedparser requests pyyaml \
    && mkdir /app

COPY rss.py /app/

WORKDIR /app
CMD /app/rss.py

