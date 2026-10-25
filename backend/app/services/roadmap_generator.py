from typing import List, Dict, Any
from dataclasses import dataclass, field

@dataclass
class RoadmapItem:
    skill_name: str
    priority: str # "high", "medium", "low"
    why_it_matters: str
    prerequisites: List[str]
    suggested_tasks: List[str]
    mini_project: str
    completion_criterion: str
    estimated_duration: str


class RoadmapGeneratorService:
    def __init__(self):
        pass

    def generate_roadmap(self, skill_assessments: List[Dict[str, Any]], job_title: str = "Target Role") -> List[RoadmapItem]:
        """
        Generates an actionable, prioritized preparation plan specifically targeting identified skill gaps.
        """
        # Focus on skills not found or partially demonstrated
        gap_items = [
            a for a in skill_assessments
            if a.get("classification") in ["Not found in resume", "Partially demonstrated", "Uncertain"]
        ]

        # Sort gaps: mandatory first, then partially demonstrated, then others
        def gap_sort_key(item):
            priority_score = 0 if item.get("priority") == "mandatory" else 1
            status_score = 0 if item.get("classification") == "Partially demonstrated" else 1
            return (priority_score, status_score)

        gap_items.sort(key=gap_sort_key)

        roadmap: List[RoadmapItem] = []

        for item in gap_items[:6]: # Top prioritized gaps
            skill = item.get("requirement_text", "Technical Skill")
            category = item.get("category", "General")
            priority = "high" if item.get("priority") == "mandatory" else "medium"
            status = item.get("classification", "Not found in resume")

            # Domain tailored tasks and mini-projects
            prereqs, tasks, mini_project, criterion, duration = self._generate_skill_specific_plan(skill, category, status)

            why_matters = (
                f"Required as a {item.get('priority', 'mandatory')} qualification for {job_title}. "
                f"Closing this gap transforms an unevidenced requirement into demonstrable project experience."
            )

            roadmap.append(RoadmapItem(
                skill_name=skill,
                priority=priority,
                why_it_matters=why_matters,
                prerequisites=prereqs,
                suggested_tasks=tasks,
                mini_project=mini_project,
                completion_criterion=criterion,
                estimated_duration=duration
            ))

        return roadmap

    def _generate_skill_specific_plan(self, skill: str, category: str, status: str):
        skill_lower = skill.lower()

        if "docker" in skill_lower or "container" in skill_lower:
            return (
                ["Basic Linux command line", "Any web application stack"],
                [
                    "Understand containerization vs virtualization, image layers, and Dockerfile syntax",
                    "Write multi-stage Dockerfiles for frontend (Node/Nginx) and backend services",
                    "Configure Docker Compose for local multi-service networking and volumes"
                ],
                "Dockerize a full-stack CRUD application with separate frontend, API, and database services connected via docker-compose.",
                "Application runs cleanly via `docker compose up` with non-root user and persistent database volumes.",
                "Estimated: 1-2 weeks (part-time)"
            )
        elif "kubernetes" in skill_lower or "k8s" in skill_lower:
            return (
                ["Docker containerization", "Networking fundamentals"],
                [
                    "Learn Pods, Deployments, Services (ClusterIP/NodePort), and ConfigMaps/Secrets",
                    "Run a local Minikube or Kind cluster and deploy sample apps",
                    "Configure Horizontal Pod Autoscaling (HPA) and rolling updates"
                ],
                "Deploy a multi-tier microservice architecture to a local Minikube cluster with ConfigMaps and health probes.",
                "Zero-downtime rolling update tested successfully with active curl requests.",
                "Estimated: 2-3 weeks (part-time)"
            )
        elif "spring boot" in skill_lower or "java" in skill_lower:
            return (
                ["Core Java (OOP, Collections, Streams, Exceptions)"],
                [
                    "Build RESTful APIs with Spring Web, Spring Data JPA, and Hibernate",
                    "Implement secure JWT-based authentication and role-based access control",
                    "Write integration tests with Testcontainers and JUnit 5"
                ],
                "Develop an authenticated E-Commerce Inventory Service with PostgreSQL and pagination.",
                "Swagger documentation live, all CRUD endpoints covered with >80% JUnit tests.",
                "Estimated: 2-3 weeks (part-time)"
            )
        elif "react" in skill_lower or "typescript" in skill_lower:
            return (
                ["Modern JavaScript (ES6+, Promises, Async/Await)"],
                [
                    "Master TypeScript interfaces, generics, and strict type checking",
                    "Implement state management and clean custom hooks with React 18+",
                    "Build reusable accessible components with Tailwind CSS"
                ],
                "Build an interactive task management dashboard with filtering, search, and local storage sync.",
                "Strict TypeScript build passes with zero `any` types and responsive mobile layout.",
                "Estimated: 1-2 weeks (part-time)"
            )
        elif "sql" in skill_lower or "postgresql" in skill_lower or "database" in skill_lower:
            return (
                ["Relational data modeling concepts"],
                [
                    "Practice complex multi-table JOINs, subqueries, and window functions",
                    "Analyze query performance using EXPLAIN ANALYZE and design composite indexes",
                    "Understand ACID transactions, isolation levels, and foreign key cascades"
                ],
                "Design a normalized schema for an Analytics platform with indexing and performance benchmarks on 100k rows.",
                "Demonstrate 10x query acceleration using EXPLAIN ANALYZE index optimization.",
                "Estimated: 1-2 weeks (part-time)"
            )
        elif "aws" in skill_lower or "cloud" in skill_lower:
            return (
                ["Basic networking, DNS, and HTTP protocol"],
                [
                    "Explore core services: EC2, S3, RDS, Lambda, and IAM least-privilege policies",
                    "Set up an automated CI/CD pipeline deploying code to cloud compute",
                    "Configure CloudWatch logs and alerts for application monitoring"
                ],
                "Deploy a containerized application to AWS ECS or App Runner backed by Amazon RDS.",
                "Working HTTPS URL live with automated GitHub Actions continuous deployment.",
                "Estimated: 2-3 weeks (part-time)"
            )
        else:
            return (
                [f"Fundamentals related to {category.replace('_', ' ').title()}"],
                [
                    f"Read official documentation and architectural best practices for {skill}",
                    f"Implement 2-3 focused coding exercises testing real-world problem scenarios in {skill}",
                    f"Integrate {skill} into an existing portfolio project"
                ],
                f"Build a standalone working prototype or integration test suite demonstrating practical mastery of {skill}.",
                f"Code pushed to GitHub with detailed README explaining trade-offs and architectural design.",
                "Estimated: 1-2 weeks (part-time)"
            )
