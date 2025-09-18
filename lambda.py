import boto3
import os

ecr = boto3.client("ecr")

def lambda_handler(event, context):
    repositories = os.environ.get("ECR_REPOSITORIES")
    images_to_keep = int(os.environ.get("IMAGES_TO_KEEP", "10"))

    if not repositories:
        raise ValueError("ECR_REPOSITORIES environment variable is required")

    repo_list = [repo.strip() for repo in repositories.split(",")]

    results = {}
    for repository_name in repo_list:
        results[repository_name] = cleanup_repository(repository_name, images_to_keep)

    return results


def cleanup_repository(repository_name, images_to_keep):
    # Get all images sorted by pushedAt (latest first)
    paginator = ecr.get_paginator("describe_images")
    response_iterator = paginator.paginate(
        repositoryName=repository_name,
        PaginationConfig={"PageSize": 100}
    )

    image_details = []
    for page in response_iterator:
        image_details.extend(page.get("imageDetails", []))

    if not image_details:
        print(f"[{repository_name}] No images found.")
        return {"deleted": 0, "kept": 0}

    # Sort by pushedAt descending
    image_details.sort(key=lambda x: x.get("imagePushedAt", 0), reverse=True)

    # Split into keep vs delete
    images_to_delete = image_details[images_to_keep:]

    if not images_to_delete:
        print(f"[{repository_name}] Nothing to delete. Keeping {images_to_keep}.")
        return {"deleted": 0, "kept": images_to_keep}

    # Collect image digests for deletion
    delete_batch = [
        {"imageDigest": img["imageDigest"]}
        for img in images_to_delete
    ]

    deleted = 0
    for i in range(0, len(delete_batch), 100):
        batch = delete_batch[i:i+100]
        resp = ecr.batch_delete_image(
            repositoryName=repository_name,
            imageIds=batch
        )
        deleted += len(resp.get("imageIds", []))

    print(f"[{repository_name}] Deleted {deleted} old images. Kept {images_to_keep}.")
    return {"deleted": deleted, "kept": images_to_keep}
