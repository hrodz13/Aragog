import datetime
import logging

import azure.functions as func
from __app__.shared import rl_client, config

def main(mytimer: func.TimerRequest) -> None:
    utc_timestamp = datetime.datetime.utcnow().replace(tzinfo=datetime.timezone.utc).isoformat()
    if mytimer.past_due:
        logging.info('The timer is past due!')
    logging.info('Timer triggered function ran at %s', utc_timestamp)

    # Start
    logging.info(config.CANNED_JOBS)
    for canned_job in config.CANNED_JOBS:
        canned_job_username = canned_job.get('username')
        logging.info(f"Logging in '{canned_job_username}'...'")
        client = rl_client.RLClient(canned_job_username, canned_job.get('password'))
        logging.info('Done.')

        reports = client.get_reports(canned_job.get('folder'))
        for report in reports:
            logging.info("'Submitting report '{}'...")
            client.submit_report(report.get('id'))
            logging.info('Done.')
