FROM python:3

ADD . /mantid_pr_bot
RUN pip install /mantid_pr_bot

ENTRYPOINT ["mantid_pr_bot"]
