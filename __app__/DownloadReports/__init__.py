import datetime
from django.utils.text import slugify
import logging

import azure.functions as func
from __app__.shared import config, env, helpers, rl_client

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Timer triggered function ran at %s', utc_timestamp)

    # Start
    for canned_job in config.CANNED_JOBS:
        logging.info('Logging in...')
        client = rl_client.RLClient(canned_job.get('username'), canned_job.get('password'))
        logging.debug(client)
        logging.info('Logged in.')

        logging.info('Getting list of reports to look for...')
        reports = client.get_reports(canned_job.get('folder'))
        logging.debug(reports)
        logging.info('Done.')

        logging.info('Getting list of jobs...')
        jobs = client.get_jobs()
        logging.debug(jobs)
        logging.info('Done.')

        container_name = canned_job.get('id')
        logging.info(f"Creating container '{container_name}' in '{env.REPORTS_STGACCT_URI}'")
        helpers.create_container(container_name)
        logging.info('Done.')

        for job in jobs:
            job_title = job.get('title')
            job_id = job.get('id')
            if job_title in [report.get('title') for report in reports]:
                logging.info(f"Downloading '{job_title}'...")
                data = client.download_report(job_id)
                logging.debug(data)
                logging.info('Done.')

                filename = slugify(f"{job_title}_{datetime.date.today()}")
                full_filename = f"{filename}.{job.get('ext')}"
                logging.info(f"Uploading '{full_filename}' to '{env.REPORTS_STGACCT_URI}'...")
                helpers.upload_blob(container_name, full_filename, data)
                logging.info('Done.')

                logging.info('Marking retrieved...')
                client.mark_retrieved(job_id)
                logging.info('Done.')
