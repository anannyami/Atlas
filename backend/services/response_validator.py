from __future__ import annotations

import re
from collections.abc import Mapping, Sequence
from typing import Any

from models.response_validation import ResponseValidationResult


class ResponseValidator:
    """Heuristically assess response quality against supplied analysis evidence."""

    REQUIRED_SECTIONS = (
        "Short Answer",
        "Repository Overview",
        "Detailed Explanation",
        "Repository Evidence",
        "Engineering Observations",
        "Conclusion",
    )
    SECTION_ALIASES = {
        "Short Answer": ("short answer",),
        "Repository Overview": ("repository overview", "repository context"),
        "Detailed Explanation": ("detailed explanation", "explanation"),
        "Repository Evidence": ("repository evidence", "key repository evidence", "evidence"),
        "Engineering Observations": ("engineering observations", "engineering analysis", "observations"),
        "Conclusion": ("conclusion", "engineering conclusion"),
    }
    GENERIC_PATTERNS = (
        re.compile(r"\bthis repository appears to\b", re.IGNORECASE),
        re.compile(r"\bit seems to\b", re.IGNORECASE),
        re.compile(r"\bin general\b", re.IGNORECASE),
        re.compile(r"\bthis project likely\b", re.IGNORECASE),
        re.compile(r"\bmost repositories\b", re.IGNORECASE),
    )
    ENGINEERING_TERMS = {
        "architecture", "tradeoff", "tradeoffs", "trade-off", "trade-offs",
        "scalability", "scalable", "maintainability", "maintainable", "coupling",
        "cohesion", "latency", "throughput", "modularity", "dependency",
        "dependencies", "boundary", "bottleneck", "failure mode", "operational",
        "security", "testability", "reliability", "migration", "deployment",
    }
    KNOWN_TECH_CLAIM = re.compile(
        r"\b(?:uses?|built with|powered by|implemented in|depends on|requires|stores data in|authenticates with)\s+(?:the\s+)?([A-Z][A-Za-z0-9.+#-]*(?:\s+[A-Z][A-Za-z0-9.+#-]*){0,2})"
    )
    TECHNOLOGY_CANDIDATES = (
        "FastAPI", "Django", "Flask", "Spring Boot", "Express", "NestJS", "React",
        "Vue", "Angular", "Svelte", "Next.js", "Vite", "PostgreSQL", "MySQL",
        "SQLite", "MongoDB", "Redis", "Docker", "Kubernetes", "Terraform", "AWS",
        "Azure", "Google Cloud", "GitHub Actions", "LangChain", "LlamaIndex",
    )
    TOKEN = re.compile(r"[a-z0-9][a-z0-9.+#/-]{2,}", re.IGNORECASE)
    STOP_WORDS = {
        "the", "and", "for", "with", "from", "this", "that", "repository", "project",
        "analysis", "based", "available", "appears", "likely", "confidence", "summary",
        "overview", "purpose", "architecture", "structure", "technology", "technologies",
        "engineering", "evidence", "current", "status", "good", "fair", "high", "low",
    }

    SCORE_WEIGHTS = {
        "structure": 0.18,
        "repository_evidence": 0.18,
        "engineering_reasoning": 0.14,
        "repository_specificity": 0.14,
        "followup_continuity": 0.10,
        "hallucination_control": 0.14,
        "length": 0.06,
        "multi_analyzer_synthesis": 0.06,
    }
    PASS_THRESHOLD = 0.68

    def validate(
        self,
        response: str,
        analysis: Mapping[str, Any],
        question: str,
        *,
        is_follow_up: bool = False,
        conversation_state: Mapping[str, Any] | None = None,
        prior_assistant_responses: Sequence[str] = (),
    ) -> ResponseValidationResult:
        text = response or ""
        word_count = len(re.findall(r"\b[\w+#./-]+\b", text))
        sections = self._extract_sections(text)
        missing_sections = [
            title
            for title in self.REQUIRED_SECTIONS
            if title not in sections or not sections[title].strip()
        ]

        anchors_by_area = self._evidence_anchors(analysis)
        all_anchors = list(dict.fromkeys(anchor for anchors in anchors_by_area.values() for anchor in anchors))
        evidence_matches = [anchor for anchor in all_anchors if self._contains_phrase(text, anchor)]
        evidence_section = sections.get("Repository Evidence", "")
        evidence_section_matches = [anchor for anchor in all_anchors if self._contains_phrase(evidence_section, anchor)]
        populated_analysis_areas = sum(bool(values) for values in anchors_by_area.values())
        limited_analysis = populated_analysis_areas < 3

        missing_repository_evidence: list[str] = []
        if not evidence_section.strip():
            missing_repository_evidence.append("Repository Evidence section is absent or empty.")
        if not evidence_matches and not limited_analysis:
            missing_repository_evidence.append("No specific fact from the supplied analysis was identifiable in the response.")
        if evidence_section.strip() and not evidence_section_matches and not limited_analysis:
            missing_repository_evidence.append("The Repository Evidence section does not match identifiable supplied analysis facts.")

        engineering_observations = sections.get("Engineering Observations", "")
        reasoning_hits = self._term_hits(text, self.ENGINEERING_TERMS)
        missing_engineering_observations = []
        if not engineering_observations.strip():
            missing_engineering_observations.append("Engineering Observations section is absent or empty.")
        elif not self._term_hits(engineering_observations, self.ENGINEERING_TERMS):
            missing_engineering_observations.append("Engineering Observations contains no explicit engineering reasoning signal.")

        generic_matches = [pattern.pattern for pattern in self.GENERIC_PATTERNS if pattern.search(text)]
        generic_reasoning = bool(generic_matches and not evidence_matches)
        supported_tech = self._supported_technology_names(analysis)
        unsupported_claims = self._unsupported_technology_claims(text, supported_tech, question)
        hallucination_risk = min(1.0, 0.25 * len(unsupported_claims))
        if generic_reasoning:
            hallucination_risk = min(1.0, hallucination_risk + 0.25)

        short_requested = self._short_answer_requested(question)
        length_score = self._length_score(word_count, short_requested, limited_analysis)
        state = conversation_state or {}
        continuity_score = self._continuity_score(
            text,
            state,
            prior_assistant_responses,
            is_follow_up,
        )
        matched_areas = [
            area
            for area, anchors in anchors_by_area.items()
            if any(self._contains_phrase(text, anchor) for anchor in anchors)
        ]
        synthesis_score = self._synthesis_score(matched_areas, anchors_by_area)
        structure_score = 1.0 - (len(missing_sections) / len(self.REQUIRED_SECTIONS))
        evidence_score = self._evidence_score(
            evidence_matches,
            evidence_section_matches,
            limited_analysis,
        )
        reasoning_score = min(1.0, len(reasoning_hits) / 3.0)
        specificity_score = self._specificity_score(evidence_matches, limited_analysis)

        category_scores = {
            "structure": structure_score,
            "repository_evidence": evidence_score,
            "engineering_reasoning": reasoning_score,
            "repository_specificity": specificity_score,
            "followup_continuity": continuity_score,
            "hallucination_control": 1.0 - hallucination_risk,
            "length": length_score,
            "multi_analyzer_synthesis": synthesis_score,
        }
        overall_score = round(
            sum(category_scores[name] * weight for name, weight in self.SCORE_WEIGHTS.items()),
            3,
        )

        issues: list[str] = []
        if missing_sections:
            issues.append("Response is missing one or more required contract sections.")
        issues.extend(missing_repository_evidence)
        issues.extend(missing_engineering_observations)
        if not short_requested and not limited_analysis and not 300 <= word_count <= 800:
            issues.append("Response length is outside the expected 300–800 word range.")
        if generic_reasoning:
            issues.append("Generic filler appears without identifiable repository-specific evidence.")
        if unsupported_claims:
            issues.append("Possible unsupported technology claims: " + ", ".join(unsupported_claims) + ".")
        if is_follow_up and continuity_score < 0.5:
            issues.append("Response may not preserve the current follow-up topic or component.")
        if synthesis_score < 0.5 and len([area for area, anchors in anchors_by_area.items() if anchors]) >= 2:
            issues.append("Response appears to rely on too few available analysis areas for synthesis.")

        passed = (
            overall_score >= self.PASS_THRESHOLD
            and not missing_sections
            and evidence_score >= 0.5
            and hallucination_risk < 0.7
            and (not is_follow_up or continuity_score >= 0.5)
        )

        return ResponseValidationResult(
            passed=passed,
            overall_score=overall_score,
            word_count=word_count,
            missing_sections=missing_sections,
            missing_repository_evidence=missing_repository_evidence,
            missing_engineering_observations=missing_engineering_observations,
            generic_reasoning=generic_reasoning,
            hallucination_risk=round(hallucination_risk, 3),
            followup_continuity=round(continuity_score, 3),
            issues=list(dict.fromkeys(issues)),
            category_scores={key: round(value, 3) for key, value in category_scores.items()},
            evidence_matches=evidence_matches[:20],
            synthesized_areas=matched_areas,
        )

    def _extract_sections(self, text: str) -> dict[str, str]:
        headings = list(re.finditer(r"^\s{0,3}#{1,6}\s+(.+?)\s*#*\s*$", text, re.MULTILINE))
        found: dict[str, str] = {}
        normalized_aliases = {
            alias: title
            for title, aliases in self.SECTION_ALIASES.items()
            for alias in aliases
        }
        for index, heading in enumerate(headings):
            heading_text = re.sub(r"\*|_", "", heading.group(1)).strip().lower()
            title = normalized_aliases.get(heading_text)
            if title:
                end = headings[index + 1].start() if index + 1 < len(headings) else len(text)
                found[title] = text[heading.end():end].strip()
        return found

    def _evidence_anchors(self, analysis: Mapping[str, Any]) -> dict[str, list[str]]:
        area_fields = {
            "repository_identity": ("repository", "repository_identity", "product_identity", "classification"),
            "purpose": ("summary", "purpose"),
            "architecture": ("architecture", "blueprint"),
            "technology": ("tech_stack",),
            "structure": ("structure", "repository_tree"),
            "knowledge": ("knowledge",),
            "health": ("health",),
            "activity": ("activity",),
        }
        anchors_by_area: dict[str, list[str]] = {}
        for area, keys in area_fields.items():
            values: list[str] = []
            for key in keys:
                self._collect_strings(analysis.get(key), values)
            anchors: list[str] = []
            anchor_keys: set[str] = set()
            for value in values:
                normalized = " ".join(value.split())
                if 4 <= len(normalized) <= 120 and normalized.lower() not in self.STOP_WORDS:
                    if normalized.lower() not in anchor_keys:
                        anchors.append(normalized)
                        anchor_keys.add(normalized.lower())
                for token in self.TOKEN.findall(normalized):
                    if token.lower() not in self.STOP_WORDS and token.lower() not in anchor_keys:
                        anchors.append(token)
                        anchor_keys.add(token.lower())
                    if len(anchors) >= 80:
                        break
                if len(anchors) >= 80:
                    break
            anchors_by_area[area] = anchors
        return anchors_by_area

    def _collect_strings(self, value: Any, output: list[str]) -> None:
        if isinstance(value, str):
            if value.strip():
                output.append(value.strip())
        elif isinstance(value, Mapping):
            for item in value.values():
                self._collect_strings(item, output)
        elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            for item in value:
                self._collect_strings(item, output)

    def _contains_phrase(self, text: str, phrase: str) -> bool:
        return bool(re.search(rf"(?<!\w){re.escape(phrase)}(?!\w)", text, re.IGNORECASE))

    def _term_hits(self, text: str, terms: set[str]) -> set[str]:
        normalized = text.lower()
        return {term for term in terms if re.search(rf"(?<!\w){re.escape(term)}(?!\w)", normalized)}

    def _supported_technology_names(self, analysis: Mapping[str, Any]) -> set[str]:
        names: set[str] = set()
        tech_stack = analysis.get("tech_stack") or {}
        for category in ("languages", "frontend", "backend", "database", "cloud", "ci_cd", "package_managers", "containers", "mobile"):
            values = tech_stack.get(category, []) if isinstance(tech_stack, Mapping) else []
            if isinstance(values, Sequence) and not isinstance(values, (str, bytes)):
                names.update(str(value).lower() for value in values if value)
        technologies = tech_stack.get("technologies", []) if isinstance(tech_stack, Mapping) else []
        for item in technologies:
            if isinstance(item, Mapping) and item.get("name"):
                names.add(str(item["name"]).lower())
        for category in ("frontend_frameworks", "backend_frameworks", "databases", "cloud", "authentication"):
            for item in (analysis.get("architecture") or {}).get(category, []):
                if isinstance(item, Mapping) and item.get("name"):
                    names.add(str(item["name"]).lower())
        return names

    def _unsupported_technology_claims(
        self,
        text: str,
        supported_names: set[str],
        question: str,
    ) -> list[str]:
        claims: list[str] = []
        question_lower = question.lower()
        question_terms = {match.group(1).lower() for match in self.KNOWN_TECH_CLAIM.finditer(question)}
        for match in self.KNOWN_TECH_CLAIM.finditer(text):
            claimed = match.group(1).strip(".,;:!?()[]{}")
            lowered = claimed.lower()
            if lowered in supported_names or lowered in question_terms:
                continue
            if claimed and claimed not in claims:
                claims.append(claimed)

        for technology in self.TECHNOLOGY_CANDIDATES:
            if technology.lower() in supported_names or technology.lower() in question_lower:
                continue
            for match in re.finditer(rf"(?<!\w){re.escape(technology)}(?!\w)", text, re.IGNORECASE):
                sentence_start = max(text.rfind(".", 0, match.start()), text.rfind("\n", 0, match.start())) + 1
                sentence_end_candidates = [position for position in (text.find(".", match.end()), text.find("\n", match.end())) if position >= 0]
                sentence_end = min(sentence_end_candidates) if sentence_end_candidates else len(text)
                sentence = text[sentence_start:sentence_end].lower()
                if re.search(r"\b(not|no|neither|without|unsupported|unknown|unverified|not evidenced|not detected)\b", sentence):
                    continue
                if technology not in claims:
                    claims.append(technology)
                break
        return claims

    def _short_answer_requested(self, question: str) -> bool:
        return bool(re.search(
            r"\b(briefly|short answer|in one sentence|one sentence|quick answer|tl;dr|keep it concise|be concise)\b",
            question,
            re.IGNORECASE,
        ))

    def _length_score(self, word_count: int, short_requested: bool, limited_analysis: bool) -> float:
        if short_requested or limited_analysis:
            return 1.0 if word_count <= 800 else 800 / max(word_count, 1)
        if 300 <= word_count <= 800:
            return 1.0
        if word_count < 300:
            return word_count / 300
        return 800 / word_count

    def _continuity_score(
        self,
        text: str,
        state: Mapping[str, Any],
        prior_assistant_responses: Sequence[str],
        is_follow_up: bool,
    ) -> float:
        if not is_follow_up:
            return 1.0
        cues = [state.get("current_topic"), state.get("current_component"), state.get("current_user_goal")]
        cue_tokens = {
            token.lower()
            for cue in cues if isinstance(cue, str)
            for token in self.TOKEN.findall(cue)
            if token.lower() not in self.STOP_WORDS
        }
        response_tokens = {token.lower() for token in self.TOKEN.findall(text)}
        topical_overlap = len(cue_tokens & response_tokens) / len(cue_tokens) if cue_tokens else 0.5
        repetition = 0.0
        response_set = response_tokens
        for previous in prior_assistant_responses[-3:]:
            previous_set = {token.lower() for token in self.TOKEN.findall(previous)}
            if response_set and previous_set:
                repetition = max(repetition, len(response_set & previous_set) / len(response_set | previous_set))
        return max(0.0, min(1.0, topical_overlap * (1.0 - min(repetition, 0.8))))

    def _evidence_score(
        self,
        evidence_matches: list[str],
        section_matches: list[str],
        limited_analysis: bool,
    ) -> float:
        if limited_analysis:
            return 0.75 if section_matches or evidence_matches else 0.5
        if not evidence_matches:
            return 0.0
        coverage = min(1.0, len(evidence_matches) / 4.0)
        return min(1.0, 0.4 + 0.4 * coverage + (0.2 if section_matches else 0.0))

    def _specificity_score(self, evidence_matches: list[str], limited_analysis: bool) -> float:
        if evidence_matches:
            return min(1.0, 0.4 + 0.15 * len(evidence_matches))
        return 0.5 if limited_analysis else 0.0

    def _synthesis_score(
        self,
        matched_areas: list[str],
        anchors_by_area: Mapping[str, list[str]],
    ) -> float:
        available_area_count = sum(bool(anchors) for anchors in anchors_by_area.values())
        required_area_count = min(3, available_area_count)
        if required_area_count == 0:
            return 0.5
        return min(1.0, len(matched_areas) / required_area_count)
