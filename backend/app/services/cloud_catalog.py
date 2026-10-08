"""Deterministic cloud service catalog — AI may only pick from here. No generic tech."""
from typing import Dict, List

# Logical layer -> platform -> candidate services
CATALOG: Dict[str, Dict[str, List[str]]] = {
    "frontend": {
        "aws": ["Amplify Hosting", "CloudFront + S3", "Vercel (external)"],
        "azure": ["Static Web Apps", "Front Door + Blob Storage"],
        "gcp": ["Firebase Hosting", "Cloud CDN + Cloud Storage"],
    },
    "backend": {
        "aws": ["ECS Fargate", "Lambda", "EKS"],
        "azure": ["Container Apps", "Functions", "AKS"],
        "gcp": ["Cloud Run", "Cloud Functions", "GKE"],
    },
    "api": {
        "aws": ["API Gateway", "AppSync"],
        "azure": ["API Management", "Container Apps Ingress"],
        "gcp": ["API Gateway", "Apigee"],
    },
    "database": {
        "aws": ["RDS for PostgreSQL", "DynamoDB", "Aurora PostgreSQL"],
        "azure": ["Azure Database for PostgreSQL", "Cosmos DB"],
        "gcp": ["Cloud SQL for PostgreSQL", "Firestore", "AlloyDB"],
    },
    "storage": {
        "aws": ["S3", "EFS"],
        "azure": ["Blob Storage", "Azure Files"],
        "gcp": ["Cloud Storage", "Filestore"],
    },
    "iam": {
        "aws": ["Cognito", "IAM + SSO"],
        "azure": ["Entra ID", "Azure RBAC"],
        "gcp": ["Identity Platform", "Cloud IAM"],
    },
    "messaging": {
        "aws": ["SQS + SNS", "EventBridge", "MSK"],
        "azure": ["Service Bus", "Event Grid", "Event Hubs"],
        "gcp": ["Pub/Sub", "Eventarc"],
    },
    "integration": {
        "aws": ["AppFlow", "EventBridge Pipes", "Step Functions"],
        "azure": ["Logic Apps", "Service Bus", "Data Factory"],
        "gcp": ["Application Integration", "Workflows", "Dataflow"],
    },
    "ai_ml": {
        "aws": ["Bedrock", "SageMaker"],
        "azure": ["Azure OpenAI Service", "AI Search"],
        "gcp": ["Vertex AI", "Gemini API"],
    },
    "observability": {
        "aws": ["CloudWatch + X-Ray"],
        "azure": ["Application Insights + Monitor"],
        "gcp": ["Cloud Monitoring + Trace"],
    },
    "security": {
        "aws": ["WAF + Shield", "Secrets Manager", "KMS"],
        "azure": ["Front Door WAF", "Key Vault", "Defender for Cloud"],
        "gcp": ["Cloud Armor", "Secret Manager", "Security Command Center"],
    },
    "deployment": {
        "aws": ["CodePipeline + ECR", "CDK"],
        "azure": ["DevOps Pipelines + ACR", "Bicep"],
        "gcp": ["Cloud Build + Artifact Registry", "Terraform"],
    },
    "environments": {
        "aws": ["Multi-account (dev/test/prod) + Organizations"],
        "azure": ["Subscriptions (dev/test/prod) + Management Groups"],
        "gcp": ["Projects (dev/test/prod) + Folders"],
    },
    "availability": {
        "aws": ["Multi-AZ + ALB autoscaling"],
        "azure": ["Availability Zones + Front Door"],
        "gcp": ["Multi-region + Global LB autoscaling"],
    },
    "backup_dr": {
        "aws": ["Backup + RDS snapshots + Route53 failover"],
        "azure": ["Recovery Services Vault + geo-restore"],
        "gcp": ["Backup and DR Service + regional failover"],
    },
}

REQUIRED_LAYERS = ["frontend", "backend", "api", "database", "iam", "observability", "security", "deployment"]


def catalog_for(platform: str) -> Dict[str, List[str]]:
    return {layer: svcs.get(platform, []) for layer, svcs in CATALOG.items()}


def validate_platform_services(platform: str, components: list) -> List[str]:
    """Return component IDs using services outside the catalog (unsupported)."""
    bad = []
    for c in components:
        layer = c.get("layer") if isinstance(c, dict) else c.layer
        svc = c.get("cloud_service") if isinstance(c, dict) else c.cloud_service
        cid = c.get("component_id", "?") if isinstance(c, dict) else c.component_id
        allowed = CATALOG.get(layer, {}).get(platform, [])
        if allowed and not any(a.lower() in svc.lower() or svc.lower() in a.lower() for a in allowed):
            bad.append(cid)
    return bad


def recommend_platform(requirement_types: List[str]) -> str:
    """Deterministic recommender — transparent rule, AI explains on top."""
    text = " ".join(requirement_types).lower()
    if "entra" in text or "microsoft" in text or ".net" in text:
        return "azure"
    if "bigquery" in text or "vertex" in text or "gcp" in text:
        return "gcp"
    return "aws"
