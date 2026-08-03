import re

from models.readme import ReadmeContent


class ReadmeParser:
    """
    Parses a GitHub README into structured information.

    Removes:

    - HTML
    - badges
    - images
    - markdown formatting
    - shields.io links

    Extracts:

    - title
    - tagline
    - first meaningful description
    - headings
    - sections
    """

    IMAGE_PATTERN = re.compile(r"!\[.*?\]\((.*?)\)")
    LINK_PATTERN = re.compile(r"\[(.*?)\]\((.*?)\)")
    HTML_PATTERN = re.compile(r"<[^>]+>")
    BADGE_PATTERN = re.compile(r"shields\.io", re.IGNORECASE)

    def parse(
        self,
        readme: str,
    ) -> ReadmeContent:

        if not readme:
            return ReadmeContent()

        images = self.IMAGE_PATTERN.findall(readme)

        badges = []

        for line in readme.splitlines():

            if self.BADGE_PATTERN.search(line):
                badges.append(line.strip())

        cleaned = self._clean(readme)

        lines = [
            line.strip()
            for line in cleaned.splitlines()
            if line.strip()
        ]

        title = ""
        tagline = ""
        description = ""

        headings = []

        sections = {}

        current_heading = None

        buffer = []

        for line in lines:

            if line.startswith("#"):

                if current_heading:

                    sections[current_heading] = "\n".join(buffer).strip()

                buffer = []

                heading = line.lstrip("#").strip()

                headings.append(heading)

                if not title:
                    title = heading

                current_heading = heading

                continue

            if current_heading:

                buffer.append(line)

            if not tagline and len(line) > 20:
                tagline = line
                continue

            if (
                not description
                and len(line) > 50
                and line != tagline
            ):
                description = line

        if current_heading:

            sections[current_heading] = "\n".join(buffer).strip()

        links = []

        for _, url in self.LINK_PATTERN.findall(readme):
            links.append(url)

        return ReadmeContent(
            title=title,
            tagline=tagline,
            description=description,
            headings=headings,
            badges=badges,
            links=links,
            images=images,
            code_blocks=readme.count("```"),
            sections=sections,
        )

    def _clean(
        self,
        text: str,
    ) -> str:
        """
        Remove HTML, images and excessive markdown.
        """

        text = self.HTML_PATTERN.sub("", text)

        text = self.IMAGE_PATTERN.sub("", text)

        text = re.sub(
            r"\[!\[.*?\]\(.*?\)\]\(.*?\)",
            "",
            text,
        )

        text = re.sub(
            r"`{3}[\s\S]*?`{3}",
            "",
            text,
        )

        text = re.sub(
            r"`([^`]*)`",
            r"\1",
            text,
        )

        text = text.replace("**", "")
        text = text.replace("__", "")
        text = text.replace("*", "")
        text = text.replace("_", "")

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        return text