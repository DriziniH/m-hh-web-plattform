FROM python:3.7
RUN useradd -ms /bin/bash admin
USER admin
WORKDIR /app
COPY requirements.txt requirements.txt
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD [ "python", "-m" , "flask", "run", "--host=0.0.0.0"]
