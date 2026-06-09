from galtea import Galtea
from galtea.domain.exceptions.entity_not_found_exception import EntityNotFoundException
from galtea.domain.exceptions.job_already_terminal_exception import JobAlreadyTerminalException

galtea = Galtea(api_key="YOUR_API_KEY")

# job_id is the value returned as result["jobId"] from evaluations.run()
job_id = "YOUR_JOB_ID"

# @start cancel_basic
try:
    response = galtea.jobs.cancel(job_id=job_id)
    print(f"Job {response.id} is now {response.state}")
except JobAlreadyTerminalException:
    print("Job has already completed or failed — nothing to cancel.")
except EntityNotFoundException:
    print("Job not found.")
# @end cancel_basic

# @start cancel_if_running
# Check whether the job is still running before deciding to cancel
status = galtea.jobs.get_status(job_id=job_id)
print(f"Job state: {status.state}  progress: {status.progress}")

terminal_states = {"completed", "failed", "cancelled"}
if status.state not in terminal_states:
    try:
        response = galtea.jobs.cancel(job_id=job_id)
        print(f"Cancelled job {response.id}")
    except JobAlreadyTerminalException:
        # The job reached a terminal state between the get_status call and cancel — safe to ignore
        print("Job completed before the cancel request arrived.")
else:
    print(f"Job already in terminal state: {status.state}")
# @end cancel_if_running
