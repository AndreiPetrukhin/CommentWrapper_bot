FROM python:3
# set work directory
WORKDIR /Users/apetrukh/PythonHW/TBot_docx_to_csv
# copy project
COPY . /Users/apetrukh/PythonHW/TBot_docx_to_csv
# install dependencies
RUN pip install --no-cache-dir -r requirements.txt
# run app
CMD ["python", "Proccessing_bot.py"]