from models.analysis import ProductIdentity, PurposeAnalysis
from models.knowledge import RepositoryKnowledge
from models.evidence import RepositoryEvidence
from services.evidence.extractor import EvidenceExtractor

class PurposeAnalyzer:
    """
    Generates an evidence-based explanation of the repository.
    """
    def __init__(self):
        self.extractor = EvidenceExtractor()

    def analyze(
        self,
        knowledge: RepositoryKnowledge,
        product: ProductIdentity,
    ) -> PurposeAnalysis:

        return PurposeAnalysis(
            what=self._build_what(product),
            why=self._build_why(knowledge),
            audience=self._build_audience(knowledge),
            problem=self._build_problem(knowledge),
            capabilities=self._build_capabilities(knowledge),
            technology_story=self._build_technology_story(knowledge),
            confidence=self._calculate_confidence(knowledge),
        )

    def _build_what(
        self,
        product: ProductIdentity,
    ) -> str:
        return product.summary
    
    def _build_why(
        self,
        knowledge: RepositoryKnowledge,
    ) -> str:

        evidence = self.extractor.extract(knowledge)

        readme = evidence.readme.lower()
        description = evidence.description.lower()

        text = f"{description}\n{readme}"

        purpose_keywords = {
            "automate": "to automate repetitive development tasks",
            "automation": "to automate repetitive development tasks",
            "analyze": "to analyze software repositories",
            "analysis": "to analyze software repositories",
            "monitor": "to monitor systems and applications",
            "dashboard": "to provide insights through dashboards",
            "visualize": "to visualize complex information",
            "deploy": "to simplify application deployment",
            "manage": "to simplify project management",
            "learn": "to support learning and education",
            "education": "to support learning and education",
            "template": "to provide a reusable project template",
            "starter": "to provide a reusable project template",
            "generator": "to generate code or project assets",
            "documentation": "to improve project documentation",
            "testing": "to improve software quality through testing",
            "api": "to expose functionality through APIs",
        }

        for keyword, purpose in purpose_keywords.items():
            if keyword in text:
                return (
                    f"This project appears to have been built {purpose}, "
                    "based on the repository documentation and detected project characteristics."
                )

        if evidence.frontend and evidence.backend:
            return (
                "This project appears to have been built to deliver a complete full-stack application, "
                "although the repository does not explicitly state its original motivation."
            )

        if evidence.backend:
            return (
                "This project appears to have been built to provide backend services or APIs, "
                "although the repository does not explicitly describe its original motivation."
            )

        if evidence.frontend:
            return (
                "This project appears to have been built to deliver a frontend user interface, "
                "although the repository does not explicitly describe its original motivation."
            )

        return (
            "Insufficient repository evidence is available to determine the original motivation for this project."
        )

    def _build_audience(
        self,
        knowledge: RepositoryKnowledge,
    ) -> str:

        evidence = self.extractor.extract(knowledge)

        audiences = set()

        frontend = [t.lower() for t in evidence.frontend]
        backend = [t.lower() for t in evidence.backend]
        databases = [t.lower() for t in evidence.databases]
        cloud = [t.lower() for t in evidence.cloud]
        cicd = [t.lower() for t in evidence.cicd]
        topics = [t.lower() for t in evidence.topics]

        # Frontend
        if frontend:
            audiences.add("frontend developers")

        # Backend
        if backend:
            audiences.add("backend developers")

        # Database
        if databases:
            audiences.add("database engineers")

        # Cloud / DevOps
        if cloud or cicd:
            audiences.add("DevOps engineers")

        # AI / ML
        ml_keywords = {
            "tensorflow",
            "pytorch",
            "keras",
            "scikit-learn",
            "machine-learning",
            "deep-learning",
            "artificial-intelligence",
            "ai",
        }

        if any(k in topics for k in ml_keywords):
            audiences.add("machine learning engineers")

        # Mobile
        mobile_keywords = {
            "flutter",
            "android",
            "ios",
            "swift",
            "kotlin",
            "react native",
        }

        if (
            any(t in mobile_keywords for t in frontend)
            or any(t in mobile_keywords for t in backend)
            or any(t in mobile_keywords for t in topics)
        ):
            audiences.add("mobile developers")

        # Library / SDK
        library_keywords = {
            "library",
            "sdk",
            "package",
            "framework",
        }

        if any(k in topics for k in library_keywords):
            audiences.add("software developers integrating this project")

        if not audiences:
            return (
                "The repository appears to target general software developers, "
                "although no specific audience is explicitly documented."
            )

        audience_list = sorted(audiences)

        if len(audience_list) == 1:
            return f"This repository is primarily intended for {audience_list[0]}."

        return (
            "This repository is primarily intended for "
            + ", ".join(audience_list[:-1])
            + f", and {audience_list[-1]}."
        )

    def _build_problem(
        self,
        knowledge: RepositoryKnowledge,
    ) -> str:

        evidence = self.extractor.extract(knowledge)

        text = (
            f"{evidence.description}\n{evidence.readme}"
        ).lower()

        problem_patterns = {
            (
                "repository",
                "analysis",
            ): (
                "This project addresses the challenge of understanding and analyzing software repositories by automating repository inspection and presenting actionable insights."
            ),

            (
                "monitor",
                "monitoring",
            ): (
                "This project addresses the challenge of monitoring systems, applications, or infrastructure by centralizing operational information."
            ),

            (
                "dashboard",
                "analytics",
            ): (
                "This project helps users interpret complex information through dashboards and analytical visualizations."
            ),

            (
                "authentication",
                "login",
                "jwt",
                "oauth",
            ): (
                "This project simplifies user authentication and authorization for modern applications."
            ),

            (
                "ecommerce",
                "shopping",
                "cart",
                "order",
                "payment",
            ): (
                "This project addresses common challenges involved in building and managing an e-commerce platform."
            ),

            (
                "api",
                "rest",
                "graphql",
            ): (
                "This project exposes application functionality through well-defined APIs for easier system integration."
            ),

            (
                "automation",
                "automate",
            ): (
                "This project reduces manual effort by automating repetitive software development or operational tasks."
            ),

            (
                "machine learning",
                "deep learning",
                "tensorflow",
                "pytorch",
            ): (
                "This project applies machine learning techniques to automate prediction, classification, or intelligent decision making."
            ),

            (
                "portfolio",
                "personal website",
            ): (
                "This project provides an online platform for presenting personal work, projects, and professional experience."
            ),

            (
                "documentation",
                "docs",
            ): (
                "This project improves software usability by organizing and presenting project documentation."
            ),
        }

        for keywords, explanation in problem_patterns.items():
            if any(keyword in text for keyword in keywords):
                return explanation

        if evidence.frontend and evidence.backend:
            return (
                "This repository appears to solve a business or application workflow by combining a frontend user interface with backend services."
            )

        if evidence.backend:
            return (
                "This repository appears to solve backend application or API-related problems, although the repository does not explicitly describe its primary objective."
            )

        if evidence.frontend:
            return (
                "This repository appears to solve user interface or user experience challenges, although the repository does not explicitly describe its primary objective."
            )

        return (
            "Insufficient repository evidence is available to determine the primary problem this project aims to solve."
        )

    def _build_capabilities(
        self,
        knowledge: RepositoryKnowledge,
    ) -> list[str]:

        evidence = self.extractor.extract(knowledge)

        capabilities = set()

        readme = evidence.readme.lower()
        description = evidence.description.lower()

        text = f"{description}\n{readme}"

        frontend = [x.lower() for x in evidence.frontend]
        backend = [x.lower() for x in evidence.backend]
        databases = [x.lower() for x in evidence.databases]
        cloud = [x.lower() for x in evidence.cloud]
        cicd = [x.lower() for x in evidence.cicd]

        structure = evidence.structure

        directories = [
            d.lower()
            for d in structure.get("major_directories", [])
        ]

        # ---------- Frontend ----------

        if frontend:
            capabilities.add("Interactive User Interface")

        if "react" in frontend:
            capabilities.add("Component-Based Frontend")

        if "next.js" in frontend:
            capabilities.add("Server-Side Rendering")

        if "vue" in frontend:
            capabilities.add("Reactive Frontend")

        # ---------- Backend ----------

        if backend:
            capabilities.add("Backend Services")

        if "fastapi" in backend:
            capabilities.add("REST API")

        if "spring boot" in backend:
            capabilities.add("Enterprise Backend")

        if "express" in backend:
            capabilities.add("Web API")

        # ---------- Database ----------

        if databases:
            capabilities.add("Data Persistence")

        # ---------- Cloud ----------

        if cloud:
            capabilities.add("Cloud Deployment")

        # ---------- CI/CD ----------

        if cicd:
            capabilities.add("Continuous Integration")

        # ---------- Folder Structure ----------

        if "api" in directories:
            capabilities.add("API Layer")

        if "services" in directories:
            capabilities.add("Business Logic Layer")

        if "controllers" in directories:
            capabilities.add("Request Handling")

        if "models" in directories:
            capabilities.add("Domain Modeling")

        if "database" in directories or "db" in directories:
            capabilities.add("Database Management")

        if "auth" in directories:
            capabilities.add("Authentication")

        if "middleware" in directories:
            capabilities.add("Request Middleware")

        if "tests" in directories:
            capabilities.add("Automated Testing")

        if "docs" in directories:
            capabilities.add("Documentation")

        if "scripts" in directories:
            capabilities.add("Automation Scripts")

        # ---------- README Keywords ----------

        keyword_map = {
            "authentication": "Authentication",
            "authorization": "Authorization",
            "jwt": "JWT Authentication",
            "oauth": "OAuth Integration",
            "docker": "Containerization",
            "websocket": "Real-Time Communication",
            "graphql": "GraphQL API",
            "cli": "Command Line Interface",
            "machine learning": "Machine Learning",
            "deep learning": "Deep Learning",
            "analytics": "Analytics",
            "dashboard": "Dashboard",
            "visualization": "Data Visualization",
            "notification": "Notifications",
            "email": "Email Integration",
            "payment": "Payment Processing",
            "chat": "Messaging",
            "search": "Search",
            "upload": "File Upload",
            "export": "Data Export",
        }

        for keyword, capability in keyword_map.items():
            if keyword in text:
                capabilities.add(capability)

        return sorted(capabilities)

    def _build_technology_story(
        self,
        knowledge: RepositoryKnowledge,
    ) -> str:

        evidence = self.extractor.extract(knowledge)

        story = []

        frontend = evidence.frontend
        backend = evidence.backend
        databases = evidence.databases
        cloud = evidence.cloud
        cicd = evidence.cicd

        if frontend:
            story.append(
                f"{', '.join(frontend)} powers the user interface and client-side experience."
            )

        if backend:
            story.append(
                f"{', '.join(backend)} provides the application's backend services and business logic."
            )

        if databases:
            story.append(
                f"{', '.join(databases)} is used for persistent data storage and retrieval."
            )

        if cloud:
            story.append(
                f"{', '.join(cloud)} supports deployment and cloud infrastructure."
            )

        if cicd:
            story.append(
                f"{', '.join(cicd)} automates continuous integration and deployment workflows."
            )

        architecture = evidence.architecture.get("pattern")

        if architecture:
            story.append(
                f"The repository follows a {architecture} architectural pattern to organize responsibilities."
            )

        if not story:
            return (
                "Insufficient repository evidence is available to explain how the detected technologies work together."
            )

        return " ".join(story)

    def _calculate_confidence(
        self,
        knowledge: RepositoryKnowledge,
    ) -> float:
        return 0.0