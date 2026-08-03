from typing import List

from models.architecture_blueprint import (
    ArchitectureBlueprint,
    ArchitectureLayer,
    ComponentNode,
    DependencyEdge,
    CommunicationPath,
    ExternalService,
    DataFlowStep,
)

from models.intelligence import RepositoryKnowledge


class ArchitectureBlueprintBuilder:
    """
    Builds a deterministic architecture blueprint
    entirely from RepositoryKnowledge.

    Never accesses raw GitHub API responses.
    """

    def build(self, knowledge: RepositoryKnowledge) -> ArchitectureBlueprint:
        architecture_type, confidence = self._infer_architecture(knowledge)

        layers = self._infer_layers(knowledge)

        components = self._infer_components(layers)

        dependencies = self._infer_dependencies(layers)

        communication = self._infer_communication(
            architecture_type,
            layers,
            knowledge,
        )

        entrypoints = self._infer_entrypoints(knowledge)

        external_services = self._infer_external_services(knowledge)

        data_flow = self._infer_data_flow(
            architecture_type,
            layers,
            knowledge,
        )

        return ArchitectureBlueprint(
            architecture_type=architecture_type,
            confidence=confidence,
            layers=layers,
            components=components,
            dependencies=dependencies,
            communication=communication,
            entrypoints=entrypoints,
            external_services=external_services,
            data_flow=data_flow,
        )

    # ------------------------------------------------------------------
    # Architecture Type
    # ------------------------------------------------------------------

    def _infer_architecture(
        self,
        knowledge: RepositoryKnowledge,
    ) -> tuple[str, float]:

        directories = {
            d.lower()
            for d in getattr(
                knowledge.structure,
                "major_directories",
                [],
            )
        }

        if {"apps", "packages"} <= directories:
            return "Monorepo", 0.98

        if "services" in directories:
            return "Microservices", 0.95

        if (
            "frontend" in directories
            and "backend" in directories
        ):
            return "Client-Server", 0.96

        if (
            "client" in directories
            and "server" in directories
        ):
            return "Client-Server", 0.96

        if (
            "api" in directories
            and (
                "web" in directories
                or "frontend" in directories
            )
        ):
            return "Full Stack", 0.93

        if (
            "lambda" in directories
            or "functions" in directories
            or "serverless" in directories
        ):
            return "Serverless", 0.92

        return "Layered Application", 0.75

    # ------------------------------------------------------------------
    # Layers
    # ------------------------------------------------------------------

    def _infer_layers(
        self,
        knowledge: RepositoryKnowledge,
    ) -> List[ArchitectureLayer]:

        directories = getattr(
            knowledge.structure,
            "major_directories",
            [],
        )

        layers = []

        layer_map = {
            "frontend": (
                "Presentation",
                [
                    "frontend",
                    "web",
                    "client",
                    "ui",
                    "components",
                ],
            ),
            "backend": (
                "Backend",
                [
                    "backend",
                    "api",
                    "server",
                ],
            ),
            "services": (
                "Service",
                [
                    "services",
                    "service",
                ],
            ),
            "database": (
                "Persistence",
                [
                    "database",
                    "db",
                    "repositories",
                    "models",
                ],
            ),
            "infrastructure": (
                "Infrastructure",
                [
                    "docker",
                    ".github",
                    "k8s",
                    "terraform",
                ],
            ),
        }

        for _, (layer_name, matches) in layer_map.items():
            found = []

            for directory in directories:
                if directory.lower() in matches:
                    found.append(directory)

            if found:
                layers.append(
                    ArchitectureLayer(
                        name=layer_name,
                        type=layer_name,
                        directories=found,
                    )
                )

        if not layers:
            layers.append(
                ArchitectureLayer(
                    name="Application",
                    type="Application",
                    directories=directories,
                )
            )

        return layers

    # ------------------------------------------------------------------
    # Components
    # ------------------------------------------------------------------

    def _infer_components(
        self,
        layers: List[ArchitectureLayer],
    ) -> List[ComponentNode]:

        components = []

        index = 1

        for layer in layers:
            for directory in layer.directories:
                components.append(
                    ComponentNode(
                        id=f"C{index}",
                        name=directory,
                        category=layer.name,
                        directory=directory,
                    )
                )
                index += 1

        return components

    # ------------------------------------------------------------------
    # Dependencies
    # ------------------------------------------------------------------

    def _infer_dependencies(
        self,
        layers: List[ArchitectureLayer],
    ) -> List[DependencyEdge]:

        dependencies = []

        for i in range(len(layers) - 1):
            dependencies.append(
                DependencyEdge(
                    source=layers[i].name,
                    target=layers[i + 1].name,
                    relation="depends_on",
                )
            )

        return dependencies

    # ------------------------------------------------------------------
    # Communication
    # ------------------------------------------------------------------

    def _infer_communication(
        self,
        architecture: str,
        layers: List[ArchitectureLayer],
        knowledge: RepositoryKnowledge,
    ) -> List[CommunicationPath]:

        communication = []

        layer_names = {
            layer.name.lower()
            for layer in layers
        }

        if (
            "presentation" in layer_names
            and "backend" in layer_names
        ):
            communication.append(
                CommunicationPath(
                    source="Presentation",
                    target="Backend",
                    protocol="HTTP/REST",
                )
            )

        if (
            "backend" in layer_names
            and "persistence" in layer_names
        ):
            communication.append(
                CommunicationPath(
                    source="Backend",
                    target="Persistence",
                    protocol="Database Driver",
                )
            )

        return communication

    # ------------------------------------------------------------------
    # Entrypoints
    # ------------------------------------------------------------------

    def _infer_entrypoints(
        self,
        knowledge: RepositoryKnowledge,
    ) -> List[str]:

        tree = getattr(knowledge, "tree", None)

        if tree is None:
            return []

        entrypoints = []

        candidates = {
            "main.py",
            "app.py",
            "server.py",
            "manage.py",
            "index.js",
            "index.ts",
            "index.tsx",
            "main.ts",
            "main.tsx",
            "server.js",
            "server.ts",
        }

        def visit(node):
            name = getattr(node, "name", "")

            if name in candidates:
                entrypoints.append(name)

            for child in getattr(node, "children", []):
                visit(child)

        visit(tree)

        return sorted(set(entrypoints))

    # ------------------------------------------------------------------
    # External Services
    # ------------------------------------------------------------------

    def _infer_external_services(
        self,
        knowledge: RepositoryKnowledge,
    ) -> List[ExternalService]:

        services = []

        tech = knowledge.tech_stack

        for database in getattr(
            tech,
            "database",
            [],
        ):
            services.append(
                ExternalService(
                    name=database,
                    type="Database",
                )
            )

        for cloud in getattr(
            tech,
            "cloud",
            [],
        ):
            services.append(
                ExternalService(
                    name=cloud,
                    type="Cloud",
                )
            )

        return services

    # ------------------------------------------------------------------
    # Data Flow
    # ------------------------------------------------------------------

    def _infer_data_flow(
        self,
        architecture: str,
        layers: List[ArchitectureLayer],
        knowledge: RepositoryKnowledge,
    ) -> List[DataFlowStep]:

        flow = []

        layer_names = [
            layer.name
            for layer in layers
        ]

        order = 1

        if "Presentation" in layer_names:
            flow.append(
                DataFlowStep(
                    order=order,
                    source="User",
                    target="Presentation",
                    description="User initiates request",
                )
            )
            order += 1

        if (
            "Presentation" in layer_names
            and "Backend" in layer_names
        ):
            flow.append(
                DataFlowStep(
                    order=order,
                    source="Presentation",
                    target="Backend",
                    description="Frontend sends API request",
                )
            )
            order += 1

        if (
            "Backend" in layer_names
            and "Persistence" in layer_names
        ):
            flow.append(
                DataFlowStep(
                    order=order,
                    source="Backend",
                    target="Persistence",
                    description="Backend reads/writes data",
                )
            )
            order += 1

        if (
            "Persistence" in layer_names
            and "Backend" in layer_names
        ):
            flow.append(
                DataFlowStep(
                    order=order,
                    source="Persistence",
                    target="Backend",
                    description="Database returns results",
                )
            )
            order += 1

        if (
            "Backend" in layer_names
            and "Presentation" in layer_names
        ):
            flow.append(
                DataFlowStep(
                    order=order,
                    source="Backend",
                    target="Presentation",
                    description="Backend returns response",
                )
            )

        return flow