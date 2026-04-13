from google.cloud import aiplatform

#! UPDATE PROJECT ID, LOCATION, GCS BUCKET AND SCRIPT PATH BEFORE RUNNING
aiplatform.init(project="project-id", location="location-id")

job = aiplatform.CustomJob.from_local_script(
    display_name="phishing-gru-training",
    script_path="pytorch_training_script.py",
    container_uri="gcr.io/cloud-aiplatform/training/pytorch-gpu.1-10",
    requirements=["torch", "torchtext", "pandas", "google-cloud-storage"],
    args=[
        "--csv_path", "gs://bucket-name/data/Phishing_Email.csv",
        "--model_output", "gs://bucket-name/output/model.pt",
        "--vocab_output", "gs://bucket-name/output/vocab.json",
    ],
    machine_type="n1-standard-4",
    accelerator_type="NVIDIA_TESLA_T4",
    accelerator_count=1,
)

job.run()