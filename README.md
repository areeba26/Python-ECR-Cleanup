# Python-ECR-Cleanup  

**Python-ECR-Cleanup** is a lightweight Python script designed to automate cleanup of Amazon ECR images. It deletes untagged or outdated images, supports custom cleanup policies, and helps optimize storage and reduce costs using AWS boto3.  

## 🚀 How It Works  
The script is intended to run as an **AWS Lambda function** (but can also be adapted for local use). It connects to ECR, lists all images in the specified repositories, and removes older ones while keeping only the latest **N** images per repository.  

- Images are sorted by `pushedAt` timestamp (latest first).  
- Only the most recent **N** images are kept (default: 10).  
- Older images are deleted in safe batches (100 at a time).  
- If no images exist, the script exits gracefully.  

## ⚙️ Environment Variables  
You can configure the cleanup behavior using environment variables:  

- **`ECR_REPOSITORIES`** *(required)*  
  Comma-separated list of ECR repository names to clean.  
  - Example:  
    ```bash
    ECR_REPOSITORIES="my-app-backend,my-app-frontend"
    ```  

- **`IMAGES_TO_KEEP`** *(optional, default: `10`)*  
  Number of latest images to retain per repository.  
  - Example:  
    ```bash
    IMAGES_TO_KEEP=5
    ```  

## 📝 Example Behavior  
If `ECR_REPOSITORIES="my-service"` and `IMAGES_TO_KEEP=3`:  
- The script fetches all images from **my-service**.  
- Keeps the 3 most recent ones.  
- Deletes the rest in safe batches.  
- Logs actions with counts of deleted and kept images.  

## 🔒 AWS Permissions Required  
The Lambda/role running this script needs at least:  
- `ecr:DescribeImages`  
- `ecr:BatchDeleteImage`  
