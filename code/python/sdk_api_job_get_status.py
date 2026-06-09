from galtea import Galtea
from galtea.domain.exceptions.entity_not_found_exception import EntityNotFoundException

galtea = Galtea(api_key="YOUR_API_KEY")

# job_id is the value returned as result["jobId"] from evaluations.run()
job_id = "YOUR_JOB_ID"

# @start get_status
try:
    status = galtea.jobs.get_status(job_id=job_id)
    print(f"State:    {status.state}")
    print(f"Progress: {status.progress}")
    if status.error:
        print(f"Error:    {status.error}")
    if status.result:
        print(f"Result:   {status.result}")
except EntityNotFoundException:
    print("Job not found.")
# @end get_status
