#!/bin/bash
set -e

ECR_REGISTRY="754724220380.dkr.ecr.ap-southeast-2.amazonaws.com"
ECR_REPOSITORY="watchme-api-avatar-uploader"
AWS_REGION="ap-southeast-2"
CONTAINER_NAME="watchme-avatar-uploader"

echo "=== ${CONTAINER_NAME} deployment ==="

# ECR login
echo "Logging in to ECR..."
aws ecr get-login-password --region $AWS_REGION | \
  docker login --username AWS --password-stdin $ECR_REGISTRY

# Pull latest image
echo "Pulling latest image..."
docker pull --platform linux/arm64 $ECR_REGISTRY/$ECR_REPOSITORY:latest

# Stop and remove existing container
echo "Stopping existing container..."
docker-compose -f docker-compose.prod.yml down || true

# Remove old image
docker rmi $ECR_REGISTRY/$ECR_REPOSITORY:latest 2>/dev/null || true

# Ensure network exists
docker network create watchme-network 2>/dev/null || true

# Start new container
echo "Starting new container..."
docker-compose -f docker-compose.prod.yml up -d

# Health check (max 60s)
echo "Running health check..."
sleep 5
for i in {1..12}; do
  if curl -f http://localhost:8014/health > /dev/null 2>&1; then
    echo "Health check passed (attempt $i/12)"
    break
  fi
  echo "  Attempt $i/12 failed, retrying in 5 seconds..."
  sleep 5
done

echo "=== Deployment complete ==="
echo "Health: http://localhost:8014/health"
echo "External: https://api.hey-watch.me/avatar/"
